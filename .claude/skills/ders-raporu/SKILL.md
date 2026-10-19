---
name: ders-raporu
description: Dersin haftalık proje raporu şablonunu (Word, .doc/.docx) projenin gerçek durumuna göre doldurur. Kullanıcı şablon yolunu verince çalışır; sade Türkçe yazar, sonuç uydurmaz, yapay zeka izi bırakmaz. Kullanıcı /ders-raporu yazdığında veya "haftalık raporu doldur" dediğinde kullan.
disable-model-invocation: true
argument-hint: "<şablon yolu> [<önceki hafta raporu yolu>] [hafta no]"
---

# Ders raporunu doldur

Girdi: `$ARGUMENTS` (şablon yolu; varsa önceki hafta raporu ve hafta no). Şablon her hafta değişebilir; **bölüm adlarını ve sırasını şablondan oku**, aşağıdaki kuralları ona uygula. Yol verilmediyse tek soru sor: "Şablon dosyasının yolu?"

`/haftalik-rapor` ekibin iç `.md` raporudur. Bu skill dersin **Word** raporudur; ikisi ayrı şeydir.

**Örnek:** üslup ve ayrıntı düzeyi için `docs/ornekler/HAFTA3_RAPOR_ORNEGI.md` dosyasını oku (içeriğini kopyalama, yalnız düzeni ve dili referans al).

## 1. Hangi haftayı yazıyoruz
- Ders haftası ile `docs/PLAN.md` haftası farklı olabilir (3. ders haftası = PLAN H1 idi, yani ders haftası − 2). İlk seferde kullanıcıya tek cümleyle teyit ettir; sonra aynı eşlemeyi kullan.
- Rapor, **o haftanın PLAN maddelerini** anlatır. Bitmiş sayılan: PLAN'da `[x]` olanlar ve kullanıcının "Perşembe'ye kadar biter" dediği maddeler.
- Önceki hafta raporu **içerik için değil, biçim ve sabit bilgiler için** (takım bilgisi, üye tablosu, form işaretleri, bağlantılar) kaynaktır. Eski raporun yöntemi ve kapsamı projeyle çelişiyorsa projeyi esas al.

## 2. Bilgiyi nereden al (hepsi hedefli okunur)
- `docs/PLAN.md` (haftanın maddeleri, sahipleri) ve `docs/planlar/H<n>.md` (yalnız ilgili kartın "Amaç" ve "Ekibe açıklama" bölümleri)
- `git log --since=<hafta başı> --pretty="%h %an %s"`
- `docs/DENEY_KAYDI.md` (sayısal sonuç yalnız buradan), `docs/KARAR_KAYDI.md`, `docs/TEKNIK_TASARIM.md` (yöntem anlatımı için ilgili bölüm), `docs/ARASTIRMA.md` (kaynaklar)
- `docs/arsiv/` ve `gptilekonuşma.md` **okunmaz**.

## 3. İçerik kuralları
- **Sonuç uydurma.** Eğitim yapılmadıysa "Bu hafta model eğitilmedi, başarı sonucu yoktur." yaz. Sayı yalnız DENEY_KAYDI'ndan, veri istatistiği yalnız çalıştırılmış çıktıdan veya ARASTIRMA'dan gelir. Doğrulanmamış bir değeri belgeye **yazma**; yazacaksan cevabın sonundaki "Teyit edilecekler" listesine ekle.
- Rapor yalnız bitmiş veya bitmek üzere olan işleri anlatır. Yapılmamış işi "yapıldı" diye yazma.
- Kapsam proje kararlarıdır: ResNet50 baseline, EfficientNet-B3, IDRiD dış test, Grad-CAM, Streamlit. Karar dışı şeyler (W&B, B4, ViT/Swin, ensemble, timm, OpenCV vb.) rapora girmez. Messidor-2, regresyon, CLAHE yalnız "Could" olduğu açıkça belirtilerek anılır.
- Test kümesi ve IDRiD'nin yalnız bir kez kullanılacağı, seçimin yalnız doğrulama verisiyle yapıldığı doğru anlatılır.
- Tıbbi iddia yok: "akademik prototiptir, tıbbi teşhis yerine geçmez".
- İş paketi tablosu PLAN'daki gerçek iş bölümüne uyar (R veri, B model/eğitim, M değerlendirme + demo). Eski rapordaki paket numaraları projeyle uyuşmuyorsa tabloyu güncelle ve metindeki "İP" atıflarını ona göre ver.
- Gelecek hafta bölümü PLAN'daki bir sonraki haftadan alınır. Önceki raporda söz verilen bir iş kayıyorsa nedeniyle tek cümleyle yaz.
- Kaynakça: yalnız metinde atıf yapılanlar, ilk geçiş sırasına göre numaralı. Tarayıcı/izleme eki taşıyan linkler (`utm_source=...`), "PubMed" gibi sayfadan kopya artıkları ve kullanılmayan kaynaklar silinir. Kaynak `docs/ARASTIRMA.md`'deki doğrulanmış listedir; listede olmayan kaynak eklenmez.

