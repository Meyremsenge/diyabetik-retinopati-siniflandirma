# CLAUDE.md — VisionDx

Üniversite dönem projesi (58. Proje): retina fundus görüntülerinden diyabetik retinopati derecesini (0–4) sınıflandıran **akademik prototip**.
Ekip: Rümeysa Akbulut (veri), Büşra Yaşar (model/eğitim), Meyrem Şenge (değerlendirme + demo). Ekip derin öğrenmede **yeni**. Kod herkesin anlatabileceği kadar sade olmalı.
Süre: 19 Ekim – 6 Aralık 2026. Teknik bitiş hedefi 22 Kasım.

Stack: Python 3.12 · PyTorch 2.14 + torchvision · scikit-learn · Pillow/NumPy · imagehash · grad-cam · Streamlit. Eğitim: Kaggle GPU veya yerel RTX 3060 (6 GB).

---

## Dil

- Kullanıcıyla **Türkçe** konuş: açıklama, ilerleme notu, soru ve hata yorumu dahil. Bu kural bağlam özetlemesinden (compaction) sonra da geçerlidir.
- Tanımlayıcılar (değişken, fonksiyon, dosya adı) İngilizce. **Docstring, yorum ve commit mesajı Türkçe.**
- Her yeni Python dosyası, amacını ve nasıl çalıştırılacağını anlatan kısa bir Türkçe docstring ile başlar.

---

## Tek doğruluk kaynağı

| Dosya | Ne için | Ne zaman okunur |
|---|---|---|
| **`docs/PLAN.md`** | İşlerin sırası, sahibi, ilerleme durumu | Her iş başında (tamamı) |
| `docs/TEKNIK_TASARIM.md` | Veri, bölme, ön işleme, model, eğitim, metrik, **dosya sözleşmeleri** | İlgili bölüm, ihtiyaç anında (`grep`) |
| `docs/KARAR_KAYDI.md` | Kararlar ve gerekçeleri | Bir karara dokunurken |
| `docs/DENEY_KAYDI.md` | Gerçek deney sonuçları | Deney koşarken veya rapor yazarken |
| `docs/EKIP_REHBERI.md` | Kim hangi dosyanın sahibi, Git düzeni | Sahiplik/iş akışı sorusunda |
| `docs/ARASTIRMA.md` | Doğrulanmış literatür ve veri bilgisi, kaynaklar | Rapor yazarken |

`@import` bilinçli olarak yok. Belgeler ihtiyaç anında, ilgili bölüm `grep` ile bulunarak okunur. `docs/arsiv/` eski taslaklardır; **okunmaz, uygulanmaz.**

Kararlar verilmiştir: **yeni mimari, model veya kütüphane önerme; uygula.** Uygularken bir karara aykırı somut kanıt görürsen (hata, bellek yetmezliği, ölçüm) sessizce sapma. Kısa bir not düş ve sor.

---

## Komutlar (proje kökünden)

| İş | Komut |
|---|---|
| Ortam (Windows) | `py -3.12 -m venv .venv` → `.venv\Scripts\activate` |
| Ortam (macOS) | `python3.12 -m venv .venv` → `source .venv/bin/activate` |
| PyTorch (yalnız NVIDIA GPU) | `pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cu126` |
| Bağımlılıklar | `pip install -r requirements.txt` |
| Test | `python -m pytest -q` |
| Veri raporu | `python -m src.inspect_dataset --data-root <yol>` |
| Eğitim | `python -m src.train --config configs/<ad>.yaml [--data-root ...] [--limit 64 --epochs 1]` |
| Tahmin | `python -m src.predict --run outputs/runs/<run_id> --split val` (test/idrid: `--final`) |
| Değerlendirme | `python -m src.evaluate --predictions outputs/runs/<run_id>/val_predictions.csv` |
| Demo | `streamlit run app/streamlit_app.py` |

*(Dosyalar yazıldıkça kesinleşir; değişirse bu tablo güncellenir.)*

---

## Değişmez kurallar (ihlal = değişiklik reddedilir)

### Veri ve değerlendirme dürüstlüğü
- **Test kümesi** (`split == "test"`) ve **IDRiD** yalnız dondurulmuş final modelle, `--final` bayrağıyla, **bir kez** kullanılır. Eğitim, erken durdurma, eşik, hiperparametre ve model seçimi → **yalnız val**.
- `splits/aptos_splits.csv` üretildikten sonra **değiştirilmez**. Değişmesi gerekirse önce sor.
- Tekrar görüntü politikası TEKNIK_TASARIM §3'tedir. Bölme, tekrar analizinden **sonra** yapılır.
- Augmentation yalnız train dönüşümünde bulunur. Val, test ve demo aynı deterministik zinciri kullanır.
- **Sonuç uydurma.** DENEY_KAYDI'na ve rapora yalnız gerçek `metrics_*.json` değerleri yazılır. Çalışmayan deney "başarısız" veya "çalıştırılmadı" diye yazılır. Duman testi (`--limit`) sonucu raporlanmaz.
- Veri seti adı, sütun adı veya dizin yapısı varsayılmaz. Önce gerçek dosya kontrol edilir (`head`, `inspect_dataset`).

### Kapsam
- Modeller: `resnet18` (yalnız duman testi), `resnet50` (baseline), `efficientnet_b3` (karşılaştırma). **Başka model yok.**
- Yasak (ayrı karar olmadan): timm, Albumentations, OpenCV, W&B, ensemble, ViT/Swin, EfficientNet-B4, Lightning, Hydra, Docker, web backend/frontend.
- Bir özellik eklemeden önce sor: "Bu olmadan PLAN'daki Must maddeleri tamamlanır mı?" Cevap evetse ekleme.
- İhtiyaç olmadan dosya, klasör veya soyutlama açma. Boş iskelet ve "ileride lazım olur" kodu yok. Sınıf yerine fonksiyon tercih et.

