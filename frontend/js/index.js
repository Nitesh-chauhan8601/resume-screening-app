(async function bootstrap() {
    const user = await fetchCurrentUser();
    if (!user) {
        window.location.href = "/login.html";
        return;
    }
    window.location.href = user.role === "admin" ? "/admin.html" : "/dashboard.html";
})();
