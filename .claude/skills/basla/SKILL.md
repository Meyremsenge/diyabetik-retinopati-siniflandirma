---
name: basla
description: Tek komutluk akış. Kişinin PLAN.md'deki sıradaki maddesini bulur, maddeyi küçük adımlara böler (test → kod → anlatım → kapatma gibi), her adımdan sonra durup kullanıcının "devam" demesini bekler. Madde bitince yeni oturum için yine /basla yazılmasını söyler. Kullanıcı /basla yazdığında çalışır.
disable-model-invocation: true
argument-hint: "(boş) | <madde-no, ör. 1.11>"
---

# Başla (tek komut, adım adım)

Amaç: kullanıcı hiçbir skill adı ezberlemesin. Her oturumda yalnız `/basla` yazar, adımlar arasında yalnız `devam` der.

## 1. Maddeyi seç

`.claude/skills/durum/SKILL.md` içindeki **1. Durumu oku**, **2. Kişiyi belirle**, **3. Hedef maddeyi seç** ve **Kartı oku** bölümlerini uygula. Ek kurallar:
- PLAN satırında `⏸` olan maddeyi atla (ertelenmiş).
- Kartın önkoşulu kişinin **kendi** başka bir maddesiyse (ör. H1 akışında `M: 1.5 → 1.1`) önce onu seç.
- Önkoşul başka bir ekip üyesini bekliyorsa ve kartta sahte veriyle ilerleme yolu yoksa, kişinin bir sonraki **yapılabilir** maddesine geç; kimin neyi beklendiğini tek satırda söyle.
- `git status`'ta yalnız `docs/PLAN.md` değişikse ve bu, dalı olmayan (kurulum/hesap) maddelerin işaretiyse normaldir; sormadan devam et, ilk kodlu maddenin dalına taşınır.

## 2. Adım planını göster (tam bu biçimde)

```
Madde: <no> — <başlık>   (Dal: <dal | yok>)
Adımlar:
  1) ...
  2) ...
Başlıyorum: Adım 1
```

Adımları madde türüne göre kur:

| Tür (karttan anla) | Adımlar |
|---|---|
| **Kod** (kartta test tablosu var) | 1) Test yaz → 2) Kodu yaz ve doğrula → 3) Anlatım → 4) Kontrol + commit |
| **Deney** (hazır promptta `/deney`) | `.claude/skills/deney/SKILL.md`'yi uygula; eğitimi kullanıcı başlatır → kaydet → commit |
| **Kurulum / hesap / ayar** (dosya değişmez) | Kartın **5. Adımlar**'ını 1–3 parçaya böl → doğrulama komutları → PLAN'ı işaretle (commit yok) |
| **Doküman** | 1) Kavramı anlat → 2) Yaz → 3) Kontrol + commit |

## 3. Adımları yürüt

Her adımda yalnız o adımı yap, sonra **dur** ve şu satırla bitir:

```
✔ Adım <k>/<N> bitti. Sıradaki: <adım adı>.  → "devam" yaz
```

Adımların içeriği:
- **Test yaz:** `.claude/skills/atdd/SKILL.md` §1–4'ü uygula (dal yoksa aç, yalnız test, kırmızıyı göster).
- **Kodu yaz ve doğrula:** `.claude/skills/durum/SKILL.md` §5'i uygula; testler yeşil olana kadar. CLAUDE.md çıktı formatıyla 3–6 satır özet.
- **Anlatım:** `.claude/skills/anlat/SKILL.md`'yi maddenin ana dosyası için uygula (sonundaki 2 soruyla). Kullanıcı "geç" derse atla.
- **Kontrol + commit:** Önce bir alt ajan (general-purpose) başlat: kartın **7. Kabul ölçütü** ve CLAUDE.md değişmez kurallarını değişen dosyalar üzerinde bağımsız denetlesin, testleri çalıştırsın, **dosya değiştirmesin**. Sorun bulursa göster ve sor. Sorun yoksa `.claude/skills/bitir/SKILL.md`'yi uygula (bu adıma "devam" denmesi commit onayıdır). Daha önce işaretlenmiş kurulum maddelerinin `docs/PLAN.md` değişikliği de bu commit'e girer.
- **Tarayıcı / elle yapılan adım** (Kaggle, GitHub ayarı): Ne yapılacağını numaralı ve kısa yaz, "bitince ekranda ne gördüğünü yaz" de ve bekle.

Onay gerektiren durumlar (`durum` SKILL'deki liste) geçerlidir: sor ve bekle.

## 4. Kullanıcının kısa cevapları

| Kullanıcı yazarsa | Yap |
|---|---|
| `devam` | Sıradaki adım |
| `atla` | Maddeyi PLAN.md'de satır sonuna ` ⏸ ertelendi` ekleyerek bırak, sıradaki maddeye geç |
| `yapıldı` | Maddeyi kullanıcı zaten bitirmiş: tek soru ile kanıtını sor (ne yaptın / nerede?), kart kabul ölçütüne uyuyorsa PLAN'da işaretle, sıradakine geç |
| `anlamadım` | O adımı daha sade anlat (anlat SKILL'in kavram bölümü) |

## 5. Madde bitince (tam bu biçimde)

```
Bitti: <no> — <başlık>
Sıradaki madde: <no> — <başlık>
👉 Yeni oturum aç ve yaz: /basla
```

Aynı oturumda yeni maddeye geçme (bağlam şişer). Oturum yarıda kalacaksa `.claude/skills/handoff/SKILL.md`'yi uygula; sonraki `/basla` kaldığı yerden devam eder.

## Kural

Kısa yaz. Kullanıcı derin öğrenmede yeni; jargonun ilk geçtiği yerde Türkçesini ver. Her adımda yalnız o adımı yap, sonraki adıma kendiliğinden geçme.
