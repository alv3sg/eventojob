/** ====== CONFIG ====== */
const API_BASE = "http://localhost:8000/v1"; // your FastAPI base
// access token in memory; refresh token should be HttpOnly cookie from API
let ACCESS_TOKEN = null;

/** ====== NAVBAR SESSION RENDER ====== */
function setAccessToken(token) {
    ACCESS_TOKEN = token || null;
}

async function getMe() {
    try {
        const res = await api("/me");
        if (!res.ok) return null;
        return await res.json();
    } catch (error) {
        console.error('Error fetching user data:', error);
        return null;
    }
}

async function renderNav() {
    const navRight = document.getElementById("nav-right");
    if (!navRight) return;

    try {
        const me = await getMe();
        if (!me) {
            navRight.innerHTML = `
                <li class="nav-item">
                    <a class="nav-link" href="/login.html">Login</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/register.html">Register</a>
                </li>`;
            return;
        }

        navRight.innerHTML = `
            <li class="nav-item">
                <a class="nav-link" href="/me_applications.html">My Applications</a>
            </li>
            ${me.role === "employer" ? `
                <li class="nav-item">
                    <a class="nav-link" href="/me_jobs_new.html">Post a Job</a>
                </li>` : ''}
            <li class="nav-item">
                <a class="nav-link" href="/me_profile.html">Profile</a>
            </li>`;
    } catch (error) {
        console.error('Error rendering navigation:', error);
    }
}

/** ====== API WRAPPER WITH 401→REFRESH ====== */
async function refresh() {
    try {
        const res = await fetch(`${API_BASE}/auth/refresh`, {
            method: "POST",
            credentials: "include"
        });
        
        if (!res.ok) {
            throw new Error("refresh_failed");
        }
        
        const data = await res.json();
        setAccessToken(data.access_token);
        return data;
    } catch (error) {
        console.error('Refresh token failed:', error);
        throw error;
    }
}

async function api(path, options = {}) {
    const headers = new Headers(options.headers || {});
    if (ACCESS_TOKEN) {
        headers.set("Authorization", `Bearer ${ACCESS_TOKEN}`);
    }

    const url = path.startsWith("http") ? path : `${API_BASE}${path}`;
    let res = await fetch(url, {
        ...options,
        headers,
        credentials: "include"
    });

    if (res.status !== 401) return res;

    // attempt refresh once
    try {
        await refresh();
        const headers2 = new Headers(options.headers || {});
        if (ACCESS_TOKEN) {
            headers2.set("Authorization", `Bearer ${ACCESS_TOKEN}`);
        }
        return fetch(url, {
            ...options,
            headers: headers2,
            credentials: "include"
        });
    } catch (error) {
        return res;
    }
}

/** ====== SIMPLE UTIL ====== */
function qs(name) {
    return new URLSearchParams(location.search).get(name);
}

function fmtMoney(n) {
    return Number(n).toFixed(2);
}

/** ====== BOOT ====== */
document.addEventListener("DOMContentLoaded", async () => {
    try {
        await refresh();
    } catch (error) {
        console.log('No valid session found, continuing as guest');
    }
    await renderNav();
});
