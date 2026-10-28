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
| E0 | | B | | resnet18 | kırp+512 | CE | | — | — | — | Duman testi, raporlanmaz |
| E1 | | B | | resnet50 | kırp+512 | CE | | | | | çalıştırılmadı |
| E2 | | B | | efficientnet_b3 | kırp+512 | CE | | | | | çalıştırılmadı |
| E3 | | B | | | kırp+512 | ağırlıklı CE | | | | | çalıştırılmadı |
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
