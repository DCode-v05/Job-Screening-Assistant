# 🎯 Job Screening Assistant

**Job Screening Assistant** is a lightweight, AI-powered web application that simplifies and accelerates the hiring process by intelligently analyzing and comparing candidate resumes to job descriptions. This tool enables recruiters and HR professionals to make data-driven decisions and identify top talent with minimal manual effort.

---

## 🧠 What It Does

Recruiters often face the challenge of manually reviewing hundreds of resumes to find the most suitable candidates for a job role. This application automates that process by:

1. **Extracting Key Details** from uploaded resumes (PDF format).
2. **Analyzing Job Descriptions** to identify crucial skills, qualifications, and keywords.
3. **Matching Candidates** based on semantic similarity and keyword overlap.
4. **Scoring and Ranking** each candidate to help recruiters focus on the best fits.

---

## 🚀 Features

- ✅ **Resume Upload**: Drag-and-drop or browse to upload multiple candidate resumes.
- ✅ **Job Description Input**: Paste or upload a job description for analysis.
- ✅ **AI-Powered Matching**: Uses Natural Language Processing (NLP) to compare resumes and job roles intelligently.
- ✅ **Compatibility Score**: Provides a percentage-based match score for each candidate.
- ✅ **User-Friendly Web Interface**: Accessible and intuitive front-end built using HTML, CSS, and Flask.
- ✅ **Docker Support**: Easily deployable via Docker for consistent environments.

---

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Jinja2 templating via Flask)
- **Backend**: Python with Flask
- **NLP Libraries**: `spacy`, `sklearn`, `pdfminer.six` for resume parsing and analysis
- **Containerization**: Docker for deployment

---

## 🧬 How It Works

This application automates the screening of resumes against a job description by extracting content from uploaded PDF resumes and a job description text, analyzing them semantically, and computing a compatibility score to rank candidates.

### 1. 📝 Resume Parsing

- **PDF Extraction**: Resumes uploaded as PDF files are processed using `pdfplumber` to extract raw text from each page.
- **Text Concatenation**: Extracted text from all pages of a resume is combined into a single string for analysis.
- **Preprocessing**: The raw text is cleaned and prepared for embedding and keyword comparison.

### 2. 🧾 Job Description Input

- **Text Input**: Users provide the job description as plain text.
- **Preprocessing**: The job description text is cleaned and tokenized similarly to resumes.

### 3. 🧮 Semantic Matching Algorithm

- **Embedding Generation**: Both the job description and each resume’s text are converted into vector embeddings using the `SentenceTransformer` model (`all-MiniLM-L6-v2`), which captures semantic meaning.
- **Similarity Scoring**: Cosine similarity is computed between the job description embedding and each resume embedding to quantify semantic relevance.
- **Ranking**: Resumes are ranked based on their similarity scores, with higher scores indicating better matches.

### 4. 📝 Feedback Generation

- **Keyword Analysis**: The system compares keywords from the job description and each resume to identify missing or matching important terms.
- **Match Percentage**: Calculates the percentage of job description keywords found in the resume.
- **Personalized Feedback**: Provides tailored suggestions to improve the resume’s alignment with the job description, considering keyword matches, missing keywords, similarity score, and resume length.

### 5. 📊 Results Display

- **API Response**: Returns a JSON list of resumes with their compatibility scores and detailed feedback.
- **Frontend UI**: Flask routes render pages where users can upload resumes, enter job descriptions, and view results interactively.
- **User Management**: Supports user registration and login with hashed passwords stored securely in MongoDB.

---

## 📦 Installation

### 🔧 Local Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Denistanb/Job_Screening_Assistant.git
   cd Job_Screening_Assistant
2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
3. **Run the Application**
   ```bash
   python app.py
4. **View in Browser**
   ```bash
   http://localhost:5000

## 🐳 Docker Deployment

To ensure platform independence and ease of deployment, the app includes a Dockerfile.

### 🔨 Build Docker Image

```bash
docker build -t job_screening_assistant .
```

### ▶️ Run Docker Container
```bash
docker run -p 5000:5000 job_screening_assistant
```
