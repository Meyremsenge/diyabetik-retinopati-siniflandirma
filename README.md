# VisionDx — Retina Görüntülerinden Diyabetik Retinopati Derecelendirme

Retina fundus görüntülerini, diyabetik retinopati şiddetinin beş derecesinden birine sınıflandıran **akademik prototip** (58. Proje).

| Sınıf | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| Anlam | DR yok | Hafif | Orta | Ağır | Proliferatif |

> ⚠️ Bu sistem klinik olarak doğrulanmamıştır ve **tıbbi teşhis yerine geçmez**.

**Ekip:** Rümeysa Akbulut (veri) · Büşra Yaşar (model/eğitim) · Meyrem Şenge (değerlendirme + demo)

## Yaklaşım (özet)

APTOS 2019 (3.662 görüntü) → tekrar görüntü temizliği → tabakalı 70/15/15 bölme → ImageNet ağırlıklı **ResNet50** (baseline) ve **EfficientNet-B3** → QWK, macro F1, sınıf bazlı recall, confusion matrix → final modelin **IDRiD** üzerinde dış testi → Grad-CAM → Streamlit demo.

Ayrıntı: [docs/TEKNIK_TASARIM.md](docs/TEKNIK_TASARIM.md)

## Durum

Plan ve ilerleme: [docs/PLAN.md](docs/PLAN.md). Sonuçlar yalnız deneyler çalıştıktan sonra [docs/DENEY_KAYDI.md](docs/DENEY_KAYDI.md)'ye yazılır.

## Kurulum

Python **3.12** gerekir.

**Windows + NVIDIA GPU**
```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cu126
pip install -r requirements.txt
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```
Beklenen: `True NVIDIA GeForce RTX ...`. `False` görürsen CUDA'sız torch kurulmuştur; yukarıdaki `--index-url` satırını tekrar çalıştır.

**macOS (Apple Silicon)**
```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -c "import torch; print(torch.backends.mps.is_available())"
```

**Kontrol:** `python -c "import torch, torchvision, sklearn, imagehash, streamlit; print(torch.__version__)"` → `2.14.1...`. Testler yazıldıktan sonra: `python -m pytest -q`

## Veri

Veri ve model ağırlıkları bu repoda **yoktur** (lisans ve boyut). Nasıl edinileceği: [data/README.md](data/README.md).

## Belgeler

| Belge | İçerik |
|---|---|
| [docs/PLAN.md](docs/PLAN.md) | 7 haftalık plan, kim ne yapacak |
| [docs/EKIP_REHBERI.md](docs/EKIP_REHBERI.md) | Görev dağılımı, Git düzeni, öğrenme kaynakları |
| [docs/TEKNIK_TASARIM.md](docs/TEKNIK_TASARIM.md) | Veri, model, eğitim, metrikler, dosya sözleşmeleri |
| [docs/ARASTIRMA.md](docs/ARASTIRMA.md) | Literatür, veri setleri, kaynaklar |
| [docs/KARAR_KAYDI.md](docs/KARAR_KAYDI.md) | Kararlar ve gerekçeleri |
| [docs/DENEY_KAYDI.md](docs/DENEY_KAYDI.md) | Deney sonuçları |
| [docs/RAPOR_TASLAGI.md](docs/RAPOR_TASLAGI.md) | Final rapor taslağı |
| [docs/HAFTALIK_RAPOR_SABLONU.md](docs/HAFTALIK_RAPOR_SABLONU.md) | Haftalık rapor şablonu |
