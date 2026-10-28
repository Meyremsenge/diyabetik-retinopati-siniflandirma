"""evaluate.py için testler (PLAN 2.10). Sahte tahmin dosyasıyla çalışır.

Çalıştırma: python -m pytest tests/test_evaluate.py -q
"""
import json
from pathlib import Path

import pandas as pd
import pytest

from src.evaluate import (
    evaluate_file, load_predictions, main, normalize_rows, split_from_filename,
)
from src.metrics import compute_metrics

Y_TRUE = [0, 0, 1, 2, 3, 4]
Y_PRED = [0, 1, 1, 2, 4, 4]


def write_fake_predictions(path: Path) -> Path:
    """Olasılıklar tahmin edilen sınıfa 0.6, diğerlerine 0.1 verir (toplam 1.0)."""
    rows = []
    for index, (true_label, predicted) in enumerate(zip(Y_TRUE, Y_PRED)):
        probabilities = [0.6 if cls == predicted else 0.1 for cls in range(5)]
        rows.append([f"p{index}", true_label, predicted] + probabilities)
    columns = ["image_id", "y_true", "y_pred", "prob_0", "prob_1", "prob_2", "prob_3", "prob_4"]
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False)
    return path


def test_split_from_filename():
    assert split_from_filename(Path("val_predictions.csv")) == "val"
    assert split_from_filename(Path("outputs/idrid_predictions.csv")) == "idrid"
    for bad_name in ("foo.csv", "train_predictions.csv"):
        with pytest.raises(ValueError):
            split_from_filename(Path(bad_name))


def test_load_predictions_missing_column(tmp_path):
    csv_path = write_fake_predictions(tmp_path / "val_predictions.csv")
    pd.read_csv(csv_path).drop(columns=["prob_4"]).to_csv(csv_path, index=False)
    with pytest.raises(ValueError, match="prob_4"):
        load_predictions(csv_path)


def test_normalize_rows():
    assert normalize_rows([[1, 1], [0, 0]]) == [[0.5, 0.5], [0.0, 0.0]]


def test_evaluate_writes_files(tmp_path):
    csv_path = write_fake_predictions(tmp_path / "val_predictions.csv")
    evaluate_file(csv_path)
    assert (tmp_path / "metrics_val.json").exists()
    assert (tmp_path / "confusion_matrix_val.png").exists()
    assert (tmp_path / "confusion_matrix_val_normalized.png").exists()


def test_metrics_json_matches_compute_metrics(tmp_path):
    csv_path = write_fake_predictions(tmp_path / "val_predictions.csv")
    returned = evaluate_file(csv_path)
    saved = json.loads((tmp_path / "metrics_val.json").read_text())
    assert saved == compute_metrics(Y_TRUE, Y_PRED)
    assert returned == saved
    assert saved["qwk"] == pytest.approx(13 / 14)
    assert saved["n"] == 6


def test_main_cli(tmp_path, capsys):
    csv_path = write_fake_predictions(tmp_path / "val_predictions.csv")
    main(["--predictions", str(csv_path)])
    assert "QWK: 0.929" in capsys.readouterr().out
