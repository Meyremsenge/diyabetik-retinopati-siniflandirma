"""Tekrar politikasını uygular ve tabakalı train/val/test bölmesini yazar (PLAN 2.4).

Ne yapar: 2.3'ün duplicate_groups.csv dosyasına göre tekrar eden görüntüleri eler,
kalanları sınıf oranlarını koruyarak %70/%15/%15 böler ve splits/aptos_splits.csv'yi yazar.
Dosya bir kez üretilir; zaten varsa betik üzerine yazmaz (ekip onayı gerekir).

Nasıl çalıştırılır (proje kökünden):
    python -m src.make_splits --data-root data/processed/aptos_512
"""
import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.inspect_dataset import load_labels

SPLIT_FRACTIONS = {"train": 0.70, "val": 0.15, "test": 0.15}


def apply_duplicate_policy(labels: pd.DataFrame, groups: pd.DataFrame) -> pd.DataFrame:
    """Her görüntü için excluded (bool) ve note ("", "duplicate", "conflicting_label") üretir.

    Çelişkili grubun tamamı elenir. Tutarlı grupta en küçük id_code kalır, diğerleri elenir.
    """
    policy = labels[["id_code", "diagnosis"]].copy()
    policy["excluded"] = False
    policy["note"] = ""
    policy = policy.set_index("id_code")

    for _, group in groups.groupby("group_id"):
        ids = sorted(group["id_code"])
        if group["conflicting"].any():
            policy.loc[ids, "excluded"] = True
            policy.loc[ids, "note"] = "conflicting_label"
        else:
            duplicates = ids[1:]
            policy.loc[duplicates, "excluded"] = True
            policy.loc[duplicates, "note"] = "duplicate"

    return policy.reset_index()


def stratified_split(df: pd.DataFrame, seed: int = 42) -> pd.Series:
    """Elenmemiş satırları sınıf oranını koruyarak train/val/test'e ayırır.

    Girdi sırası sonucu değiştirmesin diye önce id_code'a göre sıralanır.
    Dönen Series'in index'i df ile aynıdır.
    """
    ordered = df.sort_values("id_code")
    test_fraction = SPLIT_FRACTIONS["test"]
    val_fraction_of_rest = SPLIT_FRACTIONS["val"] / (1 - test_fraction)

    rest_index, test_index = train_test_split(
        ordered.index, test_size=test_fraction,
        stratify=ordered["diagnosis"], random_state=seed,
    )
    rest = ordered.loc[rest_index]
    train_index, val_index = train_test_split(
        rest.index, test_size=val_fraction_of_rest,
        stratify=rest["diagnosis"], random_state=seed,
    )

    split = pd.Series(index=df.index, dtype=object)
    split.loc[train_index] = "train"
    split.loc[val_index] = "val"
    split.loc[test_index] = "test"
    return split


def make_splits(labels: pd.DataFrame, groups: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Sütunları tam olarak id_code, split, note olan, id_code'a göre sıralı tabloyu üretir."""
    policy = apply_duplicate_policy(labels, groups)
    policy["split"] = "excluded"
    kept = policy[~policy["excluded"]]
    policy.loc[kept.index, "split"] = stratified_split(kept, seed)
    return policy.sort_values("id_code")[["id_code", "split", "note"]].reset_index(drop=True)


def print_summary(table: pd.DataFrame, labels: pd.DataFrame) -> None:
    """Her split için toplam ve sınıf bazlı sayıları, elenenlerin özetini yazar."""
    merged = table.merge(labels[["id_code", "diagnosis"]], on="id_code")
    per_class = pd.crosstab(merged["split"], merged["diagnosis"])
    per_class["toplam"] = per_class.sum(axis=1)
    print(per_class)
    excluded = table[table["split"] == "excluded"]
    n_duplicate = (excluded["note"] == "duplicate").sum()
    n_conflicting = (excluded["note"] == "conflicting_label").sum()
    print(f"excluded: {len(excluded)} (duplicate {n_duplicate}, conflicting_label {n_conflicting})")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Tekrar politikasını uygular ve tabakalı train/val/test bölmesini yazar."
    )
    parser.add_argument("--data-root", type=Path, required=True,
                        help="train.csv içeren klasör (512 kopya)")
    parser.add_argument("--groups", type=Path,
                        default=Path("outputs/data_reports/duplicate_groups.csv"),
                        help="tekrar grupları (varsayılan: outputs/data_reports/duplicate_groups.csv)")
    parser.add_argument("--out", type=Path, default=Path("splits/aptos_splits.csv"),
                        help="çıktı (varsayılan: splits/aptos_splits.csv)")
    parser.add_argument("--seed", type=int, default=42,
                        help="rastgelelik tohumu (varsayılan: 42)")
    args = parser.parse_args(argv)

    if args.out.exists():
        raise SystemExit(
            f"{args.out} zaten var; splits dosyası zaten var; değiştirmek ekip onayı ister."
        )

    labels = load_labels(args.data_root / "train.csv")
    groups = pd.read_csv(args.groups, dtype={"id_code": str})
    table = make_splits(labels, groups, args.seed)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.out, index=False)
    print_summary(table, labels)
    print(f"Yazıldı: {args.out} ({len(table)} satır)")


if __name__ == "__main__":
    main()
