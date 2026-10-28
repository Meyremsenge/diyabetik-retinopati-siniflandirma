"""IDRiD Disease Grading verisini APTOS ile aynı ön işlemeden geçirir (PLAN 3.4).

Ne yapar: IDRiD train ve test görüntülerini `prepare_image` ile (isteğe bağlı Ben Graham)
512 px kare JPEG yapar, etiketleri `image_id, diagnosis` biçiminde idrid_labels.csv'ye yazar.
İki kümede de aynı adlar (IDRiD_001) olabildiği için image_id'ye train_/test_ öneki eklenir.
Model bu veriyi yalnız final değerlendirmede (--final) görür; burada tahmin yapılmaz.

Nasıl çalıştırılır (yollar ve sütun adları indirilen dosyaya bakılarak verilir):
    python -m src.prepare_idrid --train-csv <csv> --test-csv <csv> \\
        --train-images <klasör> --test-images <klasör> --out-dir data/processed/idrid_512
"""
import argparse
from pathlib import Path

import pandas as pd
from PIL import Image
from tqdm import tqdm

from src.preprocessing import ben_graham as apply_ben_graham, prepare_image


def read_idrid_labels(csv_path: Path, image_col: str, grade_col: str, prefix: str) -> pd.DataFrame:
    """CSV'yi temizleyip image_id, source_name, diagnosis sütunlu tabloya çevirir."""
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    for column in (image_col, grade_col):
        if column not in df.columns:
            raise ValueError(
                f"{csv_path} içinde '{column}' sütunu yok. Dosyadaki sütunlar: {list(df.columns)}"
            )
    df = df.dropna(subset=[image_col, grade_col])

    grades = df[grade_col].astype(int)
    invalid = grades[~grades.between(0, 4)]
    if not invalid.empty:
        raise ValueError(f"{csv_path} içinde 0–4 dışı derece var: {sorted(invalid.unique())}")

    source_names = df[image_col].astype(str).str.strip()
    return pd.DataFrame({
        "image_id": f"{prefix}_" + source_names,
        "source_name": source_names,
        "diagnosis": grades,
    }).reset_index(drop=True)


def prepare_idrid(
    train_csv: Path, test_csv: Path, train_images: Path, test_images: Path, out_dir: Path,
    size: int = 512, ben_graham: bool = False,
    image_col: str = "Image name", grade_col: str = "Retinopathy grade",
    ext: str = ".jpg",
) -> pd.DataFrame:
    """Görüntüleri işleyip out_dir'e yazar, idrid_labels.csv'yi üretir ve tabloyu döndürür."""
    out_dir.mkdir(parents=True, exist_ok=True)
    parts = [
        (read_idrid_labels(train_csv, image_col, grade_col, "train"), train_images),
        (read_idrid_labels(test_csv, image_col, grade_col, "test"), test_images),
    ]

    for labels, image_dir in parts:
        for row in tqdm(labels.itertuples(), total=len(labels), desc="IDRiD ön işleme"):
            with Image.open(image_dir / f"{row.source_name}{ext}") as img:
                prepared = prepare_image(img, size)
            if ben_graham:
                prepared = apply_ben_graham(prepared)
            prepared.save(out_dir / f"{row.image_id}.jpg", format="JPEG", quality=95)

    combined = pd.concat([labels for labels, _ in parts], ignore_index=True)
    result = combined[["image_id", "diagnosis"]]
    result.to_csv(out_dir / "idrid_labels.csv", index=False)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="IDRiD Disease Grading verisini ortak biçime çevirir."
    )
    parser.add_argument("--train-csv", type=Path, required=True)
    parser.add_argument("--test-csv", type=Path, required=True)
    parser.add_argument("--train-images", type=Path, required=True)
    parser.add_argument("--test-images", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--size", type=int, default=512,
                        help="kenar uzunluğu, piksel (varsayılan: 512)")
    parser.add_argument("--ben-graham", action="store_true",
                        help="Ben Graham dönüşümünü de uygula")
    parser.add_argument("--image-col", default="Image name",
                        help="görüntü adı sütunu (varsayılan: 'Image name')")
    parser.add_argument("--grade-col", default="Retinopathy grade",
                        help="derece sütunu (varsayılan: 'Retinopathy grade')")
    parser.add_argument("--ext", default=".jpg",
                        help="ham görüntü uzantısı (varsayılan: .jpg)")
    args = parser.parse_args(argv)

    result = prepare_idrid(
        args.train_csv, args.test_csv, args.train_images, args.test_images, args.out_dir,
        args.size, args.ben_graham, args.image_col, args.grade_col, args.ext,
    )
    distribution = result["diagnosis"].value_counts().sort_index().to_dict()
    print(f"Yazılan görüntü: {len(result)} · {args.out_dir}")
    print(f"Sınıf dağılımı: {distribution}")


if __name__ == "__main__":
    main()
