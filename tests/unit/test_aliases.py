from unittest.mock import patch

import pytest

import cfplot as cfp


def test_scatter_calls_lineplot_with_lines_false():
    """Test that scatter delegates to lineplot with lines=False."""
    kwargs = {"x": [1, 2, 3], "y": [4, 5, 6], "color": "red"}

    module = cfp.scatter.__module__

    with patch(f"{module}.lineplot") as mock_lineplot:
        cfp.scatter(**kwargs)

    mock_lineplot.assert_called_once_with(lines=False, marker="o", **kwargs)


def test_scatter_accepts_positional_arguments():
    """Test that scatter accepts positional arguments like lineplot."""
    f = object()

    module = cfp.scatter.__module__

    with patch(f"{module}.lineplot") as mock_lineplot:
        cfp.scatter(f)

    mock_lineplot.assert_called_once_with(f, lines=False, marker="o")


def test_scatter_rejects_lines_argument():
    """Test that scatter does not accept the lines argument."""
    with pytest.raises(
        ValueError,
        match="'lines' is not a valid keyword argument for cfp.scatter",
    ):
        cfp.scatter(lines=True)


def test_scatter_defaults_to_circle_marker():
    """Test that scatter defaults to a circle marker."""
    module = cfp.scatter.__module__

    with patch(f"{module}.lineplot") as mock_lineplot:
        cfp.scatter()

    mock_lineplot.assert_called_once_with(lines=False, marker="o")


def test_scatter_accepts_custom_marker():
    """Test that scatter accepts a user-defined marker."""
    module = cfp.scatter.__module__

    with patch(f"{module}.lineplot") as mock_lineplot:
        cfp.scatter(marker="x")

    mock_lineplot.assert_called_once_with(lines=False, marker="x")
