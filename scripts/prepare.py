#!/usr/bin/env python3
"""Prepare a surah: raw/<n>/*.json -> clean/<n>/*.txt and quran/<n>.json.

Raw files (spa5k/tafsir_api) hold one entry per ayah; a tafsir that comments on
several ayat at once repeats the same text, so consecutive identical texts are
merged into one block "=== آيات a-b ===". Diacritics are stripped for reading.
"""
import json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
NAMES = {68: "القلم", 69: "الحاقة", 70: "المعارج", 71: "نوح", 72: "الجن", 73: "المزمل",
         74: "المدثر", 75: "القيامة", 76: "الإنسان", 77: "المرسلات", 78: "النبأ", 79: "النازعات", 80: "عبس", 67: "الملك"}
TASHKEEL = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")


def clean(n):
    out = ROOT / f"data/clean/{n}"
    out.mkdir(parents=True, exist_ok=True)
    for t in json.load(open(ROOT / "data/tafasir.json", encoding="utf-8")):
        f = ROOT / f"data/raw/{n}/{t['src']}.json"
        rows = json.load(open(f, encoding="utf-8")) if f.exists() else []
        blocks = []
        for r in sorted(rows, key=lambda r: r["ayah"]):
            txt = (r.get("text") or "").strip()
            if not txt:
                continue
            if blocks and blocks[-1][2] == txt:
                blocks[-1][1] = r["ayah"]
            else:
                blocks.append([r["ayah"], r["ayah"], txt])
        body = "".join(f"\n=== آيات {a}-{b} ===\n{TASHKEEL.sub('', x)}\n" for a, b, x in blocks)
        (out / f"{t['src']}.txt").write_text(body, encoding="utf-8")
    q = json.load(open(ROOT / f"data/raw/{n}/_quran.json", encoding="utf-8"))["verse"]
    ayat = [q[f"verse_{i}"] for i in range(1, len(q)) if f"verse_{i}" in q]
    (ROOT / "data/quran").mkdir(exist_ok=True)
    (ROOT / f"data/quran/{n}.json").write_text(json.dumps(
        {"surah": n, "name": NAMES[n], "ayat": ayat}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    for n in map(int, sys.argv[1:]):
        clean(n)
