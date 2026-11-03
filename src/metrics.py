"""Projedeki tüm metriklerin hesaplandığı tek yer (PLAN 1.11).

Accuracy, macro F1, QWK, sınıf bazlı recall ve karışıklık matrisi burada
hesaplanır. Başka hiçbir dosya bu metrikleri yeniden hesaplamaz; böylece
üç kişi de aynı sayıyı bulur.

Nasıl kullanılır:
    from src.metrics import compute_metrics
    sonuc = compute_metrics(y_true, y_pred)

Test:
    python -m pytest tests/test_metrics.py -q
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    recall_score,
)

CLASS_LABELS = [0, 1, 2, 3, 4]


def check_inputs(y_true, y_pred):
    """Girdileri doğrular ve NumPy dizisine çevirir."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if len(y_true) != len(y_pred):
        raise ValueError(
            f"y_true ({len(y_true)}) ve y_pred ({len(y_pred)}) uzunlukları farklı."
        )
    if len(y_true) == 0:
        raise ValueError("y_true ve y_pred boş olamaz.")

    for name, values in (("y_true", y_true), ("y_pred", y_pred)):
        unknown = sorted(set(values.tolist()) - set(CLASS_LABELS))
        if unknown:
            raise ValueError(
                f"{name} içinde geçersiz sınıf var: {unknown}. "
                f"Geçerli sınıflar: {CLASS_LABELS}."
            )
    return y_true, y_pred


def compute_metrics(y_true, y_pred) -> dict:
    """Gerçek ve tahmin edilen dereceler (0-4) için tüm metrikleri döndürür.

    Sıra önemlidir: önce gerçek (y_true), sonra tahmin (y_pred).
    Dönen sözlük doğrudan json.dump ile yazılabilir.
    """
    y_true, y_pred = check_inputs(y_true, y_pred)

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(
            f1_score(
                y_true, y_pred, labels=CLASS_LABELS, average="macro", zero_division=0
            )
        ),
        "qwk": float(
            cohen_kappa_score(
                y_true, y_pred, labels=CLASS_LABELS, weights="quadratic"
            )
        ),
        "recall_per_class": recall_score(
            y_true, y_pred, labels=CLASS_LABELS, average=None, zero_division=0
        ).tolist(),
        "confusion_matrix": confusion_matrix(
            y_true, y_pred, labels=CLASS_LABELS
        ).tolist(),
        "n": int(len(y_true)),
    }


def severe_recall(metrics: dict) -> float:
    """Ağır sınıfların (3 ve 4) recall ortalaması; D-17 eşitlik kuralında kullanılır."""
    recalls = metrics["recall_per_class"]
    return (recalls[3] + recalls[4]) / 2


def pick_best(candidates: list[dict], tie_margin: float = 0.01) -> str:
    """D-17: en yüksek QWK; ikinciyle fark tie_margin'den küçükse severe_recall büyük olan.

    candidates: [{"run_id": str, "qwk": float, "severe_recall": float}, ...]
    """
    ranked = sorted(candidates, key=lambda item: item["qwk"], reverse=True)
    first = ranked[0]
    if len(ranked) == 1:
        return first["run_id"]
    second = ranked[1]
    if first["qwk"] - second["qwk"] < tie_margin and second["severe_recall"] > first["severe_recall"]:
        return second["run_id"]
    return first["run_id"]
