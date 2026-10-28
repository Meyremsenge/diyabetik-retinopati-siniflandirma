"""APTOS görüntülerini kırpıp kare JPEG olarak kaydeder (PLAN 2.2).

Ne yapar: train.csv'deki her görüntüyü `prepare_image` ile (siyah kenar kırp,
kareye tamamla, boyutlandır) işler ve out_dir/<id_code>.jpg olarak yazar.
train.csv de out_dir'e kopyalanır; böylece out_dir tek başına bir veri klasörüdür.

Nasıl çalıştırılır (proje kökünden):
    python -m src.preprocess_images --data-root <ham APTOS klasörü> --out-dir <çıktı klasörü>
Deneme için: --limit 20
"""
import argparse
import shutil
from pathlib import Path

import pandas as pd
from PIL import Image
from tqdm import tqdm

from src.preprocessing import ben_graham as apply_ben_graham, prepare_image


def preprocess_all(
    data_root: Path, out_dir: Path, size: int = 512, limit: int | None = None,
    ben_graham: bool = False,
) -> int:
    """Görüntüleri işleyip out_dir'e yazar, yazılan görüntü sayısını döndürür."""
    csv_path = data_root / "train.csv"
    df = pd.read_csv(csv_path, dtype={"id_code": str})
    image_ids = df["id_code"].tolist()
    if limit is not None:
        image_ids = image_ids[:limit]

    out_dir.mkdir(parents=True, exist_ok=True)
    for image_id in tqdm(image_ids, desc="Ön işleme"):
        with Image.open(data_root / "train_images" / f"{image_id}.png") as img:
            prepared = prepare_image(img, size)
        if ben_graham:
            prepared = apply_ben_graham(prepared)
        prepared.save(out_dir / f"{image_id}.jpg", format="JPEG", quality=95)

    shutil.copy(csv_path, out_dir / "train.csv")
    return len(image_ids)


def folder_size_mb(folder: Path) -> float:
    total_bytes = sum(path.stat().st_size for path in folder.iterdir() if path.is_file())
    return total_bytes / (1024 * 1024)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="APTOS görüntülerini kırpar ve kare JPEG olarak kaydeder."
    )
    parser.add_argument("--data-root", type=Path, required=True,
                        help="train.csv ve train_images/ içeren ham APTOS klasörü")
    parser.add_argument("--out-dir", type=Path, required=True,
                        help="çıktı klasörü (yoksa oluşturulur)")
    parser.add_argument("--size", type=int, default=512,
                        help="kenar uzunluğu, piksel (varsayılan: 512)")
    parser.add_argument("--limit", type=int, default=None,
                        help="yalnız ilk N görüntü (deneme için)")
    parser.add_argument("--ben-graham", action="store_true",
                        help="kırpmadan sonra Ben Graham dönüşümünü uygula (E4)")
    args = parser.parse_args(argv)

    written = preprocess_all(args.data_root, args.out_dir, args.size, args.limit, args.ben_graham)
    print(
        f"Yazılan görüntü: {written} · "
        f"Klasör boyutu: {folder_size_mb(args.out_dir):.1f} MB · {args.out_dir}"
    )


if __name__ == "__main__":
    main()
