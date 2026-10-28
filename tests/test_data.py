"""data.py için testler (PLAN 2.5). Sahte görüntü ve tablolarla çalışır.

Çalıştırma: python -m pytest tests/test_data.py -q
"""
import numpy as np
import pandas as pd
import pytest
import torch
from PIL import Image
from torch.utils.data import DataLoader

from src.data import RetinaDataset, get_transforms, load_split_frame


@pytest.fixture
def image_setup(tmp_path):
    rng = np.random.default_rng(0)
    for name in ("x1", "x2", "x3"):
        pixels = rng.integers(0, 256, size=(600, 600, 3), dtype=np.uint8)
        Image.fromarray(pixels).save(tmp_path / f"{name}.jpg")
    df = pd.DataFrame({"image_id": ["x1", "x2", "x3"], "diagnosis": [0, 3, 4]})
    return df, tmp_path


def transform_names(split: str) -> list[str]:
    return [type(t).__name__ for t in get_transforms(split, 64).transforms]


def test_item_shape_and_types(image_setup):
    df, image_dir = image_setup
    tensor, label, image_id = RetinaDataset(df, image_dir, get_transforms("val", 64))[1]
    assert tensor.shape == (3, 64, 64)
    assert tensor.dtype == torch.float32
    assert label == 3 and isinstance(label, int)
    assert image_id == "x2"


def test_len(image_setup):
    df, image_dir = image_setup
    assert len(RetinaDataset(df, image_dir, get_transforms("val", 64))) == 3


def test_eval_transform_is_deterministic(image_setup):
    df, image_dir = image_setup
    dataset = RetinaDataset(df, image_dir, get_transforms("val", 64))
    assert torch.equal(dataset[0][0], dataset[0][0])


def test_train_has_augmentation_eval_does_not():
    train_names = transform_names("train")
    assert "RandomHorizontalFlip" in train_names
    assert "ColorJitter" in train_names
    for split in ("val", "test", "idrid", "demo"):
        names = transform_names(split)
        assert "RandomHorizontalFlip" not in names
        assert "ColorJitter" not in names


def test_unknown_split_raises():
    with pytest.raises(ValueError):
        get_transforms("foo", 64)


def test_dataloader_batch(image_setup):
    df, image_dir = image_setup
    dataset = RetinaDataset(df, image_dir, get_transforms("val", 64))
    images, labels, ids = next(iter(DataLoader(dataset, batch_size=2)))
    assert images.shape == (2, 3, 64, 64)
    assert labels.tolist() == [0, 3]
    assert list(ids) == ["x1", "x2"]


def test_load_split_frame(tmp_path):
    pd.DataFrame({"id_code": list("abcd"), "diagnosis": [0, 1, 2, 3]}).to_csv(
        tmp_path / "train.csv", index=False)
    splits_csv = tmp_path / "splits.csv"
    pd.DataFrame({"id_code": list("abcd"),
                  "split": ["train", "val", "excluded", "train"],
                  "note": ["", "", "duplicate", ""]}).to_csv(splits_csv, index=False)

    frame = load_split_frame(tmp_path, splits_csv, "train")
    assert list(frame.columns) == ["image_id", "diagnosis"]
    assert frame["image_id"].tolist() == ["a", "d"]
    with pytest.raises(ValueError):
        load_split_frame(tmp_path, splits_csv, "excluded")
