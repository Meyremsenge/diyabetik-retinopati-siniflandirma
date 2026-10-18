# 1. Hafta: Başlangıç ve ilk çalışan parçalar

## Haftanın hedefi
Veri setini doğrulamak, geliştirme ortamını kurmak, ortak arayüzleri kararlaştırmak ve mümkünse küçük bir veri inceleme/metric modülünü çalıştırmak. Bu hafta yüksek başarı oranı elde etmek hedef değildir.

## İlk gün: ekipten bilgi toplama
- [ ] Veri setinin tam adını ve kaynağını öğren.
- [ ] Veri klasörünün nerede olduğunu öğren.
- [ ] Etiket CSV dosyasının adını ve sütunlarını öğren.
- [ ] Görüntü sayısını ve sınıf etiketlerini doğrula.
- [ ] Mevcut rapor/ödev yönergesi/teslim formatı varsa ekipte paylaş.
- [ ] Ortak Git deposunun URL'sini ve varsayılan dalını doğrula.

## Görev dağılımı
### Rümeysa: veri inceleme
- [ ] Veri seti klasör yapısını ve etiket formatını belgele.
- [ ] Toplam görüntü sayısını, bozuk/eksik dosyaları ve sınıf dağılımını çıkar.
- [ ] Veri setinin lisans/kullanım koşullarını kaydet.
- [ ] Veri bölme için öneri hazırla; test verisinin ayrı tutulmasını gözet.

### Büşra: model eğitim iskeleti
- [ ] Python/PyTorch ortamını doğrula.
- [ ] Tek bir örnek görüntüyü okuyup tensor'a dönüştüren küçük test hazırla.
- [ ] ResNet18'in 5 sınıflı çıkış katmanı için taslak hazırla.
- [ ] Henüz tüm veri üzerinde uzun eğitim başlatma.

### Meyrem: metrik ve değerlendirme modülü
- [ ] `src/evaluation/metrics.py` için metrik fonksiyonu hazırla.
- [ ] Gerçek etiket ve tahmin dizileriyle toy test yap.
- [ ] Metriklerin ne anlama geldiğini rapor için sade şekilde açıkla.
- [ ] Büşra ile `y_true`, `y_pred` ve çıktı biçimini netleştir.

### Ortak
- [ ] Dosya isimlerini ve veri sütunlarını birlikte onayla.
- [ ] Kodları küçük adımlarla Git'e ekle.
- [ ] Herkes kendi kodunun ne yaptığını anlatabilecek durumda olsun.
- [ ] Raporun problem, amaç, veri ve yöntem bölümlerini taslak olarak yaz.

## Haftanın sonunda beklenen çıktılar
1. Veri setinin adı ve yapısı doğrulanmış olmalı.
2. Çalışma ortamı ve Git deposu çalışmalı.
3. Metrik modülü küçük örnek üzerinde çalışmalı.
4. En az bir görüntü okunabilmeli ve gösterilebilmeli.
5. İlk modelin eğitimine geçmek için teknik engeller listelenmiş olmalı.
6. Raporun yöntem bölümü mevcut gerçeklerle tutarlı olmalı.

## Haftalık toplantı gündemi
- Hangi görev tamamlandı?
- Hangi komut çalıştırıldı ve çıktı ne oldu?
- Hangi dosya değişti?
- Hangi hata veya belirsizlik var?
- Bir sonraki haftanın en küçük uygulanabilir hedefi nedir?
