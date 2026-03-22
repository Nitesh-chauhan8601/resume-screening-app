async function bootstrapResultsPage() {
    const user = await requireAuth();
    if (!user) {
        return;
    }
    bindLogout();
    document.getElementById("resultsFilterForm").addEventListener("submit", applyFilters);
    document.getElementById("exportButton").addEventListener("click", exportResults);
    await loadJobs();
}

async function loadJobs() {
    const response = await apiClient.get("/api/jobs");
    const jobs = response.jobs;
    const select = document.getElementById("resultsJobId");
    select.innerHTML = jobs.length
        ? jobs.map((job) => `<option value="${job.id}">${job.title}</option>`).join("")
        : '<option value="">No jobs available</option>';
    const queryJobId = getQueryParam("jobId");
    if (queryJobId) {
        select.value = queryJobId;
    }
    select.addEventListener("change", () => loadResults());
    if (jobs.length) {
        await loadResults();
    }
}

async function loadResults() {
    clearMessage("resultsMessage");
    const jobId = document.getElementById("resultsJobId").value;
    if (!jobId) {
        return;
    }
    const params = new URLSearchParams({
        sort: document.getElementById("sortBy").value,
    });
    const qualification = document.getElementById("qualificationFilter").value.trim();
    const minExperience = document.getElementById("experienceFilter").value.trim();
    const recommendation = document.getElementById("recommendationFilter").value.trim();

    if (qualification) {
        params.set("qualification", qualification);
    }
    if (minExperience) {
        params.set("min_experience", minExperience);
    }
    if (recommendation) {
        params.set("recommendation", recommendation);
    }

    try {
        const [resultsResponse, summaryResponse] = await Promise.all([
            apiClient.get(`/api/screening/results/${jobId}?${params.toString()}`),
            apiClient.get(`/api/reports/${jobId}/summary`),
        ]);
        renderSummary(summaryResponse.summary);
        renderResults(resultsResponse.results);
    } catch (error) {
        showMessage("resultsMessage", error.message, "error");
    }
}

function renderSummary(summary) {
    document.getElementById("summaryCandidates").textContent = summary.total_candidates;
    document.getElementById("summaryAverage").textContent = summary.average_score;
    document.getElementById("summaryStrong").textContent = summary.strong_matches;
    document.getElementById("summaryWeak").textContent = summary.weak_matches;

    const distribution = summary.score_distribution || {};
    const keys = ["80-100", "60-79", "40-59", "0-39"];
    document.getElementById("scoreDistribution").innerHTML = keys
        .map(
            (key) => `
                <div class="detail-item">
                    <strong>${key}</strong>
                    <div>${distribution[key] || 0} candidates</div>
                </div>
            `,
        )
        .join("");
}

function renderResults(results) {
    const tbody = document.getElementById("resultsTableBody");
    if (!results.length) {
        tbody.innerHTML = '<tr><td colspan="7"><div class="empty-state">No screening results found for current filters.</div></td></tr>';
        return;
    }
    tbody.innerHTML = results
        .map(
            (result) => `
                <tr>
                    <td>${result.ranking || "-"}</td>
                    <td>${result.resume?.candidate_name || "-"}</td>
                    <td>${result.suitability_score}</td>
                    <td>${result.resume?.experience_years || 0} years</td>
                    <td>${result.resume?.education || "-"}</td>
                    <td><span class="${pillClass(result.recommendation)}">${result.recommendation}</span></td>
                    <td><a href="/candidate.html?resultId=${result.id}">View analysis</a></td>
                </tr>
            `,
        )
        .join("");
}

function applyFilters(event) {
    event.preventDefault();
    loadResults();
}

function exportResults() {
    const jobId = document.getElementById("resultsJobId").value;
    if (!jobId) {
        showMessage("resultsMessage", "Please select a job profile first", "error");
        return;
    }
    window.location.href = `/api/reports/export/${jobId}?format=csv`;
}

bootstrapResultsPage();
