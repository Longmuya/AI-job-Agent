import os
import re
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from main import extract_match_score, run_job_agent


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
RESUME_PATH = BASE_DIR / "resume.pdf"
JD_PATH = BASE_DIR / "job_description.txt"
OUTPUT_PATH = BASE_DIR / "agent_output.txt"

REPORT_SECTIONS = {
    "Overall Match Score": [
        "Overall Match Score",
        "Match Score",
        "Gap Analysis and Match Score",
    ],
    "Job Description Analysis": ["Job Description Analysis"],
    "Resume Analysis": ["Resume Analysis"],
    "Gap Analysis": ["Gap Analysis", "Gap Analysis and Match Score"],
    "Application Strategy": ["Application Strategy"],
    "Cover Letter Draft": ["Cover Letter Draft", "Tailored Cover Letter"],
    "Verification / Safety Check": ["Verification / Safety Check"],
    "Cost-Benefit Analysis": ["Cost-Benefit Analysis"],
}


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: #f5f7fb;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }
        .hero {
            background: #0f172a;
            color: #f8fafc;
            padding: 28px 32px;
            border-radius: 8px;
            margin-bottom: 22px;
            border: 1px solid #1e293b;
        }
        .hero h1 {
            margin: 0 0 8px 0;
            font-size: 34px;
            letter-spacing: 0;
        }
        .hero p {
            margin: 0;
            color: #cbd5e1;
            font-size: 16px;
            line-height: 1.5;
        }
        .panel {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        }
        .section-label {
            color: #334155;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.02em;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 14px 16px;
        }
        div[data-testid="stExpander"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            background: #2563eb;
            color: white;
            border: 1px solid #2563eb;
            font-weight: 700;
            padding: 0.65rem 1rem;
        }
        .stButton > button:hover {
            background: #1d4ed8;
            border-color: #1d4ed8;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_markdown(title: str) -> str:
    escaped = re.escape(title)
    return rf"(?:\[\d+\]\s*)?{escaped}"


def clean_section_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.fullmatch(r"[-=]{5,}", stripped):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def split_report(report: str) -> dict[str, str]:
    sections = {}
    heading_pattern = re.compile(
        r"(?m)^\s*(?:\[\d+\]\s*)?(Overall Match Score|Job Description Analysis|Resume Analysis|Gap Analysis(?: and Match Score)?|Application Strategy|Tailored Cover Letter|Cover Letter Draft|Verification / Safety Check|Cost-Benefit Analysis)\s*$"
    )
    matches = list(heading_pattern.finditer(report))

    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(report)
        body = clean_section_text(report[start:end])

        for canonical, aliases in REPORT_SECTIONS.items():
            if heading in aliases:
                sections[canonical] = body
                break

    return sections


def fallback_section(report: str, title: str) -> str:
    for alias in REPORT_SECTIONS[title]:
        pattern = re.compile(
            section_markdown(alias) + r"(?P<body>.*?)(?=\n\s*(?:\[\d+\]\s*)?[A-Z][^\n]{3,80}\n|\Z)",
            flags=re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(report)
        if match:
            return clean_section_text(match.group("body"))
    return ""


def get_report_sections(report: str) -> dict[str, str]:
    sections = split_report(report)
    for title in REPORT_SECTIONS:
        if not sections.get(title):
            sections[title] = fallback_section(report, title)
    return sections


def render_report(report: str) -> None:
    sections = get_report_sections(report)
    score = extract_match_score(
        sections.get("Overall Match Score") or sections.get("Gap Analysis") or report
    )

    metric_col, progress_col = st.columns([1, 2])
    with metric_col:
        st.metric("Match Score", f"{score}/100" if score is not None else "Review report")
    with progress_col:
        if score is not None:
            st.progress(score / 100)
        else:
            st.info("The report did not contain a reliable numeric match score.")

    for title in REPORT_SECTIONS:
        content = sections.get(title, "").strip()
        with st.expander(title, expanded=title in {"Overall Match Score", "Verification / Safety Check"}):
            if content:
                st.markdown(content)
            elif title == "Verification / Safety Check":
                st.warning(
                    "No explicit verification section was detected. Review the full report before using the cover letter."
                )
            elif title == "Cost-Benefit Analysis":
                st.info(
                    "No explicit cost-benefit section was detected. Re-run with the updated agent workflow."
                )
            else:
                st.info("This section could not be separated reliably from the generated report.")

    with st.expander("Full Report"):
        st.markdown(report)


def validate_inputs(uploaded_resume, job_description: str) -> bool:
    if uploaded_resume is None:
        st.error("Please upload a PDF resume before running the agent.")
        return False

    if not uploaded_resume.name.lower().endswith(".pdf"):
        st.error("Please upload a PDF file.")
        return False

    if not job_description.strip():
        st.error("Please paste the job description before running the agent.")
        return False

    if not os.getenv("DEEPSEEK_API_KEY"):
        st.error("Missing DEEPSEEK_API_KEY. Add it to your .env file, then restart Streamlit.")
        return False

    return True


def main() -> None:
    st.set_page_config(
        page_title="AI Job Application Agent",
        page_icon="AI",
        layout="wide",
    )
    inject_css()

    st.markdown(
        """
        <div class="hero">
            <h1>AI Job Application Agent</h1>
            <p>
                Upload a resume and paste a job description to run a multi-step agent workflow:
                job analysis, resume review, gap detection, application strategy, cover letter drafting,
                verification, and cost-benefit analysis.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    input_col, output_col = st.columns([0.95, 1.45], gap="large")

    with input_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Inputs</div>', unsafe_allow_html=True)
        uploaded_resume = st.file_uploader("Resume PDF", type=["pdf"])
        job_description = st.text_area(
            "Job Description",
            height=360,
            placeholder="Paste the full job description here...",
        )
        st.caption(
            "Privacy note: the PDF is parsed locally, but LLM reasoning may call a cloud API."
        )
        run_button = st.button("Generate Application Report", type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

    with output_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Agent Report</div>', unsafe_allow_html=True)

        if run_button:
            if validate_inputs(uploaded_resume, job_description):
                try:
                    RESUME_PATH.write_bytes(uploaded_resume.getbuffer())
                    with st.spinner("Running multi-step agent workflow..."):
                        report = run_job_agent(
                            resume_path=str(RESUME_PATH),
                            jd_text=job_description,
                            job_description_path=str(JD_PATH),
                            output_path=str(OUTPUT_PATH),
                        )
                    st.session_state["latest_report"] = report
                    st.success("Report generated successfully.")
                except ValueError as exc:
                    st.error(str(exc))
                except Exception as exc:
                    st.error(
                        "The agent could not complete the report. Check the PDF, API key, and network/API settings."
                    )
                    st.exception(exc)

        latest_report = st.session_state.get("latest_report")
        if latest_report:
            render_report(latest_report)
        elif OUTPUT_PATH.exists():
            st.info("A previous report was found. Run the agent again to refresh it.")
            if st.button("Load Previous Report"):
                st.session_state["latest_report"] = OUTPUT_PATH.read_text(encoding="utf-8")
                st.rerun()
        else:
            st.info("Upload a resume and paste a job description to generate the report.")

        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
