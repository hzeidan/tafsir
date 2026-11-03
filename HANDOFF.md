# أين توقفنا (Handoff)

**آخر تحديث:** 2026-11-03

## المنجز
- سورة الملك (٦٧): ٦١٨ فائدة بلا تكرار من ٣٧ تفسيرًا (٣٧٩ فائدة مشتركة بين تفسيرين فأكثر).
- اختيار المستخدم من القائمة المرقّمة: **١–٤٠** (انظر README). المتاح منها ٣٦ + الثعلبي (إضافة).
- غير متوفر نصه في المصدر: ابن أبي حاتم، البيضاوي، الوجيز للواحدي، ابن عثيمين.
- الصفحة: `site/index.html` (محلية) و`dist/tafsir.html` (ملف واحد).
- رابط العرض (خاص بالمالك): https://claude.ai/artifact/WWV5eQ2fQQyMrRRXvJpi9V

## لم يُنجز بعد
- الدفع إلى GitHub مرفوض (403): يلزم تثبيت Claude GitHub App على `hzeidan/tafsir` أو إعادة ربط GitHub في إعدادات claude.ai.
- السورة التالية: لم يحددها المستخدم بعد.

## طريقة إضافة سورة جديدة (نفس المنهج)
1. تنزيل النصوص: `https://raw.githubusercontent.com/spa5k/tafsir_api/main/tafsir/<slug>/<n>.json` لكل `src` في `data/tafasir.json` إلى `data/raw/<n>/`.
2. تنظيفها (دمج الآيات المكررة وحذف التشكيل) إلى `data/clean/<n>/`.
3. قراءة كل تفسير وكتابة `data/benefits/<n>.<id>.json`:
   - مدخل كامل: `{"k","a","t","x","r"}`، أو إحالة `{"k"}` إذا ذُكرت الفائدة سابقًا (لا تكرار).
   - الأنواع في `data/types.json`؛ تنبيهات المحرر في `NOTES` داخل `scripts/build_data.py`.
4. `python3 scripts/build_data.py <n> && python3 scripts/build_site.py`
5. نص الآيات: `https://raw.githubusercontent.com/semarketir/quranjson/master/source/surah/surah_<n>.json` → `data/quran/<n>.json`.

## ملاحظات منهجية
- الفوائد ملخّصة من النص الفعلي للتفسير، لا من الذاكرة.
- التفاسير المتأخرة (اللباب، القنوجي، الوسيط، الشوكاني) أغلبها نقل؛ تُسجَّل كإحالات.
- مصدر «الثعالبي» برقم 528 هو في الحقيقة الثعلبي؛ و527 هو الثعالبي.
