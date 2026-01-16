#!/usr/bin/env sh
set -eu

# tools/setup_notebooks.sh
# Configure git-friendly Jupyter Notebook workflows:
# - nbstripout: strips cell outputs on commit (git clean filter)
# - nbdime: better diffs/merges for .ipynb files
#
# Run from the repository root:
#   sh tools/setup_notebooks.sh
#
# Notes:
# - nbstripout is configured as a *required* filter when installed. If the filter
#   is missing on a machine, git operations can fail. Ensure collaborators run this script.
# - nbdime git integration is applied to the *current repository* when no --global/--system
#   flags are provided. (Recommended for template repos.)

if [ ! -d ".git" ]; then
  echo "ERROR: must be run from within a git repository (repo root recommended)."
  exit 1
fi

install_pkg() {
  pkg="$1"
  if command -v uv >/dev/null 2>&1; then
    uv pip install "$pkg"
  else
    python -m pip install --upgrade pip >/dev/null 2>&1 || true
    python -m pip install "$pkg"
  fi
}

echo "Installing notebook tooling (nbstripout, nbdime)..."
install_pkg "nbstripout"
install_pkg "nbdime"

echo "Configuring nbstripout git filter using .gitattributes..."
# Install the filter + register attributes in the provided .gitattributes file.
# Docs: nbstripout --install --attributes .gitattributes
nbstripout --install --attributes .gitattributes

echo "Configuring nbdime git integration for this repository..."
# When neither --global nor --system is given, config is applied to the current repository.
# Docs: nbdime config-git --enable
nbdime config-git --enable

echo "Done."
echo ""
echo "Tip: If you also want global integration (optional), run:"
echo "  nbdime config-git --enable --global"
