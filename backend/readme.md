**Mock AI Interview - Resume Analyzer Module**
This module uses a local LLM (Ollama) to analyze resumes and rank candidates for HR.

**1. Prerequisites**
Before running, ensure you have the following installed:

--> Python 3.8+
--> Ollama (Download from ollama.com)
--> Llama 3 Model (Run ollama run llama3 in terminal)

**2. Installation**
Open your terminal in the backend folder and install the required Python libraries.
Note: pypdf is critical for reading PDF files correctly.

--> pip install flask flask-cors requests pdfplumber docx2txt pypdf

**3. Folder Structure Confirmation**
Ensure your files are placed as follows:

--> frontend/job_analyzer_interface.html
--> frontend/dashboard.html (Your main app)
--> backend/ollama_backend_service.py

**4. How to Run**

**Step 1:**:- Start the AI Backend

--> Open a terminal.
--> Navigate to the backend folder:
--> cd backend

**Run the service:**

--> python ollama_backend_service.py

**You should see: Running on http://127.0.0.1:5000. Keep this terminal open.**

**Step 2:**:- Start the Frontend

--> Navigate to the frontend folder.
--> Open job_analyzer_interface.html in your browser (or use Live Server in VS Code).
--> The "Back to Dashboard" button will look for dashboard.html in the same folder.

**5. Troubleshooting**

Error: "Unexpected EOF" or "Stream ended unexpectedly"

--> This means a PDF file is corrupted or complex.

**--> Fix: Ensure you have installed pypdf (pip install pypdf). The backend is designed to automatically switch to pypdf if the primary reader fails.**

Error: "Ollama connection error"

This means the AI is not running.
Fix: Open a separate terminal and type ollama serve or ensure the Ollama app is running in your system tray.
Error: "CORS Error" (in Browser Console)
This happens if the frontend cannot talk to the backend.
Fix: Ensure ollama_backend_service.py is running and the port is 5000.