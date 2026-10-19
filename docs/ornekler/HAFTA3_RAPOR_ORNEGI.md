# Örnek ders raporu: 3. Hafta

> **Bu dosya bir örnektir.** `/ders-raporu` skill'i raporu bu düzende ve bu üslupla yazar. Gerçek rapor Word dosyasıdır ve öğrenci numaraları içerdiği için repoya konmaz.
> Ne işe yarar: yeni bir hafta için üslup, ayrıntı düzeyi ve bölüm içeriği referansı. İçindeki rakamlar ve cümleler o haftaya aittir; kopyalanmaz.
> Hafta 3 raporu, PLAN.md'nin H1 haftasını (kurulum ve veriyi tanıma) anlatır.

**Ekip:** VisionDx · **Proje:** Retina Görüntülerinden Diyabetik Retinopati Derecelerinin Sınıflandırılması (58. Proje)

## 1. Giriş


Diyabetik retinopati (DR), diyabetin gözün arka duvarındaki retina dokusunda yaptığı hasardır ve ilerlediğinde görme kaybına yol açabilir. Hastalık, göz dibi (fundus) fotoğraflarına bakılarak, hiç belirti olmayan durumdan en ağır evre olan proliferatif retinopatiye kadar beş seviyede derecelendirilir [1].

Bu fotoğrafları değerlendirmek uzmanlık ister ve görüntü sayısı arttığında uzun sürer. Derin öğrenme yöntemlerinin göz dibi fotoğraflarından diyabetik retinopatiyi yüksek doğrulukla tespit edebildiği gösterilmiştir [2]. Bu tür sistemlerin farklı hasta gruplarında da sınanması gerektiği vurgulanmıştır [3].

Bu projede, bir göz dibi fotoğrafından hastalık seviyesini (0–4) tahmin eden bir bilgisayar programı geliştiriyoruz. Programı sıfırdan eğitmek yerine, genel fotoğraflarla önceden eğitilmiş hazır ağları (ResNet50 ve EfficientNet-B3) kendi verimize uyarlıyoruz. Çalışma akademik bir prototiptir; tıbbi teşhis yerine geçmez.

Bu rapor projenin 3. haftasını kapsar. İlk haftalarda konu, veri setleri ve iş paketleri belirlenmişti. Bu hafta uygulamaya geçildi: ortak çalışma ortamı kuruldu, eğitim verisi incelendi, modelleri kurmak ve başarıyı ölçmek için gereken ilk kodlar yazılıp test edildi. Model henüz eğitilmediği için bu raporda başarı sonucu yoktur.

## Amaç ve Hedefler


Projenin amacı, bir göz dibi fotoğrafından diyabetik retinopati seviyesini 0–4 arasında tahmin eden bir sistem geliştirmek ve başarısını dürüst biçimde ölçmektir. Sistemin yalnızca eğitimde kullandığı veride değil, hiç görmediği, başka bir kaynaktan gelen görüntülerde de denenmesi hedeflenmektedir.

Proje hedefleri şunlardır:

- APTOS 2019 veri setini incelemek, tekrar eden görüntüleri bulup eğitim ve test verisine karışmasını önlemek,
- ResNet50 ile bir başlangıç modeli (baseline) eğitmek,
- EfficientNet-B3'ü aynı koşullarda eğitip karşılaştırmak; sınıf dengesizliğinin ve ön işlemenin etkisini denemek,
- Başarıyı QWK, F1, seviye bazlı recall ve karışıklık matrisi ile ölçmek,
- Seçilen modeli APTOS test verisinde ve bağımsız IDRiD veri setinde bir kez denemek,
- Modelin görüntüde hangi bölgelere baktığını Grad-CAM ile göstermek,
- Modeli bir web sayfası üzerinden denenebilir hale getirmek.

Bu doğrultuda 3. haftada ulaşılması planlanan hedefler şunlardır:

- Ekip üyelerinin bilgisayarlarında aynı sürümlerle çalışan ortamın kurulması, Kaggle hesaplarının hazırlanması ve GitHub'da ortak çalışma düzeninin başlatılması,
- APTOS verisinin görüntü sayısı, seviye dağılımı ve görüntü boyutları açısından incelenmesi,
- Rastgeleliği sabitleme, cihaz seçme ve model kurma gibi ortak yardımcı kodların yazılması,
- Başarı ölçümlerini hesaplayan kodun yazılıp küçük örneklerle test edilmesi.
## 2. Yöntem


Bu çalışma, göz dibi fotoğraflarından diyabetik retinopati seviyesini tahmin eden bir derin öğrenme sisteminin geliştirilmesi ve farklı seçeneklerin adil biçimde karşılaştırılması üzerine kuruludur. Her deneyde yalnızca tek bir şey değiştirilir; böylece sonuçtaki farkın nedeni belli olur.

