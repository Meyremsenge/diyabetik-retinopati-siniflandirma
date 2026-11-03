# VisionDx — Deney Kaydı

> **Kural:** Buraya yalnız gerçekten çalışmış bir koşunun `outputs/runs/<run_id>/metrics_*.json` dosyasındaki değerler yazılır.
> Çalışmayan veya yarıda kalan deney **"başarısız"** ya da **"çalıştırılmadı"** diye yazılır. Tahmini/uydurma değer yazılmaz.
> Test ve IDRiD sütunları yalnız H4'teki final model için doldurulur.

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
| E4 | | | | | + Ben Graham | | | | | | çalıştırılmadı |

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
