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

    const statusEl = document.getElementById("status");

    if (!connected) {
        statusEl.innerText =
            "Hello! I'm ready to interview you. (Demo Mode: Backend not connected)";
        return;
    }

    statusEl.innerText = "✅ Backend Connected. Starting interview...";

    const res = await fetch(`${API_BASE}/start-interview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            role: "Software Engineer",
            level: "Junior",
        }),
    });

    const data = await res.json();
    document.getElementById("question").innerText = data.question;
}

document.addEventListener("DOMContentLoaded", startInterview);
