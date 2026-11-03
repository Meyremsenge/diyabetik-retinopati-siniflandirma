# VisionDx — Deney Kaydı

> **Kural:** Buraya yalnız gerçekten çalışmış bir koşunun `outputs/runs/<run_id>/metrics_*.json` dosyasındaki değerler yazılır.
> Çalışmayan veya yarıda kalan deney **"başarısız"** ya da **"çalıştırılmadı"** diye yazılır. Tahmini/uydurma değer yazılmaz.
> Test ve IDRiD sütunları yalnız H4'teki final model için doldurulur.

## Koşu çıktıları (Drive)

E1–E3 koşu çıktıları (`best.pt` dışındakiler: `metrics_val.json`, `history.csv`, `val_predictions.csv`, `config.yaml`, karışıklık matrisleri) ekip Drive klasöründedir: https://drive.google.com/drive/folders/1h7SURldpb3U_TDq9yLbF3M4r9rhUdN_J?usp=drive_link
Zip'i açıp koşu klasörlerini `outputs/runs/` altına koyun (git'e girmez). `best.pt` gerekirse Büşra'dan istenir.

## Ortak koşullar

| Ayar | Değer |
|---|---|
| Bölme | `splits/aptos_splits.csv` (commit: 46dc40c) |
| Seed | 42 |
| Görüntü boyutu | 384 *(değişirse buraya)* |
| Epoch / erken durdurma | 15 / val QWK 4 epoch |
| Optimizer | AdamW lr 1e-4, wd 1e-4, cosine |

## Koşular

| Deney | Run ID | Kim | Donanım | Model | Ön işleme | Loss | Süre | Val QWK | Val macro F1 | Val recall (0/1/2/3/4) | Durum / not |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E0 | 20261028-1705_resnet18_smoke | R (B adına) | Kaggle Tesla T4 | resnet18 | kırp+512 | CE | | — | — | — | Duman testi geçti (--limit 64 --epochs 1; ResNet50 baseline config'i de çalıştı: 20261028-1710_resnet50_baseline), raporlanmaz |
| E1 | 20261028-1716_resnet50_baseline | R (B adına) | Kaggle Tesla T4 | resnet50 | kırp+512 | CE | 5,5 dk | 0.903 | 0.663 | 0.981 / 0.471 / 0.942 / 0.320 / 0.450 | Tamamlandı. 9. epoch'ta erken durdurma, en iyi epoch 5 (metrics_val.json, n=522). Kaggle torch 2.11.0+cu128, commit 14a4a08 |
| E2 | 20261102-0849_efficientnet_b3_effb3 | B | Kaggle Tesla T4 | efficientnet_b3 | kırp+512 | CE | 7,5 dk | 0.896 | 0.662 | 0.981 / 0.471 / 0.848 / 0.560 / 0.400 | Tamamlandı. 7. epoch'ta erken durdurma, en iyi epoch 3 (metrics_val.json, n=522). Kaggle torch 2.11.0+cu128, commit 0df1961. Batch/boyut E1 ile aynı (16 / 384) |
| E3 | 20261102-1049_efficientnet_b3_weighted_ce | B | Kaggle Tesla T4 | efficientnet_b3 | kırp+512 | ağırlıklı CE | 11,5 dk | 0.898 | 0.687 | 0.981 / 0.667 / 0.717 / 0.480 / 0.650 | Tamamlandı. 13. epoch'ta erken durdurma, en iyi epoch 9 (metrics_val.json, n=522). Taban: E2 (D-17: QWK farkı <0,01, sınıf 3+4 recall ortalaması E2 0,480 > E1 0,385). Ağırlıklar [0.389, 2.062, 0.754, 4.124, 2.645]. Kaggle torch 2.11.0+cu128, commit 28d0285 |
| E4 | 20261103-1104_efficientnet_b3_ben_graham | B | Kaggle Tesla T4 | efficientnet_b3 | + Ben Graham | ağırlıklı CE | 15,7 dk | 0.913 | 0.672 | 0.974 / 0.686 / 0.681 / 0.520 / 0.600 | Tamamlandı. 15 epoch koşuldu, en iyi epoch 11 (metrics_val.json, n=522). Taban: E3 (D-17), yalnız ön işleme ve data_root farklı (`aptos_512_bg`). Ağırlıklar E3 ile aynı. Kaggle torch 2.11.0+cu128, commit 357e92f. Tek koşu, tek seed |

## Final model (H4'te doldurulur)

| Alan | Değer |
|---|---|
| Seçilen deney | |
| Seçim gerekçesi (D-17'ye göre) | |
| Checkpoint konumu (Drive) | |
| Git commit | |

| Değerlendirme | n | QWK | Macro F1 | Accuracy | Recall (0/1/2/3/4) |
|---|---|---|---|---|---|
| APTOS val | | | | | |
| APTOS test (tek sefer) | | | | | |
| IDRiD (tek sefer) | | | | | |

## 5-fold (Should)

| Fold | 1 | 2 | 3 | 4 | 5 | Ort. ± std |
|---|---|---|---|---|---|---|
| QWK | | | | | | |

## Tekrarlanabilirlik (PLAN 5.4)

| Koşu | Val QWK | Fark |
|---|---|---|
| Final config — 1 | | |
| Final config — 2 (aynı seed) | | |

## Karşılaştırma (val, E1–E4)

> `python -m src.evaluate --compare outputs/runs/<e1> ... <e4>` çıktısıdır (`outputs/figures/comparison.md`); değerler `metrics_val.json` ve `history.csv` dosyalarından gelir. D-17 kuralına göre önde: E4 (QWK 0,913; ikincisi E1 0,903, fark ≥ 0,01). Tek koşu, tek seed.

| run_id | experiment | model | loss | preprocessing | image_size | val_qwk | val_macro_f1 | recall_3 | recall_4 | severe_recall | epochs_run | best_epoch | train_minutes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20261028-1716_resnet50_baseline | E1 | resnet50 | ce | crop | 384 | 0.903 | 0.663 | 0.320 | 0.450 | 0.385 | 9 | 5 | 5.497 |
| 20261102-0849_efficientnet_b3_effb3 | E2 | efficientnet_b3 | ce | crop | 384 | 0.896 | 0.662 | 0.560 | 0.400 | 0.480 | 7 | 3 | 7.485 |
| 20261102-1049_efficientnet_b3_weighted_ce | E3 | efficientnet_b3 | weighted_ce | crop | 384 | 0.898 | 0.687 | 0.480 | 0.650 | 0.565 | 13 | 9 | 11.474 |
| 20261103-1104_efficientnet_b3_ben_graham | E4 | efficientnet_b3 | weighted_ce | crop_ben_graham | 384 | 0.913 | 0.672 | 0.520 | 0.600 | 0.560 | 15 | 11 | 15.658 |
