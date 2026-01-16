import importlib


def test_import_package_root() -> None:
    mod = importlib.import_module("spatiotemporal_lab")
    assert mod is not None
