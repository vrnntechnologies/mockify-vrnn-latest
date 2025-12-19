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
    try {
        const res = await fetch("/api/interview/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });

        if (!res.ok) {
            throw new Error("API failed");
        }

        const data = await res.json();

        document.getElementById("question").innerText =
            data.question || "No question returned";

    } catch (err) {
        console.error(err);
        document.getElementById("question").innerText =
            "Backend is reachable but interview API failed. Check console.";
    }
}



document.addEventListener("DOMContentLoaded", startInterview);
