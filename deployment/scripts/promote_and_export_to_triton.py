#!/usr/bin/env python3
"""
CI-friendly promotion + export to Triton (MLflow aliases, no stages).

Key properties:
- Export + validate FIRST
- Promote (set alias) ONLY after successful export
- Uses MLflow Model Registry aliases (e.g. prod/staging/dev/archived)
- Drops TensorFlow support (sklearn + torch only)
- Triton repo output: <output_dir>/<model_name>/<version>/{model.onnx,config.pbtxt}
"""
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import mlflow

# Optional export deps (declared in pyproject extras)
import torch
import typer
from loguru import logger
from mlflow.models import Model
from mlflow.tracking import MlflowClient
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

app = typer.Typer(add_completion=False)

# Minimal dtype mapping for config.pbtxt (extend per-need)
MLFLOW_DTYPE_TO_TRITON: Dict[str, str] = {
    "float32": "TYPE_FP32",
    "float64": "TYPE_FP64",
    "int32": "TYPE_INT32",
    "int64": "TYPE_INT64",
    "bool": "TYPE_BOOL",
    "string": "TYPE_STRING",
}


@dataclass(frozen=True)
class ExportResult:
    model_uri: str
    export_path: Path
    triton_model_name: str
    triton_version: str
    platform: str
    max_batch_size: int


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _model_uri(model_name: str, version: str) -> str:
    return f"models:/{model_name}/{version}"


def _resolve_signature(model_uri: str) -> Any:
    """Load MLflow Model metadata and return signature."""
    local_path = mlflow.artifacts.download_artifacts(artifact_uri=model_uri)
    mlmodel_path = Path(local_path) / "MLmodel"
    if not mlmodel_path.exists():
        raise RuntimeError(f"MLmodel file not found at: {mlmodel_path}")
    mlmodel = Model.load(str(mlmodel_path))
    if mlmodel.signature is None:
        raise RuntimeError(
            f"Model at {model_uri} has no signature; cannot infer Triton config."
        )
    return mlmodel.signature


