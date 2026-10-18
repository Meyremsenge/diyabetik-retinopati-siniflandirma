# VisionDx — Proje Planı (tek doğruluk kaynağı)

> Bu dosya **ne yapılacağını, kimin yapacağını ve sırasını** tutar. Her iş başında okunur.
> Madde bitince `- [ ]` → `- [x]` yapılır. Plandan sapma gerekiyorsa önce buraya not düşülür.
> Teknik ayrıntı: [TEKNIK_TASARIM.md](TEKNIK_TASARIM.md) · Kim ne yapar: [EKIP_REHBERI.md](EKIP_REHBERI.md)

**Sahipler:** `[R]` Rümeysa (veri) · `[B]` Büşra (model/eğitim) · `[M]` Meyrem (değerlendirme + demo) · `[E]` tüm ekip

**Süre:** 7 hafta (19 Ekim – 6 Aralık 2026). **Hedef: teknik iş 5. haftanın sonunda biter**; 6. hafta tampon, 7. hafta sunum.
*(H1 = 19 Ekim haftası varsayıldı. Dersin hafta numaraları farklıysa yalnız etiketleri değiştirin.)*

**Git kullanıcı adı → kişi eşlemesi** (`/durum` bunu kullanır; herkes kendi satırını doldurur):

| Kişi | Kısaltma | `git config user.name` |
|---|---|---|
| Rümeysa Akbulut | R | _(doldurulacak)_ |
| Büşra Yaşar | B | _(doldurulacak)_ |
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

**Ortak kurulum**
- [ ] 1.1 `[E]` Python 3.12 sanal ortamı + `requirements.txt` kurulumu (komutlar: README). Bitti sayılır: `python -c "import torch, torchvision, sklearn, imagehash, streamlit; print(torch.__version__)"` hatasız çalışır.
- [ ] 1.2 `[E]` Kaggle hesabı + **telefon doğrulaması** (GPU ve internet için şart) + APTOS yarışma kurallarını kabul ("Late Submission" / "I Understand and Accept").
- [ ] 1.3 `[M]` GitHub reposuna Rümeysa ve Büşra'yı *Collaborator* olarak ekle; `main` dalına doğrudan push yerine PR kuralını ekiple konuş.
- [ ] 1.4 `[E]` PLAN.md'deki git kullanıcı adı tablosunu doldur.
- [ ] 1.5 `[M]` Diskte **en az 25 GB** boş alan aç (şu an 13 GB). CUDA'lı PyTorch kur, `torch.cuda.is_available()` → `True` doğrula.

**Veri `[R]`**
- [ ] 1.6 `[R]` `src/inspect_dataset.py`: train.csv'yi okur; görüntü sayısı, eksik dosya, sınıf dağılımı, örnek boyutları raporlar. Kaggle notebook'unda (`/kaggle/input/aptos2019-blindness-detection`) çalıştır. Bitti sayılır: 3.662 satır ve dağılım (1805/370/999/193/295) **gerçek çıktıyla** doğrulandı.
- [ ] 1.7 `[R]` Veri seti bölümünün rapor taslağı (kaynak, lisans, dağılım tablosu, 3–5 örnek görüntü) → `docs/RAPOR_TASLAGI.md` §4.

**Model `[B]`**
- [ ] 1.8 `[B]` `src/utils.py`: `set_seed(seed)` ve `get_device()` (cuda → mps → cpu).
- [ ] 1.9 `[B]` `src/models.py`: `build_model(name, num_classes=5, pretrained=True)` — `resnet18`, `resnet50`, `efficientnet_b3`. Bitti sayılır: `tests/test_models.py` sahte tensörle `(2, 5)` çıktı şeklini doğrular.
- [ ] 1.10 `[B]` PyTorch transfer learning eğitimini oku/dene (kaynaklar: EKIP_REHBERI §Büşra).

**Değerlendirme `[M]`**
- [ ] 1.11 `[M]` `src/metrics.py`: `compute_metrics(y_true, y_pred) -> dict` (accuracy, macro F1, sınıf bazlı recall, confusion matrix, QWK). Bitti sayılır: `tests/test_metrics.py` elle hesaplanmış küçük örneklerle geçer (eksik sınıf durumu dahil).
- [ ] 1.12 `[M]` Metriklerin sade açıklaması → `docs/RAPOR_TASLAGI.md` §7.

**Rapor**
- [ ] 1.13 `[E]` H1 haftalık ilerleme raporu (`docs/HAFTALIK_RAPOR_SABLONU.md`; Claude ile: `/haftalik-rapor`).

