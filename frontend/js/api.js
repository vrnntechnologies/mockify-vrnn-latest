// frontend/js/api.js

async function apiRequest(endpoint, method = "GET", body = null) {
  try {
    const response = await fetch(
      `${window.APP_CONFIG.API_BASE_URL}${endpoint}`,
      {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: body ? JSON.stringify(body) : null,
      }
    );

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API Request Failed:", error);
    return {
      success: false,
      error: error.message,
    };
  }
}