def _infer_io_from_signature(
    signature: Any,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Convert MLflow signature schema to a normalized IO list:
      [{"name": str, "dtype": str, "shape": list[int|None]}]

    Supports TensorSpec and ColSpec (tabular) as a fallback.
    """
    inputs: List[Dict[str, Any]] = []
    outputs: List[Dict[str, Any]] = []

    for field in signature.inputs:
        name = getattr(field, "name", "input")
        dtype = str(getattr(field, "type", getattr(field, "dtype", "float32"))).lower()
        shape = getattr(field, "shape", None)
        inputs.append(
            {"name": name, "dtype": dtype, "shape": list(shape) if shape else []}
        )

    for field in signature.outputs:
        name = getattr(field, "name", "output")
        dtype = str(getattr(field, "type", getattr(field, "dtype", "float32"))).lower()
        shape = getattr(field, "shape", None)
        outputs.append(
            {"name": name, "dtype": dtype, "shape": list(shape) if shape else []}
        )

    return inputs, outputs


def _max_batch_size(batch: Optional[int]) -> int:
    """
    Rule:
    - None or 1 => assume NO batching => max_batch_size = 0
    - >1        => batching enabled => max_batch_size = batch
    """
    if batch is None or batch <= 1:
        return 0
    return int(batch)


def _triton_dims(shape: List[Any], max_batch_size: int) -> List[int]:
    """
    Triton dims rules:
    - If max_batch_size > 0: batch dim is implicit -> OMIT first dim
    - If max_batch_size == 0: NO batching -> keep full dims

    Convert None/-1 to -1 (dynamic).
    """
    dims: List[int] = []
    for d in shape:
        if d is None:
            dims.append(-1)
        else:
            dims.append(int(d))
    if max_batch_size > 0 and len(dims) >= 1:
        return dims[1:]
    return dims


def _triton_dtype(dtype: str) -> str:
    return MLFLOW_DTYPE_TO_TRITON.get(dtype.lower(), "TYPE_FP32")


def _write_config_pbtxt(
    out_path: Path,
    triton_model_name: str,
    platform: str,
    max_batch_size: int,
    inputs: List[Dict[str, Any]],
    outputs: List[Dict[str, Any]],
) -> None:
    in_lines: List[str] = []
    for i in inputs:
        dims = (
            _triton_dims(i.get("shape", []), max_batch_size) if i.get("shape") else []
        )
        dims_str = ", ".join(str(d) for d in dims) if dims else "-1"
        in_lines.append(
            f'  {{ name: "{i["name"]}" data_type: {_triton_dtype(i["dtype"])} dims: [ {dims_str} ] }}'
        )

    out_lines: List[str] = []
    for o in outputs:
        dims = (
            _triton_dims(o.get("shape", []), max_batch_size) if o.get("shape") else []
        )
        dims_str = ", ".join(str(d) for d in dims) if dims else "-1"
        out_lines.append(
            f'  {{ name: "{o["name"]}" data_type: {_triton_dtype(o["dtype"])} dims: [ {dims_str} ] }}'
        )

    pbtxt = (
        f'name: "{triton_model_name}"\n'
        f'platform: "{platform}"\n'
        f"max_batch_size: {max_batch_size}\n\n"
        f"input [\n" + "\n".join(in_lines) + "\n]\n\n"
        "output [\n" + "\n".join(out_lines) + "\n]\n"
    )
    (out_path / "config.pbtxt").write_text(pbtxt, encoding="utf-8")


def _export_sklearn_to_onnx(
    model_uri: str,
    out_path: Path,
    inputs: List[Dict[str, Any]],
) -> None:
    """
    Export sklearn flavor to ONNX using skl2onnx.
    Requires signature inputs. For tabular, feature count is inferred as len(inputs).
    """
    sk_model = mlflow.sklearn.load_model(model_uri)

    if not inputs:
        raise RuntimeError(
            "No inputs in model signature; cannot export sklearn model to ONNX."
        )

    # TensorSpec: infer feature count from last dim if available, else fallback
    if inputs[0].get("shape"):
        shape = inputs[0]["shape"]
        feature_dim = (
            int(shape[-1]) if shape and shape[-1] not in (None, -1) else len(inputs)
        )
    else:
        feature_dim = len(inputs)

    initial_types = [("input", FloatTensorType([None, feature_dim]))]
    onnx_model = convert_sklearn(sk_model, initial_types=initial_types)

    out_file = out_path / "model.onnx"
    out_file.write_bytes(onnx_model.SerializeToString())


def _torch_dummy_from_shape(shape: List[Any]) -> torch.Tensor:
    dims = [(1 if (d is None or int(d) == -1) else int(d)) for d in shape]
    if not dims:
        raise RuntimeError("Cannot build dummy tensor from empty shape.")
    return torch.randn(*dims)


def _export_torch_to_onnx(
    model_uri: str,
    out_path: Path,
    inputs: List[Dict[str, Any]],
) -> None:
    """
    Export pytorch flavor to ONNX.
    Requires TensorSpec-style signature inputs with shapes.
    """
    pt_model = mlflow.pytorch.load_model(model_uri)
    pt_model.eval()

    if not inputs or not inputs[0].get("shape"):
        raise RuntimeError(
            "Torch ONNX export requires TensorSpec inputs with shapes in signature."
        )

    dummy = _torch_dummy_from_shape(inputs[0]["shape"])
    out_file = out_path / "model.onnx"

    torch.onnx.export(
        pt_model,
        dummy,
        out_file.as_posix(),
        export_params=True,
        opset_version=17,
        do_constant_folding=True,
        input_names=[inputs[0]["name"]],
        output_names=["output"],
        dynamic_axes={inputs[0]["name"]: {0: "batch"}, "output": {0: "batch"}},
    )


def _detect_flavor(model_uri: str) -> str:
    local_path = mlflow.artifacts.download_artifacts(artifact_uri=model_uri)
    mlmodel_path = Path(local_path) / "MLmodel"
    mlmodel = Model.load(str(mlmodel_path))
    flavors = mlmodel.flavors or {}
    if "sklearn" in flavors:
        return "sklearn"
    if "pytorch" in flavors:
        return "pytorch"
    raise RuntimeError(f"Unsupported flavors for Triton export: {list(flavors.keys())}")


def _validate_triton_export(export_path: Path) -> None:
    cfg = export_path / "config.pbtxt"
    model = export_path / "model.onnx"
    if not cfg.exists():
        raise RuntimeError(f"Missing config.pbtxt at {cfg}")
    if not model.exists():
        raise RuntimeError(f"Missing model.onnx at {model}")
    import onnx  # noqa: WPS433

    _ = onnx.load(model.as_posix())


def _write_history(
    output_dir: Path, triton_model_name: str, entry: Dict[str, Any]
) -> None:
    history_file = output_dir / triton_model_name / "deployment_history.json"
    history_file.parent.mkdir(parents=True, exist_ok=True)

    history: List[Dict[str, Any]] = []
    if history_file.exists():
        history = json.loads(history_file.read_text(encoding="utf-8"))

    history.append(entry)
    history_file.write_text(json.dumps(history, indent=2), encoding="utf-8")


def _promote_alias(
    client: MlflowClient,
    model_name: str,
    alias: str,
    version: str,
    archive_previous: bool,
    archived_alias: str,
) -> Optional[str]:
    prev_version: Optional[str]
    try:
        prev = client.get_model_version_by_alias(model_name, alias)
        prev_version = str(prev.version)
    except Exception:
        prev_version = None

    client.set_registered_model_alias(name=model_name, alias=alias, version=version)

    if archive_previous and prev_version and prev_version != version:
        client.set_registered_model_alias(
            name=model_name, alias=archived_alias, version=prev_version
        )

    return prev_version


@app.command()
def promote_and_export(
    model_name: str = typer.Option(..., help="Registered model name in MLflow."),
    version: str = typer.Option(
        ..., help="Target MLflow model version to export and promote."
    ),
    tracking_uri: Optional[str] = typer.Option(
        None, help="MLflow tracking URI (prefer env var in CI)."
    ),
    alias: str = typer.Option("prod", help="Lifecycle alias to set (e.g., prod)."),
    archived_alias: str = typer.Option(
        "archived", help="Alias to use for previous prod (if archiving)."
    ),
    archive_previous: bool = typer.Option(
        True, help="If true, archive previous aliased version."
    ),
    output_dir: Path = typer.Option(
        Path("deployment/triton/model_repository"), help="Triton model_repository root."
    ),
    triton_model_name: Optional[str] = typer.Option(
        None, help="Override Triton model directory name."
    ),
    batch: Optional[int] = typer.Option(
        None, help="None/1 => no batching; >1 => max_batch_size=batch."
    ),
    clean_version_dir: bool = typer.Option(
        True, help="If true, delete existing version dir before exporting."
    ),
) -> None:
    """
    Export to Triton model repository and then promote via MLflow aliasing.

    Order:
    1) Export + validate Triton artifact
    2) Promote alias ONLY after export succeeds
    """
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)

    client = MlflowClient()

    model_uri = _model_uri(model_name, version)
    logger.info("Target MLflow model URI: {}", model_uri)

    triton_name = triton_model_name or model_name
    export_path = output_dir / triton_name / str(version)

    if clean_version_dir and export_path.exists():
        shutil.rmtree(export_path)
    export_path.mkdir(parents=True, exist_ok=True)

    # 1) Export
    signature = _resolve_signature(model_uri)
    inputs, outputs = _infer_io_from_signature(signature)

    max_bs = _max_batch_size(batch)
    platform = "onnxruntime_onnx"

    flavor = _detect_flavor(model_uri)
    logger.info("Detected MLflow flavor: {}", flavor)

    if flavor == "sklearn":
        _export_sklearn_to_onnx(model_uri, export_path, inputs)
    elif flavor == "pytorch":
        _export_torch_to_onnx(model_uri, export_path, inputs)
    else:
        raise RuntimeError(f"Unsupported flavor: {flavor}")

    _write_config_pbtxt(
        out_path=export_path,
        triton_model_name=triton_name,
        platform=platform,
        max_batch_size=max_bs,
        inputs=inputs,
        outputs=outputs,
    )

    _validate_triton_export(export_path)

    # 2) Promote
    prev_version = _promote_alias(
        client=client,
        model_name=model_name,
        alias=alias,
        version=version,
        archive_previous=archive_previous,
        archived_alias=archived_alias,
    )

    history_entry = {
        "timestamp_utc": _now_utc_iso(),
        "mlflow_model_name": model_name,
        "mlflow_version": version,
        "mlflow_alias_set": alias,
        "previous_version_for_alias": prev_version,
        "archived_alias": archived_alias if archive_previous else None,
        "triton_model_name": triton_name,
        "triton_version": str(version),
        "export_path": str(export_path),
        "platform": platform,
        "max_batch_size": max_bs,
        "flavor": flavor,
        "model_uri": model_uri,
    }
    _write_history(output_dir, triton_name, history_entry)

    typer.secho("Export + promotion completed.", fg=typer.colors.GREEN)
    typer.echo(f"Exported to: {export_path}")
    typer.echo(f"Set alias: {model_name}@{alias} -> v{version}")
    if archive_previous and prev_version and prev_version != version:
        typer.echo(
            f"Archived previous {alias}: v{prev_version} via alias '{archived_alias}'"
        )


if __name__ == "__main__":
    app()
