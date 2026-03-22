let latestUploadedIds = [];

async function bootstrapUploadPage() {
    const user = await requireAuth("recruiter");
    if (!user) {
        return;
    }
    bindLogout();
    document.getElementById("singleUploadForm").addEventListener("submit", uploadSingleResume);
    document.getElementById("bulkUploadForm").addEventListener("submit", uploadBulkResumes);
    document.getElementById("runScreeningButton").addEventListener("click", runScreening);
    await Promise.all([loadJobs(), loadResumes()]);
}

async function loadJobs() {
    const response = await apiClient.get("/api/jobs");
    const jobs = response.jobs;
    const select = document.getElementById("screeningJobId");
    select.innerHTML = jobs.length
        ? jobs.map((job) => `<option value="${job.id}">${job.title}</option>`).join("")
        : '<option value="">No jobs available</option>';
}

async function loadResumes() {
    const response = await apiClient.get("/api/resumes");
    const resumes = response.resumes;
    const tbody = document.getElementById("resumeTableBody");
    if (!resumes.length) {
        tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state">No resumes uploaded yet.</div></td></tr>';
        return;
    }
    tbody.innerHTML = resumes
        .map(
            (resume) => `
                <tr>
                    <td>${resume.candidate_name || "-"}</td>
                    <td>${resume.file_name}</td>
                    <td>${formatList(resume.skills)}</td>
                    <td>${resume.experience_years} years</td>
                    <td><span class="pill ${resume.parse_status}">${resume.parse_status}</span></td>
                </tr>
            `,
        )
        .join("");
}

async function uploadSingleResume(event) {
    event.preventDefault();
    await handleUpload("singleResumeFile", "/api/resumes/upload");
}

async function uploadBulkResumes(event) {
    event.preventDefault();
    await handleUpload("bulkResumeFiles", "/api/resumes/upload-bulk");
}

async function handleUpload(inputId, endpoint) {
    clearMessage("uploadMessage");
    const input = document.getElementById(inputId);
    if (!input.files.length) {
        showMessage("uploadMessage", "Please choose at least one resume file", "error");
        return;
    }
    const formData = new FormData();
    Array.from(input.files).forEach((file) => formData.append(endpoint.endsWith("bulk") ? "resumes" : "resume", file));
    try {
        const response = await apiClient.post(endpoint, formData);
        latestUploadedIds = response.uploaded.map((item) => item.id);
        const failedCount = response.failed.length;
        const note = failedCount ? ` ${failedCount} file(s) failed.` : "";
        showMessage("uploadMessage", `${response.message}.${note}`, "success");
        input.value = "";
        await loadResumes();
    } catch (error) {
        showMessage("uploadMessage", error.message, "error");
    }
}

async function runScreening() {
    clearMessage("screeningMessage");
    const jobId = document.getElementById("screeningJobId").value;
    if (!jobId) {
        showMessage("screeningMessage", "Please select a job profile", "error");
        return;
    }
    const latestOnly = document.getElementById("screenLatestOnly").checked;
    const payload = latestOnly && latestUploadedIds.length ? { resume_ids: latestUploadedIds } : {};
    try {
        const response = await apiClient.post(`/api/screening/run/${jobId}`, payload);
        showMessage("screeningMessage", `${response.message}. ${response.processed.length} candidates scored.`, "success");
        window.setTimeout(() => {
            window.location.href = `/results.html?jobId=${jobId}`;
        }, 800);
    } catch (error) {
        showMessage("screeningMessage", error.message, "error");
    }
}

bootstrapUploadPage();