### 2.1. Veri

Ana veri seti, her görüntünün 0–4 arası bir seviyeyle etiketlendiği APTOS 2019'dur (3.662 görüntü) [4]. Modelin hiç görmediği, başka bir kaynaktan gelen görüntülerde de denenebilmesi için IDRiD veri seti (516 görüntü) dış test olarak kullanılacaktır [5].

APTOS'ta aynı ya da birbirine çok benzeyen görüntüler bulunduğu bilinmektedir [6]. Bunlar hem eğitimde hem testte yer alırsa model ezberlediği görüntüyle sınanmış olur ve başarısı gerçeğinden yüksek görünür. Bu yüzden önce tekrar eden görüntüler bulunacak; aynı etiketli olanlardan biri tutulacak, etiketleri birbiriyle çelişenler tamamen çıkarılacaktır. Kalan görüntüler, seviyelerin oranı korunarak %70 eğitim, %15 doğrulama ve %15 test olarak ayrılacaktır. Bu ayırma bir kez yapılır ve sonradan değiştirilmez.

### 2.2. Görüntü ön işleme

Görüntülerin siyah kenarları kırpılır ve hepsi 512 × 512 piksele küçültülür. Eğitim sırasında görüntüler rastgele çevrilir, ±30 derece döndürülür ve parlaklık ile kontrastları hafifçe değiştirilir. Bu işlemler yalnızca eğitim verisine uygulanır; doğrulama ve test verisi hep aynı biçimde hazırlanır. Ayrı bir deneyde, aydınlatma farklarını azaltan Ben Graham yöntemi denenecektir [7].

### 2.3. Modeller ve eğitim

İlk model (baseline) olarak ResNet50 [8], karşılaştırma modeli olarak EfficientNet-B3 [9] kullanılacaktır. İkisi de genel fotoğraflarla önceden eğitilmiş hazır ağlardır. Son katmanları beş seviyeyi verecek şekilde değiştirilir ve ağın tamamı bizim verimizle yeniden eğitilir. Eğitim en fazla 15 tur sürer; doğrulama verisinde en yüksek QWK'ya ulaşılan tur saklanır. Rastgelelik ayarı sabittir, böylece aynı ayarlarla yapılan eğitim aynı sonucu verir.

### 2.4. Deneyler

- E1: ResNet50 (başlangıç modeli),
- E2: EfficientNet-B3 (E1 ile aynı koşullarda),
- E3: sınıf ağırlıklı kayıp (az görüntülü seviyelere daha çok önem verilir),
- E4: Ben Graham ön işlemesi,
- E5: 5 parçalı çapraz doğrulama (zaman kalırsa).

### 2.5. Başarının ölçülmesi

Ana ölçü QWK'dır [10]. QWK, tahminin gerçek seviyeye ne kadar yakın olduğuna bakar: seviye 3 olan bir görüntüye 2 demek, 0 demekten daha az cezalandırılır. 1 tam uyumu, 0 şans düzeyini gösterir. Bunun yanında F1, her seviye için recall (o seviyedeki hastaların ne kadarının yakalandığı), karışıklık matrisi (hangi seviyenin hangisiyle karıştırıldığı) ve doğruluk raporlanacaktır. Doğruluk tek başına başarı kanıtı sayılmaz. Başarı hedefi APTOS test verisinde QWK ≥ 0,85'tir; bu bir garanti değildir, ulaşılamazsa sonuç olduğu gibi yazılacaktır.

### 2.6. Final model ve dış doğrulama

Final model, doğrulama verisinde en yüksek QWK'yı veren modeldir. İki model arasındaki fark 0,01'den küçükse ağır iki seviyeyi (3 ve 4) daha iyi yakalayan seçilir. Bu kural sonuçlar görülmeden önce belirlenmiştir. Model seçilip dondurulduktan sonra APTOS test verisinde ve IDRiD'de yalnızca bir kez denenecek, sonuca bakılarak ayar değiştirilmeyecektir.

### 2.7. Açıklanabilirlik ve arayüz

Modelin bir görüntüde hangi bölgelere dikkat ettiği Grad-CAM yöntemiyle ısı haritası olarak gösterilecektir [11]. Bu harita modelin baktığı yeri gösterir; hastalık belirtisini bulduğu anlamına gelmez. Model, görüntü yüklenince tahmini, beş seviyenin olasılıklarını ve ısı haritasını gösteren basit bir web sayfasına bağlanacaktır. Sayfada “Akademik prototiptir; tıbbi teşhis yerine geçmez” uyarısı sürekli görünecek, yüklenen görüntü bilgisayara kaydedilmeyecektir.

### 2.8. Üçüncü hafta çalışma düzeni

