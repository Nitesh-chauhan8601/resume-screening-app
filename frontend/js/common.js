const apiClient = {
    async request(url, options = {}) {
        const response = await fetch(url, {
            credentials: "same-origin",
            headers: {
                ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
                ...(options.headers || {}),
            },
            ...options,
        });
        const contentType = response.headers.get("content-type") || "";
        const payload = contentType.includes("application/json")
            ? await response.json()
            : await response.text();

        if (!response.ok) {
            const message = typeof payload === "string" ? payload : payload.message || "Request failed";
            throw new Error(message);
        }
        return payload;
    },
    get(url) {
        return this.request(url);
    },
    post(url, body) {
        return this.request(url, {
            method: "POST",
            body: body instanceof FormData ? body : JSON.stringify(body),
        });
    },
    put(url, body) {
        return this.request(url, {
            method: "PUT",
            body: JSON.stringify(body),
        });
    },
    delete(url) {
        return this.request(url, { method: "DELETE" });
    },
};

function showMessage(elementId, message, type = "info") {
    const element = document.getElementById(elementId);
    if (!element) {
        return;
    }
    element.textContent = message;
    element.className = `message show ${type}`;
}

function clearMessage(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
        return;
    }
    element.textContent = "";
    element.className = "message";
}

function getQueryParam(name) {
    return new URLSearchParams(window.location.search).get(name);
}

function formatList(list) {
    return Array.isArray(list) && list.length ? list.join(", ") : "-";
}

function pillClass(value) {
    const safe = String(value || "").toLowerCase().replace(/\s+/g, "-");
    return `pill ${safe}`;
}

async function fetchCurrentUser() {
    try {
        const data = await apiClient.get("/api/auth/me");
        return data.user;
    } catch (_error) {
        return null;
    }
}

async function requireAuth(expectedRole) {
    const user = await fetchCurrentUser();
    if (!user) {
        window.location.href = "/login.html";
        return null;
    }
    if (expectedRole && user.role !== expectedRole) {
        window.location.href = user.role === "admin" ? "/admin.html" : "/dashboard.html";
        return null;
    }
    setUserContext(user);
    return user;
}

function setUserContext(user) {
    const badge = document.getElementById("currentUser");
    if (badge) {
        badge.textContent = `${user.name} (${user.role})`;
    }
    document.querySelectorAll("[data-role]").forEach((item) => {
        const role = item.getAttribute("data-role");
        item.style.display = role === user.role ? "" : "none";
    });
    document.querySelectorAll(".nav-link").forEach((link) => {
        if (link.getAttribute("href") === window.location.pathname) {
            link.classList.add("active");
        }
    });
}

async function logout() {
    try {
        await apiClient.post("/api/auth/logout", {});
    } finally {
        window.location.href = "/login.html";
    }
}

function bindLogout() {
    const button = document.getElementById("logoutButton");
    if (button) {
        button.addEventListener("click", logout);
    }
}

window.apiClient = apiClient;
window.showMessage = showMessage;
window.clearMessage = clearMessage;
window.getQueryParam = getQueryParam;
window.formatList = formatList;
window.pillClass = pillClass;
window.requireAuth = requireAuth;
window.fetchCurrentUser = fetchCurrentUser;
window.bindLogout = bindLogout;
