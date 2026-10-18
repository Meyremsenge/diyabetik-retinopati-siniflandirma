# Claude Code başlangıç promptu

Bu depoda `README.md`, `PROJECT_GUIDE.md`, `CLAUDE.md` ve `docs/` altındaki dosyaları oku. Bu proje, üç bilgisayar mühendisliği öğrencisinin yürüttüğü bir dönem projesidir. Öncelik basit, anlaşılır, test edilebilir bir temel görüntü sınıflandırma prototipidir.

Şu an veri setinin adı, klasör yapısı ve etiket CSV'si doğrulanmış değildir. Veri setinin APTOS olduğunu varsayma. Önce depoyu ve Git durumunu incele; mevcut dosyaları silme veya toplu yeniden yazma.

İlk yanıtında:
1. Depoda gördüğün dosyaları özetle.
2. Eksik olan ve ilk aşamada gerçekten gerekli dosyaları belirt.
3. Veri seti hakkında kesinleştirilmesi gereken soruları listele.
4. En fazla 3 küçük adımdan oluşan bir başlangıç planı öner.
5. Henüz eğitim kodu üretme; veri şeması bilinmiyor.

Ekip veri klasörü ve etiket dosyası bilgilerini sağladıktan sonra sırayla:
A. `scripts/inspect_dataset.py`: veri setini salt okunur biçimde inceleyen, toplam dosya sayısını, CSV sütunlarını, etiket dağılımını ve bulunamayan dosyaları raporlayan bir araç.
B. `src/evaluation/metrics.py`: accuracy, macro F1, sınıf bazlı recall, confusion matrix ve quadratic weighted kappa hesaplayan test edilebilir fonksiyonlar.
C. Küçük testler: metrik fonksiyonları için yapay etiket dizileriyle test ve veri inceleme betiği için kullanım yönergesi.

Kurallar:
- Yalnızca gereken dosyaları değiştir.
- Veri yollarını `pathlib` ile yönet ve komut satırı argümanları kullan.
- Etiket sütununu veya görüntü kimliği sütununu tahmin etme; kullanıcı tarafından doğrulat.
- Büyük veri dosyalarını, ağırlıkları veya sırları Git'e ekleme.
- Sonuç uydurma; test çalıştırılmadıysa bunu belirt.
- Her kod değişikliğinde dosyaların ne yaptığını, nasıl çalıştırılacağını, beklenen çıktıyı ve olası hataları sade Türkçe açıkla.
- Henüz model mimarileri, ensemble, Grad-CAM veya Streamlit ekleme.
- Tıbbi tanı veya klinik kullanım iddiası oluşturma.

İlk olarak depoyu incele ve yalnızca başlangıç planını ver.
