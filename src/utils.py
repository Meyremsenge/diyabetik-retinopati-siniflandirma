"""Rastgelelik ve cihaz seçimi yardımcıları (PLAN 1.8).

Projede rastgelelik ve cihaz seçimi yalnız buradan yapılır.
Başka dosyalarda `torch.manual_seed` veya `torch.cuda.is_available` çağırma;
bu fonksiyonları kullan.

Nasıl kullanılır (proje kökünden):
    python -c "from src.utils import get_device; print(get_device())"
"""

import random

import numpy as np
import torch


def set_seed(seed: int) -> None:
    """Python, NumPy ve PyTorch rastgelelik üreteçlerini aynı sayıyla başlatır.

    Aynı seed ile iki kez eğitince aynıya çok yakın sonuç alınır.
    Tam belirlenimcilik (torch.use_deterministic_algorithms) bilerek AÇILMAZ (D-16).
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def get_device() -> torch.device:
    """En hızlı kullanılabilir cihazı döndürür: cuda -> mps -> cpu.

    Ekrana bir şey yazmaz, yalnız döndürür.
    """
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")
