# Job Screening Assistant

**An ATS-style resume analyzer that ranks a stack of PDF resumes against a job description using sentence-embedding similarity, then explains each score in plain language.**

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask&logoColor=white) ![sentence-transformers](https://img.shields.io/badge/sentence--transformers-MiniLM-FFD21E?style=flat&logo=huggingface&logoColor=black) ![PyTorch](https://img.shields.io/badge/PyTorch-2.2-EE4C2C?style=flat&logo=pytorch&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat&logo=mongodb&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

## Overview

Recruiters end up reading the same handful of resumes over and over to figure out who actually fits a role. This is a small Flask web app that does the first pass for them: you paste in a job description, upload a batch of PDF resumes, and it scores and ranks each candidate by how closely their resume matches the job — semantically, not just by keyword grepping.

Under the hood it embeds the job description and every resume with a sentence-transformer model and ranks them by cosine similarity, then layers a keyword-overlap pass on top to write human-readable feedback for each resume ("you're missing these words", "tighten the length", etc.). It was built as a team project (Team ISS057 / "Deep Thinkers") and ships with a Dockerfile tuned for Hugging Face Spaces, where it was deployed.

## Key Features

- **Batch PDF upload** — drop in multiple resumes at once; each is validated to be a `.pdf` before processing.
- **Semantic matching** — job description and resumes are turned into embeddings with `all-MiniLM-L6-v2` and compared by cosine similarity, so a candidate who says "built REST APIs" still scores against a JD asking for "web services."
- **Ranked results** — resumes come back sorted high-to-low by match score (0–100), so the strongest candidates float to the top.
- **Per-resume feedback** — alongside the score, every resume gets tailored notes: keyword match percentage, which job keywords are missing, which ones already hit, and whether the resume is too short or too long.
- **User accounts** — registration and login backed by MongoDB, with passwords hashed using bcrypt and a password-strength regex (min 8 chars, upper + lower + digit + special).
- **JSON API** — `/api/upload` returns structured results, so the scoring engine can be called from the bundled UI or any other client.
- **Containerized** — a Dockerfile builds the whole thing (model deps included) and serves it under gunicorn, ready for Hugging Face Spaces or any container host.
- **Connection health check** — every page render pings MongoDB and surfaces a connected/disconnected status, which makes deployment debugging less of a guessing game.

## How It Works

The whole flow is a single Flask app (`app.py`) with a static front-end in `templates/`. The model is loaded once at startup so requests don't pay the load cost.

### 1. Input

The front-end (`Resume_ATS.html`) collects a job description as plain text and one or more resume files, then POSTs them as multipart form data to `/api/upload`. The route rejects the request early if the job description is missing, no files were sent, or any file isn't a PDF.

### 2. Resume parsing

Each uploaded PDF is read in-memory with `pdfplumber` — every page's text is extracted and concatenated into one string. Files that yield no extractable text (e.g. scanned image-only resumes) are skipped and logged rather than crashing the batch.

### 3. Semantic scoring

The job description is encoded once into an embedding with `SentenceTransformer("all-MiniLM-L6-v2")`. Each resume's text is encoded the same way, and `util.pytorch_cos_sim` computes cosine similarity between the JD embedding and each resume embedding. That similarity (a float in roughly 0–1) becomes the candidate's raw score; it's multiplied by 100 and rounded to two decimals for display.

### 4. Feedback generation

Scoring alone doesn't tell a candidate *why* they ranked where they did, so `generate_feedback` runs a separate keyword pass:

- It lowercases and tokenizes both the JD and the resume, then computes the set intersection (matching keywords) and difference (missing keywords).
- From that it derives a keyword match percentage and writes graded messages at the 80% / 50% / 20% thresholds.
- It cross-references the semantic score (80% / 60% / 40% bands) to comment on the deeper match.
- It checks resume word count and flags resumes under ~100 words as too thin or over ~500 as too long.

All of those snippets are joined into one feedback paragraph per resume.

### 5. Ranking and response

Resumes are sorted by score descending and returned as a JSON array of `{ resume, score, feedback }`. The front-end renders that into a results list with a score and a feedback line per candidate.

### Accounts and persistence

Login and registration (`/api/login`, `/api/register`) live in the same app and talk to MongoDB via `pymongo`. Passwords are hashed with bcrypt; registration validates strength with a regex before storing. On first boot the app seeds a default account (`user` / `User@123`) if the users collection is empty, so there's always a way in during testing.

## Highlights

- **Model:** `all-MiniLM-L6-v2` sentence-transformer, loaded once at startup.
- **Scoring:** cosine similarity × 100, rounded to 2 decimals; resumes ranked per request with no fixed cap.
- **Two-signal feedback:** combines semantic similarity with raw keyword overlap so the advice isn't a black box.
- **Deployment target:** the bundled UI points at a Hugging Face Spaces endpoint (`denistan2005-job-screening-assistant.hf.space`), and the Dockerfile is wired for the Spaces convention (gunicorn on port 7860).

This is an unsupervised similarity tool — there's no labeled test set, so there are no accuracy/F1 numbers to quote, and intentionally so.

## Tech Stack

- **Language:** Python 3.10
- **Web framework:** Flask 3.0 + Jinja2 templates, Flask-CORS, served with gunicorn
- **NLP / ML:** sentence-transformers 2.5 (`all-MiniLM-L6-v2`), PyTorch 2.2, Hugging Face transformers 4.38
- **PDF parsing:** pdfplumber
- **Database / auth:** MongoDB via pymongo, bcrypt for password hashing
- **Front-end:** HTML, CSS, vanilla JavaScript
- **Infra:** Docker (Python 3.10-slim base), deployed on Hugging Face Spaces

## Getting Started

### Prerequisites

- Python 3.10+
- pip
- A MongoDB connection string (Atlas or self-hosted) — login, registration, and the default-user seeding all need it
- Docker (optional, for the containerized path)

### Installation

```bash
git clone https://github.com/DCode-v05/Job-Screening-Assistant.git
cd Job-Screening-Assistant
pip install -r requirements.txt
```

Before running, set your MongoDB URI. In `app.py` the `MONGO_URI` value ships as the placeholder `"YOUR_MONGODB_URI"`; replace it with a real connection string (or wire it to an environment variable) or the database-backed features won't connect.

### Running locally

```bash
python app.py
```

This starts Flask on `http://localhost:5000`. The first run downloads the MiniLM model into the Hugging Face cache.

### Running with Docker

```bash
docker build -t job-screening-assistant .
docker run -p 7860:7860 job-screening-assistant
```

The container serves the app with gunicorn on port 7860 (matching the Hugging Face Spaces convention), so visit `http://localhost:7860`.

## Usage

1. Open the app and log in, or register a new account (or use the seeded `user` / `User@123` if MongoDB is connected).
2. Go to the Resume Analyzer page.
3. Paste the job description into the text box.
4. Select one or more PDF resumes to upload.
5. Submit. You get back a ranked list — each candidate with a 0–100 match score and a short feedback note on keyword fit, semantic match, and resume length.

To call the scoring engine directly:

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "job_description=Backend engineer with Python and REST API experience" \
  -F "resumes=@alice.pdf" \
  -F "resumes=@bob.pdf"
```

The response is a JSON array sorted best-match-first.

## Project Structure

```
Job-Screening-Assistant/
├── app.py                   # Flask app: routes, PDF parsing, SBERT scoring, feedback, auth
├── requirements.txt         # Python dependencies (Flask, sentence-transformers, torch, pymongo, ...)
├── Dockerfile               # Python 3.10-slim image; gunicorn on port 7860
├── README.md                # Project docs
└── templates/
    ├── index.html           # Login / register page
    ├── home.html            # Landing page ("Deep Thinkers") linking to the analyzer
    ├── Resume_ATS.html      # Analyzer UI: JD input, multi-PDF upload, results view
    └── logo.png             # Project logo
```

---

## Contact

<table>
  <tr><td><b>Portfolio:</b> <a href="https://www.denistan.me">Denistan</a></td><td><b>LinkedIn:</b> <a href="https://www.linkedin.com/in/denistanb">denistanb</a></td></tr>
  <tr><td><b>GitHub:</b> <a href="https://github.com/DCode-v05">DCode-v05</a></td><td><b>LeetCode:</b> <a href="https://leetcode.com/u/Denistan_B">Denistan_B</a></td></tr>
  <tr><td colspan="2" align="center"><b>Email:</b> <a href="mailto:denistanb05@gmail.com">denistanb05@gmail.com</a></td></tr>
</table>

Made with ❤️ by **Denistan B**
