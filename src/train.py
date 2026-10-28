"""Config dosyasına göre modeli eğitir (PLAN 2.6).

Ne yapar: Her epoch'ta train kümesinde eğitir, val kümesinde QWK ölçer, en iyi modeli
(`best.pt`) ve kayıtları `outputs/runs/<run_id>/` altına yazar. Erken durdurma uygular.
Test kümesi ve IDRiD burada kullanılmaz; yalnız train ve val görülür.

Nasıl çalıştırılır (proje kökünden):
    python -m src.train --config configs/resnet50_baseline.yaml
Duman testi (hattı hızlıca dener, sonucu raporlanmaz):
    python -m src.train --config configs/e0_smoke_resnet18.yaml --limit 64 --epochs 1
"""
import argparse
import platform
import subprocess
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import torch
import torchvision
import yaml
from torch.utils.data import DataLoader

from src.data import RetinaDataset, get_transforms, load_split_frame
from src.metrics import compute_metrics
from src.models import build_model
from src.utils import get_device, set_seed

REQUIRED_KEYS = [
    "experiment", "run_label", "model", "pretrained", "preprocessing", "num_classes",
    "image_size", "batch_size", "epochs", "early_stopping_patience", "lr", "weight_decay",
    "loss", "mixed_precision", "num_workers", "seed", "data_root", "splits_csv", "output_dir",
]
PROBABILITY_COLUMNS = [f"prob_{i}" for i in range(5)]


def load_config(path: Path) -> dict:
    """YAML config'i okur; eksik anahtar varsa adını söyleyerek hata verir."""
    config = yaml.safe_load(Path(path).read_text())
    missing_keys = [key for key in REQUIRED_KEYS if key not in config]
    if missing_keys:
        raise ValueError(f"{path} içinde eksik anahtarlar: {missing_keys}")
    return config


def make_run_dir(output_dir: Path, model_name: str, run_label: str) -> Path:
    """<tarih-saat>_<model>_<etiket> klasörünü oluşturur; varsa sonuna _2, _3 ekler."""
    base_name = f"{datetime.now():%Y%m%d-%H%M}_{model_name}_{run_label}"
    run_dir = Path(output_dir) / base_name
    suffix = 2
    while run_dir.exists():
        run_dir = Path(output_dir) / f"{base_name}_{suffix}"
        suffix += 1
    run_dir.mkdir(parents=True)
    return run_dir


