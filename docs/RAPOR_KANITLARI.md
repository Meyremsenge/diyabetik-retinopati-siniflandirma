# Rapordaki sayıların kanıtı

> Raporda (H2 haftalık rapor ve rapor taslağı) geçen her sayının **nereden geldiğini** ve **nasıl yeniden hesaplanacağını** gösterir. Sayı uydurulmaz; hepsi aşağıdaki dosyalardan çıkar. Son doğrulama: 2026-10-28, tüm değerler raporla aynı çıktı.
>
> `[git]` işaretli dosyalar depoda vardır. `[yerel]` işaretliler APTOS lisansı ve boyut nedeniyle git'e girmez; Kaggle'da (`visiondx-aptos-512`) veya ilgili komutla üretilir.

## 1. Sayı → kaynak → nasıl bulundu

| Rapordaki sayı | Değer | Kaynak | Nasıl bulundu |
|---|---|---|---|
| APTOS görüntü sayısı ve seviye dağılımı | 3.662 · 1.805 / 370 / 999 / 193 / 295 (%49,3 / 10,1 / 27,3 / 5,3 / 8,1) | `data/processed/aptos_512/train.csv` `[yerel]` | `diagnosis` sütununu say; oran = sayı / 3.662 |
| Birebir aynı (MD5) çift | 134 | `outputs/data_reports/candidate_pairs.csv` `[yerel]` (`python -m src.find_duplicates`) | `same_md5` sütunu doğru olan satır sayısı |
| Görüntü parmak izi (pHash) mesafesi 0 olan çift | 158 | aynı dosya | `distance == 0` olan satır sayısı |
| Tekrar grupları, eşik 0 (seçilen) | 139 grup · 287 görüntü · 37 çelişkili · en büyük grup 4 | aynı dosya | MD5 çiftleri + eşik ≤ 0 çiftleri `group_pairs` ile gruplanır; bir grupta farklı etiket varsa "çelişkili" |
| Eşik taraması (Şekil 3) | görüntü sayısı 287 / 577 / 1.384 / 2.339 / 3.157 / 3.526; en büyük grup 4 / 34 / 248 / 2.011 / 2.996 / 3.484 (eşik 0, 2, 4, 6, 8, 10) | aynı dosya | Her eşik için aynı gruplama |
| Tekrar grupları, eşik 4 (kullanılmadı) | 249 grup · 1.384 görüntü · 94 çelişkili · en büyük grup 248 | aynı dosya | Aynı yöntem, eşik 4. Zincirleme eşleşme nedeniyle bırakıldı (karar D-18) |
| Elenen görüntü | 185 (106 tekrar + 79 çelişkili etiket) | `splits/aptos_splits.csv` `[git]` | `split == "excluded"` satırları; `note` sütunu nedeni verir |
| Kalan ve bölme | 3.477 → eğitim 2.433 · doğrulama 522 · test 522 (%70,0 / 15,0 / 15,0) | aynı dosya | `split` sütununu say; `python -m src.make_splits` (tohum 42), bir kez üretildi |
| Kümelerdeki seviye dağılımı (Bölme tablosu) | eğitim 1250/236/645/118/184 · doğrulama ve test 268/51/138/25/40 | `splits/aptos_splits.csv` + `train.csv` | `id_code` ile birleştirip `split` × `diagnosis` say |
| IDRiD | 516 (413 eğitim + 103 test) · 0:168 · 1:25 · 2:168 · 3:93 · 4:62 | `data/processed/idrid_512/idrid_labels.csv` `[yerel]` | `python -m src.prepare_idrid`; `diagnosis` sayımı |
| E1 metrikleri | QWK 0,903 · macro F1 0,663 · accuracy 0,849 · recall 0,981 / 0,471 / 0,942 / 0,320 / 0,450 · n=522 | `docs/DENEY_KAYDI.md` `[git]` ve koşunun `metrics_val.json` dosyası | `python -m src.evaluate --predictions <koşu>/val_predictions.csv` |
| E1 eğitimi | 9 tur · en iyi tur 5 · toplam 5,5 dk | koşunun `history.csv` dosyası | `val_qwk` en büyük satır; `seconds` toplamı / 60 |
| Hata yüzdeleri (Şekil 3 yorumu) | seviye 3→2 %56 · seviye 1→2 %45 · seviye 4→2 %33 | `metrics_val.json` `confusion_matrix` | Satırı kendi toplamına böl (örn. 14 / 25) |
| Test sayısı | 86 geçti | tüm testler | `python -m pytest -q` |

E1 koşusunun dosyaları (`outputs/runs/20261028-1716_resnet50_baseline/`) Kaggle'dan `run_e1.zip` olarak indirilir; git'e girmez.

## 2. Şekiller nereden geldi

