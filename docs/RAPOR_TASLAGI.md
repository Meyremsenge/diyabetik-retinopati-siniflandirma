# Retina Görüntülerinden Diyabetik Retinopati Derecelerinin Sınıflandırılması — Final Rapor Taslağı

**Ekip:** VisionDx (58. Proje) · Rümeysa Akbulut · Büşra Yaşar · Meyrem Şenge

> **Yazım kuralları**
> - Sonuçlar yalnız [DENEY_KAYDI.md](DENEY_KAYDI.md)'deki gerçek değerlerden alınır. Henüz yapılmamış iş "planlanmaktadır" diye yazılır.
> - Klinik tanı, tarama veya güvenlik iddiası yok. Sistem akademik bir prototiptir.
> - Kaynaklar [ARASTIRMA.md](ARASTIRMA.md)'deki numaralarla verilir.
> - Her bölümün sorumlusu köşeli parantezde belirtilmiştir.

## Özet *[Ekip — en son yazılır]*
_Deneyler tamamlanınca yazılacak._

## 1. Giriş ve Problem Tanımı *[Ekip]*
Diyabetik retinopati (DR), diyabetin retina dokusunda yol açtığı değişikliklerle ortaya çıkan ve ilerleyen aşamalarda görme kaybına neden olabilen bir göz hastalığıdır. Şiddeti, Uluslararası Klinik DR Ölçeği'ne göre bulgusuz durumdan proliferatif DR'ye kadar beş seviyede değerlendirilir [1]. Fundus görüntülerinin uzmanlarca incelenmesi zaman alır. Derin öğrenme tabanlı yöntemlerin bu görüntülerden DR'yi tespit etmede etkili olabildiği gösterilmiş [2], farklı popülasyonlarda doğrulamanın önemi de vurgulanmıştır [3].

Bu projede, retinal fundus görüntülerinin 0–4 arasındaki beş DR derecesinden birine atanması, transfer öğrenmeyle eğitilen derin öğrenme modelleriyle ele alınmaktadır.

## 2. Amaç ve Kapsam *[Ekip]*
- APTOS 2019 verisini tekrar ve sızıntı kontrolüyle model eğitimine hazırlamak.
- ResNet50 (baseline) ve EfficientNet-B3 modellerini aynı koşullarda eğitip karşılaştırmak.
- Modelleri QWK, macro F1, sınıf bazlı recall ve confusion matrix ile değerlendirmek.
- Seçilen modeli hiç görmediği IDRiD veri setinde test etmek.
- Tahminleri Grad-CAM ile görselleştirmek ve Streamlit arayüzüyle sunmak.

**Kapsam dışı:** klinik kullanım, ensemble, çoklu mimari taraması, hasta düzeyinde analiz.

## 3. İlgili Çalışmalar *[Ekip]*
_Gulshan [2], Ting [3], Krause [4], ResNet [16], EfficientNet [17], Ben Graham [19], Grad-CAM [21]. Her biri için 2–3 cümle._

