"""Grad-CAM ısı haritası üretir (PLAN 3.7).

Ne yapar: Tek bir retina görüntüsü için modelin kararında hangi bölgelerin etkili olduğunu
gösteren ısı haritasını görüntünün üstüne bindirir. Bu bir lezyon tespiti DEĞİLDİR; yalnız
modelin dikkat ettiği bölgeleri gösterir. Demo (app/streamlit_app.py) `explain_image` fonksiyonunu kullanır.

Nasıl çalıştırılır (proje kökünden):
    python -m src.gradcam --run outputs/runs/<run_id> --image data/processed/aptos_512/<id>.jpg
    (çıktı varsayılan: outputs/figures/gradcam_<dosya adı>.png)
"""
import argparse
from pathlib import Path

import numpy as np
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


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Tek görüntü için Grad-CAM bindirmesi üretir.")
    parser.add_argument("--run", type=Path, required=True, help="koşu klasörü (config.yaml + best.pt)")
    parser.add_argument("--image", type=Path, required=True, help="açıklanacak görüntü")
    parser.add_argument("--out", type=Path, help="çıktı PNG (varsayılan: outputs/figures/gradcam_<dosya adı>.png)")
    args = parser.parse_args(argv)

    out_path = args.out or Path("outputs/figures") / f"gradcam_{args.image.stem}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    device = get_device()
    model, config = load_run(args.run, device)
    image = Image.open(args.image).convert("RGB")
    prediction, probabilities, heatmap = explain_image(model, config, image, device)

    # Sol: modele giren görüntü, sağ: bindirme
    side = heatmap.shape[0]
    original = np.asarray(image.resize((side, side), Image.Resampling.LANCZOS))
    Image.fromarray(np.concatenate([original, heatmap], axis=1)).save(out_path)

    print(f"Tahmin: {prediction} (olasılık {probabilities[prediction]:.2f})")
    print(f"Kaydedildi: {out_path}")


if __name__ == "__main__":
    main()
