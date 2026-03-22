async function bootstrapCandidatePage() {
    const user = await requireAuth();
    if (!user) {
        return;
    }
    bindLogout();
    const resultId = getQueryParam("resultId");
    if (!resultId) {
        showMessage("candidateMessage", "Result ID is missing", "error");
        return;
    }
    try {
        const response = await apiClient.get(`/api/screening/result/${resultId}`);
        renderCandidate(response.result);
    } catch (error) {
        showMessage("candidateMessage", error.message, "error");
    }
}

function renderCandidate(result) {
    document.getElementById("candidateTitle").textContent = result.resume.candidate_name || "Candidate Analysis";
    document.getElementById("candidateSubtitle").textContent = `${result.job.title} | Score ${result.suitability_score}`;
    document.getElementById("scoreOverall").textContent = result.suitability_score;
    document.getElementById("scoreSkills").textContent = result.skill_score;
    document.getElementById("scoreExperience").textContent = result.experience_score;
    document.getElementById("scoreEducation").textContent = result.education_score;
    document.getElementById("scoreSimilarity").textContent = result.similarity_score;
    document.getElementById("candidateEducation").textContent = result.resume.education || "-";
    document.getElementById("candidateExperience").textContent = `${result.resume.experience_years || 0} years`;
    document.getElementById("candidateRecommendation").innerHTML = `<span class="${pillClass(result.recommendation)}">${result.recommendation}</span>`;
    document.getElementById("candidateNotes").textContent = result.notes || "-";

    const matched = document.getElementById("matchedSkills");
    matched.innerHTML = result.matched_skills.length
        ? result.matched_skills.map((skill) => `<span class="skill-chip">${skill}</span>`).join("")
        : '<span class="skill-chip">No matched skills found</span>';

    const missing = document.getElementById("missingSkills");
    missing.innerHTML = result.missing_skills.length
        ? result.missing_skills.map((skill) => `<span class="skill-chip missing">${skill}</span>`).join("")
        : '<span class="skill-chip">No missing skills</span>';
}

bootstrapCandidatePage();
