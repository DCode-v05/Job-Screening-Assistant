from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from flask_cors import CORS
import io
import bcrypt
import pdfplumber
from sentence_transformers import SentenceTransformer, util
import os
import re
import warnings
import logging
import time

# Suppress the FutureWarning from huggingface_hub
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub.file_download")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load BERT model
model_ats = SentenceTransformer("all-MiniLM-L6-v2")

app = Flask(__name__)
CORS(app)  # Avoid Blocking

# MongoDB connection
MONGO_URI = "mongodb+srv://denistanb05:deni123@resumeanalyzer.vtti10v.mongodb.net/"
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True,  # Temporary for debugging
    serverSelectionTimeoutMS=60000,
    connectTimeoutMS=60000,
    socketTimeoutMS=60000,
    retryWrites=True,
    retryReads=True
)

try:
    client.server_info()  # Test connection
    logger.info("MongoDB connection successful.")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")

db_user = client['Login']
users_collection = db_user['users']

# Initialize default user if collection is empty
def init_default_user():
    try:
        if users_collection.count_documents({}, maxTimeMS=60000) == 0:
            hashed_password = bcrypt.hashpw('User@123'.encode('utf-8'), bcrypt.gensalt())
            default_user = {
                'username': 'user',
                'password': hashed_password.decode('utf-8')
            }
            users_collection.insert_one(default_user)
            logger.info("Default user initialized successfully.")
        else:
            logger.info("Default user already exists.")
    except Exception as e:
        logger.error(f"Error initializing default user: {e}")

init_default_user()

# Root route to serve index.html (login page)
@app.route('/', methods=['GET'])
def index():
    try:
        client.server_info()  # Test MongoDB connection
        mongo_status = "MongoDB: Connected"
    except Exception as e:
        mongo_status = f"MongoDB: Disconnected - {str(e)}"
    return render_template('index.html', mongo_status=mongo_status)

# Home route to serve home.html
@app.route('/home', methods=['GET'])
def home():
    try:
        client.server_info()  # Test MongoDB connection
        mongo_status = "MongoDB: Connected"
    except Exception as e:
        mongo_status = f"MongoDB: Disconnected - {str(e)}"
    return render_template('home.html', mongo_status=mongo_status)

# Resume Analyzer route
@app.route('/resume-analyzer', methods=['GET'])
def resume_analyzer():
    try:
        client.server_info()  # Test MongoDB connection
        mongo_status = "MongoDB: Connected"
    except Exception as e:
        mongo_status = f"MongoDB: Disconnected - {str(e)}"
    return render_template('Resume_ATS.html', mongo_status=mongo_status)

# Login Check
@app.route('/api/login', methods=['POST'])
def login():
    logger.info(f"Received login request: {request.get_json()}")
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        user = users_collection.find_one({'username': username})
        if not user:
            return jsonify({'success': False, 'error': 'username', 'message': 'User not found'}), 401
        
        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'success': False, 'error': 'password', 'message': 'Incorrect password'}), 401
        
        return jsonify({'success': True, 'username': username})
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'error': 'server', 'message': 'Database connection error'}), 500

# Register Storage
@app.route('/api/register', methods=['POST'])
def register():
    logger.info(f"Received register request: {request.get_json()}")
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        if users_collection.find_one({'username': username}):
            return jsonify({'success': False, 'error': 'newUsername', 'message': 'Username already exists'}), 400

        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$'
        if not re.match(password_regex, password):
            return jsonify({
                'success': False,
                'error': 'newPassword',
                'message': 'Password must be at least 8 characters and contain one uppercase, one lowercase, one number, and one special character (!@#$%^&*)'
            }), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = {
            'username': username,
            'password': hashed_password.decode('utf-8')
        }
        
        users_collection.insert_one(new_user)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Register error: {e}")
        return jsonify({'success': False, 'error': 'server', 'message': 'Database connection error'}), 500

# ATS Functions
def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file.read())) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return ""
    return text.strip()

