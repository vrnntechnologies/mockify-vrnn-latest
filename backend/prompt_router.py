import json

def build_prompt(prompt: str, prompt_type: str, context: dict) -> str:
    company = context.get("company", "Tech Company")
    role = context.get("role", "Candidate")
    round_ = context.get("round", "General")
    difficulty = context.get("difficulty", "Medium")
    persona = context.get("persona", "Normal")

    # --- CHAT MODE (Conversation) ---
    if prompt_type == "chat":
        # 1. Company Specific Context
        company_style = ""
        if company in ["TCS", "Infosys", "Wipro", "HCL Tech"]:
            company_style = """
            COMPANY STYLE (Service-Based):
            - Focus heavily on fundamentals (OOPs, SQL, basic coding logic).
            - Ask about willingness to relocate, shifts, and specific project technologies.
            - Professionalism and communication skills are paramount.
            """
        elif company in ["Google", "Amazon", "Meta", "Netflix"]:
            company_style = """
            COMPANY STYLE (Product-Based):
            - Focus on problem-solving, optimization, and deep technical understanding.
            - Expect high autonomy and "engineering excellence" in answers.
            """

        # 2. Round Specific Context
        round_context = ""
        if round_ == "HR Round":
            round_context = """
            ROUND: HR Round
            GOAL: Assess culture fit, stability, and motivation.
            
            KEY QUESTIONS TO ASK (one by one):
            1. "Tell me about yourself." (Start with this)
            2. "Why do you want to join this company?"
            3. "Why are you leaving your current job?" (If experienced)
            4. "What are your strengths and weaknesses?"
            5. "How do you handle stress?"
            6. "Where do you see yourself in 5 years?"
            
            FRESHER LOGIC:
            - If they say they are a fresher, ask about internships, final year projects, and academic challenges.
            
            EXPERIENCED LOGIC:
            - Ask about specific challenges in previous roles and reasons for switching.
            """
        elif round_ == "Behavioral":
            round_context = """
            ROUND: Behavioral
            GOAL: Assess soft skills using STAR method.
            
            KEY QUESTIONS (Friendly tone):
            1. "Tell me about a time you faced a tough decision."
            2. "Have you ever had to sell an idea to a coworker?"
            3. "Tell me about a conflict you resolved."
            4. "Describe a time you failed and how you handled it."
            
            Always ask for the 'Result' of their actions.
            """
        elif round_ == "Phone Screen":
            round_context = """
            ROUND: Phone Screen
            GOAL: Quick 5-minute background check.
            
            FOCUS:
            - Verify experience verbally (Experience, Tech Stack).
            - Basic communication skills.
            - Salary expectations and notice period.
            """
        elif round_ == "System Design":
            round_context = """
            ROUND: System Design
            GOAL: Scalable architecture discussion.
            
            TOPICS: Load Balancers, Caching, Sharding, CAP Theorem.
            Task: Ask them to design a specific system (e.g., URL Shortener, Chat App).
            """
        elif round_ in ["Technical Coding", "Technical II"]:
            round_context = """
            ROUND: Technical Coding (C++ DSA Focus)
            GOAL: Assess algorithmic thinking and C++ proficiency.
            
            STRICT RULES:
            - Ask DATA STRUCTURES & ALGORITHMS questions only.
            - Expect solutions in C++.
            - Ask about Time/Space complexity (Big O).
            """

        # 3. Persona Injection
        persona_instruction = f"You are a {persona} interviewer named Rohan."
        if persona == "Strict":
            persona_instruction += " Be formal, skeptical, and drill down into details."
        elif persona == "Friendly":
            persona_instruction += " Be encouraging, warm, and professional."

        return f"""
{persona_instruction}
You are conducting a simulated interview for {company}.
Role: {role} | Round: {round_} | Difficulty: {difficulty}

{company_style}
{round_context}

*** CRITICAL RULES ***
1. **NO RESUME REQUESTS:** Do NOT ask the candidate to upload a resume or mention "I have reviewed your resume". This is a verbal conversation. Ask them to describe their experience verbally.
2. **STAY ON TOPIC:** If the candidate goes off-topic, firmly remind them to focus on the interview.
3. **ONE QUESTION:** Ask exactly one question at a time.
4. **ASTERISKS:** Do NOT use asterisks (*) for actions (e.g., *nods*). Just speak naturally.
5. **FRESHER CHECK:** At the start, if you haven't asked yet, ask if they are a fresher or experienced. Adapt questions accordingly.
6. **PROJECT TECH STACK:** If the candidate mentions a project, explicitly ask them what tech stack they used if they haven't mentioned it.

Current Conversation Context:
{prompt}

interviewer:
"""

    # --- CODE ANALYSIS MODE ---
    if prompt_type == "code_analysis":
        return f"""
You are a Senior Technical Interviewer at {company}.
The candidate has submitted code for a {round_} problem.

Context:
Role: {role}
Difficulty: {difficulty}

Candidate's Code:
{prompt}

Your Task:
1. Analyze correctness and efficiency (Time/Space Complexity).
2. If the code is bad or incorrect, give a score of 0 for this section.
3. Ask ONE follow-up question specifically about their implementation.
"""

    # --- REPORT GENERATION (Soft but Strict) ---
    if prompt_type == "report":
        return f"""
You are a Professional Technical Recruiter.
Analyze the transcript below for a {role} interview at {company}.

TRANSCRIPT START
{prompt}
TRANSCRIPT END

*** RULE 1: EMPTY INTERVIEW CHECK ***
- Look ONLY at the "TRANSCRIPT" text above.
- If the candidate (User) said NOTHING, or only "Hello", "Stop", or the transcript is effectively empty:
   - **SCORE MUST BE 0.**
   - **VERDICT:** "Did Not Attempt"
   - **SUMMARY:** "The candidate started the session but did not answer any questions or participate in the interview."
   - **STRENGTHS:** ["None"]
   - **WEAKNESSES:** ["Did not attend the interview"]
   - **IMPROVEMENT PLAN:** ["Please attempt the interview and answer the questions to get a score."]

*** RULE 2: SCORING & EVALUATION LOGIC ***
Rate the candidate based on ACCURACY, CLARITY, and DEPTH.

1. **Correct & Clear (Score: 85-100):** - User gave accurate, detailed, and professional answers. 
   - **Verdict:** Excellent.

2. **Correct but Vague (Score: 70-84):**
   - User gave the correct answer, but it was brief, lacked depth, or missed professional keywords.
   - *Action:* Award marks for correctness, but deduct for lack of detail.
   - **Verdict:** Good.

3. **Half Correct / Vague (Score: 40-69):**
   - User's answer was only partially correct, very generic, or "fluffy" (buzzwords without meaning).
   - *Action:* Award partial marks for effort, but deduct significantly for incompleteness.
   - **Verdict:** Moderate.

4. **Incorrect / Fail (Score: 0-39):**
   - Answers were factually wrong or irrelevant.
   - **Verdict:** Better Luck Next Time.

*** RULE 3: FEEDBACK TONE (Soft but Strict) ***
- **Tone:** Professional, encouraging, but strictly accurate. 
- Do NOT be rude ("You failed"). 
- Do NOT be fake ("You did great!" if they didn't).
- **Constructive Criticism:** If they made a mistake, explain *why* it matters professionally.

*** RULE 4: IMPROVEMENT PLAN ***
- The improvement plan must be based on the **specific mistakes** made in the transcript.
- Identify exactly what professional knowledge or soft skill was missing.

*** OUTPUT FORMAT ***
- RETURN ONLY VALID JSON. 
- Just start with {{ and end with }}.

{{
    "score": <integer_0_to_100>,
    "verdict": "<Verdict String>",
    "summary": "<Soft but strict summary of performance>",
    "strengths": ["<Strength 1>", "<Strength 2>"],
    "weaknesses": ["<Weakness 1>", "<Weakness 2>"],
    "improvement_plan": ["<Step 1>", "<Step 2>", "<Step 3>"],
    "code_feedback": "<Specific critique of code or 'N/A'>"
}}
"""

    return prompt