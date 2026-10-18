---
name: ilerle
description: docs/PLAN.md'de çalışan kişinin sıradaki maddesini rapor vermeden doğrudan uygular. /durum'un sessiz hâli.
disable-model-invocation: true
---

# İlerle

`/durum` ile aynı işi yapar (kişiyi belirle → ilk işaretsiz maddesini bul → uygula), **ama durum raporu vermez.**

1. Tek satır yaz: `Başlıyorum: <madde no> <başlık>`
2. Uygula: CLAUDE.md çalışma döngüsü + doğrulama matrisi.
3. Bitince PLAN.md'de `- [x]` yap ve kısa çıktı formatıyla bitir.

`/durum`'daki onay listesi burada da geçerlidir. Bağımlılık eksikse (başkasının çıktısı yoksa) dur ve tek cümleyle söyle.
