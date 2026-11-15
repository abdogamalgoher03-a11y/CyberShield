"""All dashboard-facing display strings in one place (English + Arabic).

Design rules:
- Display-only. Nothing here changes detection rules, schemas, severities or
  pipeline output; pipeline fields remain visible verbatim for transparency.
- English strings reproduce the original dashboard text character-for-character
  so the existing behaviour and tests stay identical in English mode.
- Arabic is a faithful presentation layer: rule templates never invent data,
  they reference the finding's own evidence and technical identifiers.
"""

from __future__ import annotations

import re
from typing import Mapping

ARABIC_RATIO_THRESHOLD = 0.15

_ARABIC_CHAR = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")

# The project's severity scale only defines HIGH / MEDIUM / LOW (schemas.py
# SEVERITY_RANK). There is no CRITICAL or INFO level in this project, so those
# Arabic names are deliberately not listed as supported values.
SEVERITY_AR: dict[str, str] = {
    "HIGH": "مرتفعة",
    "MEDIUM": "متوسطة",
    "LOW": "منخفضة",
}

RISK_AR: dict[str, str] = {
    "LOW": "منخفض",
    "MEDIUM": "متوسط",
    "HIGH": "مرتفع",
}

AI_STATUS_AR: dict[str, str] = {
    "disabled": "معطّل",
    "ok": "مكتمل",
    "unavailable": "غير متاح",
    "invalid_output": "مخرجات غير صحيحة",
}

EVIDENCE_KIND_AR: dict[str, str] = {
    "event_count": "عدد الأحداث",
    "time_window": "النطاق الزمني",
    "indicator_match": "مطابقة مؤشر تهديد",
    "port_match": "منفذ غير معتاد",
    "username_match": "مطابقة مستخدم",
}

RISK_REASON_AR: dict[str, str] = {
    "No findings were present.": "لا توجد نتائج مكتشفة.",
    "Only LOW-severity findings are present.": "توجد نتائج منخفضة الخطورة فقط.",
    (
        "At least one MEDIUM-severity finding is present "
        "and no HIGH-severity finding is present."
    ): "توجد نتيجة واحدة على الأقل بخطورة متوسطة، ولا توجد نتائج مرتفعة الخطورة.",
    "At least one HIGH-severity finding is present.": "توجد نتيجة واحدة على الأقل بخطورة مرتفعة.",
}

LIMITATION_AR: dict[str, str] = {
    "Findings are indicators requiring investigation, not proof of compromise.": (
        "النتائج مؤشرات تستدعي الاستقصاء، وليست إثباتًا لاختراق."
    ),
    "The analysis is rule-based and limited to the supplied records.": (
        "التحليل يعمل بقواعد محددة مسبقًا ويقتصر على السجلات المُقدَّمة."
    ),
    "No automatic remediation is performed.": "لا يُنفَّذ أي إجراء إصلاح تلقائي.",
}

DISCLAIMER_EN = (
    "Findings are investigation indicators, not proof of compromise. Analysis is rule-based, "
    "limited to the supplied records, and uses a synthetic demo threat list. "
    "No automatic remediation is performed; every recommendation needs human approval."
)

