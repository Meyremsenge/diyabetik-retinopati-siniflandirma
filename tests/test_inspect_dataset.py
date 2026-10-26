"""src/inspect_dataset.py testleri (PLAN 1.6).

Sahte veri tmp_path içinde üretilir, gerçek APTOS gerekmez.
Çalıştırma: python -m pytest tests/test_inspect_dataset.py -q
"""
from collections import Counter
from pathlib import Path

import pandas as pd
import pytest
from PIL import Image

from src.inspect_dataset import load_labels, main, summarize_dataset


def make_fake_dataset(root: Path, extra_rows: str = "") -> Path:
    """4 satırlık CSV ve 3 görüntü üretir; 'd' görüntüsü bilerek eksiktir."""
    image_dir = root / "train_images"
    image_dir.mkdir()
    csv_path = root / "train.csv"
    csv_path.write_text("id_code,diagnosis\na,0\nb,0\nc,2\nd,4\n" + extra_rows)
    for name, size in [("a", (10, 8)), ("b", (10, 8)), ("c", (20, 16))]:
        Image.new("RGB", size).save(image_dir / f"{name}.png")
    return csv_path


def test_load_labels_reads_csv(tmp_path):
    csv_path = make_fake_dataset(tmp_path)
    df = load_labels(csv_path)
    assert len(df) == 4
    assert list(df.columns) == ["id_code", "diagnosis"]


def test_load_labels_rejects_wrong_columns(tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("image,level\na,0\n")
    with pytest.raises(ValueError, match="image"):
        load_labels(csv_path)


def test_summary_counts(tmp_path):
    csv_path = make_fake_dataset(tmp_path)
    summary = summarize_dataset(load_labels(csv_path), tmp_path / "train_images")
    assert summary["n_rows"] == 4
    assert summary["n_duplicate_ids"] == 0
    assert summary["invalid_labels"] == []
    assert summary["class_counts"] == {0: 2, 1: 0, 2: 1, 3: 0, 4: 1}


def test_summary_missing_files(tmp_path):
    csv_path = make_fake_dataset(tmp_path)
    summary = summarize_dataset(load_labels(csv_path), tmp_path / "train_images")
    assert summary["missing_files"] == ["d"]


def test_summary_image_sizes(tmp_path):
    csv_path = make_fake_dataset(tmp_path)
    summary = summarize_dataset(load_labels(csv_path), tmp_path / "train_images")
    assert summary["image_sizes"] == Counter({(10, 8): 2, (20, 16): 1})


def test_summary_invalid_label(tmp_path):
    csv_path = make_fake_dataset(tmp_path, extra_rows="e,7\n")
    summary = summarize_dataset(load_labels(csv_path), tmp_path / "train_images")
    assert summary["invalid_labels"] == [7]


def test_main_prints_report(tmp_path, capsys):
    make_fake_dataset(tmp_path)
    main(["--data-root", str(tmp_path)])
    output = capsys.readouterr().out
    assert "Satır sayısı: 4" in output
    assert "Eksik görüntü dosyası: 1" in output