---

## H2 (26 Ekim – 1 Kasım) — Veri hattı ve ilk baseline

**Veri `[R]`**
- [ ] 2.1 `[R]` `src/preprocessing.py`: `crop_black_borders(img)`, `resize_square(img, size)`. Bitti sayılır: 5 örnek görüntünün önce/sonra görseli.
- [ ] 2.2 `[R]` `src/preprocess_images.py`: tüm APTOS'u kırp + 512×512 JPEG olarak kaydet. Kaggle'da çalıştır, çıktıyı **özel (private) Kaggle dataset** `visiondx-aptos-512` olarak kaydet, ekiple paylaş.
- [ ] 2.3 `[R]` `src/find_duplicates.py`: dosya hash'i (birebir aynı) + `imagehash.phash` (çok benzer) ile tekrar grupları; çelişkili etiketli grupları listeler. Eşiği 20 çifti gözle kontrol ederek seç. Beklenen ölçek: ~130 grup / ~270 görüntü / ~37 çelişkili grup (bağımsız bir denetimin bulgusu — birebir tutması gerekmez).
- [ ] 2.4 `[R]` `src/make_splits.py`: tekrar politikası (TEKNIK_TASARIM §3) + tabakalı 70/15/15 bölme → `splits/aptos_splits.csv` (`id_code, split, note`). **Bu dosya git'e girer ve bir daha değişmez.**
- [ ] 2.5 `[R]` `src/data.py`: `RetinaDataset` + `get_transforms(split, image_size)`; augmentation **yalnız train**. Bitti sayılır: `tests/test_data.py` sahte görüntülerle şekil/etiket kontrolü.

**Model `[B]`**
- [ ] 2.6 `[B]` `configs/resnet50_baseline.yaml` + `src/train.py`: config okur, eğitir, her epoch val QWK hesaplar (`src.metrics`), en iyi checkpoint'i ve `history.csv`'yi `outputs/runs/<run_id>/` altına yazar.
- [ ] 2.7 `[B]` Duman testi (E0): `python -m src.train --config configs/resnet50_baseline.yaml --limit 64 --epochs 1`. Bitti sayılır: hatasız biter, `history.csv` oluşur. **Sonuç rapora yazılmaz.**
- [ ] 2.8 `[B]` `src/predict.py`: run klasörü + split → `predictions.csv` (`image_id, y_true, y_pred, prob_0..prob_4`). `test`/`idrid` için `--final` bayrağı zorunlu.
- [ ] 2.9 `[B]` **E1: ResNet50 baseline** tam eğitim (Kaggle GPU). Sonuç → `docs/DENEY_KAYDI.md`.

**Değerlendirme `[M]`**
- [ ] 2.10 `[M]` `src/evaluate.py`: `predictions.csv` → `metrics.json` + confusion matrix PNG (+ normalize edilmiş). Bitti sayılır: E1 val tahminleri üzerinde çalıştı.
- [ ] 2.11 `[M]` E1'i kendi GPU'nda da çalıştırıp süreyi ölç (yerel eğitim kapasitesini görmek için; sonuç farkı not edilir).

- [ ] 2.12 `[E]` H2 haftalık rapor.

---

## H3 (2–8 Kasım) — Karşılaştırma ve deneyler

- [ ] 3.1 `[B]` **E2: EfficientNet-B3**, E1 ile birebir aynı bölme/boyut/epoch/augmentation.
- [ ] 3.2 `[B]` **E3:** E1/E2'den iyi olan + ağırlıklı Cross Entropy (sınıf dengesizliği).
- [ ] 3.3 `[R]` `src/preprocessing.py`'ye `ben_graham(img)` ekle; `preprocess_images.py --ben-graham` ile ikinci 512 kopya. **E4:** en iyi ayar + Ben Graham (eğitimi B veya M çalıştırır).
- [ ] 3.4 `[R]` IDRiD (Disease Grading, 516 görüntü) indir (IEEE DataPort, ücretsiz hesap) → `src/prepare_idrid.py` ile ortak biçim (`image_id, diagnosis`) + aynı ön işleme. **Model bu veriyi şimdilik görmez.**
- [ ] 3.5 `[M]` Karşılaştırma tablosu + grafikler (`src/evaluate.py --compare run1 run2 ...`): QWK, macro F1, sınıf 3–4 recall, eğitim süresi.
- [ ] 3.6 `[M]` Val üzerinde hata analizi: en sık karışan sınıf çiftleri, 8–10 yanlış örnek görseli.
- [ ] 3.7 `[M]` `src/gradcam.py` prototipi (`grad-cam` kütüphanesi): tek görüntü → ısı haritası bindirmesi.
- [ ] 3.8 `[E]` H3 haftalık rapor.