DISCLAIMER_AR = (
    "النتائج مؤشرات للاستقصاء وليست إثباتًا لاختراق. التحليل يعمل بقواعد محددة مسبقًا، "
    "ويقتصر على السجلات المُقدَّمة، ويستخدم قائمة تهديدات تجريبية. "
    "لا يُنفَّذ أي إصلاح تلقائي؛ وكل توصية تحتاج موافقة بشرية."
)

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "app_tagline": "Defensive, educational log analysis. " + DISCLAIMER_EN,
        "input_header": "Input",
        "data_source": "Data source",
        "demo_data": "Demo data",
        "upload_csv": "Upload CSV/JSON",
        "upload_caption": "Events file (authorized data only)",
        "rules_header": "Rules",
        "failed_login_threshold": "Failed-login threshold",
        "window_minutes": "Window (minutes)",
        "unusual_ports": "Unusual ports (comma separated)",
        "unknown_outcome": "Count logins with unknown outcome",
        "unknown_outcome_help": "For logs that record a login attempt but not success/failure.",
        "run_analysis": "Run analysis",
        "initial_info": "Pick a data source in the sidebar and press **Run analysis**.",
        "choose_file_warning": "Choose a file first.",
        "error_report_validation": "Report validation failed:",
        "error_run_prefix": "Could not run analysis:",
        "error_invalid_ports": "Invalid ports",
        "error_agent_failed": "Agent '{name}' failed: {message}",
        "metric_overall_risk": "Overall risk",
        "metric_findings": "Findings",
        "metric_events_accepted": "Events accepted",
        "metric_records_rejected": "Records rejected",
        "metric_ai_summary": "AI summary",
        "severity_summary": "Severity summary",
        "findings_header": "Findings",
        "filter_severity": "Severity",
        "filter_agent": "Agent",
        "filter_search": "Search title / description",
        "no_findings_at_all": "No findings for this input.",
        "no_findings_matching": "No findings match the current filters.",
        "ai_section": "AI summary (optional)",
        "ai_mode": "AI mode",
        "ai_disabled": "Disabled",
        "ai_local": "Local (Ollama)",
        "ai_model_caption": "Ollama model",
        "ai_lang_caption": "Language",
        "ai_caption": "Off by default. Only counts and rule IDs are sent, to a local server only.",
        "ai_panel_header": "AI summary",
        "ai_status_caption": "Status: ",
        "ai_status_local": "local (Ollama)",
        "ai_status_disabled": "disabled",
        "generate_button": "Generate AI summary",
        "ai_off_info": "AI mode is off. The analysis above is fully rule-based and complete without it.",
        "ai_unavailable_warning": (
            "AI summary {status_words}: {reason}. The rule-based report is unaffected."
        ),
        "ai_not_arabic_warning": (
            "The requested summary language was Arabic, but the local model replied in a "
            "non-Arabic script. The model output is shown as returned and the issue is logged. "
            "The rule-based report is unaffected."
        ),
        "download_button": "Download JSON report",
        "limitations_header": "Report limitations",
        "glossary_header": "Glossary (beginner terms)",
        "technical_details_header": "Technical details (original pipeline text)",
        "rule_unknown_note": (
            "No Arabic explainer is defined for this rule; the original technical text is shown for accuracy."
        ),
        "suspicion_note": "Suspicion, not a confirmed breach: human verification is required.",
        "q_what": "What did the system detect?",
        "q_why": "Why was this finding raised?",
        "q_evidence": "What is the evidence in the logs?",
        "q_meaning": "What could that mean?",
        "q_step": "What is the suggested next step?",
        "q_recommendation": "System recommendation",
        "q_response_plan": "Response plan (human approval required)",
        "q_finding_meta": "rule: `{rule_id}` · agent: `{agent}` · id: `{finding_id}`",
        "ai_generated_header": "AI-generated explanation",
        "ai_notice_text": (
            "This text was generated by an AI model from a minimal summary of the report. It may be "
            "incomplete or wrong. The findings, evidence and severities above are the authoritative "
            "result. Findings are investigation indicators, not proof of compromise."
        ),
        "glossary_note": "English: {term}",
    },
    "ar": {
        "app_tagline": "تحليل سجلات دفاعي وتعليمي. " + DISCLAIMER_AR,
        "input_header": "البيانات",
        "data_source": "مصدر البيانات",
        "demo_data": "بيانات تجريبية",
        "upload_csv": "رفع ملف CSV/JSON",
        "upload_caption": "ملف السجلات (بيانات مصرّح بها فقط)",
        "rules_header": "قواعد الكشف",
        "failed_login_threshold": "حد الدخولات الفاشلة",
        "window_minutes": "النافذة الزمنية (بالدقائق)",
        "unusual_ports": "المنافذ غير المعتادة (افصلها بفاصلة)",
        "unknown_outcome": "عدّ محاولات الدخول ذات النتيجة غير المعروفة",
        "unknown_outcome_help": "للبيانات التي تظهر محاولة دخول دون بيان نجاحها أو فشلها.",
        "run_analysis": "تشغيل التحليل",
        "initial_info": "اختر مصدر البيانات من الشريط الجانبي واضغط **تشغيل التحليل**.",
        "choose_file_warning": "اختر ملفًا أولًا.",
        "error_report_validation": "فشل التحقق من صحة التقرير:",
        "error_run_prefix": "تعذّر تنفيذ التحليل:",
        "error_invalid_ports": "خطأ في المنافذ المُدخلة",
        "error_agent_failed": "فشل العامل «{name}»: {message}",
        "metric_overall_risk": "مستوى الخطر الكلي",
        "metric_findings": "عدد النتائج",
        "metric_events_accepted": "السجلات المقبولة",
        "metric_records_rejected": "السجلات المرفوضة",
        "metric_ai_summary": "ملخص الذكاء الاصطناعي",
        "severity_summary": "ملخص الخطورة",
        "findings_header": "النتائج المكتشفة",
        "filter_severity": "الخطورة",
        "filter_agent": "العامل",
        "filter_search": "بحث في العنوان/الوصف",
        "no_findings_at_all": "لا توجد نتائج لهذه البيانات.",
        "no_findings_matching": "لا توجد نتائج مطابقة للتصفية الحالية.",
        "ai_section": "ملخص الذكاء الاصطناعي (اختياري)",
        "ai_mode": "وضع الذكاء الاصطناعي",
        "ai_disabled": "معطّل",
        "ai_local": "محلي (Ollama)",
        "ai_model_caption": "نموذج Ollama",
        "ai_lang_caption": "لغة الملخص",
        "ai_caption": "معطّل افتراضيًا. تُرسَل الأعداد ومعرّفات القواعد فقط، وإلى خادم محلي فقط.",
        "ai_panel_header": "ملخص الذكاء الاصطناعي",
        "ai_status_caption": "الحالة: ",
        "ai_status_local": "محلي (Ollama)",
        "ai_status_disabled": "معطّل",
        "generate_button": "توليد الملخص بالذكاء الاصطناعي",
        "ai_off_info": "وضع الذكاء الاصطناعي معطّل. التحليل أعلاه مكتمل بدونه وهو تحليل قواعدي.",
        "ai_unavailable_warning": (
            "الملخص بالذكاء الاصطناعي {status_words}: {reason}. التقرير القائم على القواعد لم يُتأثر."
        ),
        "ai_not_arabic_warning": (
            "طلبتَ ملخصًا بالعربية، لكن النموذج المحلي أجاب بلغة غير عربية؛ النص يُعرض كما أُرجع والمشكلة مُسجّلة. "
            "تحليل القواعد أعلاه لم يُتأثر."
        ),
        "download_button": "تنزيل تقرير JSON",
        "limitations_header": "قيود التقرير",
        "glossary_header": "شرح المصطلحات (للمبتدئين)",
        "technical_details_header": "التفاصيل التقنية الأصلية من خط التحليل",
        "rule_unknown_note": (
            "لا يوجد شرح عربي مخصّص لهذه القاعدة؛ النص التقني الأصلي معروض حفاظًا على الدقة."
        ),
        "suspicion_note": "الاشتباه ≠ اختراق مؤكد: يُشترط تحقق بشري قبل أي حكم.",
        "q_what": "ماذا اكتشف النظام؟",
        "q_why": "لماذا أُطلق هذا التنبيه؟",
        "q_evidence": "ما الدليل الموجود في السجلات؟",
        "q_meaning": "ماذا قد يعني ذلك؟",
        "q_step": "ما الخطوة المقترحة للتحقق أو المعالجة؟",
        "q_recommendation": "توصية النظام:",
        "q_response_plan": "خطة الاستجابة (تتطلب موافقة بشرية)",
        "q_finding_meta": "rule: `{rule_id}` · agent: `{agent}` · id: `{finding_id}`",
        "ai_generated_header": "شرح مُولَّد بالذكاء الاصطناعي",
        "ai_notice_text": (
            "نصٌ أُنشئ بواسطة نموذج ذكاء اصطناعي اعتمادًا على ملخص مصغّر من التقرير، وقد يكون ناقصًا "
            "أو خاطئًا. النتائج والأدلة ومستويات الخطورة أعلاه هي النتيجة المرجعية. النتائج مؤشرات "
            "استقصاء وليست إثباتًا لاختراق."
        ),
        "glossary_note": "English: {term}",
    },
}


