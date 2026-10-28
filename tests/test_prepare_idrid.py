"""prepare_idrid için testler (PLAN 3.4). Sahte CSV ve görüntülerle çalışır.

Çalıştırma: python -m pytest tests/test_prepare_idrid.py -q
"""
import pandas as pd
import pytest
from PIL import Image

from src.prepare_idrid import main, prepare_idrid, read_idrid_labels

IMAGE_COL = "Image name"
GRADE_COL = "Retinopathy grade"


def write_labels(path, rows):
    """Gerçek IDRiD CSV'sine benzer: sütun adında sondaki boşluk ve boş Unnamed sütunu."""
    table = pd.DataFrame(rows, columns=[IMAGE_COL, GRADE_COL])
    table["Risk of macular edema "] = 0
    table["Unnamed: 3"] = None
    table.to_csv(path, index=False)


@pytest.fixture
def idrid_dirs(tmp_path):
    train_images = tmp_path / "train_images"
    test_images = tmp_path / "test_images"
    train_images.mkdir()
    test_images.mkdir()
    for folder, name in [(train_images, "IDRiD_001"), (train_images, "IDRiD_002"),
                         (test_images, "IDRiD_001")]:
        Image.new("RGB", (300, 200), (90, 90, 90)).save(folder / f"{name}.jpg")
    write_labels(tmp_path / "train.csv", [("IDRiD_001", 2), ("IDRiD_002", 0)])
    write_labels(tmp_path / "test.csv", [("IDRiD_001", 4)])
    return tmp_path


def test_reads_labels_with_messy_columns(idrid_dirs):
    labels = read_idrid_labels(idrid_dirs / "train.csv", IMAGE_COL, GRADE_COL, "train")
    assert labels["image_id"].tolist() == ["train_IDRiD_001", "train_IDRiD_002"]
    assert labels["diagnosis"].tolist() == [2, 0]


def test_missing_column_raises(idrid_dirs):
    with pytest.raises(ValueError, match="Retinopathy grade"):
        read_idrid_labels(idrid_dirs / "train.csv", IMAGE_COL, "DR Grade", "train")


def test_invalid_grade_raises(tmp_path):
    write_labels(tmp_path / "bad.csv", [("IDRiD_001", 7)])
    with pytest.raises(ValueError):
        read_idrid_labels(tmp_path / "bad.csv", IMAGE_COL, GRADE_COL, "train")


def run_args(root, out_dir):
    return [
        "--train-csv", str(root / "train.csv"), "--test-csv", str(root / "test.csv"),
        "--train-images", str(root / "train_images"),
        "--test-images", str(root / "test_images"),
        "--out-dir", str(out_dir), "--size", "64",
    ]


def test_prepare_writes_images_and_labels(idrid_dirs):
    out_dir = idrid_dirs / "out"
    prepare_idrid(
        idrid_dirs / "train.csv", idrid_dirs / "test.csv",
        idrid_dirs / "train_images", idrid_dirs / "test_images", out_dir, size=64,
    )
    assert len(list(out_dir.glob("*.jpg"))) == 3
    with Image.open(out_dir / "test_IDRiD_001.jpg") as img:
        assert img.size == (64, 64)
    labels = pd.read_csv(out_dir / "idrid_labels.csv")
    assert list(labels.columns) == ["image_id", "diagnosis"]
    assert len(labels) == 3


def test_main_cli(idrid_dirs, capsys):
    out_dir = idrid_dirs / "out"
    main(run_args(idrid_dirs, out_dir))
    assert len(list(out_dir.glob("*.jpg"))) == 3
    assert "Sınıf dağılımı" in capsys.readouterr().out
