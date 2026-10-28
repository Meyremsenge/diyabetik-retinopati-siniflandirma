"""train.py için testler (PLAN 2.6). Sahte veriyle çalışır, gerçek veri ve GPU gerekmez.

Çalıştırma: python -m pytest tests/test_train.py -q
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml
from PIL import Image

from src.train import REQUIRED_KEYS, load_config, main, make_run_dir

ROOT = Path(__file__).resolve().parent.parent
PREDICTION_COLUMNS = ["image_id", "y_true", "y_pred",
                      "prob_0", "prob_1", "prob_2", "prob_3", "prob_4"]
HISTORY_COLUMNS = ["epoch", "train_loss", "val_loss", "val_qwk", "val_macro_f1", "lr", "seconds"]


@pytest.fixture
def tiny_config(tmp_path):
    """12 sahte görüntü (8 train, 4 val) ve bunlara bakan küçük bir config yazar."""
    rng = np.random.default_rng(0)
    ids = [f"s{i:02d}" for i in range(12)]
    for image_id in ids:
        pixels = rng.integers(0, 256, size=(64, 64, 3), dtype=np.uint8)
        Image.fromarray(pixels).save(tmp_path / f"{image_id}.jpg")
    pd.DataFrame({"id_code": ids, "diagnosis": [i % 5 for i in range(12)]}).to_csv(
        tmp_path / "train.csv", index=False)
    pd.DataFrame({"id_code": ids, "split": ["train"] * 8 + ["val"] * 4, "note": [""] * 12}).to_csv(
        tmp_path / "splits.csv", index=False)

    config = yaml.safe_load((ROOT / "configs" / "e0_smoke_resnet18.yaml").read_text())
    config.update(
        pretrained=False, image_size=32, batch_size=4, epochs=2, num_workers=0,
        mixed_precision=False, data_root=str(tmp_path),
        splits_csv=str(tmp_path / "splits.csv"), output_dir=str(tmp_path / "runs"),
    )
    config_path = tmp_path / "tiny.yaml"
    config_path.write_text(yaml.safe_dump(config))
    return config_path, tmp_path / "runs"


def single_run_dir(runs_dir: Path) -> Path:
    run_dirs = [path for path in runs_dir.iterdir() if path.is_dir()]
    assert len(run_dirs) == 1
    return run_dirs[0]


def test_load_config_parses_floats():
    config = load_config(ROOT / "configs" / "resnet50_baseline.yaml")
    assert config["lr"] == 1e-4
    assert isinstance(config["lr"], float)


def test_load_config_missing_key(tmp_path):
    config = yaml.safe_load((ROOT / "configs" / "resnet50_baseline.yaml").read_text())
    del config["model"]
    broken_path = tmp_path / "broken.yaml"
    broken_path.write_text(yaml.safe_dump(config))
    with pytest.raises(ValueError, match="model"):
        load_config(broken_path)


def test_required_keys_match_baseline_config():
    config = yaml.safe_load((ROOT / "configs" / "resnet50_baseline.yaml").read_text())
    assert sorted(REQUIRED_KEYS) == sorted(config)


def test_make_run_dir_name(tmp_path):
    first = make_run_dir(tmp_path, "resnet18", "smoke")
    second = make_run_dir(tmp_path, "resnet18", "smoke")
    assert re.match(r"^\d{8}-\d{4}_resnet18_smoke$", first.name)
    assert second.name.endswith("_2")


def test_end_to_end_tiny_run(tiny_config):
    config_path, runs_dir = tiny_config
    main(["--config", str(config_path)])

    run_dir = single_run_dir(runs_dir)
    for name in ["config.yaml", "env.txt", "best.pt", "history.csv", "val_predictions.csv"]:
        assert (run_dir / name).exists(), name

    history = pd.read_csv(run_dir / "history.csv")
    assert list(history.columns) == HISTORY_COLUMNS
    assert len(history) == 2

    predictions = pd.read_csv(run_dir / "val_predictions.csv")
    assert list(predictions.columns) == PREDICTION_COLUMNS
    assert len(predictions) == 4
    probabilities = predictions[[f"prob_{i}" for i in range(5)]].to_numpy()
    assert np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-4)
    assert (predictions["y_pred"].to_numpy() == probabilities.argmax(axis=1)).all()


def test_epochs_override(tiny_config):
    config_path, runs_dir = tiny_config
    main(["--config", str(config_path), "--epochs", "1"])
    history = pd.read_csv(single_run_dir(runs_dir) / "history.csv")
    assert len(history) == 1
