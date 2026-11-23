
import streamlit as st
from io import BytesIO

from utils.resume_parser import extract_text

from utils.job_description_analyzer import (
    extract_skills,
    compare_skills,
    calculate_match_percentage,
    extract_keywords,
    generate_suggestions
)

from models.qwen_model import ask_qwen
from utils.error_highlighter import analyze_resume_errors
from utils.resume_editor import create_corrected_docx

from utils.sample_library import (
    get_job_roles,
    get_sample_job_description,
    get_sample_resume
)


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="logo.jpg",
    layout="wide"
)


# =====================================================
# MODERN APP STYLING
# =====================================================

st.markdown("""
<style>
:root {
    --brand: #635bff;
    --brand2: #16b8a6;
}
.stApp {
    background: linear-gradient(135deg, #f7f8ff 0%, #eef4ff 48%, #f4fbff 100%);
    color: #172033;
}
[data-testid="stHeader"] { background: rgba(247,248,255,.82); }
.block-container { max-width: 1240px; padding-top: 2rem; padding-bottom: 3rem; }
h1, h2, h3 { color: #18233b !important; letter-spacing: -.035em; }
h1 { font-weight: 850 !important; }
p, label, [data-testid="stMarkdownContainer"] { color: #34415b; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #171d3a 0%, #242c55 55%, #253d62 100%);
}
[data-testid="stSidebar"] * { color: #f5f7ff !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(255,255,255,.07);
    border: 1px solid rgba(255,255,255,.08);
    padding: 10px 12px;
    border-radius: 12px;
    margin: 5px 0;
}
[data-testid="stMetric"] {
    background: rgba(255,255,255,.88);
    border: 1px solid #e2e8f6;
    padding: 18px 20px;
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(42,58,105,.07);
}
[data-testid="stMetricLabel"] { color: #65718a !important; font-weight: 650; }
[data-testid="stMetricValue"] { color: #1b2850 !important; font-weight: 800; }
div.stButton > button, div.stDownloadButton > button {
    border-radius: 12px; font-weight: 700; min-height: 2.8rem;
    border: 1px solid #dce3f4; transition: all .18s ease;
    background: white; color: #283654;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #635bff, #3288ef);
    color: white; border: 0;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    transform: translateY(-2px); border-color: #7772ff;
    box-shadow: 0 9px 22px rgba(82,93,220,.16);
}
[data-testid="stFileUploader"] section {
    background: linear-gradient(135deg, #ffffff, #f1f5ff);
    border: 2px dashed #9aa9e8; border-radius: 18px; padding: 18px;
}
[data-testid="stFileUploaderDropzone"] { background: transparent; }
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {
    background: #fff; border: 1px solid #dce4f3; border-radius: 12px;
}
div[data-testid="stExpander"] {
    border-radius: 14px; border: 1px solid #e0e7f4; background: rgba(255,255,255,.7);
}
div[data-testid="stAlert"] { border-radius: 13px; }
hr { border-color: #dce4f3; }
.hero-panel {
    padding: 2rem 2.1rem; border-radius: 24px;
    background: linear-gradient(115deg, #282e69 0%, #4056a7 48%, #167f91 100%);
    box-shadow: 0 18px 42px rgba(43,64,143,.18);
    margin: .4rem 0 1.5rem 0;
}
.hero-panel * { color: #fff !important; }
.hero-kicker { text-transform: uppercase; letter-spacing: .15em; font-size: .74rem; font-weight: 800; opacity: .78; }
.hero-title { font-size: clamp(1.8rem, 3vw, 2.6rem); line-height: 1.12; font-weight: 850; margin: .55rem 0; }
.hero-copy { opacity: .88; font-size: 1.02rem; margin-bottom: .1rem; }
.section-card {
    background: rgba(255,255,255,.9); border: 1px solid #e2e8f5;
    border-radius: 18px; padding: 18px 20px; min-height: 130px;
    box-shadow: 0 8px 24px rgba(42,58,105,.05);
}
.section-icon { font-size: 1.65rem; margin-bottom: .45rem; }
.section-title { color: #1e2b4b; font-size: 1.05rem; font-weight: 800; }
.section-copy { color: #65718a; font-size: .9rem; margin-top: .3rem; }
.small-muted { color: #71809b; font-size: .88rem; }

/* High-contrast widget overrides for all Streamlit text controls. */
html, body, .stApp, [data-testid="stAppViewContainer"] { color-scheme: light !important; }
.stApp textarea, .stApp input,
.stApp [data-baseweb="textarea"] textarea,
.stApp [data-baseweb="input"] input {
    background: #ffffff !important;
    color: #202b40 !important;
    -webkit-text-fill-color: #202b40 !important;
    opacity: 1 !important;
}
.stApp textarea:disabled, .stApp input:disabled {
    background: #f8faff !important;
    color: #34415b !important;
    -webkit-text-fill-color: #34415b !important;
    opacity: 1 !important;
}
/* File uploader background */
[data-testid="stFileUploader"] section {
    background-color: #ffffff !important;
    border: 2px dashed #8295f5 !important;
    border-radius: 14px !important;
}

/* Uploaded filename */
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] * {
    color: #172554 !important;
    -webkit-text-fill-color: #172554 !important;
    font-weight: 600 !important;
}

/* Upload button */
[data-testid="stFileUploader"] button {
    background: #4f46e5 !important;
    color: #ffffff !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# BASIC ATS COMPATIBILITY CHECKS
# =====================================================

import re


def show_message(message, kind="info"):
    """Render a readable message card with fixed high-contrast colours."""
    palettes = {
        "success": ("#e8f7ef", "#17633b", "#b9e5cb"),
        "warning": ("#fff6df", "#805600", "#f0d58d"),
        "error": ("#fff0f0", "#9b2929", "#efc0c0"),
        "info": ("#edf4ff", "#244f91", "#c9dcfa"),
    }
    background, foreground, border = palettes.get(kind, palettes["info"])
    safe_message = (str(message).replace("&", "&amp;")
                    .replace("<", "&lt;").replace(">", "&gt;"))
    st.markdown(
        f'<div style="background:{background};color:{foreground};'
        f'border:1px solid {border};border-radius:12px;padding:14px 17px;'
        f'margin:8px 0;font-weight:600;line-height:1.5;">{safe_message}</div>',
        unsafe_allow_html=True
    )


def show_success(message, **kwargs):
    show_message(message, "success")


def show_warning(message, **kwargs):
    show_message(message, "warning")


def show_error(message, **kwargs):
    show_message(message, "error")


def show_info(message, **kwargs):
    show_message(message, "info")


def show_resume_preview(label, value, height=280):
    """Show extracted resume text in a dedicated high-contrast preview."""
    safe_value = (str(value).replace("&", "&amp;")
                  .replace("<", "&lt;").replace(">", "&gt;"))
    st.markdown(f"**{label}**")
    st.markdown(
        f'<div style="height:{height}px;overflow:auto;white-space:pre-wrap;'
        'overflow-wrap:anywhere;background:#ffffff;color:#202b40;'
        'border:1px solid #cbd5e1;border-radius:13px;padding:16px 18px;'
        'font-family:ui-monospace,SFMono-Regular,Consolas,monospace;'
        'font-size:14px;line-height:1.65;">'
        f'{safe_value}</div>',
        unsafe_allow_html=True
    )


def run_ats_checks(resume_text, resume_name):
    """Run transparent, rule-based ATS checks (not a real ATS simulation)."""
    text = resume_text or ""
    lower_text = text.lower()

    checks = []

    # Contact information
    email_found = bool(re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text
    ))
    phone_found = bool(re.search(
        r"(?:\+?\d{1,3}[\s.-]?)?(?:\d[\s.-]?){10,12}", text
    ))
    checks.append({
        "name": "Contact information",
        "passed": email_found and phone_found,
        "detail": (
            "Email and phone number detected."
            if email_found and phone_found
            else "Add a clearly written email address and 10-digit phone number."
        )
    })

    # Common resume sections
    section_groups = {
        "Education": ["education", "academic background", "qualification"],
        "Experience": ["experience", "work experience", "internship"],
        "Skills": ["skills", "technical skills", "core competencies"],
        "Projects": ["projects", "academic projects", "personal projects"]
    }
    found_sections = []
    missing_sections = []
    for section, terms in section_groups.items():
        if any(term in lower_text for term in terms):
            found_sections.append(section)
        else:
            missing_sections.append(section)

    checks.append({
        "name": "Standard resume sections",
        "passed": len(found_sections) >= 3,
        "detail": (
            "Detected: " + ", ".join(found_sections)
            if not missing_sections
            else "Detected: " + (", ".join(found_sections) or "none")
            + ". Consider adding: " + ", ".join(missing_sections) + "."
        )
    })

    # Resume length
    word_count = len(re.findall(r"\b\w+\b", text))
    checks.append({
        "name": "Resume content length",
        "passed": 150 <= word_count <= 1000,
        "detail": (
            f"Approximately {word_count} words. "
            "A concise, relevant resume is generally easier to scan."
        )
    })

    # File extension
    extension = (resume_name.rsplit(".", 1)[-1].lower()
                 if "." in (resume_name or "") else "")
    checks.append({
        "name": "File format",
        "passed": extension in {"pdf", "docx"},
        "detail": (
            f"Uploaded as .{extension}."
            if extension in {"pdf", "docx"}
            else "Use a text-based PDF or DOCX where the employer accepts it."
        )
    })

    # Avoid relying on columns/tables as the text extractor may not capture them reliably.
    checks.append({
        "name": "Readable extracted text",
        "passed": len(text.strip()) >= 200,
        "detail": (
            "Text was extracted for analysis."
            if len(text.strip()) >= 200
            else "Very little text was extracted. Check whether the file is scanned or image-based."
        )
    })

    passed = sum(1 for item in checks if item["passed"])
    score = round((passed / len(checks)) * 100)
    return {
        "score": score,
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "word_count": word_count
    }


# =====================================================
# SESSION STATE
# =====================================================

defaults = {
    "resume_text": "",
    "resume_name": "",
    "resume_file_bytes": None,
    "resume_extension": "",
    "analysis": None,
    "ai_feedback": "",
    "error_results": None,
    "ats_results": None,
    "corrections": {},
    "ignored_issues": set(),
    "job_description": "",
    "standalone_ats_results": None,
    "standalone_writing_results": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

with st.sidebar:
    st.markdown("## ✦ RESUMATE AI")
    st.caption("YOUR PERSONAL RESUME STUDIO")
    st.divider()
    selected_page = st.radio(
        "WORKSPACE",
        ["Dashboard", "Resume Analyzer", "ATS Checker", "Writing Quality"],
        key="workspace_page",
        label_visibility="visible"
    )
    st.divider()
    st.markdown("**TOOLS**")
    st.caption("AI-powered resume improvement")
    st.caption("Local Qwen model • Private analysis")
    st.markdown("---")
    st.caption("RESUMATE AI  ·  v1.0")


def render_ats_page():
    st.markdown("""
    <div class="hero-panel">
      <div class="hero-kicker">INDEPENDENT TOOL</div>
      <div class="hero-title">ATS compatibility check</div>
      <div class="hero-copy">Upload a resume and check its basic structure and readability — no job description or full analysis required.</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Choose a resume file",
        type=["pdf", "docx"],
        key="standalone_ats_upload",
        help="Upload a text-based PDF or DOCX resume."
    )
    if uploaded is not None:
        show_success(f"Ready to check: {uploaded.name}")
        if st.button("Run ATS Check", type="primary", use_container_width=True):
            try:
                extracted = extract_text(uploaded)
                if not extracted.strip():
                    show_error("No readable text was extracted. This may be a scanned PDF.")
                else:
                    st.session_state.standalone_ats_results = run_ats_checks(
                        extracted, uploaded.name
                    )
                    st.session_state.standalone_ats_name = uploaded.name
            except Exception as exc:
                show_error(f"Could not check this file: {exc}")

    ats = st.session_state.get("standalone_ats_results")
    if ats:
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("ATS Readiness Indicator", f"{ats['score']}%")
        c2.metric("Checks Passed", f"{ats['passed']} / {ats['total']}")
        c3.metric("Resume Word Count", ats["word_count"])
        st.progress(ats["score"] / 100)
        st.subheader("Compatibility checklist")
        for item in ats["checks"]:
            if item["passed"]:
                show_success(f"✓ {item['name']}  ·  {item['detail']}")
            else:
                show_warning(f"↗ {item['name']}  ·  {item['detail']}")
        st.caption(
            "This is a basic rule-based readiness indicator, not a real ATS simulation. "
            "It cannot guarantee parsing by a particular employer's software or reliably "
            "inspect visual layout, columns and tables."
        )


