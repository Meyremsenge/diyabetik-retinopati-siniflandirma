"""Demo sayfasının tanıtım bölümleri: kapak, test sonuçları, derece rehberi, çalışma adımları.

Yalnız HTML metni üretir; model veya tahmin işi yapmaz. Görsel, kodla çizilen temsili bir
SVG'dir (gerçek hasta görüntüsü değildir, internet gerektirmez).

Tek başına çalıştırılmaz; app/streamlit_app.py içe aktarır:
    streamlit run app/streamlit_app.py -- --checkpoint outputs/final/<run_id>/best.pt
"""
import base64

# Final modelin (E4) bir kez ölçülen sonuçları: docs/DENEY_KAYDI.md "Final model" tablosu
# (değer, ölçüt, veri kümesi, görüntü sayısı, kısa açıklama, dış test mi)
FINAL_RESULTS = [
    ("0,923", "QWK", "APTOS test", 522, "Tahmin gerçek dereceye ne kadar yakın; uzak hata daha çok cezalanır.", False),
    ("0,835", "Doğruluk", "APTOS test", 522, "Derecesi tam doğru bilinen görüntülerin oranı.", False),
    ("0,702", "Macro F1", "APTOS test", 522, "Beş derecenin ortalaması; az örnekli dereceler de eşit sayılır.", False),
    ("0,703", "QWK", "IDRiD dış test", 516, "Farklı klinik ve kamera. Başarı burada belirgin biçimde düşer.", True),
]

# Uluslararası Klinik DR Şiddet Ölçeği'nin kısa özeti (rapor kaynak [1])
GRADE_GUIDE = [
    ("DR yok", "Retinada diyabete bağlı bulgu görülmez."),
    ("Hafif NPDR", "Yalnız mikroanevrizma denen küçük damar baloncukları vardır."),
    ("Orta NPDR", "Mikroanevrizmadan fazlası vardır, ancak ağır düzeye ulaşmaz."),
    ("Ağır NPDR", "Yaygın kanama ve damar değişiklikleri vardır; yeni damar oluşumu yoktur."),
    ("Proliferatif DR", "Yeni damar oluşumu veya göz içine kanama görülür."),
]

STEPS = [
    ("Hazırlama", "Siyah kenarlar kırpılır, Ben Graham dönüşümüyle aydınlatma farkları azaltılır."),
    ("Sınıflandırma", "EfficientNet-B3 ağı beş derecenin her biri için bir olasılık hesaplar."),
    ("Açıklama", "Grad-CAM, modelin karar verirken ağırlık verdiği bölgeleri renklendirir."),
]

# Adım ikonları (kırpma çerçevesi, katmanlı ağ, göz)
STEP_ICONS = [
    '<path d="M6 2v14a2 2 0 0 0 2 2h14"/><path d="M18 22V8a2 2 0 0 0-2-2H2"/>',
    '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 12 10 5 10-5"/><path d="m2 17 10 5 10-5"/>',
    '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
]

# Temsili göz dibi çizimi
RETINA_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">'
    "<defs>"
    '<radialGradient id="eye" cx="45%" cy="45%" r="60%">'
    '<stop offset="0" stop-color="#F08A45"/><stop offset="0.55" stop-color="#C4502A"/>'
    '<stop offset="1" stop-color="#5E1C16"/></radialGradient>'
    '<radialGradient id="disc"><stop offset="0" stop-color="#FFF4C9"/>'
    '<stop offset="0.7" stop-color="#F7C65E"/><stop offset="1" stop-color="#E8963F" stop-opacity="0.2"/>'
    '</radialGradient><radialGradient id="macula"><stop offset="0" stop-color="#4A130F" stop-opacity="0.75"/>'
    '<stop offset="1" stop-color="#4A130F" stop-opacity="0"/></radialGradient>'
    '<clipPath id="inside"><circle cx="200" cy="200" r="160"/></clipPath></defs>'
    '<circle cx="200" cy="200" r="192" fill="none" stroke="#9FD3C7" stroke-opacity="0.25" stroke-width="1.5"/>'
    '<circle cx="200" cy="200" r="176" fill="none" stroke="#9FD3C7" stroke-opacity="0.55" '
    'stroke-width="2" stroke-dasharray="3 11"/>'
    '<circle cx="200" cy="200" r="160" fill="url(#eye)"/>'
    '<g clip-path="url(#inside)">'
    '<circle cx="245" cy="205" r="48" fill="url(#macula)"/>'
    '<g fill="none" stroke="#7E1F1A" stroke-linecap="round" opacity="0.85">'
    '<path stroke-width="7" d="M122 192C130 140 170 100 232 92S320 100 360 76"/>'
    '<path stroke-width="7" d="M122 196C132 250 168 298 226 308S318 300 352 334"/>'
    '<path stroke-width="4" d="M122 192C100 150 78 128 40 118"/>'
    '<path stroke-width="4" d="M122 196C98 236 76 266 44 282"/>'
    '<path stroke-width="3.5" d="M168 124C176 100 172 74 190 42"/>'
    '<path stroke-width="3.5" d="M172 281C186 306 182 332 204 364"/>'
    '<path stroke-width="2.5" d="M232 92C246 118 270 132 292 160"/>'
    '<path stroke-width="2.5" d="M226 308C244 284 268 272 296 252"/>'
    '<path stroke-width="1.8" d="M292 160c8 10 10 20 22 26M270 96c14 18 32 22 44 40M78 128c-4-20 2-34-8-52"/>'
    '<path stroke-width="1.8" d="M296 252c10-8 24-8 32-22M264 304c14-16 34-14 46-34M76 266c0 18 10 32 6 50"/>'
    "</g>"
    '<circle cx="124" cy="194" r="34" fill="url(#disc)"/>'
    '<g fill="#FFE08A"><circle cx="262" cy="160" r="3.5"/><circle cx="274" cy="168" r="2.5"/>'
    '<circle cx="256" cy="172" r="2"/><circle cx="214" cy="250" r="2.8"/></g>'
    '<g fill="#5A0F0D"><circle cx="196" cy="150" r="3"/><circle cx="284" cy="220" r="4"/>'
    '<circle cx="160" cy="246" r="2.4"/></g></g>'
    '<g fill="none" stroke="#CFF3EA" stroke-width="2.5">'
    '<rect x="238" y="140" width="56" height="52" rx="8"/></g>'
    "</svg>"
)


