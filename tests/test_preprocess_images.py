"""src/preprocess_images.py için testler (sahte APTOS klasörüyle, gerçek veri gerekmez).

Çalıştırma: python -m pytest tests/test_preprocess_images.py -q
"""

import pytest
from PIL import Image

from src.preprocess_images import main, preprocess_all


@pytest.fixture
def raw_dir(tmp_path):
    """3 görüntülü sahte ham APTOS klasörü: train.csv + train_images/*.png."""
    raw = tmp_path / "raw"
    (raw / "train_images").mkdir(parents=True)
    (raw / "train.csv").write_text("id_code,diagnosis\na,0\nb,1\nc,2\n")
    for image_id, size in [("a", (120, 100)), ("b", (90, 90)), ("c", (200, 150))]:
        img = Image.new("RGB", size, (0, 0, 0))
        center = (size[0] // 4, size[1] // 4, size[0] * 3 // 4, size[1] * 3 // 4)
        img.paste((120, 120, 120), center)
        img.save(raw / "train_images" / f"{image_id}.png")
    return raw


def test_writes_all_images(raw_dir, tmp_path):
    out_dir = tmp_path / "out"

    written = preprocess_all(raw_dir, out_dir, size=64)

    assert written == 3
    for image_id in ["a", "b", "c"]:
        with Image.open(out_dir / f"{image_id}.jpg") as img:
            assert img.size == (64, 64)
            assert img.mode == "RGB"


def test_copies_labels(raw_dir, tmp_path):
    out_dir = tmp_path / "out"

    preprocess_all(raw_dir, out_dir, size=64)

    assert (out_dir / "train.csv").read_text() == (raw_dir / "train.csv").read_text()


def test_limit(raw_dir, tmp_path):
    out_dir = tmp_path / "out"

    written = preprocess_all(raw_dir, out_dir, size=64, limit=2)

    assert written == 2
    assert len(list(out_dir.glob("*.jpg"))) == 2


def test_main_cli(raw_dir, tmp_path, capsys):
    out_dir = tmp_path / "out"

    main(["--data-root", str(raw_dir), "--out-dir", str(out_dir), "--size", "32"])

    assert len(list(out_dir.glob("*.jpg"))) == 3
    assert "Yazılan görüntü: 3" in capsys.readouterr().out


def test_ben_graham_flag(raw_dir, tmp_path):
    out_dir = tmp_path / "out"

    preprocess_all(raw_dir, out_dir, size=64, ben_graham=True)

    with Image.open(out_dir / "a.jpg") as img:
        corner = img.getpixel((0, 0))
    assert all(abs(channel - 128) <= 3 for channel in corner)
