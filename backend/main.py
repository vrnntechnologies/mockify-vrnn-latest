import json
import os
import re
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from ollama_client import ask_ollama
from prompt_router import build_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#app = FastAPI()
app = FastAPI(
    title="Mockify API",
    docs_url="/docs",
    openapi_url="/openapi.json",
    root_path="/api"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATS_FILE = "interview_stats.json"

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

class InterviewRequest(BaseModel):
    prompt: str
    type: str
    context: dict

class ReportRequest(BaseModel):
    transcript: str
    context: dict

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
        logger.error(f"Error in /interview/ask: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interview/analyze")
def interview_analyze(req: ReportRequest):
    try:
        logger.info("Generating Analysis Report...")
        final_prompt = build_prompt(req.transcript, "report", req.context)
        analysis_raw = ask_ollama(final_prompt)
        logger.info(f"LLM Raw Output (first 500 chars): {analysis_raw[:500]}...") 

        # --- PARSING STRATEGY ---
        analysis_data = {
            "score": 0,
            "verdict": "Better Luck Next Time",
            "summary": "Parsing failed or LLM returned invalid format.",
            "strengths": ["None observed"],
            "weaknesses": ["Parsing error"],
            "improvement_plan": ["Retry analysis"],
            "code_feedback": "N/A"
        }

        # Strategy 1: Aggressive JSON Extraction
        try:
            # 1. Find the first '{' and the last '}' to extract valid JSON string
            start_index = analysis_raw.find('{')
            end_index = analysis_raw.rfind('}')
            
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_str = analysis_raw[start_index:end_index+1]
                # Clean up common JSON errors if needed (e.g. trailing commas)
                # json_str = re.sub(r',\s*}', '}', json_str) 
                parsed = json.loads(json_str)
                analysis_data.update(parsed)
                logger.info("JSON Parsing Successful.")
            else:
                raise json.JSONDecodeError("No JSON brackets found", analysis_raw, 0)

        except json.JSONDecodeError as e:
            logger.warning(f"JSON Parsing Failed ({e}). Attempting Regex Extraction (Fallback).")
            
            # Strategy 2: Regex Extraction (Improved for Lists)
            
            # Score
            score_match = re.search(r'(?:\*\*SCORE:\*\*|SCORE:|Score:)\s*(\d+)', analysis_raw, re.IGNORECASE)
            if score_match:
                analysis_data["score"] = int(score_match.group(1))
            
            # Verdict
            verdict_match = re.search(r'(?:\*\*VERDICT:\*\*|VERDICT:|Verdict:)\s*("?[\w\s]+"?)', analysis_raw, re.IGNORECASE)
            if verdict_match:
                analysis_data["verdict"] = verdict_match.group(1).replace('"', '').strip()

            # Summary
            summary_match = re.search(r'(?:\*\*SUMMARY:\*\*|SUMMARY:|Summary:)\s*(.*?)(?:\*\*STRENGTHS:|STRENGTHS:|$)', analysis_raw, re.DOTALL | re.IGNORECASE)
            if summary_match:
                analysis_data["summary"] = summary_match.group(1).strip()
            
            # Helper to extract lists (looks for bullets *, -, or 1.)
            def extract_list(section_name):
                # Look for section header followed by content, stopping at next double-asterisk or end of string
                pattern = f"(?:\*\*{section_name}:\*\*|{section_name}:)\s*(.*?)(?:\*\*|$|{section_name.title()}:)" 
                match = re.search(pattern, analysis_raw, re.DOTALL | re.IGNORECASE)
                if match:
                    content = match.group(1)
                    # Extract lines starting with *, -, or digit
                    items = re.findall(r'(?:^|\n)\s*(?:[\*\-]|\d+\.)\s+(.+)', content)
                    # If regex finds nothing but content exists, try splitting by newline
                    if not items and len(content.strip()) > 5:
                         lines = content.split('\n')
                         # Filter empty lines
                         items = [line.strip() for line in lines if line.strip()]
                    return items
                return []

            s_list = extract_list("STRENGTHS")
            if s_list: analysis_data["strengths"] = s_list
            
            w_list = extract_list("WEAKNESSES")
            if w_list: analysis_data["weaknesses"] = w_list
            
            i_list = extract_list("IMPROVEMENT PLAN")
            if i_list: analysis_data["improvement_plan"] = i_list

        # --- UPDATE STATS ---
        try:
            stats = load_stats()
            stats["total_interviews"] += 1
            
            current_avg = stats.get("average_score", 0)
            total_count = stats["total_interviews"]
            # To calculate running average: (old_avg * (new_count - 1) + new_score) / new_count
            prev_total_sum = current_avg * (total_count - 1)
            
            new_score = analysis_data.get("score", 0)
            if not isinstance(new_score, (int, float)): new_score = 0
                
            stats["average_score"] = int((prev_total_sum + new_score) / total_count)
            
            history_item = {
                "company": req.context.get("company", "Unknown"),
                "role": req.context.get("role", "Unknown"),
                "round": req.context.get("round", "General"),
                "score": new_score,
                "verdict": analysis_data.get("verdict", "Better Luck Next Time"),
                "date": "Today"
            }
            
            history = stats.get("history", [])
            history.append(history_item)
            stats["history"] = history[-20:] # Keep last 20
            
            save_stats(stats)
        except Exception as stat_e:
            logger.error(f"Error updating stats: {stat_e}") # Don't fail the request if stats fail

        return {
            "analysis": analysis_data,
            "raw": analysis_raw
        }

    except Exception as e:
        logger.error(f"Error in /interview/analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))