def generate_feedback(resume_text, job_description, model_score):
    job_keywords = set(job_description.lower().split())
    resume_keywords = set(resume_text.lower().split())
    
    missing_keywords = job_keywords - resume_keywords
    matching_keywords = job_keywords & resume_keywords
    match_percentage = (len(matching_keywords) / len(job_keywords)) * 100 if job_keywords else 0
    resume_word_count = len(resume_text.split())
    score_percentage = model_score * 100
    
    feedback_parts = []

    if match_percentage >= 80:
        feedback_parts.append("Awesome! Your resume looks like a great fit for this job based on keywords.")
    elif match_percentage >= 50:
        feedback_parts.append("Nice work! Your resume is on the right track with keywords, but we can make it even better.")
    elif match_percentage >= 20:
        feedback_parts.append("You’ve got a start with keywords, but your resume could use some extra love to match this job.")
    else:
        feedback_parts.append("It looks like your resume might need more tailoring to match the job’s keywords.")

    if missing_keywords:
        feedback_parts.append(f"Try sprinkling in these words to boost your fit: {', '.join(sorted(missing_keywords))}.")
    else:
        feedback_parts.append("You’ve nailed it—no important words are missing from the job description!")

    if matching_keywords:
        feedback_parts.append(f"You’re already rocking words like {', '.join(sorted(list(matching_keywords)[:3]))}—keep it up!")
    else:
        feedback_parts.append("We couldn’t find any key words from the job in your resume yet.")

    if score_percentage >= 80:
        feedback_parts.append("Fantastic! The deeper analysis shows your resume is a super strong match for this role.")
    elif score_percentage >= 60:
        feedback_parts.append("Good news! The analysis suggests your resume is a solid fit, with a little room to shine brighter.")
    elif score_percentage >= 40:
        feedback_parts.append("Not bad! The analysis sees some connection to the job, but tweaking it could lift your score.")
    else:
        feedback_parts.append("Heads up! The deeper analysis thinks your resume could use more work to align with this job.")

    if resume_word_count < 100:
        feedback_parts.append("Your resume’s a little short. Adding more details could help it stand out!")
    elif resume_word_count > 500:
        feedback_parts.append("Your resume’s pretty long. Shortening it a bit might make it easier to read.")
    else:
        feedback_parts.append("The length of your resume feels just right—nice balance!")

    feedback = " ".join(feedback_parts)
    return feedback

def rank_resumes(resume_files, job_description):
    job_embedding = model_ats.encode(job_description, convert_to_tensor=True)
    resume_scores = {}
    resume_feedback = {}

    for file in resume_files:
        resume_text = extract_text_from_pdf(file)
        if not resume_text:
            logger.info(f"Skipping {file.filename} (No text extracted)")
            continue

        resume_embedding = model_ats.encode(resume_text, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(job_embedding, resume_embedding)
        score = similarity.item()

        logger.info(f"Resume: {file.filename} | Score: {score}")

        resume_scores[file.filename] = score
        resume_feedback[file.filename] = generate_feedback(resume_text, job_description, score)

    ranked_resumes = sorted(resume_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked_resumes, resume_feedback

@app.route("/upload/", methods=["POST"])
def upload_files():
    logger.info(f"Received upload request: {request.form}")
    if "job_description" not in request.form:
        return jsonify({"message": "Job description is required"}), 400

    job_description = request.form["job_description"]
    if "resumes" not in request.files:
        return jsonify({"message": "No resumes uploaded"}), 400

    resumes = request.files.getlist("resumes")
    if not resumes or all(file.filename == "" for file in resumes):
        return jsonify({"message": "No resumes uploaded"}), 400

    for file in resumes:
        if not file or not file.filename.endswith(".pdf"):
            return jsonify({"message": "Please upload only PDF files"}), 400

    logger.info(f"Received files: {[file.filename for file in resumes]}")

    ranked_results, feedback_results = rank_resumes(resumes, job_description)

    if not ranked_results:
        return jsonify({"message": "No resumes analyzed. Please try again!"}), 400

    response = [{
        "resume": resume,
        "score": round(score * 100, 2),
        "feedback": feedback_results[resume]
    } for resume, score in ranked_resumes]

    return jsonify(response)

# Local testing only (ignored when running with Gunicorn)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
