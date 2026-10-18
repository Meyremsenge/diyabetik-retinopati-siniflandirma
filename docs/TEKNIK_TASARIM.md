# VisionDx — Teknik Tasarım

> Bu belge **nasıl** yapılacağını anlatır. Sıra ve sahiplik için [PLAN.md](PLAN.md), kararların gerekçesi için [KARAR_KAYDI.md](KARAR_KAYDI.md).
> Bir bölümü değiştirmek gerekirse önce ekiple konuşulur, sonra KARAR_KAYDI'na satır eklenir.

## 1. Problem

Bir retina fundus görüntüsünü, diyabetik retinopati (DR) şiddetinin 5 sıralı sınıfından birine atamak (ICDR ölçeği):

| Sınıf | Anlam |
|---|---|
| 0 | DR yok |
| 1 | Hafif NPDR |
| 2 | Orta NPDR |
| 3 | Ağır NPDR |
| 4 | Proliferatif DR |

Akademik prototiptir. Klinik tanı, tarama veya güvenlik iddiası **yoktur**.

## 2. Veri

| Veri seti | Rol | Boyut | Etiket | Lisans/koşul |
|---|---|---|---|---|
| **APTOS 2019** | Geliştirme (train/val) + iç test | 3.662 | `train.csv`: `id_code`, `diagnosis` (0–4) | Kaggle yarışma kuralları: ticari olmayan kullanım, **yeniden dağıtım yok** |
| **IDRiD** (Disease Grading) | Dış test (yalnız final model) | 516 (413+103) | CSV: görüntü adı, DR derecesi (0–4), DME riski (0–2) | CC BY 4.0 |
| Messidor-2 *(Could)* | Ek dış test | 1.748 (4'ü değerlendirilemez) | Resmî sürümde yok → Google'ın uzman-konsensüs etiketleri (Kaggle) | ADCIS lisans formu |

APTOS'un etiketli olmayan 1.928 görüntülük yarışma test seti **kullanılmaz** (etiket yok).

### Dizin düzeni (git dışı, `data/`)

```text
data/
├── raw/aptos2019/            # Kaggle'dan (yerelde gerekmez; Kaggle'da /kaggle/input/... kullanılır)
│   ├── train.csv
│   └── train_images/<id_code>.png
├── processed/aptos_512/      # kırpılmış + 512x512 JPEG  (Kaggle dataset: visiondx-aptos-512)
├── processed/aptos_512_bg/   # aynı + Ben Graham (E4 için)
└── processed/idrid_512/      # + idrid_labels.csv (image_id, diagnosis)
```

Yerel diskte ham APTOS (~10 GB) **tutulmaz**; yalnız 512'lik kopya (~300 MB civarı beklenir) indirilir.

## 3. Tekrar görüntüler ve veri bölme (sızıntı önleme)

APTOS'ta tekrar eden ve bir kısmı **farklı etiketli** görüntüler olduğu biliniyor (ARASTIRMA.md §3). Politika:

1. **Birebir aynı** dosyalar: içerik hash'i (MD5) ile bulunur.
2. **Çok benzer** görüntüler: `imagehash.phash` (64 bit), Hamming mesafesi ≤ eşik (başlangıç 4; 20 çift gözle kontrol edilerek kesinleşir). Birleşim-bul (union-find) ile gruplara ayrılır.
3. Grup içinde etiketler **aynıysa** → tek temsilci tutulur (en küçük `id_code`), diğerleri `excluded` (`note=duplicate`).
4. Grup içinde etiketler **çelişkiliyse** → grubun tamamı `excluded` (`note=conflicting_label`). Sayısı raporlanır.
5. Kalanlar **tabakalı** (sınıf oranları korunarak) bölünür: **train %70 / val %15 / test %15**, `seed=42`.
6. Çıktı `splits/aptos_splits.csv`: `id_code, split, note` (`split ∈ {train, val, test, excluded}`). Etiket içermez → git'e girer. **Bir kez üretilir, sonra değiştirilmez.**

Kurallar:
- **Test kümesi** yalnız H4'te dondurulmuş final modelle **bir kez** kullanılır. Model seçimi, eşik, hiperparametre, erken durdurma → **yalnız val**.
- Augmentation yalnız train'e uygulanır.
- APTOS'ta hasta kimliği yok; bu sınırlılık raporda belirtilir.

## 4. Ön işleme

Tek seferlik (diskte önbellek, `src/preprocess_images.py`):
1. RGB'ye çevir.
2. **Siyah kenar kırpma:** gri tonda eşik (> 7) üstündeki piksellerin sınır kutusu.
3. 512×512'ye yeniden boyutlandır, JPEG (kalite 95) kaydet.
4. *(E4)* **Ben Graham:** `4·img − 4·GaussianBlur(img, σ≈ yarıçap/30) + 128`, ardından dairesel maske. Pillow + NumPy ile (OpenCV gerekmez).

Eğitim sırasında (`src/data.py`, `torchvision.transforms.v2`):

| Adım | train | val / test / demo |
|---|---|---|
| Resize → `image_size` (varsayılan 384) | ✓ | ✓ |
| RandomHorizontalFlip, RandomVerticalFlip | ✓ | — |
| RandomRotation(±30°) | ✓ | — |
| ColorJitter(brightness=0.2, contrast=0.2) | ✓ | — |
| ToTensor + ImageNet normalize | ✓ | ✓ |

Demo (Streamlit) **aynı** kırpma + boyut + normalize zincirini kullanır.

## 5. Modeller

`src/models.py` → `build_model(name, num_classes=5, pretrained=True)`; `torchvision` ImageNet ağırlıkları, son katman 5 çıkışlı.

| Model | Rol | Not |
|---|---|---|
| `resnet18` | Yalnız duman testi (E0) | Hızlı, boru hattını doğrular |
| `resnet50` | **Baseline** (E1) | Raporlarda söz verilen baseline |
| `efficientnet_b3` | **Karşılaştırma** (E2) | Aynı koşullarda |

timm, ViT/Swin, ensemble **yok** (KARAR_KAYDI).

## 6. Eğitim

`python -m src.train --config configs/<ad>.yaml [--data-root ...] [--limit N] [--epochs N]`

| Ayar | Varsayılan | Not |
|---|---|---|
| `image_size` | 384 | 6 GB GPU'da bellek yetmezse 320 (tüm modellerde aynı) |
| `batch_size` | 16 | Yerelde OOM olursa 8 → DENEY_KAYDI'na yazılır |
| `epochs` | 15 | Erken durdurma: val QWK 4 epoch iyileşmezse |
| optimizer | AdamW, lr 1e-4, weight_decay 1e-4 | Tüm ağ ince ayar |
| scheduler | CosineAnnealing | |
| loss | CrossEntropy | E3: sınıf ağırlıklı CE |
| mixed precision | açık (cuda) | `torch.autocast` |
| seed | 42 | `src.utils.set_seed` |
| en iyi model ölçütü | **val QWK** | |

Her koşu `outputs/runs/<YYYYMMDD-HHMM>_<model>_<etiket>/` altına yazar:
`config.yaml` (kopya) · `history.csv` (epoch, train_loss, val_loss, val_qwk, val_macro_f1, lr, süre) · `best.pt` (git dışı) · `val_predictions.csv` · `env.txt` (Python/PyTorch sürümü, GPU, git commit).

## 7. Değerlendirme

`src/metrics.py` → `compute_metrics(y_true, y_pred) -> dict` (scikit-learn; her zaman `labels=[0,1,2,3,4]` ile — eksik sınıfta hata vermemesi için):

| Metrik | Neden |
|---|---|
| **QWK** (`cohen_kappa_score(weights="quadratic")`) | **Ana metrik.** Sıralı sınıflarda uzak hatayı daha çok cezalandırır |
| Macro F1 | Her sınıfa eşit ağırlık; dengesizlikte accuracy'den dürüst |
| Sınıf bazlı recall | Özellikle sınıf 3–4 kaçırılıyor mu? |
| Confusion matrix (ham + normalize) | Hangi sınıflar karışıyor? |
| Accuracy | Yalnız bağlam için; tek başına başarı iddiası yapılmaz |

**Final model seçim kuralı (önceden sabit):** en yüksek **val QWK**. İki aday arasındaki fark < 0,01 ise sınıf 3 ve 4 recall ortalaması yüksek olan seçilir. Test ve IDRiD sonuçları seçimi **etkilemez**.

**Hedef (garanti değil):** APTOS iç test QWK ≥ 0,85 (FOG-1). Ulaşılamazsa sonuç olduğu gibi raporlanır.

### Ortak dosya sözleşmeleri

Üç kişinin birbirini beklemeden çalışması için **bu biçimler değişmez**:

| Dosya | Sütunlar | Üreten → Tüketen |
|---|---|---|
| `splits/aptos_splits.csv` | `id_code, split, note` | R → B |
| `data/processed/idrid_512/idrid_labels.csv` | `image_id, diagnosis` | R → B, M |
| `outputs/runs/<run>/{val,test,idrid}_predictions.csv` | `image_id, y_true, y_pred, prob_0, prob_1, prob_2, prob_3, prob_4` | B → M |
| `outputs/runs/<run>/metrics_<split>.json` | `accuracy, macro_f1, qwk, recall_per_class[5], confusion_matrix[5][5], n` | M → rapor |

Fonksiyon imzaları: `set_seed(seed:int)`, `get_device() -> torch.device`, `build_model(name:str, num_classes:int=5, pretrained:bool=True)`, `RetinaDataset(df, image_dir, transform)` (`__getitem__ → (tensor, label, image_id)`), `get_transforms(split:str, image_size:int)`, `compute_metrics(y_true, y_pred) -> dict`.

## 8. Deney listesi

| ID | Model | Ön işleme | Loss | Amaç |
|---|---|---|---|---|
| E0 | resnet18 | kırp+512 | CE | Duman testi (`--limit 64 --epochs 1`), **raporlanmaz** |
| E1 | resnet50 | kırp+512 | CE | **Baseline** |
| E2 | efficientnet_b3 | kırp+512 | CE | Mimari karşılaştırması |
| E3 | E1/E2'nin iyisi | kırp+512 | ağırlıklı CE | Sınıf dengesizliği etkisi |
| E4 | en iyi ayar | + Ben Graham | en iyi | Ön işleme etkisi |
| E5 *(Should)* | final ayar | final | final | 5-fold CV (train+val), ort. ± std |

Her seferinde **tek değişken** değişir. Sonuçlar yalnız `docs/DENEY_KAYDI.md`'ye, gerçek `metrics_*.json` dosyasından kopyalanarak yazılır.

## 9. Açıklanabilirlik (Grad-CAM)

`src/gradcam.py`: `grad-cam` kütüphanesi; hedef katman ResNet50 için `model.layer4[-1]`, EfficientNet-B3 için `model.features[-1]`. Çıktı: orijinal görüntü üzerine ısı haritası. Raporda **"modelin dikkat ettiği bölgeler"** olarak yorumlanır; lezyon tespiti iddiası yapılmaz.

## 10. Arayüz (Streamlit)

`streamlit run app/streamlit_app.py`
- Yükle (PNG/JPG) → doğrula (açılabiliyor mu, RGB, min. 224 px) → ön işleme (§4) → tahmin (CPU yeterli) → derece + 5 olasılık çubuğu + Grad-CAM.
- Kalıcı uyarı: *"Akademik prototiptir; tıbbi teşhis yerine geçmez."*
- Yüklenen görüntü **diske yazılmaz**, loglanmaz.
- Checkpoint yolu: `VISIONDX_CHECKPOINT` ortam değişkeni veya `--checkpoint`; dosya git'e girmez (Google Drive).
- Hedef: GPU'suz dizüstünde tahmin + Grad-CAM ≤ 10 sn.

## 11. Dizin yapısı

```text
VisionDx/
├── CLAUDE.md · README.md · requirements.txt · .gitignore
├── .claude/skills/        # /durum /ilerle /bitir /deney /haftalik-rapor /anlat /handoff
├── configs/               # resnet50_baseline.yaml, efficientnet_b3.yaml, ...
├── data/                  # git dışı (yalnız README.md)
├── splits/                # aptos_splits.csv (git'te, etiketsiz)
├── src/
│   ├── __init__.py
│   ├── utils.py           # set_seed, get_device                [B]
│   ├── models.py          # build_model                          [B]
│   ├── train.py           # CLI: eğitim                          [B]
│   ├── predict.py         # CLI: predictions.csv                 [B]
│   ├── preprocessing.py   # kırpma, boyut, Ben Graham            [R]
│   ├── data.py            # RetinaDataset, get_transforms        [R]
│   ├── inspect_dataset.py # CLI: veri raporu                     [R]
│   ├── preprocess_images.py # CLI: 512 önbellek                  [R]
│   ├── find_duplicates.py # CLI: tekrar grupları                 [R]
│   ├── make_splits.py     # CLI: splits.csv                      [R]
│   ├── prepare_idrid.py   # CLI: IDRiD ortak biçim               [R]
│   ├── metrics.py         # compute_metrics                      [M]
│   ├── evaluate.py        # CLI: metrics.json, CM, karşılaştırma [M]
│   └── gradcam.py         # Grad-CAM                             [M]
├── app/streamlit_app.py   #                                      [M]
├── tests/                 # test_metrics.py, test_models.py, test_data.py, ...
├── notebooks/             # Kaggle notebook'ları (çıktısız kaydedilir)
├── outputs/               # git dışı: runs/, figures/, data_reports/
└── docs/
```

Komutlar proje kökünden `python -m src.<modül>` biçiminde çalışır. Dosyalar **ihtiyaç doğunca** oluşturulur; boş iskelet açılmaz.
