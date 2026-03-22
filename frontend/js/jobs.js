let editingJobId = null;

async function bootstrapJobsPage() {
    const user = await requireAuth("recruiter");
    if (!user) {
        return;
    }
    bindLogout();
    await loadJobs();
    document.getElementById("jobForm").addEventListener("submit", submitJob);
    document.getElementById("jobResetButton").addEventListener("click", resetForm);
}

async function loadJobs() {
    const response = await apiClient.get("/api/jobs");
    const jobs = response.jobs;
    const tbody = document.getElementById("jobsTableBody");
    if (!jobs.length) {
        tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state">No job profiles yet.</div></td></tr>';
        return;
    }
    tbody.innerHTML = jobs
        .map(
            (job) => `
                <tr>
                    <td>${job.title}</td>
                    <td>${formatList(job.required_skills)}</td>
                    <td>${job.min_experience} years</td>
                    <td>${formatList(job.qualifications)}</td>
                    <td>
                        <div class="actions" style="margin-top: 0;">
                            <button class="btn btn-secondary" onclick="editJob(${job.id})">Edit</button>
                            <a class="btn btn-secondary" href="/results.html?jobId=${job.id}">Results</a>
                            <button class="btn btn-danger" onclick="removeJob(${job.id})">Delete</button>
                        </div>
                    </td>
                </tr>
            `,
        )
        .join("");
}

async function submitJob(event) {
    event.preventDefault();
    clearMessage("jobsMessage");
    const payload = {
        title: document.getElementById("jobTitle").value.trim(),
        description_text: document.getElementById("jobDescription").value.trim(),
        required_skills: document.getElementById("jobSkills").value.trim(),
        keywords: document.getElementById("jobKeywords").value.trim(),
        min_experience: document.getElementById("jobExperience").value,
        qualifications: document.getElementById("jobQualifications").value.trim(),
    };
    try {
        if (editingJobId) {
            await apiClient.put(`/api/jobs/${editingJobId}`, payload);
            showMessage("jobsMessage", "Job profile updated successfully", "success");
        } else {
            await apiClient.post("/api/jobs", payload);
            showMessage("jobsMessage", "Job profile created successfully", "success");
        }
        resetForm();
        await loadJobs();
    } catch (error) {
        showMessage("jobsMessage", error.message, "error");
    }
}

async function editJob(jobId) {
    const response = await apiClient.get(`/api/jobs/${jobId}`);
    const job = response.job;
    editingJobId = job.id;
    document.getElementById("formHeading").textContent = "Edit Job Profile";
    document.getElementById("jobTitle").value = job.title;
    document.getElementById("jobDescription").value = job.description_text;
    document.getElementById("jobSkills").value = formatList(job.required_skills);
    document.getElementById("jobKeywords").value = formatList(job.keywords);
    document.getElementById("jobExperience").value = job.min_experience;
    document.getElementById("jobQualifications").value = formatList(job.qualifications);
    window.scrollTo({ top: 0, behavior: "smooth" });
}

async function removeJob(jobId) {
    if (!window.confirm("Delete this job profile?")) {
        return;
    }
    try {
        await apiClient.delete(`/api/jobs/${jobId}`);
        showMessage("jobsMessage", "Job profile deleted", "success");
        if (editingJobId === jobId) {
            resetForm();
        }
        await loadJobs();
    } catch (error) {
        showMessage("jobsMessage", error.message, "error");
    }
}

function resetForm() {
    editingJobId = null;
    document.getElementById("jobForm").reset();
    document.getElementById("formHeading").textContent = "Create Job Profile";
}

window.editJob = editJob;
window.removeJob = removeJob;

bootstrapJobsPage();
