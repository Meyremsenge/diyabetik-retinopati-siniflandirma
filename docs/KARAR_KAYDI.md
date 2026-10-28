# VisionDx — Karar Kaydı

> Her önemli karar bir satır. Karar değişirse eski satır silinmez; yeni satır eklenir ve eskisi "Değişti → D-xx" olur.

| ID | Tarih | Karar | Gerekçe | Durum |
|---|---|---|---|---|
| D-01 | 2026-10-18 | Ana veri seti **APTOS 2019** (3.662 etiketli görüntü) | 1. ve 2. hafta raporlarında seçildi; 0–4 ICDR etiketli, açık erişimli | Kesin |
| D-02 | 2026-10-18 | Baseline **ResNet50**, karşılaştırma **EfficientNet-B3**; ResNet18 yalnız duman testi | Raporlarla tutarlı; proje tanımı "modellerin karşılaştırılmasını" istiyor. Kodda fark tek satır | Kesin |
| D-03 | 2026-10-18 | EfficientNet-B4, ViT/Swin, ensemble **yapılmayacak** | 7 hafta, 3 kişi; iki model karşılaştırması amacı karşılıyor | Kesin |
| D-04 | 2026-10-18 | Yalnız **torchvision** (timm yok), augmentation torchvision v2 ile (Albumentations yok), ön işleme Pillow+NumPy ile (OpenCV yok) | Daha az bağımlılık, daha kolay kurulum ve açıklama | Kesin |
| D-05 | 2026-10-18 | **W&B yerine** yerel deney kaydı: `history.csv` + `env.txt` + `docs/DENEY_KAYDI.md` | Hesap/anahtar yönetimi yok; deney sayısı az (≈5) | Kesin — FG-4 güncellendi |
| D-06 | 2026-10-18 | Birincil değerlendirme: **tekrar-farkında, tabakalı 70/15/15 bölme**; 5-fold CV *Should* (H4) | Önce çalışan bir hat; 5-fold zamana bağlı | Kesin — FG-2 / FOG-1 güncellendi |
| D-07 | 2026-10-18 | Tekrar görüntüler: tutarlı grupta tek temsilci, **çelişkili etiketli grup tamamen çıkarılır** | Sızıntıyı ve gürültülü etiketi önler; sayılar raporlanır | Kesin |
| D-08 | 2026-10-18 | Test kümesi ve IDRiD yalnız dondurulmuş final modelle **bir kez** | Dürüst değerlendirme; seçim yalnız val QWK ile | Kesin |
| D-09 | 2026-10-18 | Dış test **IDRiD (516)**; Messidor-2 *Could* (Google konsensüs etiketleriyle) | IDRiD açık lisanslı ve etiketli; Messidor-2 ek lisans adımı istiyor | Kesin — FG-1 / FG-8 güncellendi |
| D-10 | 2026-10-18 | Ben Graham *Should* (E4), CLAHE *Could* | Her ön işleme ayrı deney; zaman sınırlı | Kesin — FG-3 güncellendi |
| D-11 | 2026-10-18 | Regresyon + eşik optimizasyonu *Could* (H6) | Önce sınıflandırma baseline'ı | Kesin — FG-7 aynı |
| D-12 | 2026-10-18 | Grad-CAM (`grad-cam` kütüphanesi) ve **Streamlit** arayüzü *Must* | Proje tanımı ve FG-9/FG-10 | Kesin |
| D-13 | 2026-10-18 | Python **3.12**, PyTorch 2.14.1; yerel GPU için `cu126` | Sürücü 566.07 ile uyumlu; 3.14 çok yeni | Kesin |
| D-14 | 2026-10-18 | Veri hazırlama Kaggle'da; ekip **512 px önbelleği** (private Kaggle dataset) kullanır | Meyrem'in diskinde 13 GB boş; ham veri ~10 GB | Kesin |
| D-15 | 2026-10-18 | Görüntü boyutu 384 (bellek yetmezse tüm modellerde 320) | 6 GB GPU ile uyum; tüm modellerde aynı koşul | Ölçülünce kesinleşecek |
| D-16 | 2026-10-18 | FOG-3: "QWK farkı ≤ 0,01" eşiği yerine **aynı seed ile 2 eğitimin farkı raporlanır** | GPU'da tam belirlenimcilik garanti değil | Kesin — FOG-3 güncellendi |
| D-17 | 2026-10-18 | Final model seçim kuralı: en yüksek val QWK; fark < 0,01 ise sınıf 3+4 recall ortalaması | Kural sonuçlar görülmeden sabitlendi | Kesin |
| D-18 | 2026-10-28 | Tekrar tespitinde pHash eşiği **0** (varsayılan 4 değil) | Gerçek APTOS'ta eşik 4 tek bir grupta 248 görüntü topladı (zincirleme yanlış eşleşme; 249 grup / 1384 görüntü). Eşik 0: 139 grup / 287 görüntü / 37 çelişkili, literatürdeki beklentiyle (~130/~270/~37) uyumlu. Hesap `candidate_pairs.csv`'den | Kesin |

## 2. hafta gereksinimlerine etkisi (haftalık rapora yazılacak)

| Gereksinim | Eski | Yeni |
|---|---|---|
| FG-1 | APTOS + IDRiD + Messidor-2 | APTOS + IDRiD; Messidor-2 *Could* |
| FG-2 | pHash + 5-fold grup bölme | pHash + tekrar politikası + 70/15/15 tabakalı bölme; 5-fold *Should* |
| FG-3 | Kırpma, boyut, Ben Graham / CLAHE | Kırpma, boyut zorunlu; Ben Graham *Should*; CLAHE *Could* |
| FG-4 | ResNet50, EfficientNet-B3/B4, W&B | ResNet50 + EfficientNet-B3, config ile; yerel deney kaydı |
| FG-8 | Messidor-2 ve IDRiD dış test | IDRiD dış test (Messidor-2 *Could*) |
| FOG-1 | 5-fold ort. QWK ≥ 0,85 | APTOS iç test QWK ≥ 0,85 hedefi (garanti değil); 5-fold yapılırsa ayrıca |
| FOG-3 | Tekrar eğitimde QWK farkı ≤ 0,01 | Aynı seed ile 2 eğitimin farkı raporlanır |
