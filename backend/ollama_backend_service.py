# ollama_backend_service.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import pdfplumber
import docx2txt
from werkzeug.utils import secure_filename
from datetime import datetime

try:
    import pypdf
except ImportError:
    pypdf = None
    print("Warning: 'pypdf' not found. Install it: pip install pypdf")

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
HISTORY_FILE = 'resume_analysis_history.json'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
OLLAMA_API_URL = "http://ollama.com/api/generate"
MODEL_NAME = "llama3" 

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Helper Functions ---
def load_history_data():
    if not os.path.exists(HISTORY_FILE):
        return {"single": [], "batch": []}
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"single": [], "batch": []}

def save_to_history(category, record):
    data = load_history_data()
    record['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if category in data:
        data[category].insert(0, record)
    else:
        data[category] = [record]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    text = ""
    try:
        if ext == 'pdf':
            try:
                with pdfplumber.open(filepath) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted: text += extracted + "\n"
            except Exception as e:
                if pypdf:
                    try:
                        reader = pypdf.PdfReader(filepath)
                        for page in reader.pages:
                            extracted = page.extract_text()
                            if extracted: text += extracted + "\n"
                    except: return None 
                else: return None
        elif ext == 'docx':
            text = docx2txt.process(filepath)
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
    except: return None
    return text if text and text.strip() else None

def query_ollama(prompt, json_mode=True):
    payload = { "model": MODEL_NAME, "prompt": prompt, "stream": False, "format": "json" if json_mode else "" }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        return response.json().get('response', '')
    except: return None

# --- Routes ---

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(load_history_data())

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clears the history file."""
    empty_data = {"single": [], "batch": []}
    with open(HISTORY_FILE, 'w') as f:
        json.dump(empty_data, f, indent=4)
    return jsonify({"status": "success"})

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    if 'resume' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['resume']
    if file.filename == '' or not allowed_file(file.filename): return jsonify({"error": "Invalid file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    text = extract_text_from_file(filepath)
    if not text:
        os.remove(filepath)
        return jsonify({"error": "Corrupted file"}), 500

    prompt = f"""
    You are an expert ATS. Analyze this resume.
    Return raw JSON: {{ "ats_score": <0-100>, "skills": [], "summary": "", "improvements": [] }}
    Resume: {text[:4000]} 
    """ 
    resp = query_ollama(prompt)
    if os.path.exists(filepath): os.remove(filepath)
    try:
        data = json.loads(resp.replace('```json', '').replace('```', '').strip())
        save_to_history('single', {"filename": filename, "analysis": data})
        return jsonify(data)
    except: return jsonify({"error": "AI Error"}), 500

@app.route('/analyze_batch', methods=['POST'])
def analyze_batch():
    files = request.files.getlist('resumes')
    # Use top_n from form for history only, we return all data to frontend
    top_n_req = int(request.form.get('top_n', 10))
    
    # New Filters
    role = request.form.get('role', 'Any')
    main_lang = request.form.get('main_language', 'None')
    candidate_type = request.form.get('candidate_type', 'any')
    prefers_projects = request.form.get('prefers_projects', 'no')
    exp_years = request.form.get('exp_years', '0')

    results = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            text = extract_text_from_file(filepath)
            
            if text:
                # BRUTAL SCORING RULES
                rules = []
                rules.append(f"1. TARGET ROLE: {role}. CRITICAL: If resume is for a different role (e.g., Marketing vs Developer), SCORE = 0.")
                
                if main_lang and main_lang.lower() != 'none' and main_lang.strip() != '':
                    rules.append(f"2. MAIN LANGUAGE: {main_lang}. CRITICAL: Candidate MUST know {main_lang}. If {main_lang} is missing or weak, Max Score = 40.")
                
                if candidate_type == 'fresher':
                    rules.append("3. TYPE: Fresher. Penalize if no Projects/Hackathons/Internships are listed.")
                    if prefers_projects == 'yes':
                        rules.append("   - HR PREFERENCE: Projects are MANDATORY. High score requires significant project work.")
                elif candidate_type == 'professional':
                    rules.append(f"3. TYPE: Professional. REQUIREMENT: Approx {exp_years} years experience. Penalize significantly if experience is far below.")
                
                rule_text = "\n".join(rules)

                prompt = f"""
                Act as a STRICT & BRUTAL Technical Recruiter. Rate this resume (0-100) based ONLY on these constraints:
                {rule_text}
                
                SCORING MATRIX:
                - 90-100: Perfect Fit (Matches Role + Strong {main_lang} + Exact Experience/Projects).
                - 75-89: Good Fit (Matches Role + Good {main_lang}, minor experience gap).
                - 50-74: Average (Matches Role, but weak {main_lang} or lacks sufficient depth).
                - < 50: Weak (Matches Role but missing key skills like {main_lang}).
                - 0: WRONG ROLE (Instant Reject).
                
                Return JSON only: {{ "score": <0-100 int>, "summary": "<reason for score>" }}
                Resume Text: {text[:3500]}
                """
                
                resp = query_ollama(prompt)
                try:
                    data = json.loads(resp.replace('```json', '').replace('```', '').strip())
                    results.append({"filename": filename, "score": data.get('score', 0), "summary": data.get('summary', '')})
                except: results.append({"filename": filename, "score": 0, "summary": "Analysis Error"})
            else: results.append({"filename": filename, "score": 0, "summary": "Error: File Corrupted"})
            if os.path.exists(filepath): os.remove(filepath)

    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Save top N to history
    final_results = results[:top_n_req]
    save_to_history('batch', {"type": "fast", "files_processed": len(files), "top_n_requested": top_n_req, "results": final_results})
    
    # Return ALL results so frontend can split Top vs Good vs Rejected
    return jsonify(results)

if __name__ == '__main__':
    print(f"Starting Backend... Model: {MODEL_NAME}")
    app.run(debug=True, port=5000)