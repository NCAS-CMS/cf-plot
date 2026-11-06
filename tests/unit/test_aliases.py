import pytest
from unittest.mock import patch

import cfplot as cfp


def test_scatter_calls_lineplot_with_lines_false():
    """Test that scatter delegates to lineplot with lines=False."""
    kwargs = {"x": [1, 2, 3], "y": [4, 5, 6], "color": "red"}

    module = cfp.scatter.__module__

    with patch(f"{module}.lineplot") as mock_lineplot:
        cfp.scatter(**kwargs)

    mock_lineplot.assert_called_once_with(lines=False, **kwargs)


def test_scatter_rejects_lines_argument():
    """Test that scatter does not accept the lines argument."""
    with pytest.raises(
            ValueError, match=(
                "'lines' is not a valid keyword argument for cfp.scatter"
        )
    ):
        cfp.scatter(lines=True)
