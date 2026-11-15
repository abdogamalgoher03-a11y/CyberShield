"""CyberShield AI dashboard (Streamlit).

Run with:  streamlit run app.py

Uses the same pipeline as main.py (Manager Agent). Everything is rule-based and
local: no AI service, no network calls, no automatic remediation.
Findings are investigation indicators, not proof of compromise.

UI language: English (default) / Arabic with RTL layout. All display strings
live in ``translations.py``; switching language re-renders only the interface -
it never re-runs the analysis or changes pipeline results.

Language-switch safety: widgets that hold a value across reruns use stable
(internal, English) option values, and the visible labels are localized via
``format_func``. This keeps any stored session value inside the options list,
so switching to Arabic can never make a widget crash on stale values, and keyed
inputs keep the user's data while the language flips.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:  # charts degrade gracefully if the optional plotting package is absent
    px = go = None

from cybershield.agents.manager import ManagerRun, build_manager
from cybershield.agents.network_agent import DEFAULT_UNUSUAL_PORTS
from cybershield.ai.summarizer import AiSummaryResult, OllamaProvider, OpenAIProvider, summarize
from cybershield.reporting import report_to_json
from cybershield.schemas import FindingValidationError, ReportValidationError
from cybershield.ml.pipeline import MLTrainingError, model_status, predict_csv, train_models

from translations import (
    AI_STATUS_AR,
    ARABIC_RATIO_THRESHOLD,
    LAYOUT_CSS,
    RISK_AR,
    RTL_CSS,
    SEVERITY_AR,
    STRINGS,
    arabic_script_ratio,
    finding_explainer,
    glossary,
    t,
    translate_limitation,
    translate_risk_reason,
)

logger = logging.getLogger("cybershield.dashboard")

ROOT = Path(__file__).resolve().parent
DEMO_FILE = ROOT / "data" / "demo_full_pipeline.csv"
SEVERITIES = ["HIGH", "MEDIUM", "LOW"]

# Stable internal widget values (never rendered, only compared/stored).
_EN_STRINGS = STRINGS["en"]
SOURCE_DEMO = _EN_STRINGS["demo_data"]
SOURCE_UPLOAD = _EN_STRINGS["upload_csv"]
AI_DISABLED_VALUE = _EN_STRINGS["ai_disabled"]
AI_LOCAL_VALUE = _EN_STRINGS["ai_local"]
AI_API_VALUE = "Hosted API (OpenAI)"

AI_LANG_AR = "العربية"


def parse_ports(text: str) -> list[int]:
    """Parse '4444, 1337' into ports; raises ValueError with a readable message."""
    ports: list[int] = []
    for part in text.replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        if not part.isdigit() or not 1 <= int(part) <= 65535:
            raise ValueError(f"Invalid port: {part!r} (must be 1-65535)")
        ports.append(int(part))
    return ports


def run_analysis(
    path: Path,
    threshold: int,
    window_minutes: int,
    ports: list[int],
    count_unknown_status: bool = False,
) -> ManagerRun:
    return build_manager(
        threshold=threshold,
        window_minutes=window_minutes,
        unusual_ports=ports,
        count_unknown_status=count_unknown_status,
    ).run_file(path)


def run_uploaded(
    uploaded,
    threshold: int,
    window_minutes: int,
    ports: list[int],
    count_unknown_status: bool = False,
) -> ManagerRun:
    suffix = Path(uploaded.name).suffix.lower()
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / f"upload{suffix}"
        target.write_bytes(uploaded.getvalue())
        run = run_analysis(target, threshold, window_minutes, ports, count_unknown_status)
    return run


def _finding_view(finding) -> dict[str, object]:
    """Plain-dict view of one pipeline Finding for the (display-only) explainer."""
    return {
        "agent": finding.agent,
        "rule_id": finding.rule_id,
        "severity": finding.severity,
        "title": finding.title,
        "description": finding.description,
        "recommendation": finding.recommendation,
        "evidence": [
            {"kind": e.kind, "value": e.value, "description": e.description}
            for e in finding.evidence
        ],
    }


def _log_language_issue(summary_lang: str, ratio: float, provider: str) -> None:
    """Record the Arabic-language mismatch: stderr log + gitignored run file."""
    message = (
        "AI summary language mismatch: requested '%s', Arabic script ratio %.2f < %.2f, provider %s"
        % (summary_lang, ratio, ARABIC_RATIO_THRESHOLD, provider)
    )
    logger.warning(message)
    try:
        log_path = ROOT / ".tmp" / "ai_language_issues.log"
        log_path.parent.mkdir(exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(message + "\n")
    except OSError:
        pass


def main() -> None:
    st.set_page_config(page_title="CyberShield AI", page_icon="🛡️", layout="wide")
    # Visible at the very top of the dashboard (main area, not the sidebar) so
    # the language switch can always be found without opening any panel.
    ui_choice = st.radio(
        "اللغة / Language",
        ["English", AI_LANG_AR],
        key="ui_lang",
        horizontal=True,
    )
    lang = "ar" if ui_choice == AI_LANG_AR else "en"
    T = lambda key, **kw: t(lang, key, **kw)  # noqa: E731 - one-call display helper

    # Layout fixes are language-independent; RTL/bidi rules are Arabic-only.
    st.markdown(LAYOUT_CSS, unsafe_allow_html=True)
    if lang == "ar":
        st.markdown(RTL_CSS, unsafe_allow_html=True)

    st.title("🛡️ CyberShield AI")
    st.caption(T("app_tagline"))
    st.markdown("""<style>
    .stApp {background:linear-gradient(135deg,#07111f 0%,#0b1727 55%,#0c1c2d 100%);color:#e8f0fb}
    [data-testid="stMetric"] {background:#102238;border:1px solid #203b54;padding:14px;border-radius:10px}
    [data-testid="stSidebar"] {background:#081321}
    div[data-testid="stExpander"] {border:1px solid #203b54;border-radius:10px}
    </style><div style="padding:12px 16px;border:1px solid #21445d;border-radius:10px;
    background:linear-gradient(90deg,#10283e,#0d1c2d);margin:8px 0 18px 0">
    <span style="color:#58d9e8;font-family:monospace;letter-spacing:2px;font-size:11px">SECURITY OPERATIONS CENTER / LIVE WORKSPACE</span>
    <h2 style="margin:6px 0 2px 0;color:#edf7ff">CYBERSHIELD AI <span style="color:#58d9e8">//</span> Threat Intelligence</h2>
    <span style="color:#8fa9c0;font-size:12px">Evidence-linked detections · Machine learning · Human-approved response</span></div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.header(T("input_header"))
        source_labels = {SOURCE_DEMO: T("demo_data"), SOURCE_UPLOAD: T("upload_csv")}
        source = st.radio(
            T("data_source"),
            [SOURCE_DEMO, SOURCE_UPLOAD],
            key="source",
            format_func=source_labels.__getitem__,
        )
        uploaded = None
        if source == SOURCE_UPLOAD:
            uploaded = st.file_uploader(T("upload_caption"), type=["csv", "json"], key="upload_file")

        st.header(T("rules_header"))
        threshold = st.number_input(T("failed_login_threshold"), min_value=2, value=5, step=1, key="threshold")
        window = st.number_input(T("window_minutes"), min_value=1, value=10, step=1, key="window")
        ports_text = st.text_input(
            T("unusual_ports"),
            value=", ".join(str(p) for p in sorted(DEFAULT_UNUSUAL_PORTS)),
            key="ports",
        )
        unknown = st.checkbox(
            T("unknown_outcome"),
            value=False,
            key="count_unknown",
            help=T("unknown_outcome_help"),
        )
        run_clicked = st.button(T("run_analysis"), type="primary", key="run_btn")

        st.header(T("ai_section"))
        ai_mode_labels = {AI_DISABLED_VALUE: T("ai_disabled"), AI_LOCAL_VALUE: T("ai_local"), AI_API_VALUE: AI_API_VALUE}
        ai_mode = st.radio(
            T("ai_mode"),
            [AI_DISABLED_VALUE, AI_LOCAL_VALUE, AI_API_VALUE],
            key="ai_mode",
            format_func=ai_mode_labels.__getitem__,
        )
        # The optional AI summary follows the UI language unless the user picked
        # one manually (tracked via on_change). Display-only override; the
        # rule-based report never depends on it.
        if not st.session_state.get("ai_lang_manual", False):
            st.session_state["ai_lang"] = AI_LANG_AR if lang == "ar" else "English"

        def _mark_ai_lang_manual() -> None:
            st.session_state["ai_lang_manual"] = True

        st.selectbox(
            T("ai_lang_caption"),
            ["English", AI_LANG_AR],
            key="ai_lang",
            disabled=ai_mode != AI_LOCAL_VALUE,
            on_change=_mark_ai_lang_manual,
        )
        st.text_input(
            T("ai_model_caption"),
            value="llama3.2",
            key="ai_model",
            disabled=ai_mode != AI_LOCAL_VALUE,
        )
        st.caption(T("ai_caption"))
        if ai_mode == AI_API_VALUE:
            st.warning("Hosted AI sends only aggregate counts and rule IDs, not raw IPs, usernames, hostnames or event records. Review your data/privacy requirements before enabling it.")

    if run_clicked:
        try:
            ports = parse_ports(ports_text)
            if source == SOURCE_UPLOAD:
                if uploaded is None:
                    st.warning(T("choose_file_warning"))
                    return
                st.session_state["run"] = run_uploaded(uploaded, int(threshold), int(window), ports, unknown)
                st.session_state.pop("ai_result", None)
            else:
                st.session_state["run"] = run_analysis(DEMO_FILE, int(threshold), int(window), ports, unknown)
                st.session_state.pop("ai_result", None)
        except (FindingValidationError, ReportValidationError) as exc:  # must precede ValueError
            st.error(f"{T('error_report_validation')} {exc}")
            return
        except ValueError as exc:  # includes LoadError and bad config
            if lang == "ar" and "Invalid port" in str(exc):
                st.error(f"{T('error_invalid_ports')} ({exc})")
            else:
                st.error(f"{T('error_run_prefix')} {exc}")
            return

    render_ml_lab(lang)

    run: ManagerRun | None = st.session_state.get("run")
    if run is None:
        st.info(T("initial_info"))
        return

    render(run, lang)


def render_ml_lab(lang: str) -> None:
    """Optional offline model-training workspace; labels stay inside the ML pipeline."""
    title = "مختبر تعلم الآلة" if lang == "ar" else "Machine Learning Lab"
    with st.expander("🧠 " + title, expanded=False):
        st.caption("Random Forest + XGBoost + Isolation Forest | Offline training on a labeled CSV")
        st.warning("Use a labeled, authorized flow dataset (for example CIC-IDS2017 MachineLearningCSV). Demo event files do not contain ground-truth labels and cannot train supervised models.")
        uploaded_ml = st.file_uploader("Upload labeled CSV (Label column required)", type=["csv"], key="ml_dataset_upload")
        label_col = st.text_input("Target / label column", value="Label", key="ml_label_column")
        max_rows = st.number_input("Maximum rows to load (0 = all; large files need sufficient RAM)", min_value=0, max_value=2000000, value=250000, step=25000, key="ml_max_rows")
        if st.button("Train / retrain ML models", type="primary", key="ml_train_button"):
            if uploaded_ml is None:
                st.error("Upload a labeled CSV first.")
            else:
                import tempfile
                from pathlib import Path
                try:
                    with tempfile.TemporaryDirectory(prefix="cybershield-ml-") as temp_dir:
                        dataset_path = Path(temp_dir) / "training.csv"
                        dataset_path.write_bytes(uploaded_ml.getvalue())
                        with st.spinner("Training Random Forest, XGBoost and Isolation Forest..."):
                            result = train_models(dataset_path, label_col, max_rows=(None if int(max_rows) == 0 else int(max_rows)))
                    st.session_state["ml_training_result"] = result
                    st.success("Training completed. Metrics are based on the held-out test split.")
                except (MLTrainingError, ValueError, OSError) as exc:
                    st.error(f"Training failed: {exc}")
                except Exception as exc:  # optional XGBoost/runtime compatibility errors
                    st.error(f"Training failed safely: {type(exc).__name__}: {exc}")
        status = model_status()
        if status["trained"]:
            st.success("Trained model artifact found: models/cybershield_ml.joblib")
        else:
            st.info("No trained model yet. Rule-based analysis continues to work without ML.")
        result = st.session_state.get("ml_training_result") or status.get("training_metrics")
        if status["trained"]:
            prediction_file = st.file_uploader("Optional: upload unlabeled numeric feature CSV for ML inference", type=["csv"], key="ml_prediction_upload")
            if prediction_file is not None and st.button("Run ML predictions", key="ml_predict_button"):
                try:
                    with tempfile.TemporaryDirectory(prefix="cybershield-predict-") as temp_dir:
                        prediction_path = Path(temp_dir) / "features.csv"
                        prediction_path.write_bytes(prediction_file.getvalue())
                        predictions = predict_csv(prediction_path)
                    st.session_state["ml_predictions"] = predictions
                    st.success(f"Generated {len(predictions)} model outputs.")
                except (MLTrainingError, ValueError, OSError) as exc:
                    st.error(f"Prediction failed: {exc}")
            if st.session_state.get("ml_predictions"):
                st.markdown("**Recent model predictions**")
                st.dataframe(st.session_state["ml_predictions"][:100], use_container_width=True, hide_index=True)
                st.download_button("Download ML predictions (JSON)",
                    data=__import__("json").dumps(st.session_state["ml_predictions"], indent=2),
                    file_name="cybershield_ml_predictions.json", mime="application/json", key="ml_predictions_download")
        if result:
            metrics = result.get("metrics", {})
            rf = metrics.get("random_forest", {})
            xgb = metrics.get("xgboost", {})
            cols = st.columns(4)
            cols[0].metric("RF Accuracy", f"{rf.get('accuracy', 0):.1%}" if rf else "—")
            cols[1].metric("RF F1 (weighted)", f"{rf.get('f1_weighted', 0):.1%}" if rf else "—")
            cols[2].metric("XGBoost", "Trained" if xgb.get("accuracy") is not None else xgb.get("status", "—"))
            cols[3].metric("Isolation Forest", metrics.get("isolation_forest", {}).get("status", "—"))
            st.caption(f"Dataset: {result.get('dataset', {}).get('file_name', 'saved training run')} · Features: {result.get('dataset', {}).get('feature_count', '—')} · Test rows: {result.get('dataset', {}).get('test_rows', '—')}")
            if result.get("top_features"):
                st.markdown("**Top Random Forest features**")
                st.bar_chart({row["feature"]: row["importance"] for row in result["top_features"][:12]})
            with st.expander("Training methodology and limitations"):
                st.json({"methodology": result.get("methodology"), "limitations": result.get("limitations")})


def generate_ai_summary(run: ManagerRun) -> AiSummaryResult:
    """Build the provider from the sidebar settings; any problem becomes a safe fallback result."""
    mode = st.session_state.get("ai_mode")
    if mode == AI_DISABLED_VALUE:
        return summarize(run.report)
    try:
        if mode == AI_API_VALUE:
            import os
            provider = OpenAIProvider(os.getenv("CYBERSHIELD_OPENAI_MODEL", "gpt-4.1-mini"))
        else:
            provider = OllamaProvider(str(st.session_state.get("ai_model", "")))
    except ValueError as exc:
        name = "hosted:openai" if mode == AI_API_VALUE else "local:ollama"
        return AiSummaryResult("unavailable", name, None, reason=str(exc))
    language = "ar" if st.session_state.get("ai_lang") == AI_LANG_AR else "en"
    return summarize(run.report, provider, provider_name=provider.name, language=language)


def render_ai_panel(run: ManagerRun, lang: str) -> None:
    T = lambda key, **kw: t(lang, key, **kw)  # noqa: E731
    st.subheader(T("ai_panel_header"))
    enabled = st.session_state.get("ai_mode") != AI_DISABLED_VALUE
    status_shown = T("ai_status_local") if enabled else T("ai_status_disabled")
    st.caption(T("ai_status_caption") + status_shown)
    summary_lang = ("ar" if st.session_state.get("ai_lang") == AI_LANG_AR else "en") if enabled else "en"
    if enabled and st.button(T("generate_button"), key="generate_btn"):
        st.session_state["ai_result"] = generate_ai_summary(run)
        st.session_state["ai_result_lang"] = summary_lang
    if not enabled:
        st.info(T("ai_off_info"))
        return
    result: AiSummaryResult | None = st.session_state.get("ai_result")
    if result is None:
        return
    if result.status == "ok" and result.content:
        st.markdown(f"**{T('ai_generated_header')}** ({result.provider})")
        st.write(result.content)
        requested = st.session_state.get("ai_result_lang", "en")
        ratio = arabic_script_ratio(result.content)
        if requested == "ar" and ratio < ARABIC_RATIO_THRESHOLD:
            st.warning(T("ai_not_arabic_warning"))
            _log_language_issue(requested, ratio, result.provider)
    else:
        status_words = (
            AI_STATUS_AR.get(result.status, result.status.replace("_", " "))
            if lang == "ar"
            else result.status.replace("_", " ")
        )
        st.warning(T("ai_unavailable_warning", status_words=status_words, reason=result.reason))
    st.caption(result.notice if lang == "en" else T("ai_notice_text"))


def _render_finding_technical(finding, plan) -> None:
    """Original pipeline text for a finding (unchanged, for transparency)."""
    st.write(finding.description)
    st.markdown(f"**Rule:** `{finding.rule_id}`  |  **Events:** {len(finding.event_ids)}")
    st.markdown("**Evidence**")
    for e in finding.evidence:
        st.markdown(f"- `{e.kind}` = **{e.value}** — {e.description}")
    st.markdown(f"**Recommendation:** {finding.recommendation}")
    if plan is not None:
        st.markdown("**Response plan (human approval required)**")
        st.write(plan.action)
    st.caption(" • ".join(finding.limitations))


def render(run: ManagerRun, lang: str) -> None:
    T = lambda key, **kw: t(lang, key, **kw)  # noqa: E731
    report = run.report
    summary = report.input_summary

    for name, message in run.agent_errors.items():
        st.error(T("error_agent_failed", name=name, message=message))

    risk_value = RISK_AR.get(report.overall_risk, report.overall_risk) if lang == "ar" else report.overall_risk
    ai_metric_value = (
        AI_STATUS_AR.get(report.ai_summary.status, report.ai_summary.status)
        if lang == "ar"
        else report.ai_summary.status
    )
    cols = st.columns(5)
    cols[0].metric(T("metric_overall_risk"), risk_value)
    cols[1].metric(T("metric_findings"), len(report.findings))
    cols[2].metric(T("metric_events_accepted"), summary.events_accepted)
    cols[3].metric(T("metric_records_rejected"), summary.records_rejected)
    cols[4].metric(T("metric_ai_summary"), ai_metric_value)
    st.caption(translate_risk_reason(report.overall_risk_reason, lang))

    # SOC-style visualization inspired by the supplied reference. Every chart is
    # derived from the current imported report; no fabricated telemetry is shown.
    if px is not None and go is not None:
        left, right = st.columns([1.6, 1])
        with left:
            st.subheader("Traffic & Event Overview")
            event_rows = [event.to_dict() for event in run.load_result.events]
            if event_rows:
                import pandas as pd
                frame = pd.DataFrame(event_rows)
                frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True)
                frame = frame.dropna(subset=["timestamp"])
                if not frame.empty:
                    timeline = frame.set_index("timestamp").resample("5min").size().rename("Events").reset_index()
                    fig = px.line(timeline, x="timestamp", y="Events", template="plotly_dark", markers=True)
                    fig.update_layout(height=260, margin=dict(l=8,r=8,t=15,b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No valid timestamps available for the traffic timeline.")
            else:
                st.info("No event records were loaded.")
        with right:
            st.subheader("Finding Severity Mix")
            severity_values = {level: sum(1 for finding in report.findings if finding.severity == level)
                               for level in SEVERITIES}
            severity_values = {key: value for key, value in severity_values.items() if value}
            if severity_values:
                fig = px.pie(names=list(severity_values), values=list(severity_values.values()),
                             hole=0.62, template="plotly_dark")
                fig.update_layout(height=260, margin=dict(l=8,r=8,t=15,b=8), paper_bgcolor="rgba(0,0,0,0)",
                                  legend=dict(orientation="h",y=-0.12))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No findings in this analysis.")

    counts: dict[str, int] = {}
    for severity in SEVERITIES:
        label = SEVERITY_AR[severity] if lang == "ar" else severity
        counts[label] = sum(1 for f in report.findings if f.severity == severity)
    st.subheader(T("severity_summary"))
    st.bar_chart(counts)

    for warning in report.analysis_warnings:
        st.warning(warning)

    st.subheader(T("findings_header"))
    # Full-width filters keep long English agent ids and Arabic severity labels
    # readable in one row; they wrap only when the window itself is narrow.
    sev_labels = {s: (SEVERITY_AR[s] if lang == "ar" else s) for s in SEVERITIES}
    sev_filter = st.multiselect(
        T("filter_severity"),
        SEVERITIES,
        format_func=sev_labels.__getitem__,
        default=SEVERITIES,
        # The formatted labels change with the language; a language-specific
        # key remounts the widget so its chips never end up empty/stale.
        key=f"sev_filter_{lang}",
    )
    agents = sorted({f.agent for f in report.findings})
    agent_filter = st.multiselect(
        T("filter_agent"), agents, default=agents, key="agent_filter"
    )
    query = st.text_input(T("filter_search"), key="search").strip().lower()

    plan_by_finding = {p.related_finding_id: p for p in report.response_plan}

    def _shown_findings():
        return [
            f
            for f in report.findings
            if f.severity in set(sev_filter)
            and f.agent in agent_filter
            and (not query or query in f.title.lower() or query in f.description.lower())
        ]

    shown = _shown_findings()
    if not report.findings:
        st.success(T("no_findings_at_all"))
    elif not shown:
        st.info(T("no_findings_matching"))

    for f in shown:
        explainer = finding_explainer(_finding_view(f), lang)
        if explainer is None:
            header = f"[{f.severity}] {f.finding_id} · {f.agent} · {f.title}"
            with st.expander(header):
                _render_finding_technical(f, plan_by_finding.get(f.finding_id))
            continue
        header = f"[{explainer['severity_ar']}] {explainer['name']}"
        with st.expander(header):
            st.caption(T("q_finding_meta", rule_id=f.rule_id, agent=f.agent, finding_id=f.finding_id))
            st.markdown(f"**{T('q_what')}**")
            st.write(explainer["what"])
            st.markdown(f"**{T('q_why')}**")
            st.write(explainer["why"])
            st.markdown(f"**{T('q_evidence')}**")
            for e in explainer["evidence"]:
                st.markdown(f"- {e['kind_label']} = `{e['value']}`")
                st.caption(e["description"])
            st.markdown(f"**{T('q_meaning')}**")
            st.write(explainer["meaning"])
            st.markdown(f"**{T('q_step')}**")
            st.write(explainer["step"])
            st.markdown(f"**{T('q_recommendation')}**")
            st.write(explainer["recommendation"])
            plan = plan_by_finding.get(f.finding_id)
            if plan is not None:
                st.markdown(f"**{T('q_response_plan')}**")
                st.write(plan.action)
            st.markdown(f"⚠️ {explainer['suspicion_note']}")
            if explainer.get("unknown_rule_note"):
                st.caption(explainer["unknown_rule_note"])
            with st.expander(T("technical_details_header")):
                _render_finding_technical(f, None)

    with st.expander(T("glossary_header")):
        for item in glossary(lang):
            with st.popover(item["term"], icon="❓"):
                st.write(item["definition"])
                st.caption(T("glossary_note", term=item["term_en"]))

    render_ai_panel(run, lang)

    st.download_button(
        T("download_button"),
        data=report_to_json(report),
        file_name="cybershield_report.json",
        mime="application/json",
        key="download_btn",
    )
    with st.expander(T("limitations_header")):
        for limitation in report.limitations:
            st.markdown(f"- {translate_limitation(limitation, lang)}")


if __name__ == "__main__":  # streamlit runs the script as __main__; tests can import helpers
    main()
