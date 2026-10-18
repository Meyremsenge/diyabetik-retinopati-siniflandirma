# VisionDx: Ayrıntılı proje rehberi

## 1. Proje özeti
Retina fundus görüntülerini, diyabetik retinopati (DR) şiddetinin beş sıralı sınıfından birine ayıran bir görüntü sınıflandırma prototipi geliştirilecektir. Amaç, transfer öğrenmesi kullanarak bir temel model oluşturmak ve performansını uygun metriklerle değerlendirmektir.

**Sınıflar:** 0 = DR yok, 1 = hafif, 2 = orta, 3 = şiddetli, 4 = proliferatif DR.

Bu sistem araştırma ve ders projesi içindir; klinik karar veya tanı için kullanılamaz.

## 2. Kapsam
### İlk sürümde yapılacaklar
- Veri seti ve etiket dosyasının doğrulanması.
- Sınıf dağılımı, bozuk dosyalar ve tekrar görüntülerin incelenmesi.
- Eğitim/doğrulama/test ayrımının oluşturulması.
- Temel görüntü ön işlemesi.
- Önceden eğitilmiş ResNet18 ile transfer öğrenmesi.
- Metriklerin hesaplanması ve hata analizi.
- Sonuçların tekrarlanabilir biçimde kaydedilmesi.

### İlk sürümde yapılmayacaklar
- Klinik kullanım iddiası.
- Çok sayıda model mimarisini aynı anda denemek.
- Ensemble, gelişmiş eşik optimizasyonu veya karmaşık regresyon yaklaşımı.
- Grad-CAM ve Streamlit arayüzü, temel model tamamlanmadan.
- Doğrulanmamış veri setleri veya etiketlerle dış test.

## 3. Veri seti doğrulama kapısı
Veri setinin adı şu anda bilinmiyor. Bu nedenle kod yazmadan önce ekipten şu bilgileri isteyin:
1. Veri setinin tam adı ve indirildiği sayfa.
2. Klasör yapısı.
3. Etiket dosyasının adı ve ilk 5 satırı (kişisel/özel veri içermediğinden emin olun).
4. Görüntü sayısı ve sınıf etiketlerinin 0–4 olup olmadığı.
5. Veri kullanım lisansı ve indirme/yarışma kuralları.

APTOS 2019 daha önce düşünülen bir seçenekti ancak mevcut dosyaların APTOS olduğu doğrulanmış değildir. Veri setinin adı varsayılmamalıdır.

## 4. Veri bölme ve sızıntı önleme
- Önce verinin yapısı ve sınıf dağılımı incelenir.
- Uygun koşullarda stratified train/validation/test ayrımı kullanılır; örnek bir başlangıç oranı 70/15/15 olabilir. Nihai oran veri boyutu, sınıf dağılımı ve ders gereksinimlerine göre kararlaştırılır.
- Test kümesi yalnızca son değerlendirme için saklanır.
- Model seçimi ve ayarlar doğrulama kümesiyle yapılır.
- Aynı görüntünün kopyaları veya aynı hastaya ait görüntüler varsa bunlar farklı kümelere dağılmamalıdır.
- Augmentation yalnızca eğitim kümesine uygulanır.
- Küçük sınıflarda stratified split başarısız olursa, sebebi raporlanır ve bölme stratejisi dikkatle uyarlanır.

## 5. İlk model
ResNet18, ImageNet üzerinde önceden eğitilmiş ağırlıklarla başlangıç modeli olarak değerlendirilecektir. Son sınıflandırma katmanı 5 çıkış üretecek şekilde değiştirilir. İlk deneyde modelin tamamını eğitmek yerine önce gövde dondurulup son katman eğitilebilir; bu çalışırsa daha sonra bazı katmanlar açılarak ince ayar denenebilir. GPU ve süreye göre karar verilir.

İlk aşama hedefi yüksek başarı garantisi değildir. Hedef, uçtan uca çalışan ve sonuçları ölçülebilen temel çizgi oluşturmaktır.