def write_env_txt(run_dir: Path, device: torch.device) -> None:
    """Koşunun ortam bilgisini (sürümler, cihaz, git commit) env.txt'ye yazar."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit = "bilinmiyor"

    device_name = torch.cuda.get_device_name(0) if device.type == "cuda" else device.type
    lines = [
        f"python: {platform.python_version()}",
        f"torch: {torch.__version__}",
        f"torchvision: {torchvision.__version__}",
        f"torch.version.cuda: {torch.version.cuda}",
        f"cihaz: {device_name}",
        f"git commit: {commit}",
        f"tarih: {datetime.now():%Y-%m-%d %H:%M}",
    ]
    (run_dir / "env.txt").write_text("\n".join(lines) + "\n")


def train_one_epoch(model, loader, criterion, optimizer, device, scaler) -> float:
    """Bir epoch eğitir, görüntü başına ortalama train loss'u döndürür."""
    model.train()
    total_loss = 0.0
    for images, labels, _ in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        if scaler is not None:
            with torch.autocast("cuda", dtype=torch.float16):
                loss = criterion(model(images), labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
        total_loss += loss.item() * len(labels)
    return total_loss / len(loader.dataset)


def predict_loader(model, loader, device) -> pd.DataFrame:
    """Her görüntü için tahmin tablosu üretir (sütunlar TEKNIK_TASARIM §7 sözleşmesi)."""
    model.eval()
    rows = []
    with torch.no_grad():
        for images, labels, image_ids in loader:
            probabilities = torch.softmax(model(images.to(device)), dim=1).cpu()
            predicted = probabilities.argmax(dim=1)
            for image_id, label, guess, probs in zip(image_ids, labels, predicted, probabilities):
                rows.append([image_id, int(label), int(guess)] + probs.tolist())
    return pd.DataFrame(rows, columns=["image_id", "y_true", "y_pred"] + PROBABILITY_COLUMNS)


def evaluate_loss(model, loader, criterion, device) -> float:
    """Doğrulama kümesinde görüntü başına ortalama loss'u döndürür."""
    model.eval()
    total_loss = 0.0
    with torch.no_grad():
        for images, labels, _ in loader:
            loss = criterion(model(images.to(device)), labels.to(device))
            total_loss += loss.item() * len(labels)
    return total_loss / len(loader.dataset)


def make_loader(frame: pd.DataFrame, config: dict, split: str, device: torch.device) -> DataLoader:
    dataset = RetinaDataset(
        frame, Path(config["data_root"]), get_transforms(split, config["image_size"])
    )
    return DataLoader(
        dataset,
        batch_size=config["batch_size"],
        shuffle=(split == "train"),
        num_workers=config["num_workers"],
        pin_memory=(device.type == "cuda"),
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Config dosyasına göre modeli eğitir.")
    parser.add_argument("--config", type=Path, required=True, help="configs/<ad>.yaml")
    parser.add_argument("--data-root", help="config'teki data_root'u ezer")
    parser.add_argument("--output-dir",
                        help="config'teki output_dir'i ezer (Kaggle: /kaggle/working/outputs/runs)")
    parser.add_argument("--limit", type=int,
                        help="duman testi: train ve val'den rastgele en fazla N görüntü")
    parser.add_argument("--epochs", type=int, help="config'teki epochs'u ezer")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    if args.data_root:
        config["data_root"] = args.data_root
    if args.output_dir:
        config["output_dir"] = args.output_dir
    if args.epochs:
        config["epochs"] = args.epochs
    if config["loss"] != "ce":
        raise ValueError(f"Desteklenmeyen loss: {config['loss']!r} (şimdilik yalnız 'ce')")

    set_seed(config["seed"])
    device = get_device()

    train_frame = load_split_frame(Path(config["data_root"]), Path(config["splits_csv"]), "train")
    val_frame = load_split_frame(Path(config["data_root"]), Path(config["splits_csv"]), "val")
    if args.limit:
        train_frame = train_frame.sample(n=min(args.limit, len(train_frame)), random_state=config["seed"])
        val_frame = val_frame.sample(n=min(args.limit, len(val_frame)), random_state=config["seed"])
    train_loader = make_loader(train_frame, config, "train", device)
    val_loader = make_loader(val_frame, config, "val", device)

    model = build_model(config["model"], config["num_classes"], config["pretrained"]).to(device)
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=config["lr"], weight_decay=config["weight_decay"]
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config["epochs"])

    # Karma duyarlılık yalnız CUDA'da çalışır; mps ve cpu'da kapalı kalır
    use_mixed_precision = device.type == "cuda" and config["mixed_precision"]
    scaler = torch.amp.GradScaler("cuda") if use_mixed_precision else None

    run_dir = make_run_dir(Path(config["output_dir"]), config["model"], config["run_label"])
    (run_dir / "config.yaml").write_text(yaml.safe_dump(config))
    write_env_txt(run_dir, device)

    history_rows = []
    best_qwk = float("-inf")
    epochs_without_improvement = 0
    for epoch in range(1, config["epochs"] + 1):
        started = time.time()
        learning_rate = optimizer.param_groups[0]["lr"]
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, device, scaler)
        scheduler.step()
        val_loss = evaluate_loss(model, val_loader, criterion, device)
        predictions = predict_loader(model, val_loader, device)
        metrics = compute_metrics(predictions["y_true"], predictions["y_pred"])

        history_rows.append({
            "epoch": epoch, "train_loss": train_loss, "val_loss": val_loss,
            "val_qwk": metrics["qwk"], "val_macro_f1": metrics["macro_f1"],
            "lr": learning_rate, "seconds": time.time() - started,
        })
        # Koşu yarıda kesilse bile geçmiş kaybolmasın diye her epoch dosya yeniden yazılır
        pd.DataFrame(history_rows).to_csv(run_dir / "history.csv", index=False)
        print(f"epoch {epoch}/{config['epochs']} · train_loss {train_loss:.4f} · "
              f"val_loss {val_loss:.4f} · val_qwk {metrics['qwk']:.4f}")

        if metrics["qwk"] > best_qwk:
            best_qwk = metrics["qwk"]
            epochs_without_improvement = 0
            torch.save(
                {"model_state": model.state_dict(), "config": config,
                 "epoch": epoch, "val_qwk": metrics["qwk"]},
                run_dir / "best.pt",
            )
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= config["early_stopping_patience"]:
                print(f"Erken durdurma: {epochs_without_improvement} epoch iyileşme yok.")
                break

    # Son epoch'un değil, en iyi epoch'un tahminleri kaydedilir
    best = torch.load(run_dir / "best.pt", map_location=device)
    model.load_state_dict(best["model_state"])
    predict_loader(model, val_loader, device).to_csv(run_dir / "val_predictions.csv", index=False)
    print(f"Koşu klasörü: {run_dir}")


if __name__ == "__main__":
    main()
