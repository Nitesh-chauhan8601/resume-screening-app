async function bootstrapAdminPage() {
    const user = await requireAuth("admin");
    if (!user) {
        return;
    }
    bindLogout();
    document.getElementById("ticketForm").addEventListener("submit", createTicket);
    await Promise.all([loadHealth(), loadLogs(), loadTickets()]);
}

async function loadHealth() {
    const response = await apiClient.get("/api/admin/health");
    const health = response.health;
    document.getElementById("healthDatabase").textContent = health.database;
    document.getElementById("healthUploads").textContent = health.upload_folder;
    document.getElementById("healthErrors").textContent = health.errors_today;
    document.getElementById("healthTickets").textContent = health.open_tickets;
}

async function loadLogs() {
    const response = await apiClient.get("/api/admin/logs?limit=20");
    const tbody = document.getElementById("logsTableBody");
    if (!response.logs.length) {
        tbody.innerHTML = '<tr><td colspan="4"><div class="empty-state">No logs found.</div></td></tr>';
        return;
    }
    tbody.innerHTML = response.logs
        .map(
            (log) => `
                <tr>
                    <td>${log.level}</td>
                    <td>${log.module}</td>
                    <td>${log.message}</td>
                    <td>${new Date(log.created_at).toLocaleString()}</td>
                </tr>
            `,
        )
        .join("");
}

async function loadTickets() {
    const response = await apiClient.get("/api/admin/tickets");
    const tbody = document.getElementById("ticketsTableBody");
    if (!response.tickets.length) {
        tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state">No tickets raised.</div></td></tr>';
        return;
    }
    tbody.innerHTML = response.tickets
        .map(
            (ticket) => `
                <tr>
                    <td>${ticket.title}</td>
                    <td><span class="${pillClass(ticket.severity)}">${ticket.severity}</span></td>
                    <td><span class="${pillClass(ticket.status)}">${ticket.status}</span></td>
                    <td>${ticket.description}</td>
                    <td>
                        <div class="actions" style="margin-top: 0;">
                            <button class="btn btn-secondary" onclick="updateTicket(${ticket.id}, 'in_progress')">Mark In Progress</button>
                            <button class="btn btn-secondary" onclick="updateTicket(${ticket.id}, 'resolved')">Resolve</button>
                        </div>
                    </td>
                </tr>
            `,
        )
        .join("");
}

async function createTicket(event) {
    event.preventDefault();
    clearMessage("adminMessage");
    const payload = {
        title: document.getElementById("ticketTitle").value.trim(),
        description: document.getElementById("ticketDescription").value.trim(),
        severity: document.getElementById("ticketSeverity").value,
    };
    try {
        await apiClient.post("/api/admin/tickets", payload);
        showMessage("adminMessage", "Ticket created successfully", "success");
        document.getElementById("ticketForm").reset();
        await loadTickets();
    } catch (error) {
        showMessage("adminMessage", error.message, "error");
    }
}

async function updateTicket(ticketId, status) {
    try {
        await apiClient.put(`/api/admin/tickets/${ticketId}`, { status });
        await loadTickets();
    } catch (error) {
        showMessage("adminMessage", error.message, "error");
    }
}

window.updateTicket = updateTicket;

bootstrapAdminPage();
