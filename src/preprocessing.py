"""Fundus görüntüsü ön işleme: siyah kenar kırpma ve kare boyutlandırma.

Önbellek betiği (2.2) ve Streamlit demosu (4.5) aynı fonksiyonu, `prepare_image`'i
çağırır; böylece eğitimde ve demoda görüntü aynı şekilde hazırlanır.

Kullanım (Python içinden):
    from PIL import Image
    from src.preprocessing import prepare_image
    kare = prepare_image(Image.open("ornek.png"), size=512)

Test: python -m pytest tests/test_preprocessing.py -q
"""

import numpy as np
from PIL import Image, ImageFilter

BLACK_THRESHOLD = 7


def crop_black_borders(img: Image.Image, threshold: int = BLACK_THRESHOLD) -> Image.Image:
    """Gri tonu eşikten büyük piksellerin sınır kutusuna kırpar.

    Hiç piksel eşiği geçmiyorsa (tamamen siyah) görüntüyü olduğu gibi döndürür.
    """
    gray = np.array(img.convert("L"))
    mask = gray > threshold
    if not mask.any():
        return img

    rows = np.where(mask.any(axis=1))[0]
    columns = np.where(mask.any(axis=0))[0]
    top, bottom = rows[0], rows[-1]
    left, right = columns[0], columns[-1]
    # crop kutusunun sağ/alt kenarı dahil değildir, bu yüzden +1
    return img.crop((int(left), int(top), int(right) + 1, int(bottom) + 1))


def resize_square(img: Image.Image, size: int) -> Image.Image:
    """En-boy oranını koruyarak kısa kenarı siyahla doldurur, (size, size)'a küçültür."""
    width, height = img.size
    side = max(width, height)
    canvas = Image.new("RGB", (side, side), (0, 0, 0))
    canvas.paste(img.convert("RGB"), ((side - width) // 2, (side - height) // 2))
    return canvas.resize((size, size), Image.Resampling.LANCZOS)


def prepare_image(img: Image.Image, size: int = 512) -> Image.Image:
    """RGB'ye çevir → siyah kenarları kırp → kare boyutlandır."""
    rgb = img.convert("RGB")
    return resize_square(crop_black_borders(rgb), size)


def ben_graham(
    img: Image.Image, sigma_divisor: float = 30.0, mask_ratio: float = 0.9
) -> Image.Image:
    """Ben Graham dönüşümü: bulanık arka planı çıkarıp ince ayrıntıları öne çıkarır.

    Girdi `prepare_image` çıktısı (kare RGB) olmalı. Formül: 4*görüntü - 4*bulanık + 128.
    Merkezden uzaklığı mask_ratio * yarıçaptan büyük pikseller gri (128) yapılır.
    """
    rgb = img.convert("RGB")
    width, height = rgb.size
    radius = min(width, height) / 2
    # Pillow'da GaussianBlur'un radius parametresi standart sapmadır
    blurred = rgb.filter(ImageFilter.GaussianBlur(radius=radius / sigma_divisor))

    sharpened = 4 * np.asarray(rgb, dtype=np.float32) - 4 * np.asarray(blurred, dtype=np.float32) + 128
    result = np.clip(sharpened, 0, 255)

    rows, columns = np.ogrid[:height, :width]
    distance = np.sqrt((columns - (width - 1) / 2) ** 2 + (rows - (height - 1) / 2) ** 2)
    result[distance > mask_ratio * radius] = 128

    return Image.fromarray(result.astype(np.uint8), mode="RGB")
