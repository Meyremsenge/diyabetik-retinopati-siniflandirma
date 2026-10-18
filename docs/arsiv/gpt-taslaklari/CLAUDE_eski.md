# Claude Code çalışma kuralları

Bu depo, üniversite dönem projesi için temel seviyede ve anlaşılır bir görüntü sınıflandırma prototipidir.

## Çalışma ilkeleri
- Önce mevcut dosyaları incele; ardından kısa bir plan öner. Onay olmadan çok sayıda dosya üretme.
- Gereksinim dışı mimari, soyutlama veya özellik ekleme. Öncelik çalışan, açıklanabilir ve test edilebilir basit çözümdür.
- Her yeni Python dosyasının başında amacını kısa docstring ile açıkla.
- Kodda anlamlı değişken ve fonksiyon isimleri kullan; karmaşık tek satırlık ifadelerden kaçın.
- Kullanılan her yeni kütüphaneyi `requirements.txt` içinde gerekçeli biçimde tut.
- Veri dosyalarını, model ağırlıklarını, erişim anahtarlarını ve kişisel bilgileri Git'e ekleme.
- Veri setinin adını veya dizin yapısını varsayma. Önce kullanıcıdan gelen gerçek yolu ve örnek dosya/CSV yapısını kontrol et.
- Dosya yollarını işletim sisteminden bağımsız biçimde `pathlib` ile yönet.
- Rastgelelik tohumu için merkezi yardımcı fonksiyon kullan.
- Veri bölme, metrik hesaplama ve model eğitimini ayrı sorumluluklar olarak tut.
- Test seti eğitim, eşik seçimi, hiperparametre ayarı veya model seçimi için kullanılmamalıdır.
- Ön işleme ve veri artırma adımlarında veri sızıntısı oluşturma. Veri artırma yalnızca eğitim verisine uygulanır.
- Görüntü kimliği veya hasta kimliği varsa bölme stratejisini buna göre değerlendir; aynı hastanın/görüntünün farklı bölümlere düşmesini önle.
- Sonuç uydurma. Deney çalışmadıysa başarısız/çalıştırılmadı olarak açıkça yaz.
- Tıbbi tanı, klinik kullanım veya güvenlik iddiası oluşturma. Proje yalnızca akademik prototiptir.

## Kod yazma biçimi
- Kodun ne yaptığını, neden gerekli olduğunu ve nasıl çalıştırılacağını sade Türkçe ile açıkla.
- Komutları proje kök dizininden çalıştırılacak şekilde ver.
- Her aşama için beklenen çıktıyı ve sık görülen hata durumlarını belirt.
- Değişiklikten sonra mümkünse küçük test veya `--help`/dry-run kontrolü ekle.
- Büyük değişikliklerden önce hangi dosyaların değişeceğini bildir.
- Eğitim kodunu ilk aşamada tek bir temel modelle sınırla: ResNet18 transfer öğrenmesi.
- İlk sürümde ensemble, regresyon, çoklu mimari karşılaştırması, Grad-CAM veya arayüzü otomatik olarak ekleme. Bunlar ancak temel hat çalıştıktan sonra ayrıca kararlaştırılır.

## Çalışma akışı
1. Dosyaları ve Git durumunu incele.
2. Belirsizlikleri listele.
3. En küçük uygulanabilir adımı öner.
4. Kodla.
5. Test et ve gerçek çıktıyı raporla.
6. Değişen dosyaları ve çalıştırma komutlarını açıkla.
