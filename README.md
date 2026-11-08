# Job Screening Assistant

A Flask app that ranks PDF resumes against a job description. You paste in the job description, upload a batch of resumes, and get them back sorted by match score with a short feedback note for each.

It was a team project (Team ISS057, "Deep Thinkers") and was deployed on Hugging Face Spaces, which is why the Dockerfile serves on port 7860.

## How it works

Everything is in `app.py`, with the pages in `templates/`.

1. `Resume_ATS.html` posts the job description and the PDFs to `POST /api/upload`. The route returns 400 if the description is missing, no files were sent, or a file isn't a `.pdf`.
2. Each PDF is read in memory with `pdfplumber`. A resume with no extractable text (for example a scanned image) is skipped and logged.
3. The job description and each resume are encoded with `all-MiniLM-L6-v2` (sentence-transformers). The cosine similarity between them, times 100 and rounded to two decimals, is the score.
4. `generate_feedback` adds a keyword pass. It splits both texts on whitespace, takes the overlap and difference, and writes messages based on the keyword match percentage, the semantic score band and the resume length (under 100 or over 500 words).
5. Results come back as a JSON array of `{resume, score, feedback}`, highest score first.

Login and registration (`/api/login`, `/api/register`) use MongoDB through `pymongo`, with bcrypt hashes. Registration requires at least 8 characters with upper case, lower case, a digit and one of `!@#$%^&*`. If the users collection is empty at startup, a default account `user` / `User@123` is created.

There is no labelled data, so no accuracy numbers.

## Stack

Python 3.10, Flask, Flask-CORS, gunicorn, sentence-transformers, PyTorch, pdfplumber, pymongo, bcrypt, Docker.

## Setup

Set `MONGO_URI` in `app.py` (it is currently the placeholder `YOUR_MONGODB_URI`). Login, registration and the default-user seeding need a working MongoDB connection.

```bash
pip install -r requirements.txt
python app.py
```

The server listens on port 5000 unless `PORT` is set. The first run downloads the MiniLM model.

With Docker:

```bash
docker build -t job-screening-assistant .
docker run -p 7860:7860 job-screening-assistant
```

The HTML pages in `templates/` call the deployed Hugging Face Space (`denistan2005-job-screening-assistant.hf.space`) for the API and for page links, not the local server. To use the UI against your own instance, replace those URLs in `Resume_ATS.html`, `home.html` and `index.html`.

You can also call the API directly:

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "job_description=Python developer with Flask and SQL experience" \
  -F "resumes=@resume1.pdf" -F "resumes=@resume2.pdf"
```

## Structure

```
app.py           Flask app, scoring, feedback, auth
templates/       index (login), home, Resume_ATS pages and logo
Dockerfile
requirements.txt
```

## Limitations

Keyword matching is whitespace-based with no stop-word handling, so the "missing keywords" list is noisy. The Mongo connection is created with `tlsAllowInvalidCertificates=True`.