---

## H4 (9–15 Kasım) — Final model, test ve dış doğrulama

- [ ] 4.1 `[E]` **Model seçimi toplantısı.** Kural önceden sabit (TEKNIK_TASARIM §7): en yüksek val QWK; fark < 0,01 ise sınıf 3+4 recall ortalaması yüksek olan. Karar → `docs/KARAR_KAYDI.md`. Model **dondurulur** (checkpoint + config + commit hash).
- [ ] 4.2 `[B]` Dondurulmuş modelle APTOS test tahmini (`--final`) — **tek sefer**.
- [ ] 4.3 `[R]` Dondurulmuş modelle IDRiD (516) tahmini (`--final`) — **tek sefer**.
- [ ] 4.4 `[M]` Test + IDRiD metrikleri, iç/dış performans farkının yorumu → DENEY_KAYDI + RAPOR §8.
- [ ] 4.5 `[M]` `app/streamlit_app.py` v1: yükle → derece + 5 sınıf olasılığı + Grad-CAM + "tıbbi teşhis yerine geçmez" uyarısı; geçersiz dosyada hata; yüklenen görüntü **diske kaydedilmez**.
- [ ] 4.6 `[B]` Final checkpoint'i ekibe paylaş (Google Drive; git'e girmez) + `README`'ye indirme/konum notu.
- [ ] 4.7 `[B]` *(Should)* 5-fold çapraz doğrulama (train+val üzerinde, test hariç) final ayar için → ortalama ± std. GPU süresi yetmezse atlanır ve gerekçesi yazılır.
- [ ] 4.8 `[E]` H4 haftalık rapor.

---

## H5 (16–22 Kasım) — Demo, açıklanabilirlik, rapor → teknik bitiş

- [ ] 5.1 `[M]` Grad-CAM örnek galerisi: her sınıftan doğru + yanlış tahmin örnekleri (rapor için).
- [ ] 5.2 `[M]` Streamlit son hâli; GPU'suz bilgisayarda yanıt süresi ölçümü (hedef ≤ 10 sn, FOG-5).
- [ ] 5.3 `[R]` Temiz makinede (Mac) README'deki adımlarla uçtan uca deneme: kurulum → demo. Takılan her adım README'ye.
- [ ] 5.4 `[B]` Tekrarlanabilirlik: final config aynı seed ile 2. kez eğitilir, QWK farkı raporlanır (FOG-3).
- [ ] 5.5 `[E]` Rapor taslağının tüm bölümleri dolu (sonuçlar yalnız DENEY_KAYDI'ndaki gerçek değerlerden).
- [ ] 5.6 `[E]` H5 haftalık rapor. **K5 kontrolü: tüm Must maddeleri `[x]` mi?**

---

## H6 (23–29 Kasım) — Tampon ve isteğe bağlı işler

Yalnız K5 tamamsa. Öncelik sırası:
- [ ] 6.1 `[E]` Gecikmiş Must maddeleri (varsa) — önce bunlar.
- [ ] 6.2 `[R]` *(Could)* Messidor-2 dış testi: Google'ın uzman-konsensüs etiketleri (Kaggle) + ADCIS'ten görüntü lisansı.
- [ ] 6.3 `[M]` *(Could)* Regresyon çıkışı + eşik optimizasyonu (eşikler **yalnız val** üzerinde seçilir).
- [ ] 6.4 `[R]` *(Could)* CLAHE deneyi.
- [ ] 6.5 `[E]` Rapor dil/biçim cilası, kaynakça kontrolü.

---

## H7 (30 Kasım – 6 Aralık) — Sunum ve teslim

- [ ] 7.1 `[E]` Sunum slaytları (herkes kendi bölümünü anlatır).
- [ ] 7.2 `[E]` Demo senaryosu + 2 prova (internet yokken de çalışacak şekilde).
- [ ] 7.3 `[E]` Final rapor teslimi.
- [ ] 7.4 `[M]` Repo son kontrol: README güncel, gereksiz dosya yok, `v1.0` etiketi.

---

## Plan dışı eklenen maddeler

*(Plan dışında yapılan her iş buraya eklenir — sessizce geçilmez.)*