def t(lang: str, key: str, **kwargs: object) -> str:
    """Fetch one display string by key, with '{field}' formatting."""
    template = STRINGS.get(lang, {}).get(key) or STRINGS["en"].get(key) or key
    if kwargs:
        return template.format(**kwargs)
    return template


def arabic_script_ratio(text: str) -> float:
    """Fraction of Arabic-script letters among all letters in ``text``."""
    if not text:
        return 0.0
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return 0.0
    arabic_letters = sum(1 for ch in letters if _ARABIC_CHAR.fullmatch(ch))
    return arabic_letters / len(letters)


def translate_risk_reason(reason: object, lang: str) -> str:
    """Map a known pipeline risk-reason string; unknowns stay untouched."""
    if lang == "ar":
        return RISK_REASON_AR.get(str(reason), str(reason))
    return str(reason)


def translate_limitation(item: object, lang: str) -> str:
    if lang == "ar":
        return LIMITATION_AR.get(str(item), str(item))
    return str(item)


def _render_evidence(view: Mapping[str, object]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in view.get("evidence") or ():
        kind = str(item.get("kind", ""))
        rows.append(
            {
                "kind_label": EVIDENCE_KIND_AR.get(kind, kind),
                "kind": kind,
                "value": str(item.get("value", "")),
                "description": str(item.get("description", "")),
            }
        )
    return rows


_UNKNOWN_RULE = {
    "name": None,  # falls back to the pipeline title
    "what": "وجد محرك القواعد نمطًا يستحق الانتباه في السجلات (الأدلة الدقيقة أدناه).",
    "why": "قاعدة كشف تعمل تلقائيًا على الأعداد والمؤشرات؛ لا توجد صياغة مخصّصة لهذه القاعدة بعد.",
    "meaning": "يستحق المراجعة البشرية؛ لا حكم بدون تحقق.",
    "step": "راجع الأدلة والنص التقني الأصلي أدناه مع مالك النظام.",
}

_RULE_EXPLAINERS: dict[str, dict[str, str | None]] = {
    "AUTH-REPEATED-FAILURES": {
        "name": "تكرار عمليات تسجيل دخول فاشلة من المصدر نفسه",
        "what": "رصد قاعدة الكشف عددًا متكررًا من محاولات الدخول الفاشلة من عنوان واحد داخل نافذة زمنية محددة؛ الأعداد الدقيقة في الدليل أدناه.",
        "why": "ينطلق التنبيه عند تجاوز عدد الفشل حدّ الإعداد (قد يعني تخمين كلمة مرور، أو خطأ تكوين أداة، أو مستخدمًا نسي كلمة مرور؛ القاعدة تنظر إلى العدد لا إلى النية).",
        "meaning": "مؤشر يستحق مراجعة سجلات المصادقة لهذا العنوان؛ وجوده وحده لا يعني اختراقًا.",
        "step": "راجع سجلات المصادقة المرتبطة بالعنوان داخل النافذة الزمنية، وتأكد مع مالك النظام إن كان النشاط متوقعًا (تشغيل آلي أو مشكلة كلمة مرور) قبل أي إجراء.",
    },
    "NET-UNUSUAL-PORT": {
        "name": "اتصال بمنفذ مدرج في قائمة «المنافذ غير المعتادة»",
        "what": "ظهر اتصال شبكي نحو منفذ مدرج في القائمة المُعدّة مسبقًا؛ قيمة المنفذ ودليلها أدناه.",
        "why": "بعض البرمجيات الخبيثة تستخدم منافذ نادرة للاتصال بخادم قيادة وتحكم (C2)، لكن أدوات الإدارة والمطوّرين أيضًا يختارون منافذ غير تقليدية.",
        "meaning": "قيمة المنفذ وحدها لا تفسّر النشاط؛ يلزم معرفة الخدمة والمضيفَيْن للحكم.",
        "step": "تحقق من الخدمة العاملة على المنفذ نفسه لدى مالك النظام، وراجع قواعد جدار الحماية وسجلات الأحداث المجاورة قبل الحكم.",
    },
    "THREAT-INTEL-DEMO-MATCH": {
        "name": "مطابقة مؤشر مدرج في قائمة التهديدات المحلية",
        "what": "تواصل أحد الأجهزة مع مؤشر مدرج مسبقًا في قائمة مؤشرات التهديد المدمجة (قائمة تجريبية للتدريب)؛ التفاصيل في الدليل.",
        "why": "الاتصال بمؤشر بسمة معروفة (مثل خادم C2) يرفع الانتباه؛ والتصنيف مضبوط في الدليل.",
        "meaning": "القائمة هنا تجريبية، فالتنبيه للتدريب؛ أما قائمة تهديد حقيقية فتتطلب تحققًا مرجعيًا إضافيًا.",
        "step": "راجع أحداث الاتصال بالمؤشر وحدّد النظام الداخلي المعني، ثم شارك النتيجة مع المسؤول الأمني مع توضيح القيود أعلاه.",
    },
}


def finding_explainer(view: Mapping[str, object], lang: str) -> dict[str, object] | None:
    """Beginner-grade Arabic explanation built ONLY from the finding's data.

    Never invents counts, addresses or ports: the raw evidence values are listed
    verbatim, and the Arabic narrative references them without repeating them.
    Returns None for English (the pipeline text is already English).
    """
    if lang != "ar":
        return None

    rule_id = str(view.get("rule_id", ""))
    rule = _RULE_EXPLAINERS.get(rule_id, _UNKNOWN_RULE)

    return {
        "rule_id": rule_id,
        "agent": str(view.get("agent", "")),
        "severity_ar": SEVERITY_AR.get(str(view.get("severity", "")), str(view.get("severity", ""))),
        "name": rule["name"] or str(view.get("title", "")),
        "what": str(rule["what"]),
        "why": str(rule["why"]),
        "meaning": str(rule["meaning"]),
        "step": str(rule["step"]),
        "recommendation": str(view.get("recommendation", "")),
        "evidence": _render_evidence(view),
        "suspicion_note": t("ar", "suspicion_note"),
        "unknown_rule_note": None if rule_id in _RULE_EXPLAINERS else t("ar", "rule_unknown_note"),
    }


_GLOSSARY: tuple[dict[str, str], ...] = (
    {
        "term_ar": "عنوان IP",
        "term_en": "IP Address",
        "definition_ar": "رقم يُعرِّف جهازًا على الشبكة (مثل 192.0.2.50). يخبرك بمن تواصل مع مَن؛ ولا يخبرك وحده بما فعله المستخدم داخل الشبكة.",
        "definition": "A number identifying a device on a network (e.g. 192.0.2.50). It tells you who talked to whom - it never tells you what somebody did, on its own.",
    },
    {
        "term_ar": "منفذ (Port)",
        "term_en": "Port",
        "definition_ar": "باب فرعي لعنوان IP يحدّد الخدمة المقصودة على الجهاز (80 = صفحة ويب، 443/8443 = https غالبًا الأنظمة).",
        "definition": "A service door on a device: e.g. 80 = web page, 443/8443 = usually https.",
    },
    {
        "term_ar": "سير قيادة وتحكم (C2)",
        "term_en": "C2 Command-and-Control",
        "definition_ar": "خادم خارجي تُبلِّغ له برمجية خبيثة وتتلقى منه أوامرها؛ ملاحظة اتصال به يُعد مؤشرًا مهمًا لكنه ليس دليلًا قاطعًا وحده.",
        "definition": "An outside server that malware reports to and takes orders from; seeing contact with one is a strong indicator, not proof on its own.",
    },
    {
        "term_ar": "تسجيل دخول فاشل",
        "term_en": "Failed Login",
        "definition_ar": "محاولة دخول رُفضت: كلمة مرور خاطئة، أو خطأ في إعداد أداة، أو مستخدم نسي كلمة مروره؛ التكرار المتتالي هو ما يلفت انتباه القاعدة.",
        "definition": "A login attempt that was rejected: wrong password, a misconfigured tool, or a forgotten password - the repetition is what matters.",
    },
    {
        "term_ar": "تنبيه / نتيجة (Finding)",
        "term_en": "Finding",
        "definition_ar": "نمط لفت انتباه محرك القواعد في السجلات؛ وهو اشتباه يستحق الاستقصاء، وليس حكمًا نهائيًا بالاختراق.",
        "definition": "A pattern the rule engine noticed in the logs; it's a suspicion to investigate, not a verdict.",
    },
    {
        "term_ar": "مستوى الخطورة",
        "term_en": "Severity",
        "definition_ar": "تقدير أولوية الانتباه: مرتفعة، متوسطة، منخفضة. المشروع لا يستخدم مستويات «حريج» أو «معلوماتي».",
        "definition": "Attention priority: HIGH, MEDIUM, LOW. This project has no CRITICAL or INFO levels.",
    },
    {
        "term_ar": "خطة الاستجابة",
        "term_en": "Response Plan",
        "definition_ar": "خطوات مراجعة أو معالجة مقترحة؛ كلها تنتظر موافقة بشرية، ولا شيء يُنفَّذ تلقائيًا.",
        "definition": "Suggested review or handling steps; all of them wait for human approval, nothing runs automatically.",
    },
)


def glossary(lang: str) -> tuple[dict[str, str], ...]:
    """Glossary entries: (display_term, english_term, definition)."""
    return tuple(
        {
            "term": entry["term_ar"] if lang == "ar" else entry["term_en"],
            "term_en": entry["term_en"],
            "definition": entry["definition_ar"] if lang == "ar" else entry["definition"],
        }
        for entry in _GLOSSARY
    )


LAYOUT_CSS = """<style>/* cybershield-layout */
/* Long metric labels/values wrap instead of being clipped in narrow windows. */
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
  white-space: normal;
  overflow: visible;
  text-overflow: clip;
  overflow-wrap: anywhere;
}
/* Selected multiselect chips wrap inside the control in both languages. */
[data-testid="stMultiSelect"] [data-testid="stMultiSelectTagsContainer"] {
  flex-wrap: wrap;
  overflow-x: hidden;
  overflow-y: visible;
  height: auto;
  max-height: none;
  min-height: 2rem;
  row-gap: 0.25rem;
}
[data-testid="stMultiSelect"] > div > [role="group"] {
  height: auto;
  max-height: none;
  min-height: 2.5rem;
}
[data-testid="stMultiSelect"] [data-tag] {max-width: 100%;}
[data-testid="stMultiSelect"] [data-tag] span {
  white-space: normal;
  overflow-wrap: anywhere;
}
/* Expander headers can shrink and wrap instead of overflowing. */
[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] {
  flex: 1 1 auto;
  min-width: 0;
}
[data-testid="stExpander"] summary p {overflow-wrap: anywhere;}
[data-testid="stMetricValue"] {font-variant-numeric: tabular-nums;}
</style>"""

RTL_CSS = """<style>/* cybershield-rtl */
/* RTL is applied to text blocks only. Flipping Streamlit's layout containers
   reverses flex order inside widgets and clips multiselect chips. */
[data-testid="stMain"] p,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] li,
[data-testid="stMain"] summary p,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
  direction: rtl;
  text-align: right;
  unicode-bidi: plaintext;
}
/* Embedded English identifiers keep their own LTR order inside Arabic text. */
[data-testid="stMain"] code,
[data-testid="stMain"] kbd,
[data-testid="stMain"] samp,
[data-testid="stMain"] [data-testid="stCode"] {
  direction: ltr;
  unicode-bidi: isolate;
}
/* Keep widget internals in Streamlit's native LTR layout; labels stay RTL. */
[data-testid="stMultiSelect"],
[data-testid="stSelectbox"],
[data-testid="stTextInput"],
[data-testid="stNumberInput"],
[data-testid="stFileUploader"] {
  direction: ltr;
}
[data-testid="stMultiSelect"] [data-tag] span {unicode-bidi: plaintext;}
/* Expander headers: text right-aligned, chevron keeps its normal flex slot. */
[data-testid="stExpander"] summary p {
  direction: rtl;
  text-align: right;
  unicode-bidi: plaintext;
}
/* Never override icon fonts: doing so renders ligature names such as
   "keyboard_arrow_right" as visible text on top of the label. */
[data-testid="stIconMaterial"] {
  font-family: "Material Symbols Rounded" !important;
}
/* Arabic-friendly font for prose only, not for every descendant. */
[data-testid="stMain"] p,
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] li,
[data-testid="stMain"] summary,
[data-testid="stMain"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] label {
  font-family: "Segoe UI", "Tahoma", system-ui, sans-serif;
}
</style>"""
