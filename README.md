# Job Screening Assistant

## Project Description
Job Screening Assistant is an AI-powered web application designed to streamline and automate the resume screening process for recruiters and HR professionals. By leveraging advanced Natural Language Processing (NLP) techniques, the application analyzes and compares candidate resumes against job descriptions, providing data-driven insights and compatibility scores to identify top talent efficiently.

---

## Project Details

### Overview
Recruiters often face the challenge of manually reviewing large volumes of resumes to find suitable candidates. Job Screening Assistant automates this process by:
- Extracting and parsing key details from uploaded PDF resumes.
- Analyzing job descriptions to identify essential skills, qualifications, and keywords.
- Matching candidates using semantic similarity and keyword overlap.
- Scoring and ranking candidates to highlight the best fits.

### Core Features
- **Resume Upload:** Upload multiple candidate resumes in PDF format.
- **Job Description Input:** Paste or upload a job description for analysis.
- **AI-Powered Matching:** Utilizes NLP models to compare resumes and job requirements.
- **Compatibility Score:** Provides a percentage-based match score for each candidate.
- **Detailed Feedback:** Offers personalized suggestions to improve resume alignment.
- **User Management:** Supports user registration and login with secure password storage.
- **Web Interface:** Intuitive front-end built with Flask and Jinja2 templates.
- **Docker Support:** Easily deployable using Docker for consistent environments.

## How It Works

This application automates the screening of resumes against a job description by extracting content from uploaded PDF resumes and a job description text, analyzing them semantically, and computing a compatibility score to rank candidates.

### 1. Resume Parsing

- **PDF Extraction**: Resumes uploaded as PDF files are processed using `pdfplumber` to extract raw text from each page.
- **Text Concatenation**: Extracted text from all pages of a resume is combined into a single string for analysis.
- **Preprocessing**: The raw text is cleaned and prepared for embedding and keyword comparison.

### 2. Job Description Input

- **Text Input**: Users provide the job description as plain text.
- **Preprocessing**: The job description text is cleaned and tokenized similarly to resumes.

### 3. Semantic Matching Algorithm

- **Embedding Generation**: Both the job description and each resume’s text are converted into vector embeddings using the `SentenceTransformer` model (`all-MiniLM-L6-v2`), which captures semantic meaning.
- **Similarity Scoring**: Cosine similarity is computed between the job description embedding and each resume embedding to quantify semantic relevance.
- **Ranking**: Resumes are ranked based on their similarity scores, with higher scores indicating better matches.

### 4. Feedback Generation

- **Keyword Analysis**: The system compares keywords from the job description and each resume to identify missing or matching important terms.
- **Match Percentage**: Calculates the percentage of job description keywords found in the resume.
- **Personalized Feedback**: Provides tailored suggestions to improve the resume’s alignment with the job description, considering keyword matches, missing keywords, similarity score, and resume length.

### 5. Results Display

- **API Response**: Returns a JSON list of resumes with their compatibility scores and detailed feedback.
- **Frontend UI**: Flask routes render pages where users can upload resumes, enter job descriptions, and view results interactively.
- **User Management**: Supports user registration and login with hashed passwords stored securely in MongoDB.


---

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript (Jinja2 templating via Flask)
- **Backend:** Python (Flask)
- **NLP Libraries:** spaCy, scikit-learn, pdfplumber, sentence-transformers, torch, transformers
- **Database:** MongoDB (for user management)
- **Containerization:** Docker

---

## Getting Started

### Prerequisites
- Python 3.8+
- pip
- Docker (optional, for containerized deployment)

### Installation
1. **Clone the Repository**
   ```bash
   git clone https://github.com/TensoRag/Job-Screening-Assistant.git
   cd Job-Screening-Assistant
   ```
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Application**
   ```bash
   python app.py
   ```
4. **Access the App**
   Open your browser and go to: [http://localhost:5000](http://localhost:5000)

### Docker Deployment
1. **Build Docker Image**
   ```bash
   docker build -t job_screening_assistant .
   ```
2. **Run Docker Container**
   ```bash
   docker run -p 5000:5000 job_screening_assistant
   ```

---

## Usage
- Navigate to the home page.
- Register or log in as a user.
- Upload one or more PDF resumes.
- Paste or upload a job description.
- Submit to receive compatibility scores and detailed feedback for each candidate.

---

## Project Structure
```
Job-Screening-Assistant/
  ├── app.py                # Main Flask application
  ├── requirements.txt      # Python dependencies
  ├── Dockerfile            # Docker configuration
  ├── README.md             # Project documentation
  └── templates/            # HTML templates and static assets
      ├── home.html
      ├── index.html
      ├── Resume_ATS.html
      └── logo.png
```

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request describing your changes.
   
---

## Contact
- **GitHub:** [https://github.com/TensoRag](https://github.com/TensoRag)
- **Email:** denistanb05@gmail.com