| Şekil | Kaynak |
|---|---|
| Şekil 1: her seviyeden APTOS örneği | PLAN 1.7 çıktısı `outputs/figures/ornek_goruntuler.png` `[yerel]` |
| Şekil 2: ham → kırpılmış → Ben Graham | IDRiD `IDRiD_001.jpg`; `src.preprocessing.prepare_image` ve `ben_graham` ile üretildi |
| Şekil 3: tekrar tespitinde eşik karşılaştırması | `candidate_pairs.csv`; eşik 0, 2, 4, 6, 8, 10 için 4. bölümdeki gruplama kodu. Kesikli çizgi (yaklaşık 262): Kaggle tartışması [6], `docs/ARASTIRMA.md` §3 |
| Şekil 4: karışıklık matrisi | E1 `metrics_val.json` → `src.evaluate.normalize_rows` ve `save_confusion_matrix` |
| Şekil 5: eğitim eğrileri | E1 `history.csv` (kayıp ve `val_qwk`) |

## 3. Rapor §7'deki örnek sayılar

- "Her görüntüye 0 diyen model": accuracy 1.805 / 3.662 = 0,493; macro F1 0,132 (seviye 0 için F1 = 2 · 1.805 / (1.805 + 3.662) = 0,660; diğer dört seviye 0; ortalama 0,132); QWK 0. `src.metrics.compute_metrics` ile doğrulandı.
- Küçük QWK örneği (6 görüntü, gerçek 0,0,1,2,3,4 · tahmin 0,1,1,2,4,4): Σ w·O = 1/8, Σ w·E = 7/4, κ = 1 − (1/8)/(7/4) = 13/14 ≈ 0,929. `compute_metrics` aynı sonucu verir.

## 4. Hepsini yeniden hesapla

Proje kökünden, aşağıdaki kodu bir `python` oturumuna yapıştır. `RUN`, E1 koşusunun klasörüdür (`run_e1.zip` içinden).

```python
import json
from pathlib import Path
import pandas as pd
from src.find_duplicates import group_pairs

RUN = Path("outputs/runs/20261028-1716_resnet50_baseline")

# 1) APTOS seviye dağılımı
labels = pd.read_csv("data/processed/aptos_512/train.csv", dtype={"id_code": str})
counts = labels["diagnosis"].value_counts().sort_index()
print("APTOS:", len(labels), counts.to_dict(), (counts / len(labels) * 100).round(1).to_dict())

# 2) Tekrar tespiti (eşik 0 ve eşik 4)
pairs = pd.read_csv("outputs/data_reports/candidate_pairs.csv", dtype={"id_a": str, "id_b": str})
print("MD5 aynı çift:", int(pairs["same_md5"].sum()), "· mesafe 0 çift:", int((pairs["distance"] == 0).sum()))
label_of = {}
for row in pairs.itertuples():
    label_of[row.id_a] = row.diagnosis_a
    label_of[row.id_b] = row.diagnosis_b
for threshold in (0, 2, 4, 6, 8, 10):
    selected = pairs[(pairs["distance"] <= threshold) | pairs["same_md5"]]
    groups = pd.Series(group_pairs(list(zip(selected["id_a"], selected["id_b"]))))
    table = pd.DataFrame({"group": groups.values, "label": [label_of[i] for i in groups.index]})
    conflicting = int((table.groupby("group")["label"].nunique() > 1).sum())
    print(f"eşik {threshold}: {groups.nunique()} grup · {len(groups)} görüntü · "
          f"{conflicting} çelişkili · en büyük grup {groups.value_counts().max()}")

# 3) Bölme
splits = pd.read_csv("splits/aptos_splits.csv", dtype=str, keep_default_na=False)
print("bölme:", splits["split"].value_counts().to_dict())
print("elenme nedeni:", splits[splits["split"] == "excluded"]["note"].value_counts().to_dict())
merged = splits.merge(labels, on="id_code")
print(pd.crosstab(merged["split"], merged["diagnosis"]))

# 4) IDRiD
idrid = pd.read_csv("data/processed/idrid_512/idrid_labels.csv")
print("IDRiD:", len(idrid), idrid["diagnosis"].value_counts().sort_index().to_dict())

# 5) E1
metrics = json.loads((RUN / "metrics_val.json").read_text())
history = pd.read_csv(RUN / "history.csv")
print("E1:", {k: round(metrics[k], 3) for k in ("qwk", "macro_f1", "accuracy")}, "n =", metrics["n"])
print("recall:", [round(x, 3) for x in metrics["recall_per_class"]])
print("tur:", len(history), "· en iyi tur:", int(history.loc[history["val_qwk"].idxmax(), "epoch"]),
      "· süre (dk):", round(history["seconds"].sum() / 60, 2))
```
