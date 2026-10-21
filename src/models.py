"""Model kurulumu (PLAN 1.9).

ImageNet'te eğitilmiş bir ağı alıp son katmanını 5 sınıfa (DR derece 0-4)
uyarlar. Model adı config dosyasından gelir.

Nasıl kullanılır (proje kökünden):
    python -c "from src.models import build_model; print(build_model('resnet50').fc)"
"""

import torch
from torch import nn
from torchvision import models

SUPPORTED_MODELS = ("resnet18", "resnet50", "efficientnet_b3")


def build_model(name: str, num_classes: int = 5, pretrained: bool = True) -> torch.nn.Module:
    """Seçilen modeli kurar ve son katmanı `num_classes` çıkışlı yapar.

    pretrained=True ise ImageNet ağırlıkları indirilir (ilk seferde internet gerekir).
    """
    if name == "resnet18":
        weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        model = models.resnet18(weights=weights)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif name == "resnet50":
        weights = models.ResNet50_Weights.IMAGENET1K_V2 if pretrained else None
        model = models.resnet50(weights=weights)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif name == "efficientnet_b3":
        weights = models.EfficientNet_B3_Weights.IMAGENET1K_V1 if pretrained else None
        model = models.efficientnet_b3(weights=weights)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    else:
        raise ValueError(f"Bilinmeyen model: {name}. Seçenekler: resnet18, resnet50, efficientnet_b3")
    return model
