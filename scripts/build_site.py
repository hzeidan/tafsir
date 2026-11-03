#!/usr/bin/env python3
"""Build the viewer from site/app.html.

site/index.html   standalone page for the repo (loads site/data/<n>.js; open it directly in a browser)
dist/tafsir.html  one self-contained file with all data inlined (for sharing / publishing)
"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
app = (ROOT / "site/app.html").read_text(encoding="utf-8")
datas = sorted((ROOT / "site/data").glob("*.js"), key=lambda p: int(p.stem))
MARK = "<script>\n(function(){"
assert MARK in app

tags = "".join(f'<script src="data/{p.name}"></script>\n' for p in datas)
head = ('<!doctype html>\n<html lang="ar" dir="rtl"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>[hidden]{display:none!important}body{margin:0}</style></head><body>\n')
(ROOT / "site/index.html").write_text(head + app.replace(MARK, tags + MARK) + "\n</body></html>\n", encoding="utf-8")

inline = "".join(f"<script>{p.read_text(encoding='utf-8')}</script>\n" for p in datas)
(ROOT / "dist").mkdir(exist_ok=True)
(ROOT / "dist/tafsir.html").write_text(app.replace(MARK, inline + MARK), encoding="utf-8")
print("built site/index.html and dist/tafsir.html with", [p.stem for p in datas])
