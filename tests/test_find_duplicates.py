"""src/find_duplicates.py için testler (sahte görüntüyle, gerçek veri gerekmez).

Çalıştırma: python -m pytest tests/test_find_duplicates.py -q
"""

import shutil

import numpy as np
import pandas as pd
from PIL import Image, ImageFilter

from src.find_duplicates import (
    build_group_table,
    find_pairs,
    group_pairs,
    main,
    md5_of_file,
    phash_bits,
)


def make_noise_image(seed: int) -> Image.Image:
    """16x16 rastgele renk bloğunu 256x256'ya büyütür (seed aynıysa görüntü aynı)."""
    pixels = np.random.RandomState(seed).randint(0, 256, (16, 16, 3), dtype=np.uint8)
    return Image.fromarray(pixels).resize((256, 256), Image.Resampling.NEAREST)


def test_find_pairs_by_distance():
    ids = ["a", "b", "c"]
    bits = np.zeros((3, 64), dtype=bool)
    bits[1, :3] = True
    bits[2, :20] = True

    pairs = find_pairs(ids, bits, max_distance=4)

    assert pairs == [("a", "b", 3)]


def test_find_pairs_zero_distance():
    bits = np.zeros((2, 64), dtype=bool)

    pairs = find_pairs(["a", "b"], bits, max_distance=0)

    assert pairs == [("a", "b", 0)]


def test_group_pairs_union():
    groups = group_pairs([("a", "b"), ("b", "c"), ("d", "e")])

    assert groups == {"a": 0, "b": 0, "c": 0, "d": 1, "e": 1}


def test_group_table_conflict():
    groups = {"a": 0, "b": 0, "c": 0, "d": 1, "e": 1}
    labels = pd.DataFrame(
        {"id_code": ["a", "b", "c", "d", "e"], "diagnosis": [0, 0, 0, 1, 2]}
    )

    table = build_group_table(groups, labels)

    assert len(table) == 5
    conflict_by_group = table.groupby("group_id")["conflicting"].first().to_dict()
    assert conflict_by_group == {0: False, 1: True}


def test_md5_same_bytes(tmp_path):
    first = tmp_path / "first.png"
    make_noise_image(0).save(first)
    copy = tmp_path / "copy.png"
    shutil.copy(first, copy)
    other = tmp_path / "other.png"
    make_noise_image(1).save(other)

    assert md5_of_file(first) == md5_of_file(copy)
    assert md5_of_file(first) != md5_of_file(other)


def test_phash_similar_images(tmp_path):
    original = tmp_path / "original.png"
    make_noise_image(0).save(original)
    blurred = tmp_path / "blurred.png"
    make_noise_image(0).filter(ImageFilter.GaussianBlur(1)).save(blurred)
    different = tmp_path / "different.png"
    make_noise_image(1).save(different)

    original_bits = phash_bits(original)
    similar_distance = (original_bits != phash_bits(blurred)).sum()
    different_distance = (original_bits != phash_bits(different)).sum()

    assert similar_distance <= 4
    assert different_distance > 10


def test_main_writes_reports(tmp_path):
    data_root = tmp_path / "data"
    data_root.mkdir()
    make_noise_image(0).save(data_root / "a.jpg")
    shutil.copy(data_root / "a.jpg", data_root / "b.jpg")
    make_noise_image(1).save(data_root / "d.jpg")
    (data_root / "train.csv").write_text("id_code,diagnosis\na,0\nb,2\nd,1\n")
    out_dir = tmp_path / "reports"

    main(["--data-root", str(data_root), "--out-dir", str(out_dir)])

    groups = pd.read_csv(out_dir / "duplicate_groups.csv", dtype={"id_code": str})
    assert len(groups) == 2
    assert groups["conflicting"].all()
    pairs = pd.read_csv(out_dir / "candidate_pairs.csv", dtype={"id_a": str, "id_b": str})
    assert list(pairs.columns) == [
        "id_a", "id_b", "distance", "same_md5", "diagnosis_a", "diagnosis_b"
    ]
