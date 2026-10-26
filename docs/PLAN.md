# VisionDx — Proje Planı (tek doğruluk kaynağı)

> Bu dosya **ne yapılacağını, kimin yapacağını ve sırasını** tutar. Her iş başında okunur.
> Madde bitince `- [ ]` → `- [x]` yapılır. Plandan sapma gerekiyorsa önce buraya not düşülür.
> Her maddenin ayrıntısı (adımlar, test, kabul ölçütü) docs/planlar/H<n>.md'deki kartındadır. /durum, /ilerle ve /bitir kartı okur.
> Teknik ayrıntı: [TEKNIK_TASARIM.md](TEKNIK_TASARIM.md) · Kim ne yapar: [EKIP_REHBERI.md](EKIP_REHBERI.md)

**Sahipler:** `[R]` Rümeysa (veri) · `[B]` Büşra (model/eğitim) · `[M]` Meyrem (değerlendirme + demo) · `[E]` tüm ekip

**Süre:** 7 hafta (19 Ekim – 6 Aralık 2026). **Hedef: teknik iş 5. haftanın sonunda biter**; 6. hafta tampon, 7. hafta sunum.
*(H1 = 19 Ekim haftası varsayıldı. Dersin hafta numaraları farklıysa yalnız etiketleri değiştirin.)*

**Git kullanıcı adı → kişi eşlemesi** (`/durum` bunu kullanır; herkes kendi satırını doldurur):

| Kişi | Kısaltma | `git config user.name` |
|---|---|---|
| Rümeysa Akbulut | R | `RumeysaAkbulut` |
| Büşra Yaşar | B | `Büşra` |
| Meyrem Şenge | M | `Meyrem Şenge` |

---

## Kilometre taşları

| # | Hafta sonu | Kilometre taşı | Durum |
|---|---|---|---|
| K1 | H1 | Ortam kuruldu, APTOS doğrulandı, metrik modülü testli | ⬜ |
| K2 | H2 | Veri bölmesi sabit, **ilk ResNet50 baseline doğrulama sonucu kayıtlı** | ⬜ |
| K3 | H3 | EfficientNet-B3 karşılaştırması + 2 ek deney, IDRiD hazır | ⬜ |
| K4 | H4 | Final model seçildi ve donduruldu, test + dış test **bir kez** yapıldı | ⬜ |
| K5 | H5 | Streamlit + Grad-CAM demo çalışıyor, rapor taslağı tam → **proje teknik olarak bitti** | ⬜ |
| K6 | H6 | Tampon / "Could" işleri / rapor cilası | ⬜ |
| K7 | H7 | Final rapor, sunum, demo provası, `v1.0` etiketi | ⬜ |

---

## H1 (19–25 Ekim) — Kurulum ve veriyi tanıma

