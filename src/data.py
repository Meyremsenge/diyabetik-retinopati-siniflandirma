"""Eğitim için veri sınıfı ve görüntü dönüşümleri (PLAN 2.5).

Ne yapar: 512 px'lik kopyadan görüntüyü okuyup modele uygun tensöre çevirir.
Augmentation (aynalama, döndürme, parlaklık) yalnız train dönüşümündedir;
val, test, idrid ve demo aynı deterministik zinciri kullanır.

Nasıl kullanılır (train.py / predict.py içinden):
    frame = load_split_frame(data_root, Path("splits/aptos_splits.csv"), "train")
    dataset = RetinaDataset(frame, data_root, get_transforms("train", 224))
"""
from pathlib import Path

import pandas as pd
import torch
from PIL import Image
from torchvision.transforms import v2

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
EVAL_SPLITS = ("val", "test", "idrid", "demo")
SPLIT_NAMES = ("train", "val", "test")


class RetinaDataset(torch.utils.data.Dataset):
    """df'deki her satır için (tensör, etiket, image_id) döndürür."""

    def __init__(self, df: pd.DataFrame, image_dir: Path, transform):
        self.df = df.reset_index(drop=True)
        self.image_dir = Path(image_dir)
        self.transform = transform

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int, str]:
        row = self.df.iloc[index]
        image_id = str(row["image_id"])
        image = Image.open(self.image_dir / f"{image_id}.jpg").convert("RGB")
        return self.transform(image), int(row["diagnosis"]), image_id


def get_transforms(split: str, image_size: int) -> v2.Compose:
    """Train için augmentation'lı, EVAL_SPLITS için deterministik dönüşüm zinciri."""
    to_normalized_tensor = [
        v2.ToImage(),
        v2.ToDtype(torch.float32, scale=True),
        v2.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ]
    resize = v2.Resize((image_size, image_size))

    if split == "train":
        augmentations = [
            v2.RandomHorizontalFlip(),
            v2.RandomVerticalFlip(),
            v2.RandomRotation(30),
            v2.ColorJitter(brightness=0.2, contrast=0.2),
        ]
        return v2.Compose([resize] + augmentations + to_normalized_tensor)
    if split in EVAL_SPLITS:
        return v2.Compose([resize] + to_normalized_tensor)
    raise ValueError(f"Bilinmeyen split: {split!r}. Geçerli: train, {', '.join(EVAL_SPLITS)}")


def load_split_frame(data_root: Path, splits_csv: Path, split: str) -> pd.DataFrame:
    """İstenen split'in image_id ve diagnosis sütunlu, image_id'ye göre sıralı tablosunu verir."""
    if split not in SPLIT_NAMES:
        raise ValueError(f"split {SPLIT_NAMES} içinden biri olmalı, gelen: {split!r}")
    labels = pd.read_csv(Path(data_root) / "train.csv", dtype={"id_code": str})
    splits = pd.read_csv(splits_csv, dtype={"id_code": str}, keep_default_na=False)
    merged = labels.merge(splits[["id_code", "split"]], on="id_code")
    chosen = merged[merged["split"] == split]
    chosen = chosen.rename(columns={"id_code": "image_id"})
    return chosen[["image_id", "diagnosis"]].sort_values("image_id").reset_index(drop=True)
