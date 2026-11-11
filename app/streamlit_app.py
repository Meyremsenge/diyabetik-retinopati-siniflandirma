"""VisionDx demo arayüzü (PLAN 4.5, 5.2).

Ne yapar: Yüklenen retina görüntüsü için DR derecesini, 5 sınıf olasılığını ve Grad-CAM ısı
haritasını gösterir. Yüklenen görüntü yalnız bellekte tutulur, diske yazılmaz.
Görünüm app/style.css'ten, tema .streamlit/config.toml'dan gelir; internet bağlantısı gerekmez.

Nasıl çalıştırılır (proje kökünden):
    streamlit run app/streamlit_app.py -- --checkpoint outputs/final/<run_id>/best.pt
    (veya VISIONDX_CHECKPOINT ortam değişkeni ile checkpoint yolu verilir)
"""
import io
import os
import sys
import time
from pathlib import Path

import streamlit as st
import torch
from PIL import Image, UnidentifiedImageError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.gradcam import explain_image
from src.models import build_model
from src.preprocessing import prepare_image
from src.utils import get_device

CLASS_NAMES = {0: "DR yok", 1: "Hafif NPDR", 2: "Orta NPDR", 3: "Ağır NPDR", 4: "Proliferatif DR"}
# Derece renkleri: sakin yeşilden koyu kırmızıya
CLASS_COLORS = {0: "#3F8F6B", 1: "#8DA338", 2: "#D39B2A", 3: "#D0652E", 4: "#B23A3A"}
MODEL_NAMES = {"resnet18": "ResNet18", "resnet50": "ResNet50", "efficientnet_b3": "EfficientNet-B3"}
DISCLAIMER = "Akademik prototiptir; tıbbi teşhis yerine geçmez."
MIN_SIDE = 224
STYLE_FILE = Path(__file__).with_name("style.css")

LOGO_SVG = """<svg width="44" height="44" viewBox="0 0 44 44" aria-hidden="true">
<rect width="44" height="44" rx="13" fill="#0E5E57"/>
<circle cx="22" cy="22" r="11.5" fill="none" stroke="#E4EFEC" stroke-width="2.2"/>
<circle cx="22" cy="22" r="5" fill="#F4C25B"/>
<circle cx="25.5" cy="18.5" r="1.6" fill="#FFFFFF"/>
</svg>"""
LOCK_SVG = """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0E5E57"
stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>"""
EMPTY_SVG = """<svg width="120" height="120" viewBox="0 0 120 120" aria-hidden="true">
<circle cx="60" cy="60" r="54" fill="#EFEDE7"/>
<circle cx="60" cy="60" r="38" fill="#F7F6F2" stroke="#D9D5CB" stroke-width="2"/>
<circle cx="44" cy="58" r="7" fill="#E9C77E"/>
<path d="M44 58 C 60 40, 80 44, 92 52" stroke="#C9A99A" stroke-width="2" fill="none"/>
<path d="M44 58 C 62 70, 78 76, 90 70" stroke="#C9A99A" stroke-width="2" fill="none"/>
</svg>"""


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


def model_caption(config: dict, device: torch.device) -> str:
    """Hangi modelin, hangi ön işlemeyle, hangi cihazda çalıştığını tek satırda verir."""
    return f"Model: {config['model']} · Ön işleme: {config['preprocessing']} · Cihaz: {device.type}"


def html(markup: str) -> None:
    """Biçimli HTML parçası basar (yalnız sabit metin ve sayı; kullanıcı girdisi yok)."""
    st.markdown(markup, unsafe_allow_html=True)


def header_html() -> str:
    return (
        '<div class="vd-top"><div class="vd-brand">' + LOGO_SVG
        + '<div><div class="vd-wordmark">VisionDx</div>'
        + '<div class="vd-tagline">Retina fotoğrafından diyabetik retinopati derecelendirme</div>'
        + "</div></div></div>"
    )


