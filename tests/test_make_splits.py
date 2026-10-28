"""make_splits için testler (PLAN 2.4). Sahte etiket ve grup tablolarıyla çalışır.

Çalıştırma: python -m pytest tests/test_make_splits.py -q
"""
import pandas as pd
import pytest

from src.make_splits import apply_duplicate_policy, main, make_splits

# 200 görüntü: sınıf 0:100, 1:20, 2:50, 3:10, 4:20 (sırayla atanır)
CLASS_COUNTS = {0: 100, 1: 20, 2: 50, 3: 10, 4: 20}


def make_labels() -> pd.DataFrame:
    diagnoses = [cls for cls, count in CLASS_COUNTS.items() for _ in range(count)]
    ids = [f"img{i:03d}" for i in range(len(diagnoses))]
    return pd.DataFrame({"id_code": ids, "diagnosis": diagnoses})


def make_groups(labels: pd.DataFrame) -> pd.DataFrame:
    """g0: img000+img001 (ikisi de 0, tutarlı) · g1: img002+img003 (0 ve 2 olmalı, çelişkili)."""
    labels = labels.set_index("id_code")
    rows = [
        (0, "img000", labels.loc["img000", "diagnosis"], False),
        (0, "img001", labels.loc["img001", "diagnosis"], False),
        (1, "img002", 0, True),
        (1, "img003", 2, True),
    ]
    return pd.DataFrame(rows, columns=["group_id", "id_code", "diagnosis", "conflicting"])


def test_policy_keeps_smallest_id():
    labels = make_labels()
    policy = apply_duplicate_policy(labels, make_groups(labels)).set_index("id_code")
    assert not policy.loc["img000", "excluded"] and policy.loc["img000", "note"] == ""
    assert policy.loc["img001", "excluded"] and policy.loc["img001", "note"] == "duplicate"


def test_policy_drops_conflicting_group():
    labels = make_labels()
    policy = apply_duplicate_policy(labels, make_groups(labels)).set_index("id_code")
    for image_id in ("img002", "img003"):
        assert policy.loc[image_id, "excluded"]
        assert policy.loc[image_id, "note"] == "conflicting_label"


def test_split_columns_and_values():
    labels = make_labels()
    table = make_splits(labels, make_groups(labels))
    assert list(table.columns) == ["id_code", "split", "note"]
    assert set(table["split"]) <= {"train", "val", "test", "excluded"}
    assert len(table) == 200
    assert table["id_code"].is_monotonic_increasing


def test_split_sizes():
    labels = make_labels()
    table = make_splits(labels, make_groups(labels))
    counts = table["split"].value_counts()
    assert counts["excluded"] == 3
    assert abs(counts["test"] - 30) <= 2
    assert abs(counts["val"] - 30) <= 2
    assert abs(counts["train"] - 137) <= 3


def test_stratified():
    labels = make_labels()
    table = make_splits(labels, make_groups(labels)).merge(labels, on="id_code")
    for split in ("train", "val", "test"):
        part = table[table["split"] == split]
        assert set(part["diagnosis"]) == {0, 1, 2, 3, 4}
        assert 0.40 <= (part["diagnosis"] == 0).mean() <= 0.62


def test_no_overlap():
    labels = make_labels()
    table = make_splits(labels, make_groups(labels))
    assert table["id_code"].is_unique


def test_deterministic_and_order_independent():
    labels = make_labels()
    groups = make_groups(labels)
    first = make_splits(labels, groups)
    second = make_splits(labels, groups)
    shuffled = make_splits(labels.sample(frac=1, random_state=1), groups)
    pd.testing.assert_frame_equal(first, second)
    pd.testing.assert_frame_equal(first, shuffled)


def test_main_refuses_overwrite(tmp_path):
    labels = make_labels()
    labels.to_csv(tmp_path / "train.csv", index=False)
    make_groups(labels).to_csv(tmp_path / "groups.csv", index=False)
    out_path = tmp_path / "aptos_splits.csv"
    out_path.write_text("eski icerik")
    with pytest.raises(SystemExit):
        main(["--data-root", str(tmp_path), "--groups", str(tmp_path / "groups.csv"),
              "--out", str(out_path)])
    assert out_path.read_text() == "eski icerik"
