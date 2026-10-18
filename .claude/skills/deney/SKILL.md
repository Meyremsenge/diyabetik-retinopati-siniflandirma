---
name: deney
description: TEKNIK_TASARIM §8'deki bir deneyi (E0–E5) koşturmaya hazırlar veya biten bir koşuyu kaydeder. Test/IDRiD kullanımını engeller, tek-değişken kuralını kontrol eder ve DENEY_KAYDI.md'ye yalnız gerçek metrics_*.json değerlerini yazar. Kullanıcı /deney yazdığında çalışır.
disable-model-invocation: true
argument-hint: "<E1|E2|...> [kaydet <run_dizini>]"
---

# Deney

İki mod var: **hazırla/koştur** (varsayılan) ve **kaydet**.

## Hazırla / koştur — `/deney E2`

1. TEKNIK_TASARIM §8'den deneyin tanımını oku. Kıyaslandığı deneyin config'ini oku.
2. **Tek değişken kontrolü:** yeni config ile referans config arasındaki farkı göster. Tanımdaki değişken dışında fark varsa dur ve sor.
3. Config yoksa `configs/<deney>.yaml` olarak referanstan türet (yalnız o değişkeni değiştir).
4. Komutu ver:
   - Kaggle: notebook hücresi (EKIP_REHBERI §Büşra'daki akış)
   - Yerel: `python -m src.train --config configs/<ad>.yaml --data-root data/processed/aptos_512`
5. Tahmini süre 30 dakikayı aşıyorsa eğitimi **kendin başlatma**. Komutu ver; kullanıcı başlatsın (CLAUDE.md onay sınırı).

## Kaydet — `/deney E2 kaydet outputs/runs/<run_id>`

1. Run dizininde `config.yaml`, `history.csv`, `val_predictions.csv` olmalı. Yoksa "eksik: ..." de ve dur.
2. `metrics_val.json` yoksa üret: `python -m src.evaluate --predictions <run>/val_predictions.csv`.
3. DENEY_KAYDI.md satırını **yalnız** `metrics_val.json`, `history.csv` (süre) ve `env.txt` (donanım) değerleriyle doldur. QWK ve F1 için 3 ondalık kullan.
4. Koşu yarıda kaldıysa veya hata verdiyse satıra `başarısız — <kısa neden>` yaz; metrik alanlarını boş bırak.
5. Önceki deneylerle 2–3 cümlelik karşılaştırma yap. Fark 0,01'den küçükse "anlamlı fark yok olabilir" de. Tek koşudan kesin sonuç çıkarma.

## Yasaklar

- `split=test` veya IDRiD tahmini yalnız PLAN 4.2/4.3'te `--final` ile yapılır. Bu skill test metriği **yazmaz**.
- Değer tahmin etme, yuvarlayarak "iyileştirme", eksik alanı doldurma yok.
- Duman testi (E0, `--limit`) sonucu tabloya metrik olarak yazılmaz.
