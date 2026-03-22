window.addEventListener("DOMContentLoaded", async () => {
    const user = await fetchCurrentUser();
    if (user) {
        window.location.href = user.role === "admin" ? "/admin.html" : "/dashboard.html";
    }
});

document.getElementById("loginForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage("authMessage");
    const payload = {
        email: document.getElementById("loginEmail").value.trim(),
        password: document.getElementById("loginPassword").value,
    };
    try {
        const response = await apiClient.post("/api/auth/login", payload);
        showMessage("authMessage", response.message, "success");
        window.setTimeout(() => {
            window.location.href = response.user.role === "admin" ? "/admin.html" : "/dashboard.html";
        }, 600);
    } catch (error) {
        showMessage("authMessage", error.message, "error");
    }
});

document.getElementById("registerForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage("registerMessage");
    const payload = {
        name: document.getElementById("registerName").value.trim(),
        email: document.getElementById("registerEmail").value.trim(),
        password: document.getElementById("registerPassword").value,
    };
    try {
        const response = await apiClient.post("/api/auth/register", payload);
        showMessage("registerMessage", response.message + ". Please login now.", "success");
        document.getElementById("registerForm").reset();
    } catch (error) {
        showMessage("registerMessage", error.message, "error");
    }
});
