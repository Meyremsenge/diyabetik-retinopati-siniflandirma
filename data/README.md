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
- Gerçek yapı (zip'i `data/raw/idrid/` altına aç, git dışı):
  - Etiketler: `B. Disease Grading/2. Groundtruths/a. IDRiD_Disease Grading_Training Labels.csv` ve `b. IDRiD_Disease Grading_Testing Labels.csv`. Sütunlar `Image name`, `Retinopathy grade`, `Risk of macular edema ` (sonda boşluk var; eğitim CSV'sinde ayrıca boş sütunlar var).
  - Görüntüler: `B. Disease Grading/1. Original Images/a. Training Set/` (413) ve `b. Testing Set/` (103), uzantı `.jpg`, adlar `IDRiD_001` biçiminde (iki kümede aynı adlar var).
- Hazırlık: `src/prepare_idrid.py` `train_`/`test_` öneki ekler, APTOS ile aynı ön işlemeden geçirir ve `data/processed/idrid_512/` altına `<image_id>.jpg` + `idrid_labels.csv` (`image_id, diagnosis`) yazar:
  ```bash
  R="data/raw/idrid/B. Disease Grading"
  python -m src.prepare_idrid --train-csv "$R/2. Groundtruths/a. IDRiD_Disease Grading_Training Labels.csv" --test-csv "$R/2. Groundtruths/b. IDRiD_Disease Grading_Testing Labels.csv" --train-images "$R/1. Original Images/a. Training Set" --test-images "$R/1. Original Images/b. Testing Set" --out-dir data/processed/idrid_512
  ```

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
