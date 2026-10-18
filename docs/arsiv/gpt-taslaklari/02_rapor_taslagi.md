# Retina Görüntülerinden Diyabetik Retinopati Derecelerinin Sınıflandırılması

## 1. Özet
Bu bölüm, veri seti ve deneyler tamamlandıktan sonra yazılacaktır. Şimdilik sonuç veya başarı oranı belirtilmemelidir.

## 2. Problem Tanımı
Diyabetik retinopati, diyabetle ilişkili olarak retinada ortaya çıkabilen bir hastalık tablosudur. Bu projede, etiketlenmiş retina fundus görüntülerinin beş şiddet sınıfından birine sınıflandırılması ele alınmaktadır. Görüntü sınıflandırma yaklaşımı, ders kapsamında derin öğrenme tabanlı bir prototip geliştirmek amacıyla incelenecektir.

## 3. Projenin Amacı ve Kapsamı
Amaç, transfer öğrenmesi kullanarak temel bir görüntü sınıflandırma modeli geliştirmek ve performansını uygun değerlendirme metrikleriyle ölçmektir. Sistem klinik tanı amacı taşımaz.

## 4. Veri Seti
Veri setinin adı, kaynağı, lisansı/kullanım koşulları, toplam görüntü sayısı, etiket formatı ve sınıf dağılımı doğrulandıktan sonra doldurulacaktır.

- Veri seti:
- Kaynak:
- Toplam görüntü:
- Etiket dosyası:
- Sınıf dağılımı:
- Kullanım koşulları:

## 5. Yöntem
### 5.1 Ön işleme
Görüntüler RGB biçimine dönüştürülecek, modelin beklediği boyuta yeniden boyutlandırılacak ve uygun normalizasyon uygulanacaktır. Eğitim verisine uygun veri artırma uygulanıp uygulanmayacağı deney tasarımında belirlenecektir.

### 5.2 Model
İlk temel model olarak önceden eğitilmiş ResNet18'in beş sınıflı sınıflandırma katmanına uyarlanması planlanmaktadır.

### 5.3 Veri bölme
Eğitim, doğrulama ve test kümeleri birbirinden ayrı tutulacaktır. Test kümesi model seçimi veya ayar yapmak için kullanılmayacaktır. Nihai bölme oranları veri setinin yapısı incelendikten sonra raporlanacaktır.

## 6. Deney Düzeneği
Python ve PyTorch kullanılacaktır. Çalıştırma ortamı, model ayarları, rastgelelik tohumu ve kullanılan kütüphane sürümleri kaydedilecektir.

## 7. Değerlendirme Metrikleri
Accuracy, macro F1, sınıf bazlı recall, confusion matrix ve quadratic weighted kappa (QWK) raporlanacaktır. Sınıf dağılımı dengesiz olabileceği için accuracy tek başına yeterli kabul edilmeyecektir.

## 8. Sonuçlar
Bu bölüm deneyler tamamlandıktan sonra doldurulacaktır. Henüz elde edilmemiş sonuçlar yazılmamalıdır.

## 9. Sınırlılıklar ve Etik
Veri setinin temsil gücü, sınıf dengesizliği, görüntü kalitesi ve modelin yeni kaynaklardaki genellenebilirliği sınırlılıklar arasında değerlendirilecektir. Model klinik kullanım için doğrulanmış değildir.

## 10. Sonuç ve Gelecek Çalışmalar
Bu bölüm deney sonuçlarına göre yazılacaktır. Daha gelişmiş modeller, açıklanabilirlik görselleri veya arayüz, yalnızca temel modelin değerlendirilmesinden sonra gelecek çalışma olarak ele alınabilir.

## 11. Kaynakça
Kullanılan veri setinin resmî sayfası, model makalesi/dokümantasyonu ve ilgili akademik çalışmalar doğrulanarak eklenecektir.
