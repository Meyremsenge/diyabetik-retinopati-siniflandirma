---
name: anlat
description: Projedeki bir dosyayı, fonksiyonu veya kavramı (QWK, transfer learning, veri sızıntısı, Grad-CAM...) derin öğrenmeye yeni başlayan bir öğrenciye sade Türkçeyle anlatır, kendi kodumuza bağlar ve kısa bir kontrol alıştırması verir. Kullanıcı /anlat yazdığında veya "bunu anlamadım / açıkla" dediğinde kullan.
argument-hint: "<dosya yolu | fonksiyon | kavram>"
---

# Anlat

Hedef: ekip üyesi sunumda **kendi kodunu kendisi anlatabilsin**.

## Dosya veya fonksiyon için
1. Dosyayı oku. Ne işe yaradığını tek cümleyle söyle ve PLAN'daki hangi maddeye ait olduğunu belirt.
2. Girdi → işlem → çıktı akışını 3–6 adımda anlat. Her adımda `dosya:satır` ver, kodu kopyalama.
3. Bu dosya projede nerede kullanılıyor: kim çağırıyor, çıktısını kim tüketiyor (TEKNIK_TASARIM §7 sözleşmeleri)?
4. "Neden böyle?" sorusuna cevap ver: bir tasarım kararını (ör. `labels=[0..4]`, augmentation'ın yalnız train'de olması) gerekçesiyle açıkla.
5. Sık hata: bu dosyada yeni başlayanların en çok yaptığı 1–2 hata.

## Kavram için
1. Günlük hayattan bir benzetme (en fazla 2 cümle).
2. Teknik tanım (sade). Gerekirse küçük bir sayısal örnek ver; elle hesaplanabilecek kadar küçük olsun.
3. Bizim projede nerede geçtiği.
4. Rapor/sunumda kullanılabilecek tek cümlelik tanım.

## Her zaman
- Sonunda **2 kısa soru** sor (biri "bu satırı değiştirirsem ne olur?" tipinde). Cevapları kullanıcı yazınca değerlendir.
- Jargonun ilk geçtiği yerde Türkçesini ver: "epoch (eğitim turu)".
- 25 satırı geçme. Kullanıcı "daha detaylı" derse genişlet.
