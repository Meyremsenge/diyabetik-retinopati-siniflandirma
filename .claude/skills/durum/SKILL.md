---
name: durum
description: docs/PLAN.md'yi okur, çalışan kişinin (git user.name → R/B/M) sıradaki maddesini bulur, kısa durum raporu verir ve maddeyi uygulamaya başlar. Kullanıcı /durum yazdığında çalışır.
disable-model-invocation: true
argument-hint: "(boş) | <madde-no, ör. 2.4>"
---

# Durum ve devam

Amaç: kullanıcı prompt yazmadan, planda **kendi** kaldığı yerden devam etmek.

## 1. Durumu oku (minimum bağlam)

Yalnız şunları oku:
- `docs/PLAN.md` (tamamı)
- `git config user.name`, `git branch --show-current`, `git log --oneline -5`, `git status --short`

## 2. Kişiyi belirle

`git config user.name` değerini PLAN.md'deki "Git kullanıcı adı → kişi" tablosunda ara → `R`, `B` veya `M`.
- Bulunamazsa tek soru sor: "Rümeysa, Büşra, Meyrem — hangisisin?" Cevaba göre tabloyu doldurmayı öner.

## 3. Hedef maddeyi seç

- Argüman verildiyse o madde.
- Yoksa: kişinin `[X]` veya `[E]` etiketli **ilk işaretsiz** `- [ ]` maddesi (en erken haftadan başla).
- Seçilen madde başka birinin çıktısına bağlıysa (ör. `splits.csv` yok) bunu söyle. Bekleyenler için sahte/küçük veriyle ilerlenebilecek kısmı öner.

## 4. Kısa rapor (tam bu biçimde)

```
Kişi: <ad> · Dal: <dal> · Çalışma ağacı: <temiz | N dosya değişik>
Tamamlanan (senin): <ör. 1.8, 1.9>
Şu an: <madde no> — <başlık>
Bağımlılık: <yok | ... bekleniyor>
```

- Dal `main` ise önce dal açmayı öner: `git checkout -b <isim>/<madde>-<kisa-ad>`.
- Commit edilmemiş değişiklik önceki bir maddeye aitse **önce onu sor**; üstüne yeni iş yapma.

## 5. Uygula

Rapordan sonra durma, doğrudan başla (`/durum` = "devam et"). `CLAUDE.md` çalışma döngüsü ve doğrulama matrisine uy. Ayrıntı için TEKNIK_TASARIM'ın yalnız ilgili bölümünü `grep` ile bul.

**Önce onay gerektirenler** (CLAUDE.md "İzin ve onay sınırları"): başkasının dosyası, sözleşme/`splits` değişikliği, bağımlılık, silme, 30 dakikadan uzun eğitim, push. Bu durumda raporun sonuna `Bu madde onay gerektiriyor: <sebep>. Başlayayım mı?` ekle ve bekle.

## 6. Bitince

- PLAN.md'de kutuyu `- [x]` yap.
- CLAUDE.md çıktı formatı (Değişen / Doğrulanan / Nasıl çalışır / Kalan).
- Commit **atma**; kullanıcı `/bitir` der. Sıradaki maddeye kendiliğinden geçme.

## Kural

Kısa tut. Seçenek listesi veya uzun gerekçe yok. Plan kararlaştırılmıştır, şimdi uygulama zamanı.
