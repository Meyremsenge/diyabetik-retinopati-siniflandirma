"""src/utils.py için testler (PLAN 1.8).

Nasıl çalıştırılır (proje kökünden):
    python -m pytest tests/test_utils.py -q
"""

import random

import numpy as np
import torch

from src.utils import get_device, set_seed


def draw_random_numbers():
    """Üç kütüphaneden birer rastgele sayı çeker."""
    return (random.random(), np.random.rand(), torch.rand(1).item())


def test_set_seed_repeats_numbers():
    set_seed(42)
    first_draw = draw_random_numbers()
    set_seed(42)
    second_draw = draw_random_numbers()
    assert first_draw == second_draw


def test_different_seeds_differ():
    set_seed(1)
    first_tensor = torch.rand(3)
    set_seed(2)
    second_tensor = torch.rand(3)
    assert not torch.equal(first_tensor, second_tensor)


def test_get_device_known_type():
    assert get_device().type in {"cuda", "mps", "cpu"}


def test_get_device_falls_back_to_cpu(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: False)
    assert get_device().type == "cpu"


def test_get_device_prefers_cuda(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    assert get_device().type == "cuda"
