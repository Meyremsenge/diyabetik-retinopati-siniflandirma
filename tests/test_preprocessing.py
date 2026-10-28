"""src/preprocessing.py için testler (sahte görüntüyle, gerçek veri gerekmez).

Çalıştırma: python -m pytest tests/test_preprocessing.py -q
"""

import numpy as np
from PIL import Image

from src.preprocessing import ben_graham, crop_black_borders, prepare_image, resize_square


def test_crop_finds_bright_region():
    img = Image.new("RGB", (100, 80), (0, 0, 0))
    img.paste((120, 120, 120), (20, 10, 60, 50))  # x: 20-59, y: 10-49

    cropped = crop_black_borders(img)

    assert cropped.size == (40, 40)


def test_crop_threshold_is_strict():
    img = Image.new("RGB", (20, 20), (0, 0, 0))
    img.putpixel((2, 3), (7, 7, 7))  # eşiğe eşit → siyah sayılır
    img.putpixel((10, 12), (8, 8, 8))  # eşiğin üstünde → içerik

    cropped = crop_black_borders(img)

    assert cropped.size == (1, 1)


def test_crop_all_black_returns_same_size():
    img = Image.new("RGB", (50, 30), (0, 0, 0))

    cropped = crop_black_borders(img)

    assert cropped.size == (50, 30)


def test_resize_square_pads_and_resizes():
    img = Image.new("RGB", (40, 20), (255, 255, 255))

    squared = resize_square(img, 64)

    assert squared.size == (64, 64)
    assert squared.getpixel((32, 32)) == (255, 255, 255)
    assert squared.getpixel((32, 2)) == (0, 0, 0)


def test_prepare_image_returns_rgb_square():
    img = Image.new("L", (30, 20), 200)

    prepared = prepare_image(img)

    assert prepared.mode == "RGB"
    assert prepared.size == (512, 512)


def test_prepare_image_is_deterministic():
    rng = np.random.default_rng(0)
    pixels = rng.integers(0, 256, size=(40, 60, 3), dtype=np.uint8)
    img = Image.fromarray(pixels)

    first = prepare_image(img, 64)
    second = prepare_image(img, 64)

    assert np.array_equal(np.array(first), np.array(second))


def test_ben_graham_uniform_image_is_gray():
    uniform = Image.new("RGB", (64, 64), (100, 100, 100))
    assert (np.array(ben_graham(uniform)) == 128).all()


def test_ben_graham_mask_corner():
    rng = np.random.default_rng(0)
    noisy = Image.fromarray(rng.integers(0, 256, size=(64, 64, 3), dtype=np.uint8))
    assert ben_graham(noisy).getpixel((0, 0)) == (128, 128, 128)


def test_ben_graham_keeps_size_and_mode():
    result = ben_graham(Image.new("RGB", (100, 100), (50, 80, 20)))
    assert result.size == (100, 100)
    assert result.mode == "RGB"


def test_ben_graham_deterministic():
    rng = np.random.default_rng(1)
    noisy = Image.fromarray(rng.integers(0, 256, size=(64, 64, 3), dtype=np.uint8))
    assert np.array_equal(np.array(ben_graham(noisy)), np.array(ben_graham(noisy)))
