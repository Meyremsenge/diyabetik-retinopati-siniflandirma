---
name: atdd
description: Bir PLAN maddesinin kartını (docs/planlar/H<n>.md) okur ve kod yazmadan ÖNCE yalnız testleri karttaki test tablosuna birebir uyarak yazar, kırmızı olduklarını gösterir. Soru sormaz. Kullanıcı /atdd <madde-no> yazdığında çalışır.
disable-model-invocation: true
argument-hint: "<madde-no, ör. 2.10>"
---

# Önce test (hafif ATDD)

Argüman: `$ARGUMENTS` (madde no). Boşsa `git config user.name` ile kişiyi bul, PLAN.md'deki ilk işaretsiz kodlu maddesini al.

## 1. Kartı bul
- Hafta numarası maddenin ilk rakamıdır: `2.10` → `docs/planlar/H2.md`.
- Kartı `^## <madde-no> ` başlığından bir sonraki `^## ` başlığına kadar oku. Başka bir şey okuma (gerekirse TEKNIK_TASARIM'ın yalnız kartın andığı bölümü).

## 2. Uygun mu?
- Kartta "Test / doğrulama" altında test dosyası ve test tablosu yoksa (doküman, Kaggle, ayar maddesi): `ATDD uygulanmaz: <madde> test tablosu içermiyor.` yaz ve dur.

## 3. Testleri yaz
- Dal `main` ise önce kartın başındaki dal adıyla dal aç: `git checkout -b <dal>`.
- Karttaki **test dosyasını**, tablodaki **test adlarıyla** ve **beklenen değerlerle** birebir yaz. Test ekleme, çıkarma veya değeri değiştirme yok.
- İçe aktarmalar karttaki "Arayüz" bölümündeki imzalarla aynı (`from src.<modül> import ...`).
- Dosya Türkçe docstring ile başlar: hangi maddeyi test ettiği + `python -m pytest tests/<dosya> -q`.
- `src/` altına **kod yazma**; iskelet veya boş fonksiyon da açma.

## 4. Kırmızıyı göster
`python -m pytest tests/<dosya> -q` → beklenen: `ModuleNotFoundError` / `ImportError` veya testler başarısız. Çıktının son satırlarını göster.

## 5. Bitir
```
ATDD: <madde> — <test dosyası> (<N> test, kırmızı)
Kabul ölçütleri (karttan): <madde madde, kısaltmadan>
Sıradaki: /durum <madde>
```
Commit atma.
