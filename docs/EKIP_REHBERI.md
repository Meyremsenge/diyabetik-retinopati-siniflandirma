# VisionDx — Ekip Rehberi

> Kim ne yapar, nasıl çalışırız, nereden öğreniriz. Haftalık maddeler [PLAN.md](PLAN.md)'de.

## 1. Görev dağılımı

İlke: **herkesin bir uçtan uca sorumluluğu var ve kimse başkasını beklemiyor.** Dosya sözleşmeleri ([TEKNIK_TASARIM.md §7](TEKNIK_TASARIM.md)) sabit olduğu için üç kişi aynı anda çalışabilir. Dağılım, 1. ve 2. hafta raporlarında hocaya bildirilen rollerle tutarlıdır.

| | Rümeysa — Veri | Büşra — Model/Eğitim | Meyrem — Değerlendirme + Demo |
|---|---|---|---|
| **Sorumluluk** | Veriyi doğrulamak, temizlemek, bölmek, modele hazır hâle getirmek; dış test verisi | Modeli kurmak, eğitmek, deneyleri koşturmak, tahmin üretmek | Başarıyı ölçmek, karşılaştırmak, hataları yorumlamak; Grad-CAM ve arayüz |
| **Sahip olduğu dosyalar** | `src/preprocessing.py`, `data.py`, `inspect_dataset.py`, `preprocess_images.py`, `find_duplicates.py`, `make_splits.py`, `prepare_idrid.py`, `splits/` | `src/utils.py`, `models.py`, `train.py`, `predict.py`, `configs/` | `src/metrics.py`, `evaluate.py`, `gradcam.py`, `app/`, repo yönetimi |
| **Ürettiği** | `aptos_splits.csv`, 512 önbellek (Kaggle dataset), IDRiD ortak biçim | checkpoint'ler, `history.csv`, `*_predictions.csv` | `metrics_*.json`, grafikler, karşılaştırma tablosu, demo |
| **Raporda yazdığı bölüm** | §4 Veri seti, §5.1 Ön işleme, §5.3 Bölme | §5.2 Model, §6 Deney düzeneği | §7 Metrikler, §8 Sonuçlar, §9 Hata analizi |
| **Donanım** | Mac M2 → Kaggle'da veri işleme | Mac M2 → **Kaggle GPU** ile eğitim | RTX 3060 (6 GB) → yerel eğitim + demo |

