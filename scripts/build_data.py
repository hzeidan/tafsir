#!/usr/bin/env python3
"""Merge per-tafsir benefit files into one de-duplicated dataset.

Each file data/benefits/<surah>.<tafsir>.json is a list of entries:
  full entry : {"k": key, "a": ayah, "t": type, "x": text, "r": ref?}
  back-ref   : {"k": key}   -> this tafsir also mentions an existing benefit
A benefit is stored once; `s` lists every tafsir that mentions it.
Output: data/<surah>.json  and  site/data/<surah>.js (for file:// use).
"""
import json, sys, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TAFASIR = json.load(open(ROOT / "data/tafasir.json", encoding="utf-8"))
TYPES = json.load(open(ROOT / "data/types.json", encoding="utf-8"))
GROUPS = json.load(open(ROOT / "data/groups.json", encoding="utf-8"))
MISSING = ["تفسير ابن أبي حاتم", "البيضاوي (أنوار التنزيل)", "الوجيز للواحدي", "تفسير ابن عثيمين"]

# Editor notes (clearly separated from what the tafsir itself says).
NOTES = {
    "samawat-ibn-ashur": "اجتهاد لابن عاشور يخالف ظاهر قول جمهور المفسرين في أن السماوات سبع أجرام طباق بعضها فوق بعض.",
    "nar-makhluqa": "مذهب أهل السنة أن الجنة والنار مخلوقتان موجودتان الآن.",
    "man-fis-samaa-tawil": "هذا تأويل أشعري؛ ومذهب السلف إثبات العلوّ على ظاهره بلا تكييف (انظر قول الطبري وأضواء البيان).",
    "man-fis-samaa-ibn-ashur": "مذهب السلف إثبات العلوّ لا التفويض في المعنى.",
    "zamakhshari-itizal": "قول الزمخشري مبني على أصول المعتزلة في أفعال العباد.",
    "kab-samawat": "من الإسرائيليات، لا يُعتمد عليها.",
    "mawt-kabsh": "ثبت في الصحيحين أن الموت يُؤتى به يوم القيامة كهيئة كبش أملح فيُذبح، أما وصف الحياة بالفرس فلا يصح.",
    "fadl-ibn-asakir": "أصل فضل السورة ثابت بحديث أبي هريرة عند الترمذي وغيره.",
    "kafir-la-aql": "لا يثبت مرفوعًا.",
    "jaza-aql": "أحاديث فضل العقل ضعيفة عند أكثر المحدثين، وقال ابن القيم: أحاديث العقل كلها كذب.",
    "aql-diama": "حديث «لكل شيء دعامة، ودعامة المؤمن عقله» ضعيف جدًا.",
    "basir-ruya": "إثبات رؤية المؤمنين ربهم في الآخرة ثابت بالنصوص؛ أما الاستدلال بهذه الآية عليه فاجتهاد من الرازي.",
    "afal-ibad-razi": "مذهب أهل السنة أن الله خالق العباد وأفعالهم، وأن للعبد مشيئة وقدرة حقيقية بها يُثاب ويُعاقب.",
    "rabb-alamin-main": "لم يثبت في ذلك حديث صحيح، وإنما ذكره بعض المفسرين.",
    "ruqya-ayn": "الرقية المشروعة ما كان بالقرآن والأدعية المأثورة؛ وهذه حكاية لا يُبنى عليها حكم.",
    "fadl-laylat-qadr": "موضوع؛ من الأحاديث المختلقة في فضائل السور التي يذكرها بعض المفسرين آخر كل سورة.",
    "yunus-hadith": "لا أصل له بهذا اللفظ؛ والثابت في الصحيح: «لا ينبغي لعبد أن يقول: أنا خير من يونس بن متى».",
    "khabaya-ard": "حديث ضعيف، رواه الطبراني وأبو يعلى عن عائشة، وضعّفه المحدثون.",
    "abu-jald-ard": "لا يصح، وهو من الأخبار المنقولة عن أهل الكتاب.",
}
# Text additions merged from a later tafsir into an earlier entry.
APPEND = {
    "mustahzi-ain": " وسمّاه ابن عاشور نقلًا عن الكشاف: محمد بن زكريا الطبيب.",
}


def build(surah: int):
    by_key, order, errors, files = {}, [], [], []
    for t in TAFASIR:
        f = ROOT / f"data/benefits/{surah}.{t['id']}.json"
        if f.exists():
            files.append((t, json.load(open(f, encoding="utf-8"))))
    # pass 1: full entries; pass 2: back-references (order-independent)
    for pass_full in (True, False):
      for t, entries in files:
        for e in entries:
            k = e["k"]
            if ("x" in e) != pass_full:
                continue
            if "x" in e:
                if k in by_key:
                    errors.append(f"{t['id']}: duplicate key {k}")
                    continue
                if e["t"] not in TYPES:
                    errors.append(f"{t['id']}: bad type {e['t']} ({k})")
                by_key[k] = {"id": k, "a": e["a"], "t": e["t"], "x": e["x"],
                             "r": e.get("r", ""), "s": [t["id"]]}
                order.append(k)
            else:
                pending = by_key.get(k)
                if pending is None:
                    errors.append(f"{t['id']}: back-ref to unknown key {k}")
                elif t["id"] not in pending["s"]:
                    pending["s"].append(t["id"])
    for k, n in NOTES.items():
        if k in by_key:
            by_key[k]["n"] = n
    for k, add in APPEND.items():
        if k in by_key:
            by_key[k]["x"] += add
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)

    rank = {t["id"]: i for i, t in enumerate(TAFASIR)}
    rows = sorted((by_key[k] for k in order), key=lambda e: e["a"])
    for e in rows:
        e["s"].sort(key=rank.get)
    for e in rows:  # drop empty fields to keep the payload small
        for f in ("r",):
            if not e[f]:
                del e[f]
    quran = json.load(open(ROOT / f"data/quran/{surah}.json", encoding="utf-8"))
    out = {"surah": surah, "name": quran["name"], "ayat": quran["ayat"],
           "tafasir": TAFASIR, "groups": GROUPS, "missing": MISSING, "types": TYPES, "benefits": rows}
    (ROOT / f"data/{surah}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    site = ROOT / "site/data"
    site.mkdir(parents=True, exist_ok=True)
    (site / f"{surah}.js").write_text(
        "window.TAFSIR_DATA=window.TAFSIR_DATA||{};window.TAFSIR_DATA[%d]=%s;\n"
        % (surah, json.dumps(out, ensure_ascii=False)), encoding="utf-8")
    multi = sum(len(e["s"]) > 1 for e in rows)
    print(f"surah {surah}: {len(rows)} unique benefits, {multi} shared by 2+ tafsirs")
    for t in TAFASIR:
        print(f"  {t['name']}: {sum(t['id'] in e['s'] for e in rows)}", flush=True)


if __name__ == "__main__":
    build(int(sys.argv[1]) if len(sys.argv) > 1 else 67)
