"""build_model testleri (PLAN 1.9).

Hepsi pretrained=False çalışır, ağ gerekmez.
Nasıl çalıştırılır (proje kökünden):
    python -m pytest tests/test_models.py -q
"""

import pytest
import torch

from src.models import build_model


def _forward(model):
    """Modeli eval modunda, 2 görüntülük sahte batch ile çalıştırır."""
    model.eval()
    with torch.no_grad():
        return model(torch.randn(2, 3, 224, 224))


@pytest.mark.parametrize("name", ["resnet18", "resnet50", "efficientnet_b3"])
def test_output_shape(name):
    model = build_model(name, pretrained=False)
    assert _forward(model).shape == (2, 5)


def test_custom_num_classes():
    model = build_model("resnet18", num_classes=3, pretrained=False)
    assert _forward(model).shape == (2, 3)


def test_unknown_model_raises():
    with pytest.raises(ValueError, match="Bilinmeyen model"):
        build_model("vgg16")


@pytest.mark.parametrize(
    "name, expected",
    [("resnet18", 11179077), ("resnet50", 23518277), ("efficientnet_b3", 10703917)],
)
def test_parameter_count(name, expected):
    model = build_model(name, pretrained=False)
    assert sum(p.numel() for p in model.parameters()) == expected