def result_html(prediction: int, probabilities: list[float]) -> str:
    """Tahmin kartı: derece rozeti, ölçek ve 0–4 sırasıyla olasılık çubukları."""
    color = CLASS_COLORS[prediction]
    confidence = probabilities[prediction] * 100
    parts = [
        '<div class="vd-result">',
        f'<div class="vd-grade" style="background:{color}">{prediction}</div>',
        '<div><div class="vd-eyebrow">Tahmin edilen derece</div>',
        f'<div class="vd-grade-name">{CLASS_NAMES[prediction]}</div>',
        f'<div class="vd-confidence">Model olasılığı <b>%{confidence:.0f}</b></div></div></div>',
        '<div class="vd-scale">',
    ]
    for label in range(5):
        active = " is-active" if label == prediction else ""
        bar_color = CLASS_COLORS[label] if label <= prediction else "#E9E7E1"
        parts.append(
            f'<div class="vd-scale-cell{active}"><div class="vd-scale-bar" style="background:{bar_color}"></div>'
            f'<div class="vd-scale-label">{label}</div></div>'
        )
    parts.append('</div><div class="vd-probs">')
    for label in range(5):
        active = " is-active" if label == prediction else ""
        percent = probabilities[label] * 100
        fill = CLASS_COLORS[label] if label == prediction else "#B9C2BF"
        parts.append(
            f'<div class="vd-prob-row{active}"><span class="vd-prob-num">{label}</span>'
            f"<span>{CLASS_NAMES[label]}</span>"
            f'<div class="vd-prob-track"><div class="vd-prob-fill" style="width:{percent:.1f}%;background:{fill}"></div></div>'
            f'<span class="vd-prob-value">%{percent:.1f}</span></div>'
        )
    parts.append("</div>")
    return "".join(parts)


def main() -> None:
    st.set_page_config(page_title="VisionDx", layout="wide")
    if STYLE_FILE.exists():
        html(f"<style>{STYLE_FILE.read_text(encoding='utf-8')}</style>")

    html(header_html())
    st.warning(DISCLAIMER)

    checkpoint_path = get_checkpoint_path(sys.argv[1:])
    if checkpoint_path is None or not checkpoint_path.exists():
        st.error("Model dosyası bulunamadı. README → 'Model ağırlıkları ve demo'.")
        st.stop()

    model, config, device = load_checkpoint(str(checkpoint_path))
    st.caption(model_caption(config, device))

    left, right = st.columns([5, 7], gap="large")

    with left:
        with st.container(border=True):
            html('<div class="vd-card-title"><span class="vd-step">1</span>Görüntü yükle</div>')
            uploaded = st.file_uploader("Fundus görüntüsü yükle", type=["png", "jpg", "jpeg"])
            html(
                f'<div class="vd-note">{LOCK_SVG}<span>PNG veya JPG, en az {MIN_SIDE} piksel. '
                "Görüntü yalnız bellekte işlenir, diske kaydedilmez.</span></div>"
            )

    image = None
    if uploaded is not None:
        try:
            image = validate_image(uploaded.getvalue())
        except ValueError as error:
            with right:
                st.error(str(error))
            st.stop()

    with right:
        with st.container(border=True):
            html('<div class="vd-card-title"><span class="vd-step">2</span>Sonuç</div>')
            if image is None:
                html(
                    f'<div class="vd-empty">{EMPTY_SVG}<h3>Sonuç burada görünecek</h3>'
                    "<p>Soldan bir göz dibi fotoğrafı yükleyin. Derece, olasılıklar ve ısı haritası birkaç saniyede hazırlanır.</p></div>"
                )
                return

            start = time.perf_counter()
            with st.spinner("Görüntü inceleniyor…"):
                prediction, probabilities, heatmap = explain_image(model, config, image, device)
            elapsed = time.perf_counter() - start
            html(result_html(prediction, probabilities))

    with st.container(border=True):
        html('<div class="vd-card-title"><span class="vd-step">3</span>Modelin dikkat ettiği bölgeler</div>')
        original_column, heatmap_column = st.columns(2, gap="medium")
        with original_column:
            html('<div class="vd-img-label">Kırpılmış görüntü</div>')
            st.image(prepare_image(image, 512), width="stretch")
        with heatmap_column:
            html('<div class="vd-img-label">Grad-CAM ısı haritası</div>')
            st.image(heatmap, width="stretch")
        html(
            '<div class="vd-legend"><span>düşük</span><div class="vd-legend-bar"></div><span>yüksek dikkat</span></div>'
        )
        st.write("Isı haritası modelin dikkat ettiği bölgeleri gösterir; lezyon tespiti değildir.")

    model_name = MODEL_NAMES.get(config["model"], config["model"])
    html(
        f'<div class="vd-footer"><span>VisionDx · {model_name} · akademik prototip</span>'
        f"<span>Süre: {elapsed:.1f} sn · {device.type}</span></div>"
    )


if __name__ == "__main__":
    main()