## 6. Ön işleme
Başlangıç için:
- Görüntüyü RGB'ye dönüştürme.
- Modelin beklediği boyuta yeniden boyutlandırma (ResNet18 için başlangıçta 224x224 düşünülebilir).
- Önceden eğitilmiş ağırlıklarla uyumlu normalizasyon.
- Yalnızca eğitim verisinde hafif ve tıbbi görüntü bağlamına uygun augmentation.

Siyah kenar kırpma, CLAHE ve Ben Graham gibi ek yöntemler ilk deneyde zorunlu değildir. Önce basit hat kurulmalı, sonra tek tek ve kontrollü biçimde değerlendirilmeli.

## 7. Metrikler
- Accuracy: genel doğru tahmin oranı.
- Macro F1: her sınıfı eşit ağırlıkla değerlendirir.
- Sınıf bazlı recall: her sınıftaki gerçek örneklerin ne kadarının bulunduğunu gösterir.
- Confusion matrix: gerçek sınıflarla tahmin edilen sınıfları karşılaştırır.
- QWK: sıralı sınıflarda hatanın uzaklığını da dikkate alan ölçüttür.

QWK ana metrik olarak raporlanabilir; diğer metrikler onu tamamlar. Sınıf dengesizliği varsa yalnızca accuracy üzerinden başarı iddiasında bulunulmaz. Hiçbir eşik hedefi sonuç elde edilmeden gerçekleşmiş gibi yazılmaz.

## 8. Tekrarlanabilirlik
Her deney için şunları kaydedin:
- Veri seti sürümü/yolu ve split dosyası.
- Rastgelelik tohumu.
- Model ve önceden eğitilmiş ağırlık türü.
- Görüntü boyutu ve normalizasyon.
- Batch size, epoch, learning rate, optimizer ve loss.
- Python/PyTorch/torchvision sürümleri.
- En iyi modelin hangi doğrulama metriğiyle seçildiği.
- Eğitim/validasyon kayıpları ve metrikler.
- Çalıştırma tarihi ve bilinen sınırlamalar.

## 9. Önerilen dosya yapısı
```text
VisionDx/
├── README.md
├── CLAUDE.md
├── PROJECT_GUIDE.md
├── requirements.txt
├── .gitignore
├── configs/
│   └── config.yaml
├── data/
│   └── README.md
├── src/
│   ├── data/
│   │   ├── dataset.py
│   │   └── prepare_data.py
│   ├── models/
│   │   └── resnet18.py
│   ├── evaluation/
│   │   └── metrics.py
│   └── utils/
│       └── seed.py
├── scripts/
│   ├── inspect_dataset.py
│   └── evaluate.py
├── notebooks/
├── reports/
└── app/
    └── app.py
```
Bu yapı bir hedeftir; tüm dosyalar ilk gün oluşturulmak zorunda değildir. Kod çalıştıkça gerekli dosyalar eklenir.

## 10. Git ve veri güvenliği
- `data/`, model checkpoint'leri, büyük görüntüler ve sırlar Git'e eklenmemelidir.
- `data/README.md` içine veri setinin nasıl elde edildiği ve beklenen dizin yapısı yazılabilir; görüntüler repoya eklenmez.
- Her görev için küçük ve anlaşılır commit'ler atılır.
- Ekip üyeleri ortak bir `main` dalını korur; mümkünse her görev ayrı branch ve pull request ile birleştirilir.
- Kaggle API anahtarı veya erişim token'ı kaynak koduna, prompt'a ya da Git'e yazılmaz.

## 11. Raporun temel bölümleri
1. Özet
2. Problem tanımı ve motivasyon
3. Amaç ve kapsam
4. İlgili çalışmalar
5. Veri seti ve etiketler
6. Yöntem
7. Deney düzeneği ve değerlendirme metrikleri
8. Gerçekleşen deneyler ve sonuçlar
9. Hata analizi
10. Sınırlılıklar ve etik değerlendirme
11. Sonuç ve gelecek çalışmalar
12. Kaynakça

Raporun mevcut aşamasında deney sonuçları yerine planlanan yöntem yazılır. Sonuç bölümü model eğitilip değerlendirilince güncellenir.
