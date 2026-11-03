"""src/gradcam.py testleri (PLAN 3.7). Çalıştır: python -m pytest tests/test_gradcam.py -q"""
import numpy as np
import pytest
import torch
from PIL import Image

from src.gradcam import compute_gradcam, explain_image, get_target_layer, overlay
from src.models import build_model


def make_model(name: str = "resnet18") -> torch.nn.Module:
    return build_model(name, 5, pretrained=False).eval()


def test_target_layer_resnet():
    model = make_model("resnet18")
    assert get_target_layer(model, "resnet18") is model.layer4[-1]


def test_target_layer_efficientnet():
    model = make_model("efficientnet_b3")
    assert get_target_layer(model, "efficientnet_b3") is model.features[-1]


def test_target_layer_unknown():
    with pytest.raises(ValueError):
        get_target_layer(make_model(), "vgg16")


def test_cam_shape_and_range():
    cam = compute_gradcam(make_model(), "resnet18", torch.randn(1, 3, 64, 64))
    assert cam.shape == (64, 64)
    assert cam.min() >= 0 and cam.max() <= 1


def test_cam_with_explicit_class():
    cam = compute_gradcam(make_model(), "resnet18", torch.randn(1, 3, 64, 64), target_class=3)
    assert cam.shape == (64, 64)


def test_overlay_shape():
    result = overlay(Image.new("RGB", (100, 80)), np.random.rand(64, 64).astype(np.float32))
    assert result.shape == (64, 64, 3)
    assert result.dtype == np.uint8


def test_explain_image():
    config = {"model": "resnet18", "image_size": 64, "preprocessing": "crop"}
    image = Image.fromarray(np.random.randint(60, 255, (300, 300, 3), dtype=np.uint8))
    prediction, probabilities, heatmap = explain_image(make_model(), config, image, torch.device("cpu"))
    assert 0 <= prediction <= 4
    assert len(probabilities) == 5
    assert sum(probabilities) == pytest.approx(1.0, abs=1e-4)
    assert heatmap.shape == (64, 64, 3)
