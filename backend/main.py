import json
import os
import re
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from ollama_client import ask_ollama
from prompt_router import build_prompt

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# FASTAPI APP (🚨 NO root_path HERE 🚨)
# --------------------------------------------------
app = FastAPI(
    title="Mockify API",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# --------------------------------------------------
# CORS
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# FILES
# --------------------------------------------------
STATS_FILE = "interview_stats.json"

# --------------------------------------------------
# UTILS
# --------------------------------------------------
def load_stats():
    if not os.path.exists(STATS_FILE):
        return {"total_interviews": 0, "average_score": 0, "history": []}
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load stats: {e}")
        return {"total_interviews": 0, "average_score": 0, "history": []}

def save_stats(stats):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save stats: {e}")

# --------------------------------------------------
# MODELS
# --------------------------------------------------
class InterviewRequest(BaseModel):
    prompt: str
    type: str
    context: dict

class ReportRequest(BaseModel):
    transcript: str
    context: dict

# --------------------------------------------------
# ROUTES
# --------------------------------------------------
@app.get("/stats")
def get_stats():
    return load_stats()

@app.post("/interview/ask")
def interview_ask(req: InterviewRequest):
    try:
        final_prompt = build_prompt(req.prompt, req.type, req.context)
        reply = ask_ollama(final_prompt)
        return {"reply": reply}
    except Exception as e:
        logger.error(f"/interview/ask error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interview/analyze")
def interview_analyze(req: ReportRequest):
    try:
        logger.info("Generating analysis report...")

        final_prompt = build_prompt(req.transcript, "report", req.context)
        analysis_raw = ask_ollama(final_prompt)

        analysis_data = {
            "score": 0,
            "verdict": "Better Luck Next Time",
            "summary": "Unable to parse AI response.",
            "strengths": ["None observed"],
            "weaknesses": ["Parsing failed"],
            "improvement_plan": ["Retry interview"],
            "code_feedback": "N/A"
        }

        # ---------- JSON EXTRACTION ----------
        try:
            start = analysis_raw.find("{")
            end = analysis_raw.rfind("}")
            if start != -1 and end != -1:
                parsed = json.loads(analysis_raw[start:end+1])
                analysis_data.update(parsed)
        except Exception as e:
            logger.warning(f"JSON parsing failed: {e}")

        # ---------- UPDATE STATS ----------
        try:
            stats = load_stats()
            stats["total_interviews"] += 1

            new_score = analysis_data.get("score", 0)
            prev_avg = stats.get("average_score", 0)
            count = stats["total_interviews"]

            stats["average_score"] = int(((prev_avg * (count - 1)) + new_score) / count)

            stats["history"].append({
                "company": req.context.get("company", "Unknown"),
                "role": req.context.get("role", "Unknown"),
                "round": req.context.get("round", "General"),
                "score": new_score,
                "verdict": analysis_data.get("verdict", "N/A"),
                "date": "Today"
            })

            stats["history"] = stats["history"][-20:]
            save_stats(stats)
        except Exception as e:
            logger.error(f"Stats update failed: {e}")

        return {"analysis": analysis_data}

    except Exception as e:
        logger.error(f"/interview/analyze error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
