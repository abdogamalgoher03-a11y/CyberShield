# تشغيل CyberShield AI على Windows 11

## تشغيل سريع
1. ثبّت Python 3.11 (64-bit).
2. فك ملف ZIP في مجلد عادي.
3. افتح المجلد وشغّل `RUN_CYBERSHIELD_WINDOWS.bat`.
4. بعد تثبيت المكتبات واجتياز الاختبارات، ستفتح لوحة Streamlit في المتصفح.

## تشغيل يدوي
افتح PowerShell داخل مجلد المشروع:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
streamlit run app.py
```

## تفعيل تعلم الآلة
1. من لوحة التحكم افتح **Machine Learning Lab**.
2. ارفع ملف CSV مصرحًا لك باستخدامه ويحتوي على عمود `Label` وخصائص تدفق رقمية.
3. اترك اسم عمود الهدف `Label` إذا كان هذا هو اسم العمود في الملف.
4. اضغط **Train / retrain ML models**.
5. راجع مقاييس Random Forest وXGBoost وIsolation Forest والخصائص الأعلى أهمية.
6. ارفع CSV آخر بلا عمود Label لتشغيل التنبؤ، ويجب أن يحتوي على نفس خصائص التدريب.

## التدريب من سطر الأوامر
```powershell
python -m cybershield.ml train --csv "C:\datasets\flows.csv" --label-column Label
python -m cybershield.ml status
python -m cybershield.ml predict --csv "C:\datasets\unlabeled.csv" --output predictions.json
```

## الذكاء الاصطناعي التوليدي (اختياري)
- Ollama: شغّل Ollama محليًا ثم اختر Local (Ollama) من الشريط الجانبي.
- OpenAI: اضبط `CYBERSHIELD_OPENAI_API_KEY` في متغيرات البيئة ثم اختر Hosted API (OpenAI).
- يظل AI مغلقًا افتراضيًا. لا تُرسل سجلات خام إلى خدمة خارجية؛ الملخص المرسل محدود بإحصاءات وقواعد مجمعة.

## ملاحظات مهمة للمسابقة
- المشروع لا يراقب الشبكة مباشرة ولا يلتقط الحزم؛ يحلل ملفات سجلات/تدفقات يرفعها المستخدم.
- بيانات العرض التجريبي ليست بيانات قياس أداء ML.
- يجب تدريب النماذج على Dataset موثق ومسموح الاستخدام، وتوثيق التقسيم ومنع تسرب البيانات قبل عرض المقاييس على لجنة التحكيم.
- كل توصيات الاستجابة استشارية وتتطلب موافقة بشرية؛ لا توجد إجراءات حظر أو تغيير إعدادات تلقائية.