def hero_html(logo_svg: str) -> str:
    """Üst kapak: marka, başlık, kısa açıklama ve temsili retina çizimi."""
    image = base64.b64encode(RETINA_SVG.encode("utf-8")).decode("ascii")
    chips = ("EfficientNet-B3", "Grad-CAM açıklaması", "İnternetsiz çalışır")
    chip_html = "".join(f'<span class="vd-chip">{chip}</span>' for chip in chips)
    return (
        '<div class="vd-hero"><div class="vd-hero-text">'
        f'<div class="vd-brand">{logo_svg}<span class="vd-wordmark">VisionDx</span></div>'
        '<div class="vd-hero-title">Göz dibi fotoğrafından diyabetik retinopati derecelendirme</div>'
        '<div class="vd-hero-sub">Fotoğrafı yükleyin; model 0–4 arasındaki dereceyi tahmin etsin ve '
        "karar verirken nereye baktığını göstersin.</div>"
        f'<div class="vd-chips">{chip_html}</div></div>'
        '<div class="vd-hero-art">'
        f'<img src="data:image/svg+xml;base64,{image}" alt="Temsili retina çizimi">'
        "<span>Temsili çizim</span></div></div>"
    )


def section_title(title: str, subtitle: str) -> str:
    return f'<div class="vd-section"><div class="vd-section-title">{title}</div><div>{subtitle}</div></div>'


def icon_svg(paths: str) -> str:
    """24x24 çizgi ikon; renk CSS'teki currentColor'dan gelir."""
    return (
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>'
    )


def results_html() -> str:
    """Test sonuç kartları: değer, 0–1 ölçek çubuğu ve ölçütün kısa açıklaması."""
    tiles = []
    for value, name, dataset, count, explanation, is_external in FINAL_RESULTS:
        width = float(value.replace(",", ".")) * 100
        external = " is-external" if is_external else ""
        tiles.append(
            f'<div class="vd-stat{external}">'
            f'<div class="vd-stat-top"><span class="vd-stat-tag">{dataset}</span><span>{count} görüntü</span></div>'
            f'<div class="vd-stat-value">{value}</div><div class="vd-stat-name">{name}</div>'
            f'<div class="vd-meter"><div style="width:{width:.1f}%"></div></div>'
            f'<div class="vd-stat-note">{explanation}</div></div>'
        )
    return (
        section_title("Modelin sınanmış başarısı", "Model, eğitimde görmediği görüntülerde bir kez ölçüldü. 1,0 en iyi değerdir.")
        + f'<div class="vd-grid vd-grid-4">{"".join(tiles)}</div>'
    )


def grade_guide_html(colors: dict[int, str], active: int | None = None) -> str:
    """Derece rehberi; active verilirse o derecenin kartı 'Bu görüntü' diye vurgulanır."""
    cards = []
    for grade, (name, description) in enumerate(GRADE_GUIDE):
        is_active = grade == active
        tag = '<span class="vd-tile-tag">Bu görüntü</span>' if is_active else ""
        cards.append(
            f'<div class="vd-tile vd-grade-tile{" is-active" if is_active else ""}" style="--grade:{colors[grade]}">'
            f'<div class="vd-tile-head"><span class="vd-badge">{grade}</span>{tag}</div>'
            f"<b>{name}</b><p>{description}</p></div>"
        )
    return (
        section_title("Derece rehberi", "Uluslararası Klinik DR Şiddet Ölçeği'nin kısa özeti.")
        + f'<div class="vd-grid vd-grid-5">{"".join(cards)}</div>'
    )


def steps_html() -> str:
    """Çalışma adımları; kartlar arasında akış oku vardır."""
    cards = "".join(
        f'<div class="vd-tile vd-flow-tile"><div class="vd-tile-head"><span class="vd-icon">{icon_svg(icon)}</span>'
        f'<span class="vd-flow-step">Adım {number}</span></div><b>{title}</b><p>{description}</p></div>'
        for number, ((title, description), icon) in enumerate(zip(STEPS, STEP_ICONS), start=1)
    )
    return (
        section_title("Nasıl çalışır?", "Yüklenen görüntü üç aşamadan geçer.")
        + f'<div class="vd-grid vd-grid-3 vd-flow">{cards}</div>'
    )
