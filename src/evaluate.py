"""Tahmin dosyasından metrik dosyası ve confusion matrix görselleri üretir (PLAN 2.10).

Ne yapar: `<split>_predictions.csv` dosyasını okur, `src.metrics.compute_metrics` ile metrikleri
hesaplar ve `metrics_<split>.json` ile iki confusion matrix görselini (ham + satır-normalize) yazar.
Rapordaki ve DENEY_KAYDI'ndaki sayıların tek kaynağı bu JSON dosyasıdır.

Nasıl çalıştırılır (proje kökünden):
    python -m src.evaluate --predictions outputs/runs/<run_id>/val_predictions.csv
    python -m src.evaluate --compare outputs/runs/<e1> outputs/runs/<e2> ...   (yalnız val; PLAN 3.5)
"""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # ekran olmadan (sunucu, Kaggle) çalışsın diye pyplot'tan önce seçilir
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import ConfusionMatrixDisplay

from src.metrics import CLASS_LABELS, compute_metrics, pick_best, severe_recall

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


def summarize_run(run_dir: Path) -> dict:
    """Bir koşunun val özetini döndürür. metrics_val.json yoksa val_predictions.csv'den üretir."""
    run_dir = Path(run_dir)
    metrics_path = run_dir / "metrics_val.json"
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text())
    else:
        metrics = evaluate_file(run_dir / "val_predictions.csv")
    config = yaml.safe_load((run_dir / "config.yaml").read_text())
    history = pd.read_csv(run_dir / "history.csv")
    best_row = history.loc[history["val_qwk"].idxmax()]
    return {
        "run_id": run_dir.name,
        "experiment": config.get("experiment", ""),
        "model": config["model"],
        "loss": config.get("loss", ""),
        "preprocessing": config.get("preprocessing", ""),
        "image_size": config.get("image_size", ""),
        "val_qwk": metrics["qwk"],
        "val_macro_f1": metrics["macro_f1"],
        "recall_3": metrics["recall_per_class"][3],
        "recall_4": metrics["recall_per_class"][4],
        "severe_recall": severe_recall(metrics),
        "epochs_run": int(len(history)),
        "best_epoch": int(best_row["epoch"]),
        "train_minutes": float(history["seconds"].sum() / 60),
    }


def write_markdown_table(table: pd.DataFrame, path: Path) -> None:
    """DataFrame'i elle '| a | b |' satırlarıyla yazar (tabulate bağımlılığı yok)."""
    lines = ["| " + " | ".join(table.columns) + " |",
             "|" + "---|" * len(table.columns)]
    for _, row in table.iterrows():
        cells = [f"{value:.3f}" if isinstance(value, float) else str(value) for value in row]
        lines.append("| " + " | ".join(cells) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_comparison_bar(table: pd.DataFrame, path: Path) -> None:
    """Her koşu için val QWK ve macro F1 yan yana çubuk grafiği."""
    labels = [f"{row.experiment}\n{row.model}" for row in table.itertuples()]
    positions = np.arange(len(table))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(positions - 0.2, table["val_qwk"], width=0.4, label="QWK")
    ax.bar(positions + 0.2, table["val_macro_f1"], width=0.4, label="Macro F1")
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=20)
    ax.set_ylim(0, 1)
    ax.set_title("Val karşılaştırması")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_learning_curves(run_dirs: list[Path], table: pd.DataFrame, path: Path) -> None:
    """Her koşunun epoch → val QWK eğrisi."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for run_dir, row in zip(run_dirs, table.itertuples()):
        history = pd.read_csv(Path(run_dir) / "history.csv")
        ax.plot(history["epoch"], history["val_qwk"], marker="o", label=f"{row.experiment} {row.model}")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Val QWK")
    ax.set_title("Öğrenme eğrileri")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def compare_runs(run_dirs: list[Path], out_dir: Path) -> pd.DataFrame:
    """Koşuları tek tabloda toplar; csv, md ve iki grafik yazar, tabloyu döndürür."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame([summarize_run(run_dir) for run_dir in run_dirs])
    table.to_csv(out_dir / "comparison.csv", index=False)
    write_markdown_table(table, out_dir / "comparison.md")
    save_comparison_bar(table, out_dir / "comparison_bar.png")
    save_learning_curves(run_dirs, table, out_dir / "learning_curves.png")
    return table


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Tahmin dosyasından metrics_<split>.json ve confusion matrix görselleri üretir."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--predictions", type=Path,
                      help="outputs/runs/<run_id>/<split>_predictions.csv")
    mode.add_argument("--compare", type=Path, nargs="+", metavar="RUN",
                      help="outputs/runs/<run_id> klasörleri (yalnız val sonuçları karşılaştırılır)")
    parser.add_argument("--out-dir", type=Path,
                        help="çıktı klasörü (varsayılan: --predictions için tahmin dosyasının klasörü, "
                             "--compare için outputs/figures)")
    args = parser.parse_args(argv)

    if args.compare:
        table = compare_runs(args.compare, args.out_dir or Path("outputs/figures"))
        print(table.to_string(index=False, float_format=lambda value: f"{value:.3f}"))
        candidates = [{"run_id": row.run_id, "qwk": row.val_qwk, "severe_recall": row.severe_recall}
                      for row in table.itertuples()]
        print(f"D-17'ye göre önde: {pick_best(candidates)}")
        return

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
