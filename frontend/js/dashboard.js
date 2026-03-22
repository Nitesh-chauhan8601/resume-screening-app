async function loadDashboard() {
    const user = await requireAuth("recruiter");
    if (!user) {
        return;
    }
    bindLogout();
    await Promise.all([loadStats(), loadResumes()]);
}

async function loadStats() {
    const response = await apiClient.get("/api/dashboard/stats");
    const stats = response.stats;
    document.getElementById("totalJobs").textContent = stats.total_jobs;
    document.getElementById("totalResumes").textContent = stats.total_resumes;
    document.getElementById("screenedCandidates").textContent = stats.screened_candidates;

    const jobsContainer = document.getElementById("recentJobs");
    if (!stats.recent_jobs.length) {
        jobsContainer.innerHTML = '<div class="empty-state">Create your first job profile to begin screening.</div>';
        return;
    }
    jobsContainer.innerHTML = `
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Skills</th>
                        <th>Experience</th>
                        <th>Results</th>
                    </tr>
                </thead>
                <tbody>
                    ${stats.recent_jobs
                        .map(
                            (job) => `
                                <tr>
                                    <td>${job.title}</td>
                                    <td>${formatList(job.required_skills)}</td>
                                    <td>${job.min_experience} years</td>
                                    <td><a href="/results.html?jobId=${job.id}">View results</a></td>
                                </tr>
                            `,
                        )
                        .join("")}
                </tbody>
            </table>
        </div>
    `;
}

async function loadResumes() {
    const response = await apiClient.get("/api/resumes");
    const resumes = response.resumes.slice(0, 6);
    const container = document.getElementById("resumeSnapshot");
    if (!resumes.length) {
        container.innerHTML = '<div class="empty-state">Upload resumes to start AI analysis.</div>';
        return;
    }
    container.innerHTML = `
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Candidate</th>
                        <th>Skills</th>
                        <th>Experience</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${resumes
                        .map(
                            (resume) => `
                                <tr>
                                    <td>${resume.candidate_name || "-"}</td>
                                    <td>${formatList(resume.skills)}</td>
                                    <td>${resume.experience_years} years</td>
                                    <td><span class="pill ${resume.parse_status}">${resume.parse_status}</span></td>
                                </tr>
                            `,
                        )
                        .join("")}
                </tbody>
            </table>
        </div>
    `;
}

loadDashboard();
