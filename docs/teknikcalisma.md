# Teknik Çalışma Notları — `src/metrics.py` (PLAN 1.11)

Sunumda kendi kodumu anlatabilmek için tuttuğum notlar.

## Konu kısaca

`src/metrics.py`, modelin tahmin ettiği derece (0–4) ile gerçek dereceyi karşılaştırıp tüm metrikleri hesaplayan **tek** fonksiyondur: `compute_metrics(y_true, y_pred)`. Sıra önemlidir: önce gerçek, sonra tahmin.

Döndürdüğü değerler:

| Anahtar | Anlamı |
|---|---|
| `accuracy` | Doğru tahmin oranı |
| `macro_f1` | Her sınıfa eşit ağırlık veren F1 skoru |
| `qwk` | Karesel ağırlıklı kappa: tahminin gerçeğe ne kadar uzak olduğunu karesiyle cezalandırır (ana metriğimiz) |
| `recall_per_class` | Her derece için "gerçek vakaların kaçını yakaladık?" |
| `confusion_matrix` | 5×5 karışıklık matrisi (satır = gerçek, sütun = tahmin) |
| `n` | Örnek sayısı |

Akış: girdi doğrulanır (`check_inputs`) → sklearn ile metrikler hesaplanır → sonuç sade Python tiplerine çevrilir (JSON'a yazılabilsin diye).

Neden `labels=[0,1,2,3,4]`: küçük bir val kümesinde bir sınıf hiç görünmese bile matris hep 5×5 çıkar.

## Soru 1 — 3'ü 4 yerine 0 tahmin edersek QWK ne olur?

**Cevap: Azalır.** QWK hatayı derece farkının karesiyle cezalandırır.

- 3 → 4 hatası: 1 derece uzak, ceza 1² = 1
- 3 → 0 hatası: 3 derece uzak, ceza 3² = 9

Doğruluk (accuracy) aynı kalsa bile QWK düşer. Klinik anlamı: ağır hastayı sağlıklı sanmak, bir derece yanılmaktan çok daha kötüdür.

## Soru 2 — `zero_division=0` olmasa ne olur?

`y_true`'da hiç 3 yoksa 3. sınıfın recall'u "0 gerçek örneğe bölme" olur. `zero_division=0` olmazsa sklearn `UndefinedMetricWarning` uyarısı verir ve sonucu kendisi belirler. `zero_division=0` ile bu sınıf için sonuç `0.0` yazılır, uyarı çıkmaz ve JSON'a düzgün bir sayı gider.

## Sunumda tek cümle

"QWK, tahminin gerçeğe ne kadar uzak olduğunu karesiyle cezalandırır; bu yüzden ağır vakayı hafif sanmak metriğimizi sert düşürür."

## Sık hata

`compute_metrics(y_pred, y_true)` gibi sırayı ters vermek. Hata çıkmaz ama recall ve karışıklık matrisi sessizce yanlış olur.
