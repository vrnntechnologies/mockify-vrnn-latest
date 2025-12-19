const API_BASE = window.APP_CONFIG.API_BASE_URL;

async function checkBackend() {
    try {
        const res = await fetch(`${API_BASE}/health`);
        if (!res.ok) throw new Error("Backend down");
        return true;
    } catch (err) {
        console.error("Backend check failed:", err);
        return false;
    }
}

async function startInterview() {
    const connected = await checkBackend();

    if (!connected) {
        document.getElementById("question").innerText =
            "Backend not connected.";
        return;
    }

    const res = await fetch(`${API_BASE}/interview/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            role: "Software Engineer",
            level: "Junior",
            history: []
        }),
    });

    const data = await res.json();

    document.getElementById("question").innerText =
        data.question || "No question received";
}


document.addEventListener("DOMContentLoaded", startInterview);