Bu hafta yapılan işler, iş paketlerinin ilk adımlarıdır. Her iş küçük parçalara bölündü ve her parçanın ne zaman bitmiş sayılacağı baştan yazıldı. Kodlar, yazan kişinin dışında bir ekip üyesinin de çalıştırıp anlatabileceği sadelikte tutuldu. Kodlar GitHub'da tutuluyor; herkes kendi dalında çalışıyor ve değişiklikler ana dala bir arkadaşın incelemesinden sonra alınıyor.

## 3. Proje Yönetimi

### 3.1. Takım üyeleri ve görevleri

- **Rümeysa Akbulut:** veri setlerinin hazırlanması, görüntü ön işleme, tekrar eden görüntülerin kontrolü, veri ayırma, IDRiD dış testi.
- **Büşra Yaşar (takım kaptanı):** eğitim ve tahmin kodları, ResNet50 baseline, EfficientNet-B3 ve ek deneyler, deney kayıtları.
- **Meyrem Şenge:** başarı ölçümleri, model karşılaştırması, hata analizi, Grad-CAM, web arayüzü.

### 3.2. İş paketleri

| İP | İş paketi | Sorumlu |
|---:|---|---|
| 1 | **Ortam ve ekip düzeni:** Python ortamının, Kaggle hesaplarının ve GitHub çalışma düzeninin kurulması. | Tüm Ekip |
| 2 | **Veri inceleme:** APTOS verisinin görüntü sayısı, seviye dağılımı ve boyutlarının incelenmesi. | Rümeysa Akbulut |
| 3 | **Görüntü ön işleme:** Siyah kenarların kırpılması, 512 × 512 piksele küçültme ve Ben Graham yönteminin uygulanması. | Rümeysa Akbulut |
| 4 | **Tekrar kontrolü ve veri ayırma:** Aynı veya çok benzer görüntülerin bulunması, çelişkili etiketlerin ayıklanması; eğitim, doğrulama ve test verisinin bir kez ayrılması. | Rümeysa Akbulut |
| 5 | **Veri yükleme ve veri artırma:** Görüntülerin modele verilmesi; eğitimde çevirme, döndürme ve parlaklık değişimi. | Rümeysa Akbulut |
| 6 | **Model ve eğitim kodu:** Ortak yardımcı kodlar, modellerin kurulması, eğitim ve tahmin kodlarının yazılması. | Büşra Yaşar |
| 7 | **Baseline eğitimi (E1):** ResNet50'nin eğitilmesi ve ilk sonucun kaydedilmesi. | Büşra Yaşar |
| 8 | **Karşılaştırma deneyleri (E2–E5):** EfficientNet-B3 eğitimi, sınıf ağırlıklı kayıp, Ben Graham deneyi; zaman kalırsa 5 parçalı çapraz doğrulama. | Büşra Yaşar |
| 9 | **Başarı ölçümü ve karşılaştırma:** QWK, F1, recall ve karışıklık matrisinin hesaplanması; deney sonuçlarının tabloda karşılaştırılması. | Meyrem Şenge |
| 10 | **Hata analizi:** Yanlış tahmin edilen görüntülerin ve en sık karışan seviyelerin incelenmesi. | Meyrem Şenge |
| 11 | **Final model, test ve dış doğrulama:** Final modelin seçilip dondurulması; APTOS test ve IDRiD verisinde birer kez denenmesi. | Tüm Ekip |
| 12 | **Grad-CAM:** Modelin görüntüde baktığı bölgelerin ısı haritasıyla gösterilmesi. | Meyrem Şenge |
| 13 | **Web arayüzü:** Görüntü yükleyip tahmin ve ısı haritasını görebilme; uyarı metni ve gizlilik kuralları. | Meyrem Şenge |
| 14 | **Rapor, sunum ve demo:** Rapor bölümlerinin yazılması, sunumun hazırlanması ve demo provaları. | Tüm Ekip |

## 4. Teori ve Sonuçlar


### 4.1. Yaklaşım

Problem, bir göz dibi fotoğrafının 0–4 arası beş seviyeden birine atanması olarak ele alınmaktadır. Görüntüler hazırlandıktan sonra, önceden eğitilmiş ResNet50 ve EfficientNet-B3 ağları bu probleme uyarlanacak ve aynı koşullarda karşılaştırılacaktır. Final model seçildikten sonra APTOS test verisinde ve IDRiD'de birer kez denenecek, Grad-CAM ile modelin baktığı bölgeler gösterilecektir.

### 4.2. Bu haftanın sonuçları

Bu hafta model eğitilmedi. Haftanın çıktıları, eğitimin temelini oluşturan hazırlıklardır.

Veri incelemesi: APTOS 2019 eğitim verisi Kaggle üzerinde incelendi. Etiket dosyasında 3.662 görüntü var ve hepsinin görüntü dosyası bulundu. Görüntülerin seviyelere dağılımı aşağıdaki tablodadır.