## 4. Veri Seti *[Rümeysa]*
- **APTOS 2019** [5]: Hindistan'daki Aravind Eye Hospital'dan toplanan ve 2019 Kaggle yarışmasıyla yayımlanan 3.662 etiketli fundus görüntüsü. Etiketler 0–4 ICDR derecesidir. Sınıf dağılımı PLAN 1.6 çıktısıdır (Kaggle, `src/inspect_dataset.py`; notebook: https://www.kaggle.com/code/rmeysaakbulut/notebookb9fd0088e2). Satır sayısı 3.662, tekrarlanan `id_code` 0, geçersiz etiket yok, eksik görüntü dosyası 0:

| Sınıf | 0 | 1 | 2 | 3 | 4 | Toplam |
|---|---|---|---|---|---|---|
| Görüntü | 1805 | 370 | 999 | 193 | 295 | 3662 |
| Oran | %49,3 | %10,1 | %27,3 | %5,3 | %8,1 | |

- **IDRiD** [6]: 516 görüntü, yalnız dış test. Sınıf dağılımı PLAN 3.4 çıktısıdır (`src/prepare_idrid.py`; train 413 + test 103): sınıf 0: 168, sınıf 1: 25, sınıf 2: 168, sınıf 3: 93, sınıf 4: 62.
- Lisans ve kullanım koşulları: APTOS için Kaggle yarışma kuralları (ticari olmayan kullanım, yeniden dağıtım yok) [9], IDRiD için CC BY 4.0.
- **Görüntü özellikleri:** APTOS görüntüleri PNG biçimindedir ve boyutları tekdüze değildir: 17 farklı boyut vardır; en küçüğü 474×358, en büyüğü 4288×2848 pikseldir. En sık görülen boyutlar 1050×1050 (974), 2416×1736 (638), 2588×1958 (533), 3216×2136 (410) ve 2048×1536 (351) pikseldir. Bu nedenle görüntüler eğitimden önce kareye getirilip yeniden boyutlandırılır (§5.1).
- **Kullanılmayan veri:** APTOS'un etiketsiz 1.928 görüntülük yarışma test seti kullanılmamıştır.
- **Sınıf dengesizliği:** Sınıf 0 verinin yaklaşık %49,3'ünü, sınıf 3 ise yalnızca %5,3'ünü oluşturur. Bu yüzden accuracy tek başına yanıltıcıdır; QWK, macro F1 ve sınıf bazlı recall raporlanır (§7).
![Şekil 4.1 — Her sınıftan bir örnek (sınıf 0–4)](../outputs/figures/ornek_goruntuler.png)

- **Şekil 4.1** — Her sınıftan bir örnek (dosya: `outputs/figures/ornek_goruntuler.png`; APTOS lisansı nedeniyle görüntü git'e girmez, yalnız yerelde bulunur ve final rapora eklenir).
- **Tekrar görüntü analizi:** _PLAN 2.3 çıktısı: grup sayısı, çıkarılan görüntü, çelişkili grup._

## 5. Yöntem
### 5.1 Ön işleme *[Rümeysa]*
Siyah kenar kırpma, 512×512 önbellek, eğitimde 384 px. Augmentation (çevirme, ±30° döndürme, parlaklık/kontrast) yalnız eğitim verisine uygulanır. Ben Graham ön işlemesi ayrı bir deney olarak (E4) değerlendirilir.
### 5.2 Model *[Büşra]*
ImageNet ağırlıklı ResNet50 [16] ve EfficientNet-B3 [17]. Son katman 5 sınıfa uyarlanır ve tüm ağ ince ayarlanır.
### 5.3 Veri bölme ve sızıntı önleme *[Rümeysa]*
Tekrar politikası (TEKNIK_TASARIM §3), ardından tabakalı 70/15/15 bölme. Test kümesi yalnız final modelle bir kez kullanılır.

## 6. Deney Düzeneği *[Büşra]*
_Donanım (Kaggle P100/T4, RTX 3060), yazılım sürümleri (env.txt), hiperparametre tablosu, deney listesi E1–E4._

## 7. Değerlendirme Metrikleri *[Meyrem]*
Model her görüntü için beş seviyeden (0–4) birini tahmin eder. Başarıyı tek bir sayıyla değil, birbirini tamamlayan ölçülerle değerlendiriyoruz.

### 7.1 Doğruluk (accuracy)

Doğru tahmin edilen görüntülerin tüm görüntülere oranıdır. Anlaşılması kolaydır, ama bu veride yanıltıcıdır: APTOS'un 3.662 görüntüsünün 1.805'i (%49,3) seviye 0'dır. Her görüntüye "0" diyen bir model %49,3 doğruluk alır, oysa hasta olan hiçbir görüntüyü yakalamaz. Aynı model için QWK 0, macro F1 ise 0,132 çıkar (seviye 0'ın F1 değeri 0,660, diğer dört seviyeninki 0'dır; ortalama 0,132). Bu yüzden doğruluk tek başına başarı kanıtı sayılmaz.

### 7.2 Seviye bazlı recall ve macro F1

Recall, bir seviyedeki görüntülerin ne kadarının doğru yakalandığını gösterir. Örneğin seviye 3'teki 20 görüntünün 10'una "3" denmişse seviye 3 için recall 0,5'tir. Precision ise modelin "3" dediği görüntülerin ne kadarının gerçekten seviye 3 olduğudur. F1, bir seviye için recall ile precision'ı tek sayıda birleştirir. Macro F1, beş seviyenin F1 değerlerinin ortalamasıdır ve her seviyeye eşit ağırlık verir.

Seviye 3 ve 4 veride azdır (%5,3 ve %8,1) ama en ağır hastaları temsil eder; bunları kaçırmak en pahalı hatadır. Doğruluk bu seviyelerdeki başarısızlığı gizleyebildiği için recall ve macro F1 ayrıca izlenir.

### 7.3 Karışıklık matrisi (confusion matrix)

5 × 5'lik bir tablodur: satır gerçek seviyeyi, sütun modelin tahminini gösterir. Köşegen doğru tahminleri, köşegen dışındaki hücreler hangi seviyenin hangisiyle karıştırıldığını gösterir. Satır-normalize hâlinde her satır kendi toplamına bölünür; böylece "seviye 3'teki görüntülerin yüzde kaçına hangi seviye denmiş?" sorusu doğrudan okunur ve az görüntülü seviyeler de görünür kalır.

### 7.4 QWK (quadratic weighted kappa)

QWK [18], tahminin gerçek seviyeye ne kadar yakın olduğunu ölçer ve APTOS yarışmasının resmî ölçüsüdür. Fikir şudur: seviye 3 olan bir görüntüye 2 demek, 0 demekten daha hafif bir hatadır. Formül:

    κ = 1 − ( Σ wij · Oij ) / ( Σ wij · Eij )
    wij = (i − j)² / (K − 1)²,  K = 5 (seviye sayısı)

- Oij: gerçek seviyesi i, tahmini j olan görüntü sayısı (karışıklık matrisi).
- Eij: model rastgele tahmin etseydi beklenen sayı. Eij = (gerçek seviyesi i olanların sayısı) × (tahmini j olanların sayısı) / (toplam görüntü).
- wij: hata ağırlığı. Bir basamaklık hata 1/16 = 0,0625, iki basamaklık hata 0,25, dört basamaklık hata (örneğin 0 yerine 4) 1 sayılır. Uzak hata, yakın hatadan 16 kat pahalıdır.

Tam uyumda κ = 1, tahminler şans düzeyindeyse κ = 0 olur.

Küçük bir örnek, 6 görüntü: gerçek seviyeler 0, 0, 1, 2, 3, 4; model 0, 1, 1, 2, 4, 4 demiş. İki hata var ve ikisi de bir basamaklık (0 yerine 1, 3 yerine 4). Formülün payındaki Σ wij · Oij = 2 × (1/16) = 0,125 olur. Paydadaki Σ wij · Eij ise beklenen sayılarla 1,75 çıkar. Böylece κ = 1 − 0,125 / 1,75 = 1 − 1/14 = 13/14 ≈ 0,929. Aynı iki hata birer basamak değil de dört basamak uzağa düşseydi QWK çok daha düşük olurdu.

### 7.5 Final model seçim kuralı

Final model, doğrulama verisinde en yüksek QWK'yı veren modeldir. İki modelin QWK farkı 0,01'den küçükse, seviye 3 ve 4'ün recall ortalaması daha yüksek olan seçilir (karar D-17). Kural sonuçlar görülmeden belirlendi. Seçim yalnız doğrulama verisiyle yapılır; test kümesine ve IDRiD'ye model dondurulduktan sonra yalnız bir kez bakılır.

## 8. Sonuçlar *[Meyrem]*
_Deneyler tamamlandıktan sonra DENEY_KAYDI'ndan doldurulacak: karşılaştırma tablosu, confusion matrix, test ve IDRiD sonuçları, iç/dış fark._

## 9. Hata Analizi ve Açıklanabilirlik *[Meyrem]*
_Sık karışan sınıflar, örnek hatalar, Grad-CAM galerisi._

## 10. Arayüz *[Meyrem]*
_Ekran görüntüsü, kullanım adımları, yanıt süresi ölçümü._

## 11. Sınırlılıklar ve Etik *[Ekip]*
- APTOS ve IDRiD Hindistan kaynaklı; popülasyon çeşitliliği sınırlı.
- APTOS'ta hasta kimliği yok, hasta düzeyinde sızıntı tamamen dışlanamaz.
- Etiketlerde uzmanlar arası farklılık var [4]; çelişkili tekrarlar bunun göstergesi.
- Sistem klinik olarak doğrulanmamıştır, tanı amacıyla kullanılamaz. Arayüz yüklenen görüntüyü saklamaz.

## 12. Sonuç ve Gelecek Çalışmalar *[Ekip]*
_Sonuçlara göre. Aday konular: Messidor-2, regresyon + eşik, daha yüksek çözünürlük._

## Kaynakça
ARASTIRMA.md → "Kaynaklar" listesinden yalnız metinde atıf yapılanlar alınır.
