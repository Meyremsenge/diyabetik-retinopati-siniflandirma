---
name: haftalik-rapor
description: Haftalık ilerleme raporu taslağını git geçmişi, PLAN.md, DENEY_KAYDI.md ve KARAR_KAYDI.md'den üretir; yapılmayanı yapılmış göstermez. Kullanıcı /haftalik-rapor yazdığında çalışır.
disable-model-invocation: true
argument-hint: "<hafta no, ör. 2> (boş = içinde bulunulan hafta)"
---

# Haftalık rapor

## 1. Topla
- Hafta tarih aralığını PLAN.md başlığından al (H1 = 19–25 Ekim 2026 ...).
- `git log --since=<başlangıç> --until=<bitiş+1> --all --pretty="%h %an %s"`
- PLAN.md'deki o haftanın maddeleri ve `[x]` durumları
- DENEY_KAYDI.md'de o hafta dolan satırlar
- KARAR_KAYDI.md'de o hafta eklenen satırlar
- Kaptan: EKIP_REHBERI §1 dönüşüm listesi

## 2. Yaz
`docs/HAFTALIK_RAPOR_SABLONU.md` biçiminde → `docs/haftalik/H<n>.md`.
- Her "Tamamlandı" satırı bir **kanıta** bağlanır: commit hash, dosya veya komut çıktısı. Kanıt yoksa durum "doğrulanamadı — ekip teyit etmeli" olur.
- Bitmeyen maddeler "devam ediyor" veya "yapılamadı (neden)" olarak yazılır. Neden bilinmiyorsa `_(neden: ekip doldurmalı)_` yaz.
- Sayısal sonuç yalnız DENEY_KAYDI'ndan alınır. Yoksa "Bu hafta deneysel sonuç yoktur." yazılır.
- Gelecek hafta tablosu PLAN.md'deki bir sonraki haftadan alınır.
- Dil: resmî, sade, akademik Türkçe. Abartı ("başarıyla", "mükemmel") yok.

## 3. Bitir
Dosya yolunu ver. Ekibin doldurması gereken boşlukları madde madde listele. Commit atma.
