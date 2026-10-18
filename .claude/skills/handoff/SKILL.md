---
name: handoff
description: Yarım kalan işi yeni bir Claude oturumunun (veya başka bir ekip üyesinin) devam ettirebilmesi için HANDOFF.md yazar/günceller.
---

1. Proje kökünde `HANDOFF.md` varsa önce oku.
2. Şu başlıklarla oluştur/güncelle (Türkçe, kısa):
   - **Kim / dal / PLAN maddesi**
   - **Hedef:** neyi bitirmeye çalışıyoruz
   - **Yapılanlar:** dosyalar ve çalıştırılan komutlar (gerçek çıktı özetiyle)
   - **İşe yarayanlar**
   - **İşe yaramayanlar:** tekrar denenmesin diye, hata mesajıyla
   - **Sıradaki adımlar:** net, sıralı
   - **Açık sorular:** kime sorulmalı
3. Dosya yolunu ver. Yeni oturumda yalnız "HANDOFF.md'yi oku ve devam et" demek yeter.

`HANDOFF.md` geçicidir. Madde bitince silinir ve commit'lenmez (gerekirse `.gitignore`'a eklenmesini öner).
