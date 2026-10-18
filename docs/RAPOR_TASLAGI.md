# Retina Görüntülerinden Diyabetik Retinopati Derecelerinin Sınıflandırılması — Final Rapor Taslağı

**Ekip:** VisionDx (58. Proje) · Rümeysa Akbulut · Büşra Yaşar · Meyrem Şenge

> **Yazım kuralları**
> - Sonuçlar yalnız [DENEY_KAYDI.md](DENEY_KAYDI.md)'deki gerçek değerlerden alınır. Henüz yapılmamış iş "planlanmaktadır" diye yazılır.
> - Klinik tanı, tarama veya güvenlik iddiası yok. Sistem akademik bir prototiptir.
> - Kaynaklar [ARASTIRMA.md](ARASTIRMA.md)'deki numaralarla verilir.
> - Her bölümün sorumlusu köşeli parantezde belirtilmiştir.

## Özet *[Ekip — en son yazılır]*
_Deneyler tamamlanınca yazılacak._

## 1. Giriş ve Problem Tanımı *[Ekip]*
Diyabetik retinopati (DR), diyabetin retina dokusunda yol açtığı değişikliklerle ortaya çıkan ve ilerleyen aşamalarda görme kaybına neden olabilen bir göz hastalığıdır. Şiddeti, Uluslararası Klinik DR Ölçeği'ne göre bulgusuz durumdan proliferatif DR'ye kadar beş seviyede değerlendirilir [1]. Fundus görüntülerinin uzmanlarca incelenmesi zaman alır. Derin öğrenme tabanlı yöntemlerin bu görüntülerden DR'yi tespit etmede etkili olabildiği gösterilmiş [2], farklı popülasyonlarda doğrulamanın önemi de vurgulanmıştır [3].

Bu projede, retinal fundus görüntülerinin 0–4 arasındaki beş DR derecesinden birine atanması, transfer öğrenmeyle eğitilen derin öğrenme modelleriyle ele alınmaktadır.

## 2. Amaç ve Kapsam *[Ekip]*
- APTOS 2019 verisini tekrar ve sızıntı kontrolüyle model eğitimine hazırlamak.
- ResNet50 (baseline) ve EfficientNet-B3 modellerini aynı koşullarda eğitip karşılaştırmak.
- Modelleri QWK, macro F1, sınıf bazlı recall ve confusion matrix ile değerlendirmek.
- Seçilen modeli hiç görmediği IDRiD veri setinde test etmek.
- Tahminleri Grad-CAM ile görselleştirmek ve Streamlit arayüzüyle sunmak.

**Kapsam dışı:** klinik kullanım, ensemble, çoklu mimari taraması, hasta düzeyinde analiz.

## 3. İlgili Çalışmalar *[Ekip]*
_Gulshan [2], Ting [3], Krause [4], ResNet [16], EfficientNet [17], Ben Graham [19], Grad-CAM [21]. Her biri için 2–3 cümle._

## 4. Veri Seti *[Rümeysa]*
- **APTOS 2019** [5]: 3.662 etiketli fundus görüntüsü. Sınıf dağılımı (literatürdeki değer; PLAN 1.6'da kendi çıktımızla doğrulanacak):

| Sınıf | 0 | 1 | 2 | 3 | 4 | Toplam |
|---|---|---|---|---|---|---|
| Görüntü | 1805 | 370 | 999 | 193 | 295 | 3662 |
| Oran | %49,3 | %10,1 | %27,3 | %5,3 | %8,1 | |

- **IDRiD** [6]: 516 görüntü, yalnız dış test. _Dağılım PLAN 3.4'te._
- Lisans ve kullanım koşulları: APTOS için Kaggle yarışma kuralları (ticari olmayan kullanım, yeniden dağıtım yok), IDRiD için CC BY 4.0.
- **Tekrar görüntü analizi:** _PLAN 2.3 çıktısı: grup sayısı, çıkarılan görüntü, çelişkili grup._

## 5. Yöntem
### 5.1 Ön işleme *[Rümeysa]*
Siyah kenar kırpma, 512×512 önbellek, eğitimde 384 px. Augmentation (çevirme, ±30° döndürme, parlaklık/kontrast) yalnız eğitim verisine uygulanır. Ben Graham ön işlemesi ayrı bir deney olarak (E4) değerlendirilir.
### 5.2 Model *[Büşra]*
ImageNet ağırlıklı ResNet50 [16] ve EfficientNet-B3 [17]. Son katman 5 sınıfa uyarlanır ve tüm ağ ince ayarlanır.
### 5.3 Veri bölme ve sızıntı önleme *[Rümeysa]*
Tekrar politikası (TEKNIK_TASARIM §3), ardından tabakalı 70/15/15 bölme. Test kümesi yalnız final modelle bir kez kullanılır.

## 6. Deney Düzeneği *[Büşra]*
_Donanım (Kaggle P100/T4, RTX 3060), yazılım sürümleri (env.txt), hiperparametre tablosu, deney listesi E1–E4._

## 7. Değerlendirme Metrikleri *[Meyrem]*
_PLAN 1.12: QWK (formül ve sezgi), macro F1, recall, confusion matrix; accuracy'nin neden tek başına yetmediği (sınıf 0 ≈ %49)._

## 8. Sonuçlar *[Meyrem]*
_Deneyler tamamlandıktan sonra DENEY_KAYDI'ndan doldurulacak: karşılaştırma tablosu, confusion matrix, test ve IDRiD sonuçları, iç/dış fark._

## 9. Hata Analizi ve Açıklanabilirlik *[Meyrem]*
_Sık karışan sınıflar, örnek hatalar, Grad-CAM galerisi._

## 10. Arayüz *[Meyrem]*
_Ekran görüntüsü, kullanım adımları, yanıt süresi ölçümü._

## 11. Sınırlılıklar ve Etik *[Ekip]*
- APTOS ve IDRiD Hindistan kaynaklı; popülasyon çeşitliliği sınırlı.
- APTOS'ta hasta kimliği yok, hasta düzeyinde sızıntı tamamen dışlanamaz.
- Etiketlerde uzmanlar arası farklılık var [4]; çelişkili tekrarlar bunun göstergesi.
- Sistem klinik olarak doğrulanmamıştır, tanı amacıyla kullanılamaz. Arayüz yüklenen görüntüyü saklamaz.

## 12. Sonuç ve Gelecek Çalışmalar *[Ekip]*
_Sonuçlara göre. Aday konular: Messidor-2, regresyon + eşik, daha yüksek çözünürlük._

## Kaynakça
ARASTIRMA.md → "Kaynaklar" listesinden yalnız metinde atıf yapılanlar alınır.
