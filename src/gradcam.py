"""Grad-CAM ısı haritası üretir (PLAN 3.7, 5.1).

Ne yapar: Tek bir retina görüntüsü için modelin kararında hangi bölgelerin etkili olduğunu
gösteren ısı haritasını görüntünün üstüne bindirir. Bu bir lezyon tespiti DEĞİLDİR; yalnız
modelin dikkat ettiği bölgeleri gösterir. Demo (app/streamlit_app.py) `explain_image` fonksiyonunu kullanır.

Nasıl çalıştırılır (proje kökünden):
    python -m src.gradcam --run outputs/runs/<run_id> --image data/processed/aptos_512/<id>.jpg
    (çıktı varsayılan: outputs/figures/gradcam_<dosya adı>.png)

    python -m src.gradcam --run outputs/runs/<run_id> --gallery
    (val_predictions.csv'den her sınıf için 1 doğru + 1 yanlış örnek; çıktı: outputs/figures/gallery/)
    Galeri yalnız val kullanır; test/IDRiD tahmin dosyaları okunmaz.
"""
import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # pencere açmadan dosyaya çizer
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from PIL import Image
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

from src.data import get_transforms
from src.predict import load_run
from src.preprocessing import BLACK_THRESHOLD, ben_graham, prepare_image
from src.utils import get_device


def get_target_layer(model: torch.nn.Module, model_name: str) -> torch.nn.Module:
    """Grad-CAM'in bakacağı son evrişim katmanını döndürür."""
    if model_name in ("resnet18", "resnet50"):
        return model.layer4[-1]
    if model_name == "efficientnet_b3":
        return model.features[-1]
    raise ValueError(f"Grad-CAM için bilinmeyen model: {model_name!r}")


def compute_gradcam(
    model: torch.nn.Module,
    model_name: str,
    input_tensor: torch.Tensor,
    target_class: int | None = None,
) -> np.ndarray:
    """(1, 3, H, W) girdi için (H, W) boyutunda, 0-1 aralığında ısı haritası üretir.

    target_class None ise modelin kendi tahmini açıklanır. Gradyan gerektiği için
    bu fonksiyon `torch.no_grad()` içinde çağrılmamalıdır.
    """
    layer = get_target_layer(model, model_name)
    targets = None if target_class is None else [ClassifierOutputTarget(target_class)]
    with GradCAM(model=model, target_layers=[layer]) as cam:
        grayscale = cam(input_tensor=input_tensor, targets=targets)[0]
    return grayscale.astype(np.float32)


def overlay(rgb_image: Image.Image, cam: np.ndarray) -> np.ndarray:
    """Isı haritasını görüntünün üstüne bindirir; (H, W, 3) uint8 döndürür."""
    height, width = cam.shape
    resized = rgb_image.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
    rgb_float = np.asarray(resized, dtype=np.float32) / 255.0
    return show_cam_on_image(rgb_float, cam, use_rgb=True)


def explain_image(
    model: torch.nn.Module, config: dict, image: Image.Image, device: torch.device
) -> tuple[int, list[float], np.ndarray]:
    """Bellekteki bir görüntü için (tahmin, 5 sınıf olasılığı, Grad-CAM bindirmesi) döndürür.

    Dosya okumaz veya yazmaz; demo bunu yüklenen görüntüyle doğrudan çağırır.
    """
    cropped = prepare_image(image, 512)
    model_input = cropped
    if config.get("preprocessing") == "crop_ben_graham":
        model_input = ben_graham(cropped)

    transform = get_transforms("demo", config["image_size"])
    input_tensor = transform(model_input).unsqueeze(0).to(device)

    with torch.no_grad():
        probabilities = torch.softmax(model(input_tensor), dim=1)[0]
    prediction = int(probabilities.argmax())

    # Gradyan gerektiği için no_grad dışında, tahmin edilen sınıf için
    cam = compute_gradcam(model, config["model"], input_tensor, target_class=prediction)
    # Ben Graham geometriyi değiştirmez; harita, okunması kolay olsun diye kırpılmış
    # (Ben Graham'sız) görüntünün üstüne çizilir. Retina dışındaki siyah alan boyanmaz.
    heatmap = overlay(cropped, cam)
    height, width = cam.shape
    small = cropped.resize((width, height), Image.Resampling.LANCZOS)
    outside_retina = np.asarray(small.convert("L")) <= BLACK_THRESHOLD
    heatmap[outside_retina] = np.asarray(small)[outside_retina]
    return prediction, probabilities.tolist(), heatmap