### Kod biçimi
- Yollar `pathlib.Path` ile yönetilir. Sabit mutlak yol yok; yol CLI argümanı veya config ile gelir.
- Rastgelelik yalnız `src.utils.set_seed` ile ayarlanır. Cihaz seçimi yalnız `src.utils.get_device` ile yapılır (cuda → mps → cpu).
- Anlamlı isimler kullan; karmaşık tek satırlık ifade yazma. Metrikler `src/metrics.py` dışında yeniden hesaplanmaz.
- Dosya sözleşmelerindeki sütun adları ve fonksiyon imzaları (TEKNIK_TASARIM §7) değiştirilmez. Değişmesi gerekirse önce sor, çünkü üç kişinin kodunu etkiler.

### Gizlilik ve güvenlik
- Veri, görüntü, checkpoint (`*.pt`), `outputs/`, Kaggle anahtarı (`kaggle.json`) ve `.env` **asla** git'e girmez.
- `gptilekonuşma.md` öğrenci numaraları içerir. Git'e eklenmez ve içeriği başka dosyaya kopyalanmaz.
- Tıbbi tanı, tarama veya klinik güvenlik iddiası oluşturulmaz. Arayüzde "tıbbi teşhis yerine geçmez" uyarısı kalıcıdır. Yüklenen görüntü diske yazılmaz.

---

## İzin ve onay sınırları

**Var olan dosyayı değiştirmeden önce** ne değişeceğini tek cümleyle söyle. Yeni dosya açmak, PLAN maddesinin kapsamındaysa serbesttir.

**Önce açık onay al:**
- Başka bir ekip üyesinin sahip olduğu dosyayı değiştirmek (EKIP_REHBERI §1). Önce kullanıcıya kimin dosyası olduğunu söyle.
- Dosya sözleşmesi, `splits/` veya config varsayılanını değiştirmek
- Bağımlılık eklemek veya sürüm değiştirmek (`requirements.txt`'de gerekçesiyle)
- Dosya/klasör silmek, toplu yeniden adlandırmak, 3+ dosyalık refactor
- 30 dakikadan uzun sürecek eğitim başlatmak
- `git push`, PR açmak, dış servise veri göndermek

**Kesin yasaklar:** `git add -A` / `git add .` (dosyaları adıyla ekle) · `git push --force` · `main`'e doğrudan commit · test/IDRiD üzerinde `--final` olmadan tahmin.

---

## Çalışma döngüsü

```
ANLA → PLAN maddesini bul → HEDEFLİ OKU → KÜÇÜK ADIMLA UYGULA → ÇALIŞTIR, GERÇEK ÇIKTIYI GÖR → KISA RAPOR + AÇIKLAMA
```

- Repoyu baştan sona okuma. İlgili modülü, onu çağıranları, testini ve gerekirse belgenin ilgili bölümünü oku.
- Belirsizlik varsa bağımsız kısımları bitir, kalan kısım için sor. Tahminle yanlış kod yazma.
- Ekip yeni öğreniyor: her kod değişikliğinden sonra **ne yaptığını, neden gerektiğini, nasıl çalıştırılacağını, beklenen çıktıyı ve sık hataları** sade Türkçeyle 3–6 satırda anlat. Uzun kod bloklarını cevaba kopyalama; `dosya:satır` ver.

---

## Doğrulama matrisi

| Değişiklik | Çalıştırılacak |
|---|---|
| Yalnız doküman | Hiçbiri |
| `metrics.py`, `preprocessing.py`, `data.py`, `models.py`, `utils.py` | İlgili `tests/test_*.py` + `python -m pytest -q` |
| CLI betiği (`inspect_*`, `make_splits`, `evaluate`...) | `--help` + küçük gerçek/sahte girdiyle bir çalıştırma |
| `train.py` / config | Duman testi: `--limit 64 --epochs 1` (cpu/mps'de de geçmeli) |
| `predict.py` | Duman testi koşusunun val'inde çalıştır, CSV sütunlarını kontrol et |
| `app/` | `streamlit run` + bir örnek görüntü + geçersiz dosya denemesi |
| Bağımlılık değişikliği | Temiz venv'de `pip install -r requirements.txt` + tüm testler |

Test atlamak tasarruf değildir. Test kırıldıysa çıktısıyla birlikte söyle, gizleme.

---

## Çıktı formatı

```
Değişen: src/metrics.py — compute_metrics eklendi (PLAN 1.11)
Doğrulanan: python -m pytest tests/test_metrics.py -q (5 geçti)
Nasıl çalışır: <2-4 satır sade açıklama>
Kalan: —
```

---

## Git ve commit

- Herkes kendi dalında çalışır: `<isim>/<plan-no>-<kisa-ad>`. `main`'e yalnız PR ile girilir.
- Her mantıklı birim ayrı commit. Mesaj Türkçe, tek satır, gövdede `PLAN x.y`.
- **Commit'i kullanıcı söyleyince at** (istisna: `/bitir`). Push etme; kullanıcı ayrıca söyler.
- Claude ile yazılan commitlerin sonuna: `Co-Authored-By: Claude <noreply@anthropic.com>`

---

## Proje komutları (`.claude/skills/`)

`/durum` · `/ilerle` · `/bitir` · `/deney <id>` · `/haftalik-rapor` · `/anlat <dosya|kavram>` · `/handoff`. Ayrıntı: EKIP_REHBERI §4.
