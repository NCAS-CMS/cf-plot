"""Pytest bootstrap for local repository imports."""

from pathlib import Path
import sys


# Ensure tests import the current checkout before any site-packages install.
REPO_ROOT = Path(__file__).resolve().parents[1]
repo_root_str = str(REPO_ROOT)
if sys.path[0] != repo_root_str:
    sys.path.insert(0, repo_root_str)
