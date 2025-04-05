# Importing
from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import io
import bcrypt
import pdfplumber
from sentence_transformers import SentenceTransformer, util

# Load BERT model
model_ats = SentenceTransformer("all-MiniLM-L6-v2")

app = Flask(__name__)
CORS(app) # Avoid Blocking

# MongoDB connection
client = MongoClient(
    "mongodb+srv://denistanb05:eTopU4aZ67dDmSXb@hackathoncluster.8pkzngw.mongodb.net/?retryWrites=true&w=majority"
)
client = MongoClient(MONGO_URI)
db_user = client['Login']
users_collection = db_user['users']

# Initialize default user if collection is empty
def init_default_user():
    if users_collection.count_documents({}) == 0:
        hashed_password = bcrypt.hashpw('User@123'.encode('utf-8'), bcrypt.gensalt())
        default_user = {
            'username': 'user',
            'password': hashed_password.decode('utf-8')
        }
        users_collection.insert_one(default_user)

init_default_user()

# Login Check
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({'username': username})
    
    if not user:
        return jsonify({'success': False, 'error': 'username', 'message': 'User not found'}), 401
    
    if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'success': False, 'error': 'password', 'message': 'Incorrect password'}), 401
    
    return jsonify({'success': True, 'username': username})

# Register Storage
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if users_collection.find_one({'username': username}):
        return jsonify({'success': False, 'error': 'newUsername', 'message': 'Username already exists'}), 400

    # Password validation
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$'
    import re
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

# ATS
def extract_text_from_pdf(file):
    """Extract text from a PDF file object in memory."""
    text = ""
    try:
        # Use io.BytesIO to treat the file content as a file-like object in memory
        with pdfplumber.open(io.BytesIO(file.read())) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""
    return text.strip()

def generate_feedback(resume_text, job_description, model_score):
    """Generate friendly feedback based on resume, job description, and model score."""
    job_keywords = set(job_description.lower().split())
    resume_keywords = set(resume_text.lower().split())
    
    # Calculate key metrics
    missing_keywords = job_keywords - resume_keywords
    matching_keywords = job_keywords & resume_keywords
    match_percentage = (len(matching_keywords) / len(job_keywords)) * 100 if job_keywords else 0
    resume_word_count = len(resume_text.split())
    score_percentage = model_score * 100  # Convert model score (0-1) to percentage
    
    # Initialize feedback list
    feedback_parts = []

    # Feedback based on keyword match percentage
    if match_percentage >= 80:
        feedback_parts.append("Awesome! Your resume looks like a great fit for this job based on keywords.")
    elif match_percentage >= 50:
        feedback_parts.append("Nice work! Your resume is on the right track with keywords, but we can make it even better.")
    elif match_percentage >= 20:
        feedback_parts.append("You’ve got a start with keywords, but your resume could use some extra love to match this job.")
    else:
        feedback_parts.append("It looks like your resume might need more tailoring to match the job’s keywords.")

    # Feedback on missing keywords
    if missing_keywords:
        feedback_parts.append(f"Try sprinkling in these words to boost your fit: {', '.join(sorted(missing_keywords))}.")
    else:
        feedback_parts.append("You’ve nailed it—no important words are missing from the job description!")

    # Feedback on matching keywords
    if matching_keywords:
        feedback_parts.append(f"You’re already rocking words like {', '.join(sorted(list(matching_keywords)[:3]))}—keep it up!")
    else:
        feedback_parts.append("We couldn’t find any key words from the job in your resume yet.")

    # Feedback based on model score
    if score_percentage >= 80:
        feedback_parts.append("Fantastic! The deeper analysis shows your resume is a super strong match for this role.")
    elif score_percentage >= 60:
        feedback_parts.append("Good news! The analysis suggests your resume is a solid fit, with a little room to shine brighter.")
    elif score_percentage >= 40:
        feedback_parts.append("Not bad! The analysis sees some connection to the job, but tweaking it could lift your score.")
    else:
        feedback_parts.append("Heads up! The deeper analysis thinks your resume could use more work to align with this job.")

    # Feedback based on resume length
    if resume_word_count < 100:
        feedback_parts.append("Your resume’s a little short. Adding more details could help it stand out!")
    elif resume_word_count > 500:
        feedback_parts.append("Your resume’s pretty long. Shortening it a bit might make it easier to read.")
    else:
        feedback_parts.append("The length of your resume feels just right—nice balance!")

    # Combine feedback into a single string
    feedback = " ".join(feedback_parts)
    return feedback

def rank_resumes(resume_files, job_description):
    """Rank resumes based on similarity to the job description without saving to disk."""
    job_embedding = model_ats.encode(job_description, convert_to_tensor=True)
    resume_scores = {}
    resume_feedback = {}

    for file in resume_files:
        resume_text = extract_text_from_pdf(file)
        if not resume_text:
            print(f"Skipping {file.filename} (No text extracted)")
            continue

        resume_embedding = model_ats.encode(resume_text, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(job_embedding, resume_embedding)
        score = similarity.item()

        print(f"Resume: {file.filename} | Score: {score}")

        resume_scores[file.filename] = score
        resume_feedback[file.filename] = generate_feedback(resume_text, job_description, score)  # Pass score here

    ranked_resumes = sorted(resume_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked_resumes, resume_feedback

@app.route("/upload/", methods=["POST"])
def upload_files():
    """Handle file uploads and return ranking results without saving to disk."""
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

    print(f"Received files: {[file.filename for file in resumes]}")

    ranked_results, feedback_results = rank_resumes(resumes, job_description)

    if not ranked_results:
        return jsonify({"message": "No resumes analyzed. Please try again!"}), 400

    response = [{
        "resume": resume,
        "score": round(score * 100, 2),
        "feedback": feedback_results[resume]
    } for resume, score in ranked_results]

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
