---
name: bitir
description: Üzerinde çalışılan docs/PLAN.md maddesini kapatır — doğrulama matrisine göre test çalıştırır, planı işaretler, sızıntı/sır kontrolü yapar, kişinin kendi dalına commit atar ve tek blok özet verir.
disable-model-invocation: true
argument-hint: "(boş) | <commit mesajı>"
---

# Maddeyi kapat

## Kartı oku

Madde no `<h>.<n>` ise kart `docs/planlar/H<h>.md` dosyasındadır. Dosyanın tamamını okuma; yalnız o kartı al:

```bash
sed -n '/^## <h>\.<n> —/,/^## /p' docs/planlar/H<h>.md
```

(Son satır bir sonraki kartın başlığıdır; yok say.)

## 1. Doğrula
- Kartın **"6. Test / doğrulama"** bölümündeki komutu çalıştır ve **gerçek çıktıyı** göster.
- Kartta komut yoksa CLAUDE.md doğrulama matrisine göre minimum gerekli kontrolü çalıştır.
- Kartın **"7. Kabul ölçütü"** maddelerini **tek tek** kontrol et; her biri için ✅/❌ ve kanıtı (komut çıktısı veya dosya) yaz.
- Test kırılırsa veya bir ölçüt sağlanmazsa **dur, commit atma**. Çıktıyı göster ve sor.

## 2. Planı güncelle
Yalnız **tüm kabul ölçütleri sağlanınca** PLAN.md'de maddeyi `- [x]` yap.

`[E]` kişi başı maddelerde (`R⬜ B⬜ M⬜`): kişiyi `git config user.name` ile PLAN.md'deki kişi tablosundan bul; **yalnız kendi harfini** ✅ yap (ör. `M⬜` → `M✅`). Üç harf de ✅ olunca `- [x]` yap. Kişi tabloda yoksa sor ve tabloya kendi satırını yazmayı öner.
 Plan dışı bir şey yapıldıysa "Plan dışı eklenen maddeler" bölümüne yaz.
Madde bir deney sonucuysa DENEY_KAYDI'nın dolu olduğunu kontrol et.

## 3. Commit öncesi kontrol
`git status --short` çıktısında şunlar varsa **commit atma, sor**:
- `data/`, `outputs/`, `*.pt`, `*.pth`, görüntü dosyaları (`*.png`, `*.jpg`; `docs/` altındaki rapor görselleri hariç)
- `kaggle.json`, `.env`, `gptilekonuşma.md`
- Başka bir ekip üyesinin sahip olduğu dosya (EKIP_REHBERI §1). Sahibi haberdar mı diye sor.

## 4. Commit
- Dal `main` ise commit atma. Önce `<isim>/<madde>-<kisa-ad>` dalı açmayı öner.
- Dosyaları **adıyla** ekle (`git add -A` / `git add .` yasak).
- Mesaj Türkçe, tek satır (`$ARGUMENTS` verildiyse onu kullan). Gövde: `PLAN x.y`, son satır: `Co-Authored-By: Claude <noreply@anthropic.com>`.
- `git push` **yapma**.

## 5. Özet

```
Kapatıldı: <madde no> <başlık>
Doğrulandı: <komut → sonuç>
Commit: <kısa hash> <mesaj> (dal: <dal>)
Sıradaki: <kişinin bir sonraki işaretsiz maddesi>
Paylaşmak için: git push -u origin <dal> → GitHub'da PR aç → bir arkadaşın incelesin
```
