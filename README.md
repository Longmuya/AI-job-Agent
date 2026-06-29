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
```
Installation
1. Clone the repository
git clone YOUR_GITHUB_REPOSITORY_LINK
cd AI-Job-Agent

Replace YOUR_GITHUB_REPOSITORY_LINK with the actual GitHub repository URL.

2. Create a virtual environment
python -m venv .venv

Activate the virtual environment:

For Windows:

.venv\Scripts\activate

For macOS / Linux:

source .venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
API Key Configuration

This project uses the DeepSeek API for large language model reasoning.

Create a .env file in the project root directory:

DEEPSEEK_API_KEY=your_api_key_here

Do not upload your .env file to GitHub, because it may contain private API keys.

How to Run

After installing dependencies and configuring the API key, run:

streamlit run app.py

Then open the local Streamlit URL shown in the terminal, usually:

http://localhost:8501
Usage
Upload a PDF resume.
Paste a target job description into the text box.
Click the generate button.
Wait for the LangGraph workflow to complete.
Review the generated report.
Expand each section to inspect the match score, gap analysis, application strategy, cover letter draft, safety check, and cost-benefit analysis.
Example Output

The prototype can generate a structured report containing:

Overall match score
Job description analysis
Resume analysis
Skill gap analysis
Application strategy
Tailored cover letter draft
Verification / safety check
Cost-benefit analysis

In the sample run, the system generated a match score of 78/100 and produced a complete application report.

Trust and Safety Design

AI Job Agent includes a verification / safety check node to reduce the risk of unsupported or exaggerated claims.

The system checks whether generated content is supported by the original resume, including:

Skills not mentioned in the resume
Tools or certificates not supported by evidence
Overstated experience
Job description keywords added without resume support

However, the current safety check still relies on language model judgement. Users should always review and revise the generated content before using it in real applications.

Limitations

This project is an early-stage prototype and has several limitations:

PDF parsing works best with text-based resumes
Scanned or image-based resumes may not be extracted correctly
Match scores are semantic estimates, not calibrated hiring predictions
The system uses cloud-based LLM reasoning, so resume text is sent to the API provider
The system has not yet been evaluated with large-scale real application outcomes
Claim-level evidence verification is planned but not fully implemented
Future Work

Future improvements may include:

OCR fallback for scanned resumes
Pydantic schemas for structured agent outputs
More transparent match score sub-components
Claim-level verification against resume evidence
User feedback collection
Application outcome tracking
B2B deployment for university career centres or training institutions
Demo Video

A 3-minute road-show demonstration video has been uploaded to the Canvas Group 15 discussion thread.

The video demonstrates:

Resume upload
Job description input
Report generation
Expandable report sections
Match score display
Verification / safety-check output