**Ortak:** model seçimi toplantısı (H4), haftalık rapor (kaptan dönüşümlü), sunum, kod incelemesi (her PR'ı sahibi dışında **bir kişi** onaylar).

**Haftalık kaptan dönüşümü** (haftalık raporu toplar ve gönderir): H1 Meyrem · H2 Rümeysa · H3 Büşra · H4 Meyrem · H5 Rümeysa · H6 Büşra · H7 tüm ekip.

## 2. Kişi bazlı yol haritası

### Rümeysa — Veri
1. **H1:** Kaggle'da yeni notebook → "Add Input" → APTOS 2019. `inspect_dataset.py` ile sayıları doğrula.
2. **H2:** Kırpma + 512 önbellek → çıktıyı *Save Version* → *Output* → **New Dataset** (private) `visiondx-aptos-512`, ekibe paylaş. Tekrar görüntü analizi ve `aptos_splits.csv`. `RetinaDataset`.
3. **H3:** Ben Graham; IDRiD indirme ve hazırlama.
4. **H4–H5:** IDRiD final tahmini; temiz makinede kurulum testi.
- **Öğrenme kaynakları:** pandas temelleri (10 Minutes to pandas), Pillow `Image`/`ImageFilter`, `imagehash` README, scikit-learn `train_test_split(stratify=...)`, PyTorch "Datasets & DataLoaders" eğitimi.

### Büşra — Model/Eğitim
1. **H1:** `utils.py`, `models.py` + test. PyTorch "Transfer Learning for Computer Vision" eğitimini Kaggle'da baştan sona çalıştır.
2. **H2:** `train.py` + config; duman testi; **E1 ResNet50 baseline** (Kaggle GPU).
3. **H3:** E2 EfficientNet-B3, E3 ağırlıklı CE (+E4'ü Rümeysa/Meyrem ile).
4. **H4–H5:** Final test tahmini, checkpoint paylaşımı, 5-fold (Should), tekrar eğitim.
- **Kaggle'da eğitim akışı:**
  ```text
  Notebook ayarları: Accelerator = GPU (T4 x2 veya P100), Internet = On
  Inputs: aptos2019-blindness-detection + visiondx-aptos-512
  !git clone https://github.com/Meyremsenge/diyabetik-retinopati-siniflandirma.git
  %cd diyabetik-retinopati-siniflandirma
  !pip install -q imagehash grad-cam
  !python -m src.train --config configs/resnet50_baseline.yaml --data-root /kaggle/input/visiondx-aptos-512
  ```
  Çıktılar `/kaggle/working/outputs/...` altına düşer; `best.pt` ve `val_predictions.csv` indirilir. Kaggle'ın hazır PyTorch'u kullanılır, sürümü `env.txt`'ye yazılır.
- **Öğrenme kaynakları:** PyTorch "Training a Classifier" + "Transfer Learning" eğitimleri, `torchvision.models` belgesi (ResNet50, EfficientNet-B3 ağırlıkları), `torch.autocast` (mixed precision).

### Meyrem — Değerlendirme + Demo
1. **H1:** Disk temizliği (≥ 25 GB boş), CUDA'lı PyTorch kurulumu, repo yönetimi; `metrics.py` + testler.
2. **H2:** `evaluate.py`; E1'i yerel GPU'da da koşturup süre ölçümü.
3. **H3:** Karşılaştırma tablosu, hata analizi, Grad-CAM prototipi.
4. **H4–H5:** Test/IDRiD metrikleri, Streamlit, Grad-CAM galerisi.
- **Yerel eğitim:** Kaggle'dan `visiondx-aptos-512` indir → `data/processed/aptos_512/` → `python -m src.train --config ... --data-root data/processed/aptos_512`.
- **Öğrenme kaynakları:** scikit-learn `cohen_kappa_score`, `classification_report`, `confusion_matrix` belgeleri; `ConfusionMatrixDisplay`; `pytorch-grad-cam` README; Streamlit "Get started" + `st.file_uploader`.

## 3. Git çalışma düzeni

- `main` her zaman çalışır durumda olur. **Herkes kendi dalında çalışır:** `<isim>/<plan-no>-<kisa-ad>` (ör. `meyrem/1.11-metrics`).
- Bir PLAN maddesi = bir dal = bir PR. PR açıklamasına PLAN numarası yazılır.
- PR'ı **bir başka ekip üyesi** inceler; testler geçmeden birleştirilmez.
- Commit mesajı Türkçe, kısa: `metrikler: QWK ve macro F1 eklendi (PLAN 1.11)`.
- `git add .` kullanmayın; dosyaları adıyla ekleyin. Veri, checkpoint, `outputs/` **asla** commit'lenmez (`.gitignore` engeller, yine de `git status`'a bakın).

```bash
git checkout main && git pull
git checkout -b meyrem/1.11-metrics
# ... çalış ...
git add src/metrics.py tests/test_metrics.py
git commit -m "metrikler: compute_metrics ve testleri (PLAN 1.11)"
git push -u origin meyrem/1.11-metrics
# GitHub'da PR aç → bir arkadaşın incelesin → merge
```

## 4. Claude Code ile çalışma

Repoda hazır komutlar (`.claude/skills/`):

| Komut | Ne yapar |
|---|---|
| `/durum` | PLAN.md'yi okur, **senin** sıradaki maddeni bulur, kısa durum verir ve başlar |
| `/ilerle` | Aynısı, rapor vermeden |
| `/bitir` | Testleri çalıştırır, PLAN'ı işaretler, kendi dalına commit atar |
| `/deney <id>` | Bir deneyi koşturur/kaydeder; sonucu DENEY_KAYDI'na **yalnız gerçek dosyadan** yazar |
| `/haftalik-rapor` | Git geçmişi + PLAN + DENEY_KAYDI'ndan haftalık rapor taslağı |
| `/anlat <dosya veya kavram>` | Kodu/kavramı sade Türkçeyle anlatır, küçük alıştırma verir |
| `/handoff` | Yarım kalan işi bir sonraki oturuma devretmek için HANDOFF.md yazar |

**Kural:** Claude'un yazdığı kodu `/anlat` ile anlamadan PR açmayın. Sunumda herkes kendi kodunu anlatacak.

Claude Code kullanmayan ekip üyesi aynı düzeni elle uygular: PLAN.md'den maddeyi seç → kodla → `python -m pytest` → PLAN'ı işaretle → PR.

## 5. "Bitti" tanımı (her madde için)

1. Kod çalışıyor ve **gerçek çıktısı** görüldü (ekran çıktısı/PNG/CSV).
2. Varsa testi geçiyor (`python -m pytest`).
3. Yeni Python dosyasının başında amacını anlatan docstring var.
4. PLAN.md'de `[x]`, gerekiyorsa DENEY_KAYDI / RAPOR_TASLAGI güncel.
5. Sahibi dışında biri PR'ı inceledi.

## 6. Haftalık toplantı (30 dk, sabit gün)

1. Her kişi 3 dk: ne bitti, hangi komut, gerçek çıktı ne? (PLAN'dan)
2. Engeller — kim kimden ne bekliyor?
3. Sözleşme değişikliği gerekiyor mu? (gerekirse KARAR_KAYDI)
4. Gelecek hafta maddeleri ve kaptan.

## 7. Repoyu ilk kez çektiğinde Claude'a ne diyeceksin

Repoyu ilk kez klonladıktan sonra Claude Code'u proje klasöründe aç ve aşağıdaki mesajı yapıştır (`<Rümeysa|Büşra>` yerine kendi adını yaz):

```text
Ben <Rümeysa|Büşra>. Bu repoyu ilk kez açıyorum. CLAUDE.md, docs/EKIP_REHBERI.md ve docs/PLAN.md'yi oku.
1) `git config user.name` değerimi PLAN.md'deki kişi tablosuna yaz (sadece kendi satırım).
2) README'deki macOS kurulumunu benimle adım adım yap ve her komutun çıktısını kontrol et.
3) Sonra /durum ile benim ilk maddemi başlat. Kodu yazdıktan sonra bana /anlat ile açıkla.
```
