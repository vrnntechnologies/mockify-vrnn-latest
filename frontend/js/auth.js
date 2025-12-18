// frontend/js/auth.js

const AUTH_KEY = "mockify_auth";

// ---------- LOGIN ----------
async function login(username, password) {
  const user = {
    username: username || "demo_user",
    loggedInAt: new Date().toISOString(),
  };

  localStorage.setItem(AUTH_KEY, JSON.stringify(user));
  return true;
}

// ---------- LOGOUT ----------
function logout() {
  localStorage.removeItem(AUTH_KEY);
  window.location.href = "index.html";
}

// ---------- AUTH CHECK ----------
function isLoggedIn() {
  return localStorage.getItem(AUTH_KEY) !== null;
}

// ---------- GET USER ----------
function getCurrentUser() {
  const data = localStorage.getItem(AUTH_KEY);
  return data ? JSON.parse(data) : null;
}

// ---------- ROUTE PROTECTION ----------
//function protectPage() {
  //if (!isLoggedIn()) {
   // window.location.href = "index.html";
  //}
//}

// ---------- UI HELPERS ----------
function updateNavbarAuth() {
  const loginBtn = document.getElementById("loginBtn");
  const dashboardLink = document.getElementById("nav-dashboard");

  if (!loginBtn) return;

  if (isLoggedIn()) {
    loginBtn.textContent = "Logout";
    loginBtn.onclick = logout;

    if (dashboardLink) dashboardLink.classList.remove("hidden");
  } else {
    loginBtn.textContent = "Log In";
    loginBtn.onclick = handleAuthClick;

    if (dashboardLink) dashboardLink.classList.add("hidden");
  }
}

// ---------- MODAL HANDLERS ----------
function handleAuthClick() {
  const modal = document.getElementById("loginModal");
  if (modal) {
    modal.classList.remove("hidden");
    modal.classList.add("flex");
  }
}

function closeLoginModal() {
  const modal = document.getElementById("loginModal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
}

async function handleLoginSubmit(e) {
  e.preventDefault();

  const username = document.getElementById("username")?.value;
  const password = document.getElementById("password")?.value;

  const success = await login(username, password);
  if (success) {
    closeLoginModal();
    updateNavbarAuth();
    window.location.href = "interview.html";
  }
}

function handleDemoLogin() {
  login("demo", "demo");
  updateNavbarAuth();
  window.location.href = "interview.html";
}

document.addEventListener("DOMContentLoaded", updateNavbarAuth);
