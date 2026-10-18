# VisionDx — Araştırma Notları

> Rapor yazarken buradaki **doğrulanmış** bilgiler ve kaynaklar kullanılır. Araştırma tarihi: Ekim 2026.
> "Doğrulanmadı" işaretli bilgiler raporda kesin bilgi gibi yazılmaz.

## 1. Diyabetik retinopati ve derecelendirme

- Derecelendirmede **Uluslararası Klinik DR Şiddet Ölçeği (ICDR)** kullanılır: 0 DR yok, 1 hafif NPDR, 2 orta NPDR, 3 ağır NPDR, 4 proliferatif DR [1]. APTOS ve IDRiD bu ölçeği kullanır.
- Derin öğrenmenin fundus görüntülerinden DR tespitinde etkili olabildiği Gulshan ve ark. [2] ve farklı popülasyonlarda doğrulanmasının önemi Ting ve ark. [3] tarafından gösterilmiştir.
- Uzmanlar arasında derecelendirme farklılığı yüksektir. Krause ve ark. [4] uzman-konsensüs (adjudication) etiketlerinin model değerlendirmesini belirgin biçimde değiştirdiğini gösterir. Bu bilgi, APTOS'taki çelişkili etiketli tekrar görüntüleri yorumlamak için önemlidir.

## 2. Veri setleri (doğrulanmış)

| | APTOS 2019 | IDRiD (Disease Grading) | Messidor-2 |
|---|---|---|---|
| Kaynak | Aravind Eye Hospital (Hindistan), Kaggle yarışması [5] | Nanded'deki tek bir göz kliniği (Hindistan), ISBI 2018 [6] | Fransa, Messidor projesi [7] |
| Etiketli görüntü | 3.662 (train). 1.928 test görüntüsünün etiketi yok | 516 = 413 train + 103 test | 1.748 (874 muayene) |
| Sınıf dağılımı | 0:1805 · 1:370 · 2:999 · 3:193 · 4:295 | Kendi CSV'sinden hesaplanacak | Konsensüs etiketleri: yaklaşık %58 / 15 / 20 / 4 / 2 |
| Etiket | `train.csv`: `id_code`, `diagnosis` | DR derecesi 0–4 + DME riski 0–2 | **Resmî sürümde yok.** Google'ın 3 retina uzmanı konsensüs etiketleri Kaggle'da ("Messidor-2 DR Grades": image id, adjudicated DR grade, DME, gradable; 4 görüntü değerlendirilemez) [4][8] |
| Lisans | Kaggle yarışma kuralları: ticari olmayan/akademik kullanım, yeniden dağıtım yok [9] | CC BY 4.0 [6] | ADCIS lisans formu |
| Bilinen sorun | Tekrar ve çelişkili etiketli görüntüler (§3), farklı klinik/kamera, gürültülü görüntüler [10] | Küçük, tek merkez | Etiket kaynağı üçüncü taraf |

**Doğrulanmadı:** APTOS indirme boyutu (~10 GB; test görüntüleri dahil). Kaggle "Data" sekmesinden kontrol edilecek.

**Ekip için sonuç:**
- APTOS'un yarısı sınıf 0, sınıf 3 ise yaklaşık %5. Bu yüzden accuracy yanıltıcıdır; QWK, macro F1 ve sınıf bazlı recall raporlanır.
- 2. hafta raporundaki "Messidor-2'de etiket yok" riskinin bir çözümü var (Google etiketleri). Yine de iş yükü nedeniyle bu adım *Could* önceliğinde.
- IDRiD de Hindistan'dan olduğu için APTOS'a benziyor. Dış test "farklı merkez" sayılır ama "farklı popülasyon" sayılmaz. Bu sınırlılık raporda belirtilir.

## 3. APTOS'ta tekrar görüntüler (veri sızıntısı riski)

- Kaggle tartışmasında yaklaşık **262 tekrar görüntü** konuşulmuş. Bazı katılımcılar bunları çıkarmanın skoru pek değiştirmediğini, bazıları ise tekrarların uzman anlaşmazlığı hakkında bilgi taşıdığını söylemiş [11].
- Bağımsız bir GitHub denetimi (resmî değil): **134 birebir + 14 çok benzer çift → 131 grup, 270 görüntü (%7,4)**. Bu grupların **37'sinde etiketler çelişiyor** [12].
- Başka bir projede, bölme sonrasında tutulan 549 görüntünün 27'sinin eğitim kümesinde birebir kopyası olduğu bildirilmiş [13].
- **Karar:** Tekrar kontrolü bölmeden önce yapılır (TEKNIK_TASARIM §3). Bu, 2. hafta gereksinim analizindeki FG-2'nin gerekçesidir.

## 4. Beklenen başarı (literatür)

| Çalışma | Model | QWK | Not |
|---|---|---|---|
| IJSR (2026) [14] | ResNet50 (ImageNet) | 0,860 | Kendi bölmesi, test |
| IPB tezi [15] | ResNet50 + CLAHE + oversampling | 0,924 (test) | Farklı ön işleme |
| Kaggle 1.'si | Ensemble | ≈0,93 *(doğrulanmadı)* | Yarışma özel lider tablosu; karşılaştırılabilir değil |

- Tek bir ResNet50 için bildirilen QWK değerleri bölme ve ön işlemeye göre yaklaşık **0,86–0,92** arasında. Hedefimiz olan ≥ 0,85 makul görünüyor ama **garanti değil**.
- Tekrar görüntüler doğru ayrılınca skor biraz düşebilir. Bu düşüş, ölçümün dürüst olduğunu gösterir; raporda böyle açıklanır.

## 5. Yöntemler

