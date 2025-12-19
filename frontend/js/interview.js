const API_BASE = window.APP_CONFIG.API_BASE_URL;

async function checkBackend() {
    try {
        const res = await fetch("/api/health", {
            method: "GET",
            cache: "no-store"
        });

        if (!res.ok) {
            console.error("Health check failed:", res.status);
            return false;
        }

        const data = await res.json();
        return data.status === "ok";
    } catch (err) {
        console.error("Health check error:", err);
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
