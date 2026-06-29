import os
import re
from typing import Optional, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from pypdf import PdfReader


load_dotenv()


class JobAgentState(TypedDict):
    resume_text: str
    job_description: str
    jd_requirements: Optional[str]
    resume_analysis: Optional[str]
    gap_analysis: Optional[str]
    application_strategy: Optional[str]
    cover_letter: Optional[str]
    verification_safety_check: Optional[str]
    cost_benefit_analysis: Optional[str]
    final_report: Optional[str]


def get_llm() -> ChatOpenAI:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing DEEPSEEK_API_KEY. Add it to your .env file before running the agent."
        )

    return ChatOpenAI(
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        api_key=api_key,
        temperature=0.3,
    )


def read_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text.strip()


def read_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()


def analyze_jd(state: JobAgentState):
    llm = get_llm()
    prompt = f"""
You are a job market analysis agent.

Analyze the following job description and extract:
1. Required technical skills
2. Required soft skills
3. Education or experience requirements
4. Main job responsibilities
5. Keywords that should appear in a resume

Job Description:
{state["job_description"]}

Return the answer in clear bullet points.
"""
    response = llm.invoke(prompt)
    return {"jd_requirements": response.content}


def analyze_resume(state: JobAgentState):
    llm = get_llm()
    prompt = f"""
You are a resume analysis agent.

Analyze the candidate resume below.

Resume:
{state["resume_text"]}

Evaluate:
1. Technical skills
2. Projects or work experience
3. Education background
4. Strengths
5. Weaknesses

Return the answer in clear bullet points.
"""
    response = llm.invoke(prompt)
    return {"resume_analysis": response.content}


def gap_analysis(state: JobAgentState):
    llm = get_llm()
    prompt = f"""
You are a job application matching agent.

Compare the job description requirements and the resume analysis.

Job Requirements:
{state["jd_requirements"]}

Resume Analysis:
{state["resume_analysis"]}

Produce:
1. Match score from 0 to 100
2. Matched skills
3. Missing skills
4. Real skill gaps versus presentation gaps
5. Resume improvement suggestions
6. Whether the candidate should apply, including an honest warning if underqualified

Return the result in a professional but easy-to-understand format.
"""
    response = llm.invoke(prompt)
    return {"gap_analysis": response.content}


def application_strategy(state: JobAgentState):
    llm = get_llm()
    prompt = f"""
You are a career strategy agent.

Based on the job requirements, resume analysis, and gap analysis,
decide the best application strategy for the candidate.

Job Requirements:
{state["jd_requirements"]}

Resume Analysis:
{state["resume_analysis"]}

Gap Analysis:
{state["gap_analysis"]}

Generate:
1. Application Priority: High / Medium / Low
2. Key reasons
3. Suggested actions before applying
4. Learning recommendations
5. How the candidate should position themselves

Keep the output concise, practical, and easy to present.
"""
    response = llm.invoke(prompt)
    return {"application_strategy": response.content}


def generate_cover_letter(state: JobAgentState):
    llm = get_llm()
    prompt = f"""
You are a professional cover letter writing agent.

Based on the following information, write a tailored cover letter.

Job Requirements:
{state["jd_requirements"]}

Resume Analysis:
{state["resume_analysis"]}

Gap Analysis:
{state["gap_analysis"]}

Application Strategy:
{state["application_strategy"]}

Requirements:
- Professional tone
- Around 250 words
- Do not invent fake experience
- Emphasize the candidate's relevant strengths
- Make it specific to this job

Return only the cover letter.
"""
    response = llm.invoke(prompt)
    return {"cover_letter": response.content}


def verification_safety_check(state: JobAgentState):
    llm = get_llm()
    prompt = f"""
You are a verification and safety agent for a job application workflow.

Use the resume evidence, job requirements, gap analysis, and cover letter below.

Resume Text:
{state["resume_text"]}

Job Requirements:
{state["jd_requirements"]}

Gap Analysis:
{state["gap_analysis"]}

Cover Letter:
{state["cover_letter"]}

Check:
1. Which cover letter skills or claims are directly supported by the resume
2. Any claims that are weakly supported or should be softened
3. Whether the draft invents experience the candidate does not have
4. Real skill gaps versus presentation gaps
5. Whether the candidate appears underqualified and needs an honest warning
6. Privacy note: PDF parsing is local, but LLM reasoning may call a cloud API

Return concise bullet points. Be strict and do not overstate the candidate.
"""
    response = llm.invoke(prompt)
    return {"verification_safety_check": response.content}


