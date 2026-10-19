---
name: ilerle
description: docs/PLAN.md'de çalışan kişinin sıradaki maddesini rapor vermeden doğrudan uygular. /durum'un sessiz hâli.
disable-model-invocation: true
---

# İlerle

`/durum` ile aynı işi yapar (kişiyi belirle → ilk işaretsiz maddesini bul → uygula), **ama durum raporu vermez.**

1. Tek satır yaz: `Başlıyorum: <madde no> <başlık>`
2. Kartı oku (`/durum`'daki "Kartı oku" komutu: `sed -n '/^## <h>\.<n> —/,/^## /p' docs/planlar/H<h>.md`; dosyanın tamamını okuma).
3. Kartın **Adımlar**, **Arayüz** ve **Test** bölümlerini uygula; CLAUDE.md çalışma döngüsü + doğrulama matrisine uy.
4. Bitince PLAN.md'de `- [x]` yap (`[E]` kişi başı maddede yalnız kendi harfini ✅ yap, üçü ✅ olunca `[x]`) ve kısa çıktı formatıyla bitir.

`/durum`'daki onay listesi burada da geçerlidir. Kartın **Önkoşul**'u bitmemişse dur ve tek cümleyle söyle; kartta sahte veriyle yapılabilecek bir yol varsa onu öner.
