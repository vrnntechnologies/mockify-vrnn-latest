// frontend/js/aiRouter.js

async function askAI(payload) {
  /*
    payload example:
    {
      type: "interview_question",
      company: "google",
      role: "software_engineer",
      difficulty: "medium"
    }
  */

  if (window.APP_CONFIG.AI_MODE === "local") {
    return apiRequest("/ai/local", "POST", payload);
  } else {
    return apiRequest("/ai/cloud", "POST", payload);
  }
}
