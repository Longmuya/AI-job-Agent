# AI Job Agent

AI Job Agent is a LangGraph-based compound AI system for job application support.  
It helps users analyse the match between a resume and a target job description, generate a structured application report, and produce a tailored cover letter draft.

This project is designed as a small AI agent prototype. It does not automatically submit job applications. Instead, it works as a human-in-the-loop decision-support tool, allowing users to review, revise, and decide whether to use the generated suggestions.

---

## Features

- Upload a PDF resume through a Streamlit web interface
- Input a target job description
- Extract resume text using `pypdf`
- Analyse job requirements and candidate background
- Generate a match score and skill gap analysis
- Provide application strategy suggestions
- Generate a tailored cover letter draft
- Run a verification / safety check to identify unsupported or overstated claims
- Display the final report in expandable sections
- Estimate basic cost-benefit information such as token usage and time saving

---

## System Architecture

The system contains three main layers:

1. **User Interaction Layer**  
   Implemented with Streamlit. Users can upload a resume, enter a job description, and view the generated report.

2. **Document Processing Layer**  
   Uses `pypdf` to extract text from the uploaded PDF resume.

3. **Agent Workflow Layer**  
   Uses LangGraph to organise the job application process into multiple nodes, including:

   - Job description analysis
   - Resume analysis
   - Gap analysis
   - Application strategy generation
   - Cover letter generation
   - Verification and safety checking
   - Cost-benefit analysis
   - Final report generation

---

## Project Structure

```text
AI-Job-Agent/
│
├── app.py                  # Streamlit frontend
├── main.py                 # LangGraph agent workflow
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── resume.pdf              # Sample resume for testing
├── job_description.txt     # Sample job description for testing
├── agent_output.txt        # Example generated output
└── .gitignore              # Files ignored by Git