def render_writing_quality_page():
    st.markdown("""
    <div class="hero-panel">
      <div class="hero-kicker">INDEPENDENT TOOL</div>
      <div class="hero-title">Resume writing quality</div>
      <div class="hero-copy">Find grammar mistakes, spelling errors and weak sentences without running job matching.</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload a resume for writing review",
        type=["pdf", "docx"],
        key="standalone_writing_upload"
    )
    if uploaded is not None:
        if st.button("Check Writing Quality", type="primary", use_container_width=True):
            try:
                text = extract_text(uploaded)
                if not text.strip():
                    show_error("No readable text was extracted from this file.")
                else:
                    with st.spinner("Qwen AI is reviewing your resume..."):
                        st.session_state.standalone_writing_results = analyze_resume_errors(text)
            except Exception as exc:
                show_error(f"Writing review failed: {exc}")

    result = st.session_state.get("standalone_writing_results")
    if result:
        st.divider()
        st.subheader("Review summary")
        st.write(result.get("summary", "Review completed."))
        issues = result.get("issues", [])
        st.metric("Verified writing issues", len(issues))
        if issues:
            for n, issue in enumerate(issues, 1):
                with st.expander(f"Issue {n}: {issue.get('issue_type', 'Writing issue')}"):
                    st.markdown("**Original text**")
                    show_error(issue.get("exact_text", ""))
                    st.markdown("**Why it needs attention**")
                    st.write(issue.get("explanation", ""))
                    st.markdown("**Suggested improvement**")
                    show_success(issue.get("suggestion", ""))
        else:
            show_success("No verified writing issues were detected.")


def render_home_dashboard():
    st.markdown("""
    <div class="hero-panel">
      <div class="hero-kicker">WELCOME TO RESUMATE AI</div>
      <div class="hero-title">Your career story, made stronger.</div>
      <div class="hero-copy">Choose a tool to get started. Each tool works independently, so you can run an ATS check without completing a full resume analysis.</div>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("Your workspace")
    a, b = st.columns(2)
    with a:
        st.markdown('<div class="section-card"><div class="section-icon">📊</div><div class="section-title">Resume Analyzer</div><div class="section-copy">Compare your resume with a job description, identify skill gaps and get AI feedback.</div></div>', unsafe_allow_html=True)
        if st.button("Open Resume Analyzer →", key="home_resume", use_container_width=True):
            st.session_state.workspace_page = "Resume Analyzer"
            st.rerun()
    with b:
        st.markdown('<div class="section-card"><div class="section-icon">🧩</div><div class="section-title">ATS Checker</div><div class="section-copy">Check resume structure, contact details and extracted text independently.</div></div>', unsafe_allow_html=True)
        if st.button("Open ATS Checker →", key="home_ats", use_container_width=True):
            st.session_state.workspace_page = "ATS Checker"
            st.rerun()
    c, d = st.columns(2)
    with c:
        st.markdown('<div class="section-card"><div class="section-icon">✍️</div><div class="section-title">Writing Quality</div><div class="section-copy">Review grammar, spelling and weak sentences with your local Qwen model.</div></div>', unsafe_allow_html=True)
        if st.button("Open Writing Quality →", key="home_writing", use_container_width=True):
            st.session_state.workspace_page = "Writing Quality"
            st.rerun()
    with d:
        st.markdown('<div class="section-card"><div class="section-icon">🔒</div><div class="section-title">Private local AI</div><div class="section-copy">Your Qwen analysis runs through your local LM Studio server.</div></div>', unsafe_allow_html=True)
    st.divider()
    st.caption("Tip: Start with ATS Checker for a quick standalone check, or use Resume Analyzer for a complete job-specific review.")


# =====================================================
# PAGE ROUTING
# =====================================================

if selected_page == "Dashboard":
    render_home_dashboard()
elif selected_page == "ATS Checker":
    render_ats_page()
elif selected_page == "Writing Quality":
    render_writing_quality_page()
else:


# =====================================================
# MAIN HEADING
# =====================================================

    st.markdown("""
    <div class="hero-panel">
      <div class="hero-kicker">RESUME INTELLIGENCE PLATFORM</div>
      <div class="hero-title">Make your next career move with confidence.</div>
      <div class="hero-copy">One workspace to analyze, optimize and strengthen your resume.</div>
    </div>
    """, unsafe_allow_html=True)


    # =====================================================
    # RESUME UPLOAD
    # =====================================================

    st.divider()
    st.header("📂 Upload Your Resume")

    resume = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx"],
        key="resume_upload"
    )

    if resume:

        show_success("Resume uploaded successfully!")

        st.write("File name:", resume.name)

        if st.button("Extract Resume Text"):

            try:

                resume_text = extract_text(resume)

                if resume_text.strip():

                    st.session_state.resume_text = resume_text
                    st.session_state.resume_name = resume.name
                    st.session_state.resume_file_bytes = resume.getvalue()

                    st.session_state.resume_extension = (
                        resume.name.rsplit(".", 1)[-1].lower()
                    )

                    # Reset previous results
                    st.session_state.analysis = None
                    st.session_state.ai_feedback = ""
                    st.session_state.error_results = None
                    st.session_state.ats_results = None
                    st.session_state.corrections = {}
                    st.session_state.ignored_issues = set()

                    show_success(
                        "Resume text extracted successfully!"
                    )

                else:

                    show_warning(
                        "No text found. This may be a scanned PDF."
                    )

            except Exception as e:

                show_error(f"Error reading resume: {e}")


    # =====================================================
    # DISPLAY EXTRACTED RESUME
    # =====================================================

    if st.session_state.resume_text:

        st.subheader("📃 Extracted Resume Content")

        show_resume_preview(
            "Extracted Resume Text",
            st.session_state.resume_text,
            height=280
        )


    # =====================================================
    # JOB DESCRIPTION + SAMPLE JOB DESCRIPTIONS
    # =====================================================

    st.divider()

    st.header("💼 Job Description")

    st.write(
        "Paste a job description or choose a sample description "
        "for your preferred career role."
    )

    col_jd, col_samples = st.columns([2, 1])

    # Sample selector
    with col_samples:

        st.subheader("📚 Sample Job Descriptions")

        job_roles = get_job_roles()

        selected_jd_role = st.selectbox(
            "Choose a career role",
            job_roles,
            key="selected_jd_role"
        )

        sample_jd = get_sample_job_description(
            selected_jd_role
        )

        with st.expander("Preview Sample Job Description"):

            st.write(sample_jd)

        if st.button(
            "Insert Sample Job Description",
            use_container_width=True
        ):

            st.session_state.job_description = sample_jd

            st.rerun()


    # Job description input
    with col_jd:

        job_description = st.text_area(
            "Paste the job description here",
            height=350,
            placeholder="Paste the complete job description here...",
            key="job_description"
        )


    # =====================================================
    # SAMPLE RESUME LIBRARY
    # =====================================================

    st.divider()

    st.header("📖 Sample Resume Library")

    st.write(
        "Explore sample resume templates for different career roles. "
        "Use them as references when preparing your own resume."
    )

    selected_resume_role = st.selectbox(
        "Choose a resume template",
        get_job_roles(),
        key="selected_resume_role"
    )

    sample_resume = get_sample_resume(
        selected_resume_role
    )

    with st.expander(
        f"Preview {selected_resume_role} Resume"
    ):

        st.text_area(
            "Sample Resume",
            value=sample_resume,
            height=400,
            disabled=True,
            key="sample_resume_preview"
        )

    st.download_button(
        label="📥 Download Sample Resume Template",
        data=sample_resume,
        file_name=(
            selected_resume_role.replace("/", "-").replace(" ", "_")
            + "_Sample_Resume.txt"
        ),
        mime="text/plain"
    )


    # =====================================================
    # ANALYZE RESUME
    # =====================================================

    st.divider()

    if st.button(
        "🔍 Analyze Resume",
        type="primary",
        use_container_width=True
    ):

        if not st.session_state.resume_text:

            show_warning(
                "Please upload and extract your resume first."
            )

        elif not st.session_state.job_description.strip():

            show_warning(
                "Please enter a job description."
            )

        else:

            try:

                resume_skills = extract_skills(
                    st.session_state.resume_text
                )

                required_skills = extract_skills(
                    st.session_state.job_description
                )

                matching_skills, missing_skills = compare_skills(
                    resume_skills,
                    required_skills
                )

                match_percentage = calculate_match_percentage(
                    resume_skills,
                    required_skills
                )

                keywords = extract_keywords(
                    st.session_state.job_description
                )

                suggestions = generate_suggestions(
                    missing_skills
                )

                st.session_state.analysis = {
                    "resume_skills": resume_skills,
                    "required_skills": required_skills,
                    "matching_skills": matching_skills,
                    "missing_skills": missing_skills,
                    "match_percentage": match_percentage,
                    "keywords": keywords,
                    "suggestions": suggestions
                }

                st.session_state.ai_feedback = ""
                st.session_state.error_results = None
                st.session_state.ats_results = None
                st.session_state.corrections = {}
                st.session_state.ignored_issues = set()

                show_success("Resume analysis completed!")

            except Exception as e:

                show_error(f"Analysis failed: {e}")


    # =====================================================
    # DISPLAY ANALYSIS RESULTS
    # =====================================================

    if st.session_state.analysis is not None:

        results = st.session_state.analysis

        # =================================================
        # PROFESSIONAL DASHBOARD
        # =================================================

        st.divider()
        st.title("📊 Professional Resume Dashboard")
        st.caption(
            "A quick overview of how your resume matches the selected job description."
        )

        match_score = float(results.get("match_percentage", 0))
        matching_count = len(results.get("matching_skills", []))
        missing_count = len(results.get("missing_skills", []))
        total_required = matching_count + missing_count

        writing_issues = 0
        if st.session_state.error_results is not None:
            writing_issues = len(
                st.session_state.error_results.get("issues", [])
            )

        # KPI cards
        metric1, metric2, metric3, metric4 = st.columns(4)

        with metric1:
            st.metric("🎯 Job Match Score", f"{match_score:.1f}%")

        with metric2:
            st.metric("✅ Matching Skills", matching_count)

        with metric3:
            st.metric("⚠️ Missing Skills", missing_count)

        with metric4:
            issue_label = (
                str(writing_issues)
                if st.session_state.error_results is not None
                else "Not checked"
            )
            st.metric("📝 Writing Issues", issue_label)

        # Match score progress
        st.subheader("Overall Match")
        st.progress(max(0.0, min(match_score / 100, 1.0)))

        if total_required:
            st.caption(
                f"{matching_count} of {total_required} identified job skills "
                "were found in your resume."
            )
        else:
            st.caption(
                "No job skills were identified from the job description. "
                "Try adding a more detailed job description."
            )

        # Matching vs. missing skills chart
        st.subheader("Skills Breakdown")
        if total_required:
            chart_data = {
                "Skill count": {
                    "Matching skills": matching_count,
                    "Missing skills": missing_count
                }
            }
            st.bar_chart(chart_data)
        else:
            show_info("The skills chart will appear after skills are identified.")

        # Downloadable plain-text report
        report_lines = [
            "AI RESUME ANALYSIS REPORT",
            "=" * 32,
            f"Resume: {st.session_state.resume_name or 'Uploaded resume'}",
            f"Job match score: {match_score:.1f}%",
            "",
            f"Matching skills ({matching_count}):",
            ", ".join(results.get("matching_skills", [])) or "None identified",
            "",
            f"Missing skills ({missing_count}):",
            ", ".join(results.get("missing_skills", [])) or "None identified",
            "",
            "Important job keywords:",
            ", ".join(results.get("keywords", [])) or "None identified",
            "",
            "Resume improvement suggestions:",
            *[
                f"- {suggestion}"
                for suggestion in results.get("suggestions", [])
            ],
            "",
            "Note: The match score is based on the application's keyword/skill "
            "matching logic. It is not a guarantee of ATS performance or hiring outcome."
        ]

        if st.session_state.error_results is not None:
            report_lines.extend([
                "",
                "Writing quality summary:",
                st.session_state.error_results.get(
                    "summary", "Writing quality check completed."
                ),
                f"Verified writing issues: {writing_issues}"
            ])

        report_text = "\n".join(report_lines)

        st.download_button(
            label="📥 Download Analysis Report",
            data=report_text,
            file_name="Resume_Analysis_Report.txt",
            mime="text/plain",
            key="download_analysis_report"
        )

        st.divider()
        st.title("📊 Resume Analysis Results")

        st.metric(
            "Resume Match Percentage",
            f"{results['match_percentage']:.2f}%"
        )

        st.progress(
            results["match_percentage"] / 100
        )

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("✅ Matching Skills")

            if results["matching_skills"]:

                for skill in results["matching_skills"]:
                    st.write(f"✅ {skill}")

            else:

                st.write("No matching skills found.")

        with col2:

            st.subheader("❌ Missing Skills")

            if results["missing_skills"]:

                for skill in results["missing_skills"]:
                    st.write(f"❌ {skill}")

            else:

                show_success("No missing skills found.")

        st.divider()

        st.subheader("🔑 Important Job Keywords")

        if results["keywords"]:
            st.write(", ".join(results["keywords"]))
        else:
            st.write("No keywords identified.")

        st.divider()

        st.subheader("💡 Resume Improvement Suggestions")

        for suggestion in results["suggestions"]:
            show_info(suggestion)

        st.divider()

        st.subheader("📋 Skills Overview")

        col3, col4 = st.columns(2)

        with col3:

            st.write("**Resume Skills**")
            st.write(results["resume_skills"])

        with col4:

            st.write("**Required Job Skills**")
            st.write(results["required_skills"])


        # =================================================
        # QWEN AI FEEDBACK
        # =================================================

        st.divider()

        st.title("🤖 AI-Powered Resume Feedback")

        st.write(
            "Get deeper feedback from your locally running Qwen AI model."
        )

        if st.button("Generate AI Feedback"):

            prompt = f"""
    You are an expert resume analyst.

    Analyze the resume against the job description.

    RESUME:
    {st.session_state.resume_text[:10000]}

    JOB DESCRIPTION:
    {st.session_state.job_description[:5000]}

    Provide:

    1. Resume Strengths
    2. Resume Weaknesses
    3. Missing or weak qualifications
    4. Project and experience improvements
    5. Specific resume recommendations
    6. Overall assessment

    IMPORTANT:
    - Only use information present in the resume.
    - Never invent skills, projects or achievements.
    - Clearly identify missing information.
    - Give practical recommendations.
    """

            with st.spinner("Qwen AI is analyzing your resume..."):

                try:

                    st.session_state.ai_feedback = ask_qwen(prompt)

                except Exception as e:

                    show_error(f"AI feedback failed: {e}")

        if st.session_state.ai_feedback:

            st.markdown(
                st.session_state.ai_feedback
            )


        # =================================================
        # RESUME WRITING QUALITY CHECKER
        # =================================================

        st.divider()

        st.title("🔍 Resume Writing Quality Checker")

        st.write(
            "Find grammar mistakes, spelling errors and weak sentences."
        )

        if st.button("Check Resume for Mistakes"):

            with st.spinner("Qwen AI is checking your resume..."):

                try:

                    st.session_state.error_results = (
                        analyze_resume_errors(
                            st.session_state.resume_text
                        )
                    )

                    st.session_state.corrections = {}
                    st.session_state.ignored_issues = set()

                except Exception as e:

                    show_error(f"Mistake detection failed: {e}")

        if st.session_state.error_results is not None:

            error_results = st.session_state.error_results

            st.subheader("📝 Writing Quality Summary")

            st.write(
                error_results.get(
                    "summary",
                    "Analysis completed."
                )
            )

            issues = error_results.get("issues", [])

            if issues:

                st.subheader(
                    f"Found {len(issues)} Writing Issues"
                )

                # =========================================
                # INTERACTIVE CORRECTION EDITOR
                # =========================================

                for index, issue in enumerate(issues):

                    issue_type = issue.get(
                        "issue_type",
                        "Writing issue"
                    )

                    exact_text = issue.get(
                        "exact_text",
                        ""
                    )

                    suggestion = issue.get(
                        "suggestion",
                        ""
                    )

                    with st.expander(
                        f"Issue {index + 1}: {issue_type}"
                    ):

                        st.markdown("**Original text:**")
                        st.markdown(
                            f'<div style="background:#fff0f0;color:#8f2525;'
                            f'border:1px solid #efc0c0;border-radius:12px;'
                            f'padding:14px 17px;font-weight:600;'
                            f'overflow-wrap:anywhere;">'
                            f'{exact_text}</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown("**Explanation:**")

                        st.write(
                            issue.get("explanation", "")
                        )

                        if index in st.session_state.corrections:

                            show_success(
                                "Correction added to your edited resume."
                            )

                            st.write("**Applied correction:**")

                            st.write(
                                st.session_state.corrections[index][
                                    "suggestion"
                                ]
                            )

                        elif index in st.session_state.ignored_issues:

                            show_info("You ignored this issue.")

                        else:

                            edited_text = st.text_area(
                                "Edit suggested correction",
                                value=suggestion,
                                key=f"edit_suggestion_{index}",
                                height=100
                            )

                            col_apply, col_ignore = st.columns(2)

                            with col_apply:

                                if st.button(
                                    "Apply Correction",
                                    key=f"apply_{index}"
                                ):

                                    if edited_text.strip():

                                        st.session_state.corrections[index] = {
                                            "exact_text": exact_text,
                                            "suggestion": edited_text.strip()
                                        }

                                        st.rerun()

                                    else:

                                        show_warning(
                                            "Correction cannot be empty."
                                        )

                            with col_ignore:

                                if st.button(
                                    "Ignore Issue",
                                    key=f"ignore_{index}"
                                ):

                                    st.session_state.ignored_issues.add(
                                        index
                                    )

                                    st.rerun()


                # =========================================
                # CORRECTION SUMMARY
                # =========================================

                st.divider()

                st.subheader("📋 Correction Summary")

                selected_count = len(
                    st.session_state.corrections
                )

                ignored_count = len(
                    st.session_state.ignored_issues
                )

                remaining_count = max(
                    0,
                    len(issues) - selected_count - ignored_count
                )

                st.write(
                    f"Corrections selected: {selected_count}"
                )

                st.write(
                    f"Issues ignored: {ignored_count}"
                )

                st.write(
                    f"Issues remaining: {remaining_count}"
                )


                # =========================================
                # DOWNLOAD CORRECTED RESUME
                # =========================================

                st.divider()

                st.subheader("📥 Download Corrected Resume")

                if st.session_state.corrections:

                    try:

                        corrections_list = list(
                            st.session_state.corrections.values()
                        )

                        corrected_file, applied, not_found = (
                            create_corrected_docx(
                                BytesIO(
                                    st.session_state.resume_file_bytes
                                ),
                                corrections_list,
                                file_type=st.session_state.resume_extension
                            )
                        )

                        st.write(
                            f"Successfully applied: {len(applied)} correction(s)"
                        )

                        if not_found:

                            show_warning(
                                f"{len(not_found)} correction(s) "
                                "could not be located in the document."
                            )

                        if applied:

                            st.download_button(
                                label="📥 Download Corrected Resume",
                                data=corrected_file.getvalue(),
                                file_name="Corrected_Resume.docx",
                                mime=(
                                    "application/vnd.openxmlformats-officedocument."
                                    "wordprocessingml.document"
                                )
                            )

                        if st.session_state.resume_extension == "pdf":

                            show_info(
                                "PDF text has been reconstructed into a Word "
                                "document. Original PDF formatting may differ."
                            )

                    except Exception as e:

                        show_error(
                            f"Could not create corrected resume: {e}"
                        )

                else:

                    show_info(
                        "Apply at least one correction to enable downloading."
                    )

            else:

                show_success(
                    "No verified writing issues were detected."
                )
