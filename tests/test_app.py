"""app/streamlit_app.py testleri (PLAN 4.5). Çalıştır: python -m pytest tests/test_app.py -q"""
import io
import sys
from pathlib import Path

import pytest
import torch
from PIL import Image
from streamlit.testing.v1 import AppTest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.streamlit_app import DISCLAIMER, get_checkpoint_path, validate_image
from src.models import build_model

APP_FILE = str(Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py")


def png_bytes(size: tuple[int, int], mode: str = "RGB") -> bytes:
    buffer = io.BytesIO()
    Image.new(mode, size).save(buffer, format="PNG")
    return buffer.getvalue()


def test_validate_image_rejects_garbage():
    with pytest.raises(ValueError, match="açılamadı"):
        validate_image(b"not an image")


def test_validate_image_rejects_small():
    with pytest.raises(ValueError, match="224"):
        validate_image(png_bytes((100, 100)))


def test_validate_image_accepts_rgba():
    image = validate_image(png_bytes((300, 300), "RGBA"))
    assert image.mode == "RGB"


def test_checkpoint_path_from_args_and_env(monkeypatch):
    monkeypatch.delenv("VISIONDX_CHECKPOINT", raising=False)
    assert get_checkpoint_path(["--checkpoint", "a.pt"]) == Path("a.pt")
    assert get_checkpoint_path([]) is None
    monkeypatch.setenv("VISIONDX_CHECKPOINT", "b.pt")
    assert get_checkpoint_path([]) == Path("b.pt")


def test_app_shows_disclaimer_without_checkpoint(monkeypatch):
    monkeypatch.delenv("VISIONDX_CHECKPOINT", raising=False)
    at = AppTest.from_file(APP_FILE).run()
    assert at.warning[0].value == DISCLAIMER
    assert any("Model dosyası bulunamadı" in error.value for error in at.error)


def test_app_with_tiny_checkpoint(tmp_path, monkeypatch):
    config = {"model": "resnet18", "num_classes": 5, "image_size": 64, "preprocessing": "crop"}
    model = build_model("resnet18", 5, pretrained=False)
    checkpoint_path = tmp_path / "best.pt"
    torch.save({"model_state": model.state_dict(), "config": config}, checkpoint_path)
    monkeypatch.setenv("VISIONDX_CHECKPOINT", str(checkpoint_path))

    at = AppTest.from_file(APP_FILE, default_timeout=60).run()
    assert not at.exception
    assert not at.error
    assert at.warning[0].value == DISCLAIMER
    assert len(at.get("file_uploader")) == 1