## 4. Dil ve üslup
- Sade, doğrudan Türkçe. Kısa cümle. Okuyan, derin öğrenmeyi bilmeyen bir ders hocası gibi düşün.
- Teknik terim gerekiyorsa ilk geçişte bir cümleyle açıkla (QWK: tahminin gerçek seviyeye yakınlığı; recall: o seviyedeki hastaların ne kadarının yakalandığı). Kod, dosya, komut, kütüphane adı ve sürüm numarası verme; "ortam kuruldu" yeterlidir.
- Yapay zeka izi taşıyan kalıplardan kaçın: "önemli bir rol oynamaktadır", "kapsamlı", "bu bağlamda", "dikkat çekmektedir", "başarıyla tamamlanmıştır", "mükemmel", "sağlam bir temel", gereksiz "ayrıca/öte yandan" zinciri, her paragrafı aynı kalıpla bitirme, aşırı madde işareti ve uzun tire (—) kullanımı. Abartı yok; rakam ve olgu var.
- Şablondaki yönerge cümleleri ("…açıklanır.", "…belirtilir.") belgeden **silinir**. Yazım hatalarını (şablondan gelenler dahil) düzelt: "T.C.", "ÇALIŞMASI", "PROJESİ".
- Form kutuları (Bölüm 2–3 ✔/✘) önceki haftadan aynen kalır; değiştirmek kullanıcının kararıdır, sor.

## 5. Word'de nasıl yapılır (Windows, PowerShell + Word COM)
Bunlar bu projede denenip çalışan yöntemlerdir:
- Dosya adında Türkçe karakter varsa Word `Open` başarısız olur → dosyayı scratchpad'e **ASCII adla kopyala**, onu aç. `.doc` şablon da bu şekilde açılır.
- Önceki haftanın `.docx`'ini kopyalayıp üstünde çalışmak, boş şablonu doldurmaktan güvenlidir (biçim, tablolar, bağlantılar hazır). Şablon yapısı değiştiyse yeni şablonu esas al.
- İçerik çoğunlukla **tek hücreli tablolarda**dır: `$d.Tables(n).Cell(1,1).Range.Text = "paragraf1`rparagraf2"` ile yaz, sonra paragraf paragraf biçimle (başlık `Font.Bold`, madde `ListFormat.ApplyBulletDefault()`, `RemoveNumbers()` ile sıfırla). Silme sonrası paragraf sırası kayar; hep **sondan başa** sil.
- Word Türkçe sürüm: yerleşik stil adları Türkçedir (`"Table Grid"` çalışmaz) → `$tablo.Borders.Enable=$true` kullan.
- Tablo içine tablo: boş paragrafın `Range`'ine `$d.Tables.Add($rg,satır,sütun)`.
- Kaynakçada köprü alanları kalır: `Range.Fields.Unlink()` ve `Font.Underline=0`.
- `.ps1` dosyasını Türkçe karakterle yazıyorsan UTF-8 **BOM'lu** kaydet (`[IO.File]::WriteAllText($f,$t,(New-Object Text.UTF8Encoding $true))`), yoksa karakterler bozulur.
- Takılan Word oturumları dosyayı kilitler: hata alırsan `Get-Process WINWORD | Stop-Process -Force`, sonra tekrar dene.
- Çıktı: `C:\Users\<kullanıcı>\Downloads\Hafta<n>_Proje raporu.docx` (`SaveAs2(yol,16)`). Şablonun ve önceki raporun üstüne yazma. Çıktıyı **git'e ekleme** (öğrenci numarası içerir).

## 6. Kontrol (teslimden önce)
- docx'ten metni çıkar (`python -I` ile; çıktıyı dosyaya UTF-8 yaz, konsola değil) ve şunları tara: eski kapsam kalıntıları (W&B, B4, ViT, ensemble, Messidor), `chatgpt`, "2. hafta" gibi eski hafta ifadeleri, şablon yönergeleri, boş bölüm, metindeki atıf numaralarının kaynakçayla uyuşması.
- Tablo ve sayfa sayısını `ComputeStatistics(2)` ile ver. PDF'i görüntüye çeviren araç bu makinede yok; sayfa görünümünü kullanıcının Word'de bir kez açıp bakması gerektiğini söyle.

## 7. Cevap biçimi (kısa)
```
Hazır: <dosya yolu> (<N> sayfa)
Yazılan: <bölüm bölüm tek satır>
Teyit edilecekler: <belgede geçen ama çalıştırılmış çıktıdan doğrulanmamış değerler; her biri için nereden bakılacağı>
Bitmezse çıkarılacak cümleler: <rapor hangi işin yetişeceğini varsayıyor>
```
Commit atma; rapor git dışıdır.
