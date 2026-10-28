"""predict.py için testler (PLAN 2.8). Sahte veriyle küçük bir koşu eğitip tahmin eder.

Çalıştırma: python -m pytest tests/test_predict.py -q
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml
from PIL import Image

from src.predict import main as predict_main
from src.train import main as train_main

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_COLUMNS = ["image_id", "y_true", "y_pred",
                    "prob_0", "prob_1", "prob_2", "prob_3", "prob_4"]


def save_random_images(folder: Path, names: list[str]) -> None:
    rng = np.random.default_rng(0)
    for name in names:
        pixels = rng.integers(0, 256, size=(64, 64, 3), dtype=np.uint8)
        Image.fromarray(pixels).save(folder / f"{name}.jpg")


@pytest.fixture
def run_dir(tmp_path):
    """14 sahte görüntü (8 train, 4 val, 2 test) ile bir kez 1 epoch eğitir."""
    ids = [f"s{i:02d}" for i in range(14)]
    save_random_images(tmp_path, ids)
    pd.DataFrame({"id_code": ids, "diagnosis": [i % 5 for i in range(14)]}).to_csv(
        tmp_path / "train.csv", index=False)
    pd.DataFrame({"id_code": ids,
                  "split": ["train"] * 8 + ["val"] * 4 + ["test"] * 2,
                  "note": [""] * 14}).to_csv(tmp_path / "splits.csv", index=False)

    config = yaml.safe_load((ROOT / "configs" / "e0_smoke_resnet18.yaml").read_text())
    config.update(
        pretrained=False, image_size=32, batch_size=4, epochs=1, num_workers=0,
        mixed_precision=False, data_root=str(tmp_path),
        splits_csv=str(tmp_path / "splits.csv"), output_dir=str(tmp_path / "runs"),
    )
    config_path = tmp_path / "tiny.yaml"
    config_path.write_text(yaml.safe_dump(config))
    train_main(["--config", str(config_path)])
    return next((tmp_path / "runs").iterdir())


def test_predict_val_writes_contract_columns(run_dir):
    predict_main(["--run", str(run_dir), "--split", "val"])
    predictions = pd.read_csv(run_dir / "val_predictions.csv")
    assert list(predictions.columns) == CONTRACT_COLUMNS
    assert len(predictions) == 4


def test_test_requires_final(run_dir):
    with pytest.raises(SystemExit) as error:
        predict_main(["--run", str(run_dir), "--split", "test"])
    assert error.value.code == 2
    assert not (run_dir / "test_predictions.csv").exists()


def test_test_with_final_runs_once(run_dir):
    predict_main(["--run", str(run_dir), "--split", "test", "--final"])
    output_path = run_dir / "test_predictions.csv"
    assert len(pd.read_csv(output_path)) == 2

    first_content = output_path.read_text()
    with pytest.raises(SystemExit):
        predict_main(["--run", str(run_dir), "--split", "test", "--final"])
    assert output_path.read_text() == first_content


def test_idrid_requires_data_root(run_dir):
    with pytest.raises(SystemExit):
        predict_main(["--run", str(run_dir), "--split", "idrid", "--final"])


def test_idrid_reads_labels(run_dir, tmp_path):
    idrid_dir = tmp_path / "idrid"
    idrid_dir.mkdir()
    save_random_images(idrid_dir, ["IDRiD_001", "IDRiD_002"])
    pd.DataFrame({"image_id": ["IDRiD_001", "IDRiD_002"], "diagnosis": [2, 0]}).to_csv(
        idrid_dir / "idrid_labels.csv", index=False)

    predict_main(["--run", str(run_dir), "--split", "idrid", "--final",
                  "--data-root", str(idrid_dir)])
    predictions = pd.read_csv(run_dir / "idrid_predictions.csv")
    assert len(predictions) == 2
    assert predictions["y_true"].tolist() == [2, 0]
