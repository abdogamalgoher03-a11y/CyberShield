# مصادر البيانات البحثية وخطة التدريب متعددة المصادر

هذه المصادر مؤسسات/مشروعات بحثية معروفة. وجود المصدر في هذه القائمة لا يعني أن ملفات البيانات قد نُزّلت أو دُرّبت داخل النسخة الحالية. سجّل تاريخ التنزيل والترخيص وبصمة SHA-256 لكل ملف قبل التدريب.

## المصادر الأساسية

| المجموعة | الجهة | نوع البيانات | فئات/نطاق | ملاحظات |
|---|---|---|---|---|
| CIC-IDS2017 | Canadian Institute for Cybersecurity, UNB | PCAP وتدفقات CSV معنونة | benign وBrute Force وDoS/DDoS وWeb وInfiltration وBotnet وPortScan | مرجع مناسب كبداية؛ الصفحة الرسمية تشرح خصائص التدفقات والتسميات والأوراق المطلوب الاستشهاد بها. |
| CSE-CIC-IDS2018 | Communications Security Establishment + CIC/UNB | PCAP وتدفقات CSV وسجلات مضيف | Brute Force وHeartbleed وBotnet وDoS/DDoS وWeb وInfiltration | كبير جدًا؛ توجد ملاحظات بحثية منشورة حول مشكلات في بعض التسميات/التوليد، لذا يلزم تدقيق البيانات وعدم افتراض الكمال. |
| UNSW-NB15 | UNSW Canberra / ACCS Cyber Range Lab | تدفقات CSV وPCAP | 9 عائلات هجوم مع benign | يوجد تقسيم منشور للتدريب والاختبار؛ يجب الاستشهاد بالأوراق الخمس المطلوبة للاستخدام الأكاديمي. |
| CICIoT2023 | Canadian Institute for Cybersecurity | PCAP وCSV | 33 هجومًا ضمن 7 فئات على بيئة IoT | مفيد كاختبار منفصل لتوسيع المجال إلى IoT، وليس دمجه عشوائيًا مع بيانات enterprise. |

## الروابط الرسمية

- CIC-IDS2017: https://www.unb.ca/cic/datasets/ids-2017.html
- CSE-CIC-IDS2018: https://www.unb.ca/cic/datasets/ids-2018.html
- UNSW-NB15: https://research.unsw.edu.au/projects/unsw-nb15-dataset
- CICIoT2023: https://www.unb.ca/cic/datasets/iotdataset-2023.html

## سياسة التدريب المعتمدة

1. لا تخلط ملفات من مصادر مختلفة في CSV واحد تلقائيًا. تختلف أسماء الخصائص وتعريفاتها وأدوات استخراجها وتوزيعاتها.
2. درّب نموذجًا مستقلًا لكل مصدر أولًا، مع حفظ ملف النموذج والتقرير وبصمة البيانات.
3. استخدم التقسيم الرسمي train/test في UNSW-NB15 عند تقييم ذلك التقسيم، ولا تعِد خلطه عشوائيًا ثم تدّعي أنه اختبار مستقل.
4. في CIC datasets استخدم تقسيمًا زمنيًا/حسب اليوم أو حسب الجلسة متى أمكن، بعد مراجعة التكرارات وتسرب التدفقات.
5. لا تجعل IP أو timestamp أو Flow ID أو أعمدة مشتقة من التسمية خصائص تدريب.
6. اعرض Macro-F1 وper-class precision/recall وconfusion matrix بجانب Accuracy؛ راجع false negatives خصوصًا.
7. Isolation Forest غير مراقب؛ لا تعرض anomaly score كأنه احتمال هجوم أو Accuracy.
8. لا تدّعِ التعميم بين المصادر إلا بعد اختبار نموذج على مصدر مستقل بخصائص متوافقة دون إعادة تدريبه على ذلك المصدر.
9. احفظ إصدار المكتبات، seed، عدد الصفوف، توزيع الفئات، أسماء الأعمدة، تاريخ التنزيل، الترخيص، SHA-256، وأي عمليات تنظيف.

## تشغيل benchmark مستقل لكل مصدر

بعد تنزيل ملفات CSV المسموح استخدامها ووضعها في `data/raw/`:

```powershell
python tools/benchmark_datasets.py `
  --dataset CIC2017=data/raw/cic2017.csv:Label `
  --dataset UNSW_NB15=data/raw/UNSW_NB15_training-set.csv:attack_cat `
  --max-rows 250000
```

- كل Dataset يُدرّب في مجلد مستقل تحت `models/<NAME>/`.
- `--max-rows 0` يقرأ كل الصفوف وقد يحتاج RAM كبيرًا.
- يخرج تقريرًا موحدًا في `reports/dataset_benchmark.json` يتضمن بصمة SHA-256 ونتائج كل تجربة.
- إذا استخدمت UNSW `label` بدل `attack_cat` فهذه تجربة binary (normal/attack)، أما `attack_cat` فهي متعددة الفئات؛ اذكر الاختيار بوضوح.

## حدود النسخة الحالية

لم تُضمّن ملفات datasets الضخمة أو نماذج مدرّبة في المستودع. لا توجد بيانات بحثية أصلية مرفقة في مجلد المشروع الحالي؛ ملفات CSV الصغيرة الموجودة أمثلة/اختبارات فقط ولا تصلح لادعاء أداء تنافسي. لذلك يجب تنفيذ التنزيل والتدريب الفعلي قبل عرض أي نتائج على لجنة التحكيم.