- [ ] 1.1 `[E]` Python 3.12 ortamı + requirements kurulumu R✅ B✅ M⬜ → [kart](planlar/H1.md#m1-1)
- [ ] 1.2 `[E]` Kaggle hesabı + telefon doğrulaması + APTOS kuralları R✅ B✅ M⬜ → [kart](planlar/H1.md#m1-2)
- [ ] 1.3 `[M]` GitHub collaborator + PR kuralı → [kart](planlar/H1.md#m1-3)
- [ ] 1.4 `[E]` Git kullanıcı adı tablosunu doldur R✅ B✅ M⬜ → [kart](planlar/H1.md#m1-4)
- [ ] 1.5 `[M]` Disk 25 GB + CUDA'lı PyTorch → [kart](planlar/H1.md#m1-5)
- [x] 1.6 `[R]` Veri raporu (`src/inspect_dataset.py`) → [kart](planlar/H1.md#m1-6)
- [x] 1.7 `[R]` Veri seti bölümü rapor taslağı → [kart](planlar/H1.md#m1-7)
- [x] 1.8 `[B]` `src/utils.py` (`set_seed`, `get_device`) → [kart](planlar/H1.md#m1-8)
- [x] 1.9 `[B]` `src/models.py` (`build_model`) → [kart](planlar/H1.md#m1-9)
- [ ] 1.10 `[B]` Transfer learning eğitimini oku/dene → [kart](planlar/H1.md#m1-10)
- [ ] 1.11 `[M]` `src/metrics.py` (`compute_metrics`) → [kart](planlar/H1.md#m1-11)
- [ ] 1.12 `[M]` Metrik açıklaması (RAPOR §7) → [kart](planlar/H1.md#m1-12)
- [ ] 1.13 `[E]` H1 haftalık rapor → [kart](planlar/H1.md#m1-13)

---

## H2 (26 Ekim – 1 Kasım) — Veri hattı ve ilk baseline

- [ ] 2.1 `[R]` `src/preprocessing.py` (kırpma, kareye boyutlandırma) → [kart](planlar/H2.md#m2-1)
- [ ] 2.2 `[R]` `src/preprocess_images.py` (512 px önbellek) → [kart](planlar/H2.md#m2-2)
- [ ] 2.3 `[R]` `src/find_duplicates.py` (tekrar grupları) → [kart](planlar/H2.md#m2-3)
- [ ] 2.4 `[R]` `src/make_splits.py` → `splits/aptos_splits.csv` → [kart](planlar/H2.md#m2-4)
- [ ] 2.5 `[R]` `src/data.py` (`RetinaDataset`, `get_transforms`) → [kart](planlar/H2.md#m2-5)
- [ ] 2.6 `[B]` `configs/resnet50_baseline.yaml` + `src/train.py` → [kart](planlar/H2.md#m2-6)
- [ ] 2.7 `[B]` Duman testi (E0) → [kart](planlar/H2.md#m2-7)
- [ ] 2.8 `[B]` `src/predict.py` → [kart](planlar/H2.md#m2-8)
- [ ] 2.9 `[B]` E1: ResNet50 baseline tam eğitim → [kart](planlar/H2.md#m2-9)
- [ ] 2.10 `[M]` `src/evaluate.py` → [kart](planlar/H2.md#m2-10)
- [ ] 2.11 `[M]` E1'i yerel GPU'da çalıştır, süreyi ölç → [kart](planlar/H2.md#m2-11)
- [ ] 2.12 `[E]` H2 haftalık rapor → [kart](planlar/H2.md#m2-12)

---

## H3 (2–8 Kasım) — Karşılaştırma ve deneyler

- [ ] 3.1 `[B]` E2: EfficientNet-B3 → [kart](planlar/H3.md#m3-1)
- [ ] 3.2 `[B]` E3: ağırlıklı Cross Entropy → [kart](planlar/H3.md#m3-2)
- [ ] 3.3 `[R]` `ben_graham` + E4 → [kart](planlar/H3.md#m3-3)
- [ ] 3.4 `[R]` IDRiD hazırlığı (`src/prepare_idrid.py`) → [kart](planlar/H3.md#m3-4)
- [ ] 3.5 `[M]` Karşılaştırma tablosu + grafikler → [kart](planlar/H3.md#m3-5)
- [ ] 3.6 `[M]` Val hata analizi → [kart](planlar/H3.md#m3-6)
- [ ] 3.7 `[M]` `src/gradcam.py` prototipi → [kart](planlar/H3.md#m3-7)
- [ ] 3.8 `[E]` H3 haftalık rapor → [kart](planlar/H3.md#m3-8)

---

## H4 (9–15 Kasım) — Final model, test ve dış doğrulama

- [ ] 4.1 `[E]` Model seçimi toplantısı + dondurma → [kart](planlar/H4.md#m4-1)
- [ ] 4.2 `[B]` APTOS test tahmini (`--final`, tek sefer) → [kart](planlar/H4.md#m4-2)
- [ ] 4.3 `[R]` IDRiD tahmini (`--final`, tek sefer) → [kart](planlar/H4.md#m4-3)
- [ ] 4.4 `[M]` Test + IDRiD metrikleri ve yorum → [kart](planlar/H4.md#m4-4)
- [ ] 4.5 `[M]` `app/streamlit_app.py` v1 → [kart](planlar/H4.md#m4-5)
- [ ] 4.6 `[B]` Final checkpoint paylaşımı + README notu → [kart](planlar/H4.md#m4-6)
- [ ] 4.7 `[B]` *(Should)* 5-fold çapraz doğrulama (E5) → [kart](planlar/H4.md#m4-7)
- [ ] 4.8 `[E]` H4 haftalık rapor → [kart](planlar/H4.md#m4-8)

---

## H5 (16–22 Kasım) — Demo, açıklanabilirlik, rapor → teknik bitiş

- [ ] 5.1 `[M]` Grad-CAM örnek galerisi → [kart](planlar/H5.md#m5-1)
- [ ] 5.2 `[M]` Streamlit son hâli + CPU yanıt süresi → [kart](planlar/H5.md#m5-2)
- [ ] 5.3 `[R]` Temiz Mac'te uçtan uca kurulum denemesi → [kart](planlar/H5.md#m5-3)
- [ ] 5.4 `[B]` Tekrarlanabilirlik (2. eğitim, aynı seed) → [kart](planlar/H5.md#m5-4)
- [ ] 5.5 `[E]` Rapor taslağı tüm bölümler → [kart](planlar/H5.md#m5-5)
- [ ] 5.6 `[E]` H5 haftalık rapor + K5 kontrolü → [kart](planlar/H5.md#m5-6)

---

## H6 (23–29 Kasım) — Tampon ve isteğe bağlı işler

- [ ] 6.1 `[E]` Gecikmiş Must maddeleri → [kart](planlar/H6.md#m6-1)
- [ ] 6.2 `[R]` *(Could)* Messidor-2 dış testi → [kart](planlar/H6.md#m6-2)
- [ ] 6.3 `[M]` *(Could)* Regresyon çıkışı + eşik optimizasyonu → [kart](planlar/H6.md#m6-3)
- [ ] 6.4 `[R]` *(Could)* CLAHE deneyi → [kart](planlar/H6.md#m6-4)
- [ ] 6.5 `[E]` Rapor dil/biçim cilası → [kart](planlar/H6.md#m6-5)

---

## H7 (30 Kasım – 6 Aralık) — Sunum ve teslim

- [ ] 7.1 `[E]` Sunum slaytları → [kart](planlar/H7.md#m7-1)
- [ ] 7.2 `[E]` Demo senaryosu + 2 prova → [kart](planlar/H7.md#m7-2)
- [ ] 7.3 `[E]` Final rapor teslimi → [kart](planlar/H7.md#m7-3)
- [ ] 7.4 `[M]` Repo son kontrol + `v1.0` etiketi → [kart](planlar/H7.md#m7-4)

---

## Plan dışı eklenen maddeler

*(Plan dışında yapılan her iş buraya eklenir — sessizce geçilmez.)*
