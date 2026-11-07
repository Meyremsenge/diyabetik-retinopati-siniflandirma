"""VisionDx demo arayüzü (PLAN 4.5).

Ne yapar: Yüklenen retina görüntüsü için DR derecesini, 5 sınıf olasılığını ve Grad-CAM ısı
haritasını gösterir. Yüklenen görüntü yalnız bellekte tutulur, diske yazılmaz.

Nasıl çalıştırılır (proje kökünden):
    streamlit run app/streamlit_app.py -- --checkpoint outputs/runs/<run_id>/best.pt
    (veya VISIONDX_CHECKPOINT ortam değişkeni ile checkpoint yolu verilir)
"""
import io
import os
import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st
import torch
from PIL import Image, UnidentifiedImageError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.gradcam import explain_image
from src.models import build_model
from src.utils import get_device

CLASS_NAMES = {0: "DR yok", 1: "Hafif NPDR", 2: "Orta NPDR", 3: "Ağır NPDR", 4: "Proliferatif DR"}
DISCLAIMER = "Akademik prototiptir; tıbbi teşhis yerine geçmez."
MIN_SIDE = 224


def get_checkpoint_path(argv: list[str]) -> Path | None:
    """Önce --checkpoint argümanına, yoksa VISIONDX_CHECKPOINT ortam değişkenine bakar."""
    if "--checkpoint" in argv:
        position = argv.index("--checkpoint")
        if position + 1 < len(argv):
            return Path(argv[position + 1])
    from_env = os.environ.get("VISIONDX_CHECKPOINT")
    return Path(from_env) if from_env else None


@st.cache_resource
def load_checkpoint(path: str) -> tuple[torch.nn.Module, dict, torch.device]:
    """Modeli bir kez yükler. pretrained=False: demo internetsiz çalışmalı."""
    device = get_device()
    # Grad-CAM mps'te sorun çıkarabildiği için demoda mps yerine cpu kullanılır
    if device.type == "mps":
        device = torch.device("cpu")
    checkpoint = torch.load(path, map_location=device, weights_only=False)
    config = checkpoint["config"]
    model = build_model(config["model"], config["num_classes"], pretrained=False)
    model.load_state_dict(checkpoint["model_state"])
    return model.to(device).eval(), config, device


def validate_image(data: bytes) -> Image.Image:
    """Yüklenen baytları doğrular ve RGB görüntü döndürür; sorun varsa ValueError fırlatır."""
    try:
        Image.open(io.BytesIO(data)).verify()
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except (UnidentifiedImageError, OSError, SyntaxError):
        raise ValueError("Görüntü açılamadı. PNG veya JPG bir fundus görüntüsü yükleyin.") from None
    if min(image.size) < MIN_SIDE:
        raise ValueError(f"Görüntü çok küçük (en az {MIN_SIDE} piksel).")
    return image


def main() -> None:
    st.set_page_config(page_title="VisionDx")
    st.title("VisionDx — Diyabetik Retinopati Sınıflandırma")
    st.warning(DISCLAIMER)

    checkpoint_path = get_checkpoint_path(sys.argv[1:])
    if checkpoint_path is None or not checkpoint_path.exists():
        st.error("Model dosyası bulunamadı. README → 'Model ağırlıkları ve demo'.")
        st.stop()

    model, config, device = load_checkpoint(str(checkpoint_path))

    uploaded = st.file_uploader("Fundus görüntüsü yükle", type=["png", "jpg", "jpeg"])
    if uploaded is None:
        return

    try:
        image = validate_image(uploaded.getvalue())
    except ValueError as error:
        st.error(str(error))
        st.stop()

    start = time.perf_counter()
    prediction, probabilities, heatmap = explain_image(model, config, image, device)
    elapsed = time.perf_counter() - start

    st.subheader(f"Tahmin: {prediction} — {CLASS_NAMES[prediction]}")
    chart_data = pd.DataFrame(
        {"Olasılık": probabilities}, index=[CLASS_NAMES[i] for i in range(5)]
    )
    st.bar_chart(chart_data)

    left, right = st.columns(2)
    left.image(image, caption="Yüklenen görüntü")
    right.image(heatmap, caption="Grad-CAM bindirmesi")
    st.write("Isı haritası modelin dikkat ettiği bölgeleri gösterir; lezyon tespiti değildir.")
    st.caption(f"Süre: {elapsed:.1f} sn")


if __name__ == "__main__":
    main()