| Seviye | Anlamı | Görüntü sayısı | Oran |
|---|---|---:|---:|
| 0 | Hastalık yok | 1.805 | %49,3 |
| 1 | Hafif | 370 | %10,1 |
| 2 | Orta | 999 | %27,3 |
| 3 | Ağır | 193 | %5,3 |
| 4 | Proliferatif (en ağır) | 295 | %8,1 |

Görüntülerin yaklaşık yarısı hastalık belirtisi olmayan seviye 0'dır; en ağır iki seviye toplamın yalnızca %13'ünü oluşturur. Bu yüzden başarıyı yalnızca doğrulukla ölçmek yanıltıcı olurdu: model her görüntüye “hastalık yok” dese bile yaklaşık %49 doğruluk elde eder. Bu nedenle ana ölçü olarak QWK kullanılacak ve her seviyede hastaların ne kadarının yakalandığı (recall) ayrıca izlenecektir. Az görüntülü seviyeler için eğitimde sınıf ağırlığı denenecektir. Görüntü boyutları birbirinden çok farklıdır; en büyükleri üç binden fazla piksel genişliğindedir. Bu yüzden eğitimden önce hepsi 512 × 512 piksele küçültülecektir.

Ortak çalışma ortamı: Herkesin bilgisayarında aynı Python sürümü (3.12) ve aynı kütüphane sürümleriyle çalışan ortam kuruldu. Kaggle hesapları (ekran kartı kullanımı için) hazırlandı ve APTOS yarışma kuralları kabul edildi. Kodlar GitHub'da tutuluyor.

Yardımcı kodlar: Rastgeleliği sabitleyen fonksiyon, çalışılacak cihazı seçen fonksiyon (ekran kartı, Mac'te Apple çipi ya da işlemci) ve ResNet18, ResNet50 ile EfficientNet-B3 ağlarını aynı biçimde kuran fonksiyon yazıldı. Ağların çıkışı beş seviyeye göre ayarlandı ve sahte verilerle denendi.

Başarı ölçümü: QWK, F1, doğruluk, seviye bazlı recall ve karışıklık matrisini hesaplayan kod yazıldı. Elle hesaplanmış küçük örneklerle ve bir seviyenin hiç tahmin edilmediği durumla test edildi. Bu hafta yazılan dosyaların 27 testinin tamamı geçti.

### 4.3. Gelecek hafta

Gelecek hafta şunlar planlanmaktadır:

- Görüntülerin kırpılıp 512 × 512 piksele küçültülmesi,
- Tekrar eden görüntülerin bulunması ve veri ayırmanın (eğitim, doğrulama, test) bir kez yapılması,
- Görüntüleri modele veren yapının ve eğitim kodunun yazılması,
- ResNet50 ile ilk eğitimin (E1) yapılması,
- Tahmin ve değerlendirme dosyalarının yazılması.
## Kaynaklar

[1] Wilkinson, C. P., Ferris, F. L., Klein, R. E., vd. (2003). Proposed international clinical diabetic retinopathy and diabetic macular edema disease severity scales. Ophthalmology, 110(9), 1677–1682.

[2] Gulshan, V., Peng, L., Coram, M., vd. (2016). Development and validation of a deep learning algorithm for detection of diabetic retinopathy in retinal fundus photographs. JAMA, 316(22), 2402–2410.

[3] Ting, D. S. W., Cheung, C. Y.-L., Lim, G., vd. (2017). Development and validation of a deep learning system for diabetic retinopathy and related eye diseases using retinal images from multiethnic populations with diabetes. JAMA, 318(22), 2211–2223.

[4] Kaggle. (2019). APTOS 2019 Blindness Detection. https://www.kaggle.com/competitions/aptos2019-blindness-detection

[5] Porwal, P., Pachade, S., Kamble, R., vd. (2018). Indian Diabetic Retinopathy Image Dataset (IDRiD): A database for diabetic retinopathy screening research. Data, 3(3), 25. https://doi.org/10.3390/data3030025

[6] Kaggle APTOS 2019 tartışması: tekrar eden görüntüler. https://www.kaggle.com/c/aptos2019-blindness-detection/discussion/100489

[7] Graham, B. (2015). Kaggle Diabetic Retinopathy Detection competition report.

[8] He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. IEEE Conference on Computer Vision and Pattern Recognition (CVPR).

[9] Tan, M., & Le, Q. V. (2019). EfficientNet: Rethinking model scaling for convolutional neural networks. International Conference on Machine Learning (ICML).

[10] Cohen, J. (1968). Weighted kappa: Nominal scale agreement with provision for scaled disagreement or partial credit. Psychological Bulletin, 70(4), 213–220.

[11] Selvaraju, R. R., Cogswell, M., Das, A., vd. (2017). Grad-CAM: Visual explanations from deep networks via gradient-based localization. IEEE International Conference on Computer Vision (ICCV).
