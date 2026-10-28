"""Eğitilmiş modelle tahmin dosyası üretir (PLAN 2.8).

Ne yapar: Bir koşu klasöründeki `best.pt` ile val, test veya IDRiD görüntülerini tahmin edip
`<run>/<split>_predictions.csv` yazar. Test ve IDRiD "sınav kağıdı" gibidir: yalnız `--final`
bayrağıyla ve bir kez çalışır (D-08); dosya zaten varsa ikinci kez çalışmayı reddeder.

Nasıl çalıştırılır (proje kökünden):
    python -m src.predict --run outputs/runs/<run_id> --split val
    python -m src.predict --run outputs/runs/<run_id> --split test --final
    python -m src.predict --run outputs/runs/<run_id> --split idrid --final --data-root data/processed/idrid_512
"""
import argparse
from pathlib import Path

import pandas as pd
import torch
import yaml

from src.data import load_split_frame
from src.models import build_model
from src.train import make_loader, predict_loader
from src.utils import get_device

FINAL_SPLITS = ("test", "idrid")


def load_run(run_dir: Path, device: torch.device) -> tuple[torch.nn.Module, dict]:
    """Koşu klasöründeki config.yaml ve best.pt'den değerlendirme modunda modeli kurar."""
    config = yaml.safe_load((run_dir / "config.yaml").read_text())
    checkpoint = torch.load(run_dir / "best.pt", map_location=device)
    model = build_model(config["model"], config["num_classes"], pretrained=False)
    model.load_state_dict(checkpoint["model_state"])
    return model.to(device).eval(), config


def load_frame(split: str, data_root: Path, splits_csv: Path) -> pd.DataFrame:
    """image_id ve diagnosis sütunlu tabloyu verir (val/test bölme dosyasından, idrid kendi CSV'sinden)."""
    if split == "idrid":
        return pd.read_csv(data_root / "idrid_labels.csv", dtype={"image_id": str})
    return load_split_frame(data_root, splits_csv, split)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Eğitilmiş modelle tahmin dosyası üretir: <run>/<split>_predictions.csv"
    )
    parser.add_argument("--run", type=Path, required=True, help="outputs/runs/<run_id>")
    parser.add_argument("--split", choices=["val", "test", "idrid"], required=True)
    parser.add_argument("--data-root", type=Path,
                        help="val/test için varsayılan: run config'indeki data_root; "
                             "idrid için zorunlu (data/processed/idrid_512)")
    parser.add_argument("--final", action="store_true",
                        help="test ve idrid için zorunlu: dondurulmuş final modelle tek seferlik değerlendirme")
    args = parser.parse_args(argv)

    # Bu kontroller model yüklenmeden önce yapılır; test/IDRiD yanlışlıkla açılmasın
    output_path = args.run / f"{args.split}_predictions.csv"
    if args.split in FINAL_SPLITS:
        if not args.final:
            parser.error("test/idrid yalnız --final ile çalışır (dondurulmuş final model, tek seferlik).")
        if output_path.exists():
            raise SystemExit(
                f"{args.split} tahmini zaten yapılmış; bu küme bir kez kullanılır (D-08)."
            )
    if args.split == "idrid" and args.data_root is None:
        parser.error("idrid için --data-root zorunlu (ör. data/processed/idrid_512).")

    device = get_device()
    model, config = load_run(args.run, device)
    if args.data_root is not None:
        config["data_root"] = str(args.data_root)

    frame = load_frame(args.split, Path(config["data_root"]), Path(config["splits_csv"]))
    loader = make_loader(frame, config, args.split, device)
    predictions = predict_loader(model, loader, device)
    predictions.to_csv(output_path, index=False)
    print(f"{len(predictions)} satır yazıldı: {output_path}")


if __name__ == "__main__":
    main()
