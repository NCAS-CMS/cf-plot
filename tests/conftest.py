"""Pytest bootstrap for local repository imports."""

import sys
from pathlib import Path

import pytest

# Ensure tests import the current checkout before any site-packages install.
REPO_ROOT = Path(__file__).resolve().parents[1]
repo_root_str = str(REPO_ROOT)
if sys.path[0] != repo_root_str:
    sys.path.insert(0, repo_root_str)


def pytest_addoption(parser):
    """Add options for skipping certain aspects of testing, etc."""
    parser.addoption(
        "--skip-image-comparison",
        "-I",
        action="store_true",
        default=False,
        help="Skip reference image comparison while running tests.",
    )


@pytest.fixture(autouse=True)
def skip_image_comparison(request, monkeypatch):
    """Optionally skip reference image comparisons."""
    if request.config.getoption("--skip-image-comparison"):
        monkeypatch.setattr(
            request.module,
            "_assert_reference_match",
            lambda example_id: None,
            raising=False,
        )
