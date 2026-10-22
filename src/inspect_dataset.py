"""APTOS etiket dosyasını ve görüntü klasörünü kontrol edip ekrana rapor yazar (PLAN 1.6).

Ne yapar: train.csv'yi okur; satır sayısı, tekrarlanan id, geçersiz etiket,
eksik görüntü dosyası, sınıf dağılımı ve görüntü boyutlarını sayar. Dosya üretmez.

Nasıl çalıştırılır (proje kökünden):
    python -m src.inspect_dataset --data-root <train.csv'nin olduğu klasör>
Kaggle'da: --data-root /kaggle/input/aptos2019-blindness-detection
"""
import argparse
from collections import Counter
from pathlib import Path

import pandas as pd
from PIL import Image
from tqdm import tqdm

REQUIRED_COLUMNS = ["id_code", "diagnosis"]
CLASS_LABELS = [0, 1, 2, 3, 4]


def load_labels(csv_path: Path) -> pd.DataFrame:
    """CSV'yi okur; gerekli sütunlar yoksa gerçek sütunları göstererek hata verir."""
    df = pd.read_csv(csv_path, dtype={"id_code": str})
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"{csv_path} içinde {missing_columns} sütunları yok. "
            f"Dosyadaki sütunlar: {list(df.columns)}"
        )
    return df


def summarize_dataset(df: pd.DataFrame, image_dir: Path, ext: str = ".png") -> dict:
    """Etiket tablosunu ve görüntü klasörünü sayarak özet sözlüğü döndürür."""
    labels = df["diagnosis"]
    invalid_labels = sorted(int(v) for v in labels[~labels.isin(CLASS_LABELS)].unique())
    class_counts = {label: int((labels == label).sum()) for label in CLASS_LABELS}

    missing_files = []
    image_sizes = Counter()
    for id_code in tqdm(df["id_code"], desc="Görüntüler", leave=False):
        image_path = image_dir / f"{id_code}{ext}"
        if not image_path.exists():
            missing_files.append(id_code)
            continue
        # Pillow yalnız dosya başlığını okur; görüntüyü belleğe yüklemez.
        with Image.open(image_path) as img:
            image_sizes[img.size] += 1

    return {
        "n_rows": len(df),
        "n_duplicate_ids": int(df["id_code"].duplicated().sum()),
        "invalid_labels": invalid_labels,
        "class_counts": class_counts,
        "missing_files": sorted(missing_files),
        "image_sizes": image_sizes,
    }


def format_report(summary: dict, csv_path: Path) -> str:
    """Özet sözlüğünü okunabilir Türkçe rapor metnine çevirir."""
    n_rows = summary["n_rows"]
    lines = [
        "APTOS veri raporu",
        f"CSV: {csv_path}",
        f"Satır sayısı: {n_rows}",
        f"Tekrarlanan id_code: {summary['n_duplicate_ids']}",
    ]

    invalid_labels = summary["invalid_labels"]
    lines.append(f"Geçersiz etiket: {invalid_labels if invalid_labels else 'yok'}")

    missing_files = summary["missing_files"]
    lines.append(f"Eksik görüntü dosyası: {len(missing_files)}")
    if missing_files:
        lines.append(f"  ilk 10: {', '.join(missing_files[:10])}")

    lines.append("Sınıf dağılımı:")
    for label, count in summary["class_counts"].items():
        percent = 100 * count / n_rows if n_rows else 0.0
        lines.append(f"  {label}: {count} (%{percent:.1f})")

    image_sizes = summary["image_sizes"]
    lines.append("Görüntü boyutu (genişlik x yükseklik):")
    lines.append(f"  farklı boyut sayısı: {len(image_sizes)}")
    if image_sizes:
        most_common = ", ".join(f"{w}x{h} ({n})" for (w, h), n in image_sizes.most_common(5))
        smallest = min(image_sizes, key=lambda size: size[0] * size[1])
        largest = max(image_sizes, key=lambda size: size[0] * size[1])
        lines.append(f"  en sık 5: {most_common}")
        lines.append(
            f"  en küçük alan: {smallest[0]}x{smallest[1]} · "
            f"en büyük alan: {largest[0]}x{largest[1]}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="APTOS etiket dosyasını ve görüntü klasörünü kontrol eder."
    )
    parser.add_argument("--data-root", type=Path, required=True,
                        help="train.csv ve görüntü klasörünü içeren klasör")
    parser.add_argument("--csv", default="train.csv",
                        help="etiket dosyasının adı (varsayılan: train.csv)")
    parser.add_argument("--image-dir", default="train_images",
                        help="görüntü klasörünün adı (varsayılan: train_images)")
    parser.add_argument("--ext", default=".png",
                        help="görüntü uzantısı (varsayılan: .png)")
    args = parser.parse_args(argv)

    csv_path = args.data_root / args.csv
    df = load_labels(csv_path)
    summary = summarize_dataset(df, args.data_root / args.image_dir, args.ext)
    print(format_report(summary, csv_path))


if __name__ == "__main__":
    main()