- **Transfer öğrenme:** ImageNet'te eğitilmiş ağırlıklarla başlayıp tüm ağı ince ayarlamak. Küçük tıbbi veri setlerinde standart yaklaşım.
- **ResNet** [16]: artık (residual) bağlantılarla derin ağların eğitilebilmesini sağlar. Baseline olarak yaygındır.
- **EfficientNet** [17]: derinlik, genişlik ve çözünürlüğü birlikte ölçekler. Benzer doğrulukta daha az parametre kullanır.
- **QWK** [18]: iki derecelendirici arasındaki uyumu, uzak hataları karesel ağırlıkla cezalandırarak ölçer. APTOS yarışmasının resmî metriğidir. −1 ile 1 arasında değer alır; 1 tam uyum, 0 tesadüfi uyum demektir.
- **Ben Graham ön işlemesi** [19][20]: görüntüden Gauss bulanıklaştırmasıyla tahmin edilen arka planı çıkarır (`4·(img − blur) + 128`) ve aydınlatma farklarını azaltır. 2015 Kaggle DR yarışmasının birincisinin yöntemidir. TensorFlow Datasets'te "btgraham-300" adıyla bir varyantı bulunur.
- **Grad-CAM** [21]: son evrişim katmanının gradyanlarından sınıfa özgü bir ısı haritası üretir. Bize "model nereye bakıyor" sorusunun görsel cevabını verir; lezyon tespiti değildir.

## 6. Donanım ve ortam (ölçüldü)

| Ekip üyesi | Donanım | Kullanım |
|---|---|---|
| Meyrem | ASUS ROG Strix G15, **RTX 3060 Laptop 6 GB**, sürücü 566.07, C: diskinde **13 GB boş** | Yerel eğitim (cu126) + demo. Önce disk temizliği gerekli |
| Rümeysa, Büşra | MacBook M2 | Kod geliştirme, küçük testler (`mps`). Tam eğitim Kaggle'da |
| Kaggle | P100 16 GB veya 2×T4; haftada ~30 saat (resmî değil, hesapta görünür), oturum ≤ 12 saat [22] | Veri hazırlama + eğitim |

Kurulu Python sürümleri: 3.10, 3.11, 3.12, 3.14. Proje **3.12** ile çalışacak; 3.14 bazı kütüphaneler için çok yeni olabilir. PyTorch 2.14.1'in `cu126` sürümü mevcut ve 566 sürücüsüyle uyumlu.

## Kaynaklar

1. Wilkinson CP ve ark. *Proposed international clinical diabetic retinopathy and diabetic macular edema disease severity scales.* Ophthalmology. 2003;110(9):1677–1682.
2. Gulshan V ve ark. *Development and validation of a deep learning algorithm for detection of diabetic retinopathy in retinal fundus photographs.* JAMA. 2016;316(22):2402–2410.
3. Ting DSW ve ark. *Development and validation of a deep learning system for diabetic retinopathy and related eye diseases using retinal images from multiethnic populations with diabetes.* JAMA. 2017;318(22):2211–2223.
4. Krause J ve ark. *Grader variability and the importance of reference standards for evaluating machine learning models for diabetic retinopathy.* Ophthalmology. 2018;125(8):1264–1272. https://arxiv.org/abs/1710.01711
5. APTOS 2019 Blindness Detection, Kaggle. https://www.kaggle.com/competitions/aptos2019-blindness-detection
6. Porwal P ve ark. *Indian Diabetic Retinopathy Image Dataset (IDRiD): A Database for Diabetic Retinopathy Screening Research.* Data. 2018;3(3):25. https://doi.org/10.3390/data3030025 · https://idrid.grand-challenge.org/Data/ · https://ieee-dataport.org/node/956
7. Decencière E ve ark. *Feedback on a publicly distributed image database: the Messidor database.* Image Anal Stereol. 2014;33(3):231–234. · Abràmoff MD ve ark. JAMA Ophthalmol. 2013;131(3):351–357. · https://www.adcis.net/en/third-party/messidor2/
8. Messidor-2 DR Grades (Google Brain), Kaggle — ayna: https://baselight.app/u/kaggle/dataset/google_brain_messidor2_dr_grades
9. APTOS 2019 kuralları: https://www.kaggle.com/competitions/aptos2019-blindness-detection/rules · lisans özeti: https://arxiv.org/pdf/2605.13015
10. Benchmarking Bayesian Deep Learning on DR Detection Tasks: https://arxiv.org/pdf/2211.12717
11. Kaggle APTOS tartışması #100489: https://www.kaggle.com/c/aptos2019-blindness-detection/discussion/100489
12. aptos-leakage-audit (GitHub): https://github.com/Fire-Dev2/aptos-leakage-audit
13. diabetic-retinopathy-cdss PR #2 (GitHub): https://github.com/CloudTechy/diabetic-retinopathy-cdss/pull/2
14. IJSR v15i8: https://www.ijsr.net/archive/v15i8/SR26812222953.pdf
15. IPB Repository: https://repository.ipb.ac.id/handle/123456789/178452
16. He K, Zhang X, Ren S, Sun J. *Deep Residual Learning for Image Recognition.* CVPR 2016.
17. Tan M, Le QV. *EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks.* ICML 2019.
18. Cohen J. *Weighted kappa: Nominal scale agreement with provision for scaled disagreement or partial credit.* Psychological Bulletin. 1968;70(4):213–220.
19. Graham B. *Kaggle Diabetic Retinopathy Detection competition report.* 2015.
20. Deep image mining for diabetic retinopathy screening: https://arxiv.org/pdf/1610.07086 · TFDS: https://www.tensorflow.org/datasets/catalog/diabetic_retinopathy_detection
21. Selvaraju RR ve ark. *Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization.* ICCV 2017.
22. Ücretsiz GPU kaynakları (2026): https://gpuperhour.com/blog/free-cloud-gpus-and-credits