def pick_gallery_rows(predictions: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Her gerçek sınıf için 1 doğru + 1 yanlış tahmin satırı seçer (en çok 10 satır).

    Grup boşsa (ör. sınıf 4'te hiç yanlış yoksa) atlanır. Sabit seed aynı seçimi verir.
    Dönen sütunlar: image_id, y_true, y_pred, kind ("dogru" | "yanlis").
    """
    picked = []
    for label in sorted(predictions["y_true"].unique()):
        same_class = predictions[predictions["y_true"] == label]
        is_correct = same_class["y_pred"] == label
        for kind, group in (("dogru", same_class[is_correct]), ("yanlis", same_class[~is_correct])):
            if group.empty:
                continue
            row = group.sample(n=1, random_state=seed)[["image_id", "y_true", "y_pred"]].copy()
            row["kind"] = kind
            picked.append(row)
    return pd.concat(picked, ignore_index=True)


def side_by_side(image: Image.Image, heatmap: np.ndarray) -> np.ndarray:
    """Sol: modele giren görüntü, sağ: Grad-CAM bindirmesi."""
    side = heatmap.shape[0]
    original = np.asarray(image.resize((side, side), Image.Resampling.LANCZOS))
    return np.concatenate([original, heatmap], axis=1)


def make_gallery(run_dir: Path, data_root: Path, out_dir: Path) -> None:
    """Val tahminlerinden örnek seçer, her biri için PNG ve hepsi için gallery.png üretir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    predictions = pd.read_csv(run_dir / "val_predictions.csv")
    rows = pick_gallery_rows(predictions)

    device = get_device()
    model, config = load_run(run_dir, device)

    figure, axes = plt.subplots(5, 2, figsize=(8, 18))
    for axis in axes.flat:
        axis.axis("off")
        axis.text(0.5, 0.5, "örnek yok", ha="center", va="center", transform=axis.transAxes)
    figure.suptitle("Sol sütun: doğru tahmin · Sağ sütun: yanlış tahmin (val)", fontsize=12)

    for row in rows.itertuples():
        image = Image.open(data_root / f"{row.image_id}.jpg").convert("RGB")
        prediction, _, heatmap = explain_image(model, config, image, device)
        if prediction != row.y_pred:
            # Önbellekteki tahminle anlık tahmin farklıysa uyar (başlık CSV'deki tahmini gösterir)
            print(f"Uyarı: {row.image_id} için anlık tahmin {prediction}, CSV'de {row.y_pred}")
        pair = side_by_side(image, heatmap)
        title = f"Gerçek: {row.y_true} · Tahmin: {row.y_pred}"
        Image.fromarray(pair).save(out_dir / f"{row.y_true}_{row.kind}_{row.image_id}.png")

        axis = axes[row.y_true, 0 if row.kind == "dogru" else 1]
        axis.clear()
        axis.imshow(pair)
        axis.set_title(title, fontsize=10)
        axis.axis("off")

    figure.tight_layout()
    figure.savefig(out_dir / "gallery.png", dpi=120)
    plt.close(figure)
    print(f"{len(rows)} örnek + gallery.png kaydedildi: {out_dir}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Grad-CAM bindirmesi üretir (tek görüntü veya val galerisi).")
    parser.add_argument("--run", type=Path, required=True, help="koşu klasörü (config.yaml + best.pt)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--image", type=Path, help="açıklanacak görüntü")
    mode.add_argument(
        "--gallery",
        action="store_true",
        help="val_predictions.csv'den her sınıf için 1 doğru + 1 yanlış örnek üretir (yalnız val)",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("data/processed/aptos_512"),
        help="512 önbellek klasörü (varsayılan data/processed/aptos_512)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="--image için PNG (varsayılan outputs/figures/gradcam_<ad>.png); "
        "--gallery için klasör (varsayılan outputs/figures/gallery)",
    )
    args = parser.parse_args(argv)

    if args.gallery:
        make_gallery(args.run, args.data_root, args.out or Path("outputs/figures/gallery"))
        return

    out_path = args.out or Path("outputs/figures") / f"gradcam_{args.image.stem}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    device = get_device()
    model, config = load_run(args.run, device)
    image = Image.open(args.image).convert("RGB")
    prediction, probabilities, heatmap = explain_image(model, config, image, device)
    Image.fromarray(side_by_side(image, heatmap)).save(out_path)

    print(f"Tahmin: {prediction} (olasılık {probabilities[prediction]:.2f})")
    print(f"Kaydedildi: {out_path}")


if __name__ == "__main__":
    main()
