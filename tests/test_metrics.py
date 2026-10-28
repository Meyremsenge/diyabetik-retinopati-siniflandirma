"""src/metrics.py için testler (PLAN 1.11).

Beklenen değerler elle hesaplandı (hesap: docs/planlar/H1.md kart 1.11).

Nasıl çalıştırılır (proje kökünden):
    python -m pytest tests/test_metrics.py -q
"""

import json

import numpy as np
import pytest

from src.metrics import compute_metrics

SMALL_TRUE = [0, 0, 1, 2, 3, 4]
SMALL_PRED = [0, 1, 1, 2, 4, 4]


def assert_small_example(result):
    """Küçük örneğin elle hesaplanmış sonuçlarını denetler."""
    assert result["accuracy"] == pytest.approx(4 / 6)
    assert result["macro_f1"] == pytest.approx(0.6)
    assert result["qwk"] == pytest.approx(13 / 14)
    assert result["recall_per_class"] == pytest.approx([0.5, 1, 1, 0, 1])
    assert result["confusion_matrix"] == [
        [1, 1, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
    ]
    assert result["n"] == 6


def test_perfect_prediction():
    labels = [0, 1, 2, 3, 4]
    result = compute_metrics(labels, labels)

    assert result["accuracy"] == pytest.approx(1.0)
    assert result["macro_f1"] == pytest.approx(1.0)
    assert result["qwk"] == pytest.approx(1.0)
    assert result["recall_per_class"] == pytest.approx([1, 1, 1, 1, 1])
    assert result["confusion_matrix"] == np.eye(5, dtype=int).tolist()
    assert result["n"] == 5


def test_small_example():
    assert_small_example(compute_metrics(SMALL_TRUE, SMALL_PRED))


def test_missing_classes():
    result = compute_metrics([0, 0, 2, 2], [0, 2, 2, 2])

    assert result["accuracy"] == pytest.approx(0.75)
    assert result["macro_f1"] == pytest.approx(22 / 75)
    assert result["qwk"] == pytest.approx(0.5)
    assert result["recall_per_class"] == pytest.approx([0.5, 0, 1, 0, 0])
    assert result["confusion_matrix"] == [
        [1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 2, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]


def test_accepts_numpy_arrays():
    result = compute_metrics(np.array(SMALL_TRUE), np.array(SMALL_PRED))
    assert_small_example(result)


def test_result_is_json_ready():
    result = compute_metrics(SMALL_TRUE, SMALL_PRED)

    json.dumps(result)
    assert set(result) == {
        "accuracy",
        "macro_f1",
        "qwk",
        "recall_per_class",
        "confusion_matrix",
        "n",
    }


def test_length_mismatch_raises():
    with pytest.raises(ValueError):
        compute_metrics([0, 1], [0])


def test_out_of_range_label_raises():
    with pytest.raises(ValueError):
        compute_metrics([0, 1], [0, 5])
