"""Safety and cleanup checks for the human-approved baseline refresh."""

import pytest
from PIL import Image

from scripts import refresh_image_references as refresh


def _example(root, example_id="4", directory=None):
    directory = directory or refresh.GENERATED_DIRS[0]
    generated = root / directory / f"gen_fig_{example_id}.png"
    reference = (
        root / "tests" / "reference-example-images"
        / f"ref_fig_{example_id}.png"
    )
    generated.parent.mkdir(parents=True, exist_ok=True)
    reference.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (10, 10), "white").save(reference)
    Image.new("RGB", (10, 10), "red").save(generated)
    diff = generated.with_name(f"{generated.stem}-failed-diff.png")
    Image.new("RGB", (10, 10), "black").save(diff)
    return generated, reference, diff


def test_preview_changes_nothing(tmp_path, monkeypatch, capsys):
    generated, reference, diff = _example(tmp_path)
    original = reference.read_bytes()
    monkeypatch.setattr(refresh, "REPO_ROOT", tmp_path)
    assert refresh.main(["4"]) == 0
    assert reference.read_bytes() == original
    assert generated.exists() and diff.exists()
    assert "Preview only" in capsys.readouterr().out


def test_write_updates_only_selected_and_cleans_its_diff(
    tmp_path, monkeypatch
):
    generated, reference, diff = _example(tmp_path)
    other_generated, other_reference, other_diff = _example(tmp_path, "5")
    original_other = other_reference.read_bytes()
    monkeypatch.setattr(refresh, "REPO_ROOT", tmp_path)
    assert refresh.main(["4", "--write"]) == 0
    assert reference.read_bytes() == generated.read_bytes()
    assert not diff.exists()
    assert other_reference.read_bytes() == original_other
    assert other_generated.exists() and other_diff.exists()
    assert not list(reference.parent.glob("tmp*.png"))


def test_all_selects_both_directories_but_not_diffs(tmp_path):
    _example(tmp_path, "4")
    _example(tmp_path, "16b", refresh.GENERATED_DIRS[1])
    updates = refresh.plan_updates(tmp_path, [], all_generated=True)
    assert {update.reference.name for update in updates} == {
        "ref_fig_4.png", "ref_fig_16b.png"
    }


@pytest.mark.parametrize("problem", ["missing", "corrupt", "duplicate"])
def test_preflight_failure_writes_nothing(
    tmp_path, monkeypatch, problem
):
    _, reference, diff = _example(tmp_path, "4")
    generated, _, _ = _example(tmp_path, "5")
    original = reference.read_bytes()
    if problem == "missing":
        generated.unlink()
    elif problem == "corrupt":
        generated.write_bytes(b"not an image")
    else:
        _example(tmp_path, "5", refresh.GENERATED_DIRS[1])
    monkeypatch.setattr(refresh, "REPO_ROOT", tmp_path)
    assert refresh.main(["4", "5", "--write"]) == 1
    assert reference.read_bytes() == original
    assert diff.exists()


def test_missing_reference_is_not_silently_created(tmp_path):
    _, reference, _ = _example(tmp_path)
    reference.unlink()
    with pytest.raises(ValueError, match="Missing existing reference"):
        refresh.plan_updates(tmp_path, ["4"])


def test_path_traversal_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="Invalid example ID"):
        refresh.plan_updates(tmp_path, ["../../outside"])


def test_unchanged_reference_still_cleans_selected_diff(tmp_path):
    generated, reference, diff = _example(tmp_path)
    reference.write_bytes(generated.read_bytes())
    updates = refresh.plan_updates(tmp_path, ["4", "4"])
    assert len(updates) == 1
    assert not updates[0].changed
    refresh.apply_updates(updates)
    assert not diff.exists()
    assert generated.exists()
