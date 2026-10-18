# Veri klasörü

Bu klasörün içeriği **git'e girmez** (yalnız bu README). Sebep: APTOS kuralları yeniden dağıtımı yasaklıyor ve veri büyük.

## 1. APTOS 2019 — geliştirme verisi

- Kaynak: https://www.kaggle.com/competitions/aptos2019-blindness-detection/data
- Erişim: Kaggle hesabı → yarışma sayfası → kuralları kabul et (her ekip üyesi ayrı ayrı).
- Yapı (Kaggle'da `/kaggle/input/aptos2019-blindness-detection/`):
  - `train.csv` → `id_code`, `diagnosis` (0–4), 3.662 satır
  - `train_images/<id_code>.png`
  - `test.csv`, `test_images/`, `sample_submission.csv` → **kullanılmaz** (etiket yok)
- **Ham veriyi yerele indirmeyin** (~10 GB). Ekip, Rümeysa'nın Kaggle'da ürettiği küçük kopyayı kullanır:
  - Kaggle dataset (private, ekibe paylaşılır): `visiondx-aptos-512` → yerelde `data/processed/aptos_512/`

## 2. IDRiD — dış test verisi (yalnız final model)

- Kaynak: https://ieee-dataport.org/node/956 (ücretsiz IEEE hesabı → "Dataset Files") · bilgi: https://idrid.grand-challenge.org/Data/
- Kullanılan kısım: **B. Disease Grading** (413 train + 103 test görüntü + 2 CSV). İkisi de dış test olarak birlikte kullanılır.
- Lisans: CC BY 4.0 (raporda atıf zorunlu).
- CSV sütun adları indirildikten sonra kontrol edilecek. `src/prepare_idrid.py` bunları `image_id, diagnosis` biçimine çevirir.

## 3. Messidor-2 — isteğe bağlı (Could)

- Görüntüler: https://www.adcis.net/en/third-party/messidor2/ (lisans formu)
- Etiketler: Kaggle "Messidor-2 DR Grades" (Google, uzman konsensüsü). Değerlendirilemez 4 görüntü çıkarılır.

## Beklenen yerel düzen

```text
data/
├── processed/
│   ├── aptos_512/          # <id_code>.jpg (+ train.csv kopyası)
│   ├── aptos_512_bg/       # Ben Graham sürümü (E4)
│   └── idrid_512/          # <image_id>.jpg + idrid_labels.csv
└── raw/                    # (isteğe bağlı) ham dosyalar
```

Gerçek yapı bundan farklıysa kod yazmadan önce bu README güncellenir.
