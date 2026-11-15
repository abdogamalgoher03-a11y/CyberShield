# Agent 5 — Incident Response Agent (Handoff لـ Agent 6)

## هيكل الملفات (حطوها بنفس المسارات في المشروع)
```
cybershield/agents/incident_response.py   <- كود الـ Agent
tests/test_incident_response.py           <- 24 اختبار (+ اختبار تكامل مع Agent 4 / build_report)
data/demo_findings.json                   <- Findings تجريبية للديمو
demo_agent5.py                            <- سكريبت الديمو (يحفظ cybershield_response_plan.json)
```

## وظيفة الـ Agent
بياخد الـ Findings ويطلع **توصيات تحقيق** (مش تنفيذ) مربوطة بـ `finding_id`:
- الخطوات بتتغير حسب الخطورة: HIGH (مراجعة في نفس اليوم + حفظ الأدلة + تصعيد) / MEDIUM (خلال يوم عمل) / LOW (مراجعة روتينية).
- خطوات إضافية حسب الـ agent: `threat_intelligence` / `network` / `log_analyzer`.
- أي توصية فيها إجراء احتواء بتكون "اطلب موافقة" فقط، ومفيش حظر أو عزل تلقائي.
- كل عنصر `requires_human_approval = True`.

## الاستدعاء (للـ Manager)
```python
from cybershield.agents.incident_response import build_response_plan

# لو الـ Findings لسه فيها finding-000 وهتتعين IDs داخل build_report (زي اختبار Agent 4):
plan = build_response_plan(findings, assume_order_ids=True)
report = build_report(load_result=load_res, findings=findings, response_plan=plan)

# لو الـ Findings عندها IDs نهائية:
plan = build_response_plan(report_findings)
```
- `include_details=True` بيضيف `severity, agent, rule_id, steps` للعنصر (للـ Dashboard مثلًا). الافتراضي: 4 مفاتيح بس.

## شكل المخرجات (response_plan item)
| الحقل | القيمة |
|---|---|
| related_finding_id | `finding-001` ... |
| action | نص بالخطوات المرقمة |
| rationale | سبب + "not proof of compromise" + إشعار عدم التنفيذ التلقائي |
| requires_human_approval | `True` |

## الأخطاء (`IncidentResponseError.code`)
missing_finding_id, unassigned_finding_id, invalid_finding_id, duplicate_finding_id, invalid_severity

## افتراضات Agent 6 (اتأكدوا في `tests/test_manager_pipeline.py`) ✅
0. الـ Manager بيدّي الـ IDs النهائية قبل ما يستدعي الـ Agent، فمفيش اعتماد على `assume_order_ids`، وبيتأكد إن الـ plan مربوط بنفس IDs التقرير.
1. **ترتيب الـ IDs:** `assume_order_ids=True` بيفترض إن `build_report` بيرقّم الـ Findings بنفس ترتيب الإدخال (finding-001, 002...). لو بيرتبهم تاني (مثلًا حسب الخطورة) استخدموا الـ IDs بعد الـ build.
2. **شكل `response_plan`:** مبني على اللي ظهر في اختبار Agent 4. لو `schemas.py` فيه حقول إضافية إجبارية أو بيمنع حقول زيادة، يتعدل `to_dict`.
3. **عدد العناصر لكل Finding:** حاليًا عنصر واحد لكل Finding (الخطوات داخل `action`).
4. اسم الـ agent في الـ schema هو `network_agent`؛ الـ Agent بيقبل `network` و`network_agent` الاتنين.
5. الـ Agent بيقبل dict أو object (زي Finding) بدون ما يستورد `schemas.py`.

## التشغيل
```
pytest tests/test_incident_response.py
python demo_agent5.py
```
