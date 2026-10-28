"""Tahmin dosyasından metrik dosyası ve confusion matrix görselleri üretir (PLAN 2.10).

Ne yapar: `<split>_predictions.csv` dosyasını okur, `src.metrics.compute_metrics` ile metrikleri
hesaplar ve `metrics_<split>.json` ile iki confusion matrix görselini (ham + satır-normalize) yazar.
Rapordaki ve DENEY_KAYDI'ndaki sayıların tek kaynağı bu JSON dosyasıdır.

Nasıl çalıştırılır (proje kökünden):
    python -m src.evaluate --predictions outputs/runs/<run_id>/val_predictions.csv
"""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # ekran olmadan (sunucu, Kaggle) çalışsın diye pyplot'tan önce seçilir
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay

from src.metrics import CLASS_LABELS, compute_metrics

PREDICTION_COLUMNS = ["image_id", "y_true", "y_pred",
                      "prob_0", "prob_1", "prob_2", "prob_3", "prob_4"]
VALID_SPLITS = ("val", "test", "idrid")
FILENAME_SUFFIX = "_predictions.csv"


def split_from_filename(path: Path) -> str:
    """`val_predictions.csv` → "val". Desen veya küme adı geçersizse ValueError verir."""
    name = Path(path).name
    if not name.endswith(FILENAME_SUFFIX):
        raise ValueError(f"Dosya adı <split>{FILENAME_SUFFIX} biçiminde olmalı: {name}")
    split = name[: -len(FILENAME_SUFFIX)]
    if split not in VALID_SPLITS:
        raise ValueError(f"Geçersiz küme {split!r}; geçerli: {VALID_SPLITS}")
    return split


def load_predictions(path: Path) -> pd.DataFrame:
    """Tahmin CSV'sini okur; sözleşmedeki sütunlar eksikse hangileri olduğunu söyler."""
    predictions = pd.read_csv(path, dtype={"image_id": str})
    missing_columns = [col for col in PREDICTION_COLUMNS if col not in predictions.columns]
    if missing_columns:
        raise ValueError(f"{path} içinde eksik sütunlar: {missing_columns}")
    return predictions


def normalize_rows(cm: list[list[int]]) -> list[list[float]]:
    """Her satırı kendi toplamına böler; toplamı 0 olan satır 0.0 kalır."""
    normalized = []
    for row in cm:
        total = sum(row)
        normalized.append([count / total if total else 0.0 for count in row])
    return normalized


def save_confusion_matrix(cm, path: Path, title: str, normalized: bool) -> None:
    """Confusion matrix'i PNG olarak kaydeder. Satır = gerçek sınıf, sütun = tahmin."""
    fig, ax = plt.subplots(figsize=(6, 5))
    display = ConfusionMatrixDisplay(np.array(cm), display_labels=CLASS_LABELS)
    display.plot(ax=ax, cmap="Blues", values_format=".2f" if normalized else "d")
    ax.set_xlabel("Tahmin")
    ax.set_ylabel("Gerçek")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def evaluate_file(predictions_path: Path, out_dir: Path | None = None) -> dict:
    """Metrikleri hesaplayıp dosyalara yazar ve metrik sözlüğünü döndürür."""
    predictions_path = Path(predictions_path)
    split = split_from_filename(predictions_path)
    out_dir = Path(out_dir) if out_dir else predictions_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    predictions = load_predictions(predictions_path)
    metrics = compute_metrics(predictions["y_true"], predictions["y_pred"])

    (out_dir / f"metrics_{split}.json").write_text(json.dumps(metrics, indent=2) + "\n")
    cm = metrics["confusion_matrix"]
    save_confusion_matrix(cm, out_dir / f"confusion_matrix_{split}.png",
                          f"Confusion matrix ({split})", normalized=False)
    save_confusion_matrix(normalize_rows(cm), out_dir / f"confusion_matrix_{split}_normalized.png",
                          f"Confusion matrix ({split}, satır-normalize)", normalized=True)
    return metrics


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Tahmin dosyasından metrics_<split>.json ve confusion matrix görselleri üretir."
    )
    parser.add_argument("--predictions", type=Path, required=True,
                        help="outputs/runs/<run_id>/<split>_predictions.csv")
    parser.add_argument("--out-dir", type=Path,
                        help="çıktı klasörü (varsayılan: tahmin dosyasının klasörü)")
    args = parser.parse_args(argv)

    split = split_from_filename(args.predictions)
    metrics = evaluate_file(args.predictions, args.out_dir)
    recalls = " / ".join(f"{value:.2f}" for value in metrics["recall_per_class"])
    print(f"{split} · n={metrics['n']}")
    print(f"QWK: {metrics['qwk']:.3f} · macro F1: {metrics['macro_f1']:.3f} · "
          f"accuracy: {metrics['accuracy']:.3f}")
    print(f"recall (0/1/2/3/4): {recalls}")
    print(f"Yazıldı: metrics_{split}.json, confusion_matrix_{split}.png, "
          f"confusion_matrix_{split}_normalized.png")


if __name__ == "__main__":
    main()
