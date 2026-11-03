"""evaluate.py için testler (PLAN 2.10). Sahte tahmin dosyasıyla çalışır.

Çalıştırma: python -m pytest tests/test_evaluate.py -q
"""
import json
from pathlib import Path

import pandas as pd
import pytest

from src.evaluate import (
    compare_runs, evaluate_file, load_predictions, main, normalize_rows,
    split_from_filename, summarize_run,
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


def make_fake_run(run_dir: Path, experiment: str, perfect: bool) -> Path:
    """Sahte koşu klasörü: config.yaml, 3 satırlık history.csv ve val_predictions.csv."""
    run_dir.mkdir()
    (run_dir / "config.yaml").write_text(
        f"experiment: {experiment}\nmodel: resnet18\nloss: ce\npreprocessing: crop\nimage_size: 64\n")
    pd.DataFrame({"epoch": [1, 2, 3], "val_qwk": [0.5, 0.9, 0.7], "seconds": [60.0, 60.0, 60.0]}
                 ).to_csv(run_dir / "history.csv", index=False)
    write_fake_predictions(run_dir / "val_predictions.csv")
    if perfect:
        predictions = pd.read_csv(run_dir / "val_predictions.csv")
        predictions["y_pred"] = predictions["y_true"]
        predictions.to_csv(run_dir / "val_predictions.csv", index=False)
    return run_dir


def test_summarize_run_creates_metrics_if_missing(tmp_path):
    run_dir = make_fake_run(tmp_path / "run_a", "EA", perfect=False)
    summary = summarize_run(run_dir)
    assert (run_dir / "metrics_val.json").exists()
    assert summary["best_epoch"] == 2
    assert summary["train_minutes"] == pytest.approx(3.0)


def test_compare_writes_outputs(tmp_path):
    runs = [make_fake_run(tmp_path / "run_a", "EA", perfect=False),
            make_fake_run(tmp_path / "run_b", "EB", perfect=True)]
    out_dir = tmp_path / "figures"
    table = compare_runs(runs, out_dir)
    for name in ("comparison.csv", "comparison.md", "comparison_bar.png", "learning_curves.png"):
        assert (out_dir / name).exists()
    assert len(table) == 2
    assert len(pd.read_csv(out_dir / "comparison.csv")) == 2


def test_compare_prints_leader(tmp_path, capsys):
    run_a = make_fake_run(tmp_path / "run_a", "EA", perfect=False)
    run_b = make_fake_run(tmp_path / "run_b", "EB", perfect=True)
    main(["--compare", str(run_a), str(run_b), "--out-dir", str(tmp_path / "figures")])
    assert "önde: run_b" in capsys.readouterr().out


def test_predictions_and_compare_exclusive(tmp_path):
    csv_path = write_fake_predictions(tmp_path / "val_predictions.csv")
    with pytest.raises(SystemExit):
        main(["--predictions", str(csv_path), "--compare", str(tmp_path)])


def test_top_confusions():
    from src.evaluate import top_confusions
    cm = compute_metrics(Y_TRUE, Y_PRED)["confusion_matrix"]
    assert top_confusions(cm) == [(0, 1, 1), (3, 4, 1)]


def test_pick_error_examples_order():
    from src.evaluate import pick_error_examples
    rows = []
    for image_id, true_label, predicted, p in [("p0", 0, 0, 0.9), ("p1", 0, 4, 0.5),
                                                ("p2", 4, 3, 0.7), ("p3", 2, 1, 0.9)]:
        rest = (1 - p) / 4
        probabilities = [p if cls == predicted else rest for cls in range(5)]
        rows.append([image_id, true_label, predicted] + probabilities)
    columns = ["image_id", "y_true", "y_pred", "prob_0", "prob_1", "prob_2", "prob_3", "prob_4"]
    examples = pick_error_examples(pd.DataFrame(rows, columns=columns))
    assert list(examples["image_id"]) == ["p1", "p3", "p2"]


def test_errors_rejects_test_file(tmp_path):
    csv_path = write_fake_predictions(tmp_path / "test_predictions.csv")
    with pytest.raises(ValueError):
        main(["--errors", str(csv_path), "--data-root", str(tmp_path)])


def test_save_error_grid(tmp_path):
    from PIL import Image
    from src.evaluate import pick_error_examples, save_error_grid
    for index in range(3):
        Image.new("RGB", (32, 32)).save(tmp_path / f"p{index}.jpg")
    examples = pd.DataFrame({"image_id": ["p0", "p1", "p2"], "y_true": [0, 1, 2], "y_pred": [1, 2, 3],
                             "prob_0": 0.1, "prob_1": 0.2, "prob_2": 0.3, "prob_3": 0.4, "prob_4": 0.0})
    save_error_grid(examples, tmp_path, tmp_path / "errors.png")
    assert (tmp_path / "errors.png").exists()
