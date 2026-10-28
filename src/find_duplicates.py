"""Tekrar eden ve çelişkili etiketli görüntüleri bulur (PLAN 2.3).

Ne yapar: Birebir aynı (MD5) ve çok benzer (pHash) görüntü çiftlerini bulup gruplar,
bir grupta birbirinden farklı etiket varsa o grubu "çelişkili" işaretler.
2.4 (make_splits) `duplicate_groups.csv` dosyasını okuyup bölmeyi buna göre yapar.

Nasıl çalıştırılır (proje kökünden):
    python -m src.find_duplicates --data-root data/processed/aptos_512
Çıktılar (git dışı): <out-dir>/duplicate_groups.csv ve <out-dir>/candidate_pairs.csv
"""
import argparse
import hashlib
from pathlib import Path

import imagehash
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

from src.inspect_dataset import load_labels

REVIEW_MAX_DISTANCE = 10  # eşik seçimi için bu mesafeye kadar tüm çiftler listelenir


def md5_of_file(path: Path) -> str:
    """Dosyanın baytlarından MD5 üretir; birebir aynı dosyalar aynı değeri verir."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def phash_bits(path: Path) -> np.ndarray:
    """Görüntünün 64 bitlik pHash'ini bool dizi olarak döndürür."""
    with Image.open(path) as img:
        return imagehash.phash(img).hash.flatten()


def find_pairs(
    ids: list[str], bits: np.ndarray, max_distance: int
) -> list[tuple[str, str, int]]:
    """Hamming mesafesi max_distance veya daha az olan (id_a, id_b, mesafe) çiftlerini bulur."""
    pairs = []
    for i in range(len(ids) - 1):
        distances = (bits[i] != bits[i + 1:]).sum(axis=1)
        for offset in np.where(distances <= max_distance)[0]:
            j = i + 1 + offset
            id_a, id_b = sorted([ids[i], ids[j]])
            pairs.append((id_a, id_b, int(distances[offset])))
    return sorted(pairs, key=lambda pair: (pair[2], pair[0], pair[1]))


def group_pairs(pairs: list[tuple[str, str]]) -> dict[str, int]:
    """Çiftleri birleştirip gruplar: {id_code: group_id}. Numaralar en küçük id_code'a göre verilir."""
    parent: dict[str, str] = {}

    def find_root(item: str) -> str:
        parent.setdefault(item, item)
        while parent[item] != item:
            parent[item] = parent[parent[item]]  # yolu kısalt
            item = parent[item]
        return item

    for id_a, id_b in pairs:
        parent[find_root(id_a)] = find_root(id_b)

    members: dict[str, list[str]] = {}
    for item in list(parent):
        members.setdefault(find_root(item), []).append(item)

    groups_by_smallest_id = sorted(members.values(), key=min)
    return {
        item: group_id
        for group_id, group_members in enumerate(groups_by_smallest_id)
        for item in group_members
    }


def build_group_table(groups: dict[str, int], labels: pd.DataFrame) -> pd.DataFrame:
    """group_id, id_code, diagnosis, conflicting sütunlu tabloyu üretir."""
    table = pd.DataFrame(
        {"group_id": list(groups.values()), "id_code": list(groups.keys())}
    )
    table = table.merge(labels[["id_code", "diagnosis"]], on="id_code", how="left")
    different_labels = table.groupby("group_id")["diagnosis"].transform("nunique") > 1
    table["conflicting"] = different_labels
    return table.sort_values(["group_id", "id_code"]).reset_index(drop=True)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Tekrar eden ve çelişkili etiketli görüntüleri bulur."
    )
    parser.add_argument("--data-root", type=Path, required=True,
                        help="train.csv ve görüntüleri içeren klasör (512 kopya)")
    parser.add_argument("--threshold", type=int, default=0,
                        help="pHash Hamming eşiği (varsayılan: 0, bkz. KARAR_KAYDI D-18)")
    parser.add_argument("--ext", default=".jpg",
                        help="görüntü uzantısı (varsayılan: .jpg)")
    parser.add_argument("--out-dir", type=Path, default=Path("outputs/data_reports"),
                        help="rapor klasörü (varsayılan: outputs/data_reports)")
    args = parser.parse_args(argv)

    labels = load_labels(args.data_root / "train.csv")
    ids = labels["id_code"].tolist()
    diagnosis_by_id = dict(zip(labels["id_code"], labels["diagnosis"]))

    md5_by_id = {}
    bits_list = []
    for image_id in tqdm(ids, desc="MD5 ve pHash"):
        path = args.data_root / f"{image_id}{args.ext}"
        md5_by_id[image_id] = md5_of_file(path)
        bits_list.append(phash_bits(path))
    bits = np.array(bits_list, dtype=bool)

    candidate_pairs = find_pairs(ids, bits, REVIEW_MAX_DISTANCE)
    same_md5_pairs = [
        (id_a, id_b) for id_a, id_b, _ in candidate_pairs
        if md5_by_id[id_a] == md5_by_id[id_b]
    ]
    close_pairs = [
        (id_a, id_b) for id_a, id_b, distance in candidate_pairs
        if distance <= args.threshold
    ]
    groups = group_pairs(same_md5_pairs + close_pairs)
    group_table = build_group_table(groups, labels)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    group_table.to_csv(args.out_dir / "duplicate_groups.csv", index=False)
    pairs_table = pd.DataFrame(
        [
            (id_a, id_b, distance, md5_by_id[id_a] == md5_by_id[id_b],
             diagnosis_by_id[id_a], diagnosis_by_id[id_b])
            for id_a, id_b, distance in candidate_pairs
        ],
        columns=["id_a", "id_b", "distance", "same_md5", "diagnosis_a", "diagnosis_b"],
    )
    pairs_table.to_csv(args.out_dir / "candidate_pairs.csv", index=False)

    n_conflicting = group_table.loc[group_table["conflicting"], "group_id"].nunique()
    print(f"Görüntü: {len(ids)}")
    print(f"Birebir aynı (MD5) çift: {len(same_md5_pairs)}")
    print(f"pHash <= {args.threshold} çift: {len(close_pairs)}")
    print(
        f"Tekrar grubu: {group_table['group_id'].nunique()} · "
        f"gruplardaki görüntü: {len(group_table)} · çelişkili grup: {n_conflicting}"
    )


if __name__ == "__main__":
    main()