def estimate_token_count(*texts: str) -> int:
    combined = "\n".join(text or "" for text in texts)
    return max(1, len(combined) // 4)


def extract_match_score(text: Optional[str]) -> Optional[int]:
    if not text:
        return None

    patterns = [
        r"match\s*score[^0-9]{0,20}(\d{1,3})\s*/\s*100",
        r"(\d{1,3})\s*/\s*100",
        r"(\d{1,3})\s*%",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            score = int(match.group(1))
            if 0 <= score <= 100:
                return score
    return None


def cost_benefit_analysis(state: JobAgentState):
    input_tokens = estimate_token_count(state["resume_text"], state["job_description"])
    output_tokens = estimate_token_count(
        state["jd_requirements"],
        state["resume_analysis"],
        state["gap_analysis"],
        state["application_strategy"],
        state["cover_letter"],
        state["verification_safety_check"],
    )
    total_tokens = input_tokens + output_tokens
    estimated_api_cost = total_tokens * 0.000002
    match_score = extract_match_score(state["gap_analysis"])
    score_text = f"{match_score}/100" if match_score is not None else "Not reliably detected"

    analysis = f"""
**Agentic Autonomy**
- This system is not a single-turn chatbot. It runs a multi-step workflow: job description analysis, resume analysis, gap analysis, application strategy, cover letter drafting, verification, and final reporting.
- Each step passes structured context to the next step, which makes the output easier to inspect and debug.

**Profit Logic**
- A job seeker can turn a resume and job description into a structured application report in minutes instead of spending 1-2 hours manually tailoring a resume and cover letter.
- As a SaaS workflow, it could support pay-per-report, monthly job-search subscriptions, or university career-service licensing.

**Trust & Robustness**
- The verification step checks whether cover letter claims are supported by resume evidence.
- The report separates real skill gaps from presentation gaps and warns when the candidate may be underqualified.
- The system explicitly avoids fake experience and over-packaging.

**Commercial Stress Test**
- Estimated run size: about {total_tokens:,} tokens ({input_tokens:,} input/context tokens and {output_tokens:,} generated/report tokens).
- Rough API cost estimate: about ${estimated_api_cost:.4f} per run using a conservative generic token-cost assumption. Actual cost depends on the provider and model pricing.
- Human alternative: 60-120 minutes of manual resume/JD analysis and cover letter tailoring. At $25/hour, that time is worth roughly $25-$50.
- Detected match score: {score_text}.
"""
    return {"cost_benefit_analysis": analysis.strip()}


def generate_final_report(state: JobAgentState):
    score = extract_match_score(state["gap_analysis"])
    score_text = f"{score}/100" if score is not None else "See Gap Analysis"
    final_report = f"""
==============================
AI JOB APPLICATION AGENT REPORT
==============================

[1] Overall Match Score

{score_text}

------------------------------

[2] Job Description Analysis

{state["jd_requirements"]}

------------------------------

[3] Resume Analysis

{state["resume_analysis"]}

------------------------------

[4] Gap Analysis

{state["gap_analysis"]}

------------------------------

[5] Application Strategy

{state["application_strategy"]}

------------------------------

[6] Cover Letter Draft

{state["cover_letter"]}

------------------------------

[7] Verification / Safety Check

{state["verification_safety_check"]}

------------------------------

[8] Cost-Benefit Analysis

{state["cost_benefit_analysis"]}
"""
    return {"final_report": final_report}


def build_graph():
    graph = StateGraph(JobAgentState)

    graph.add_node("analyze_jd", analyze_jd)
    graph.add_node("analyze_resume", analyze_resume)
    graph.add_node("gap_analysis", gap_analysis)
    graph.add_node("application_strategy", application_strategy)
    graph.add_node("generate_cover_letter", generate_cover_letter)
    graph.add_node("verification_safety_check", verification_safety_check)
    graph.add_node("cost_benefit_analysis", cost_benefit_analysis)
    graph.add_node("generate_final_report", generate_final_report)

    graph.add_edge(START, "analyze_jd")
    graph.add_edge("analyze_jd", "analyze_resume")
    graph.add_edge("analyze_resume", "gap_analysis")
    graph.add_edge("gap_analysis", "application_strategy")
    graph.add_edge("application_strategy", "generate_cover_letter")
    graph.add_edge("generate_cover_letter", "verification_safety_check")
    graph.add_edge("verification_safety_check", "cost_benefit_analysis")
    graph.add_edge("cost_benefit_analysis", "generate_final_report")
    graph.add_edge("generate_final_report", END)

    return graph.compile()


def run_job_agent(
    resume_path: str = "resume.pdf",
    jd_text: Optional[str] = None,
    job_description_path: str = "job_description.txt",
    output_path: str = "agent_output.txt",
) -> str:
    if not os.getenv("DEEPSEEK_API_KEY"):
        raise ValueError(
            "Missing DEEPSEEK_API_KEY. Add it to your .env file before running the agent."
        )

    if not os.path.exists(resume_path):
        raise FileNotFoundError(f"Missing input file: {resume_path}")

    if jd_text is None:
        if not os.path.exists(job_description_path):
            raise FileNotFoundError(f"Missing input file: {job_description_path}")
        job_description = read_txt(job_description_path)
    else:
        job_description = jd_text.strip()
        with open(job_description_path, "w", encoding="utf-8") as file:
            file.write(job_description)

    resume_text = read_pdf(resume_path)

    if not resume_text:
        raise ValueError("The resume PDF is empty or cannot be read.")

    if not job_description:
        raise ValueError("The job description file is empty.")

    app = build_graph()

    result = app.invoke(
        {
            "resume_text": resume_text,
            "job_description": job_description,
            "jd_requirements": None,
            "resume_analysis": None,
            "gap_analysis": None,
            "application_strategy": None,
            "cover_letter": None,
            "verification_safety_check": None,
            "cost_benefit_analysis": None,
            "final_report": None,
        }
    )

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(result["final_report"])

    return result["final_report"]


if __name__ == "__main__":
    print("AI Job Application Agent Started")
    print("--------------------------------")
    print("Resume loaded from resume.pdf")
    print("Job description loaded from job_description.txt")
    print("Running agent workflow...")

    report = run_job_agent()

    print(report)
    print("Result saved to agent_output.txt")
