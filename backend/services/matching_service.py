try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:  # pragma: no cover
    TfidfVectorizer = None
    cosine_similarity = None

from backend.utils.text_cleaner import remove_bias_terms
from backend.utils.validators import split_multi_value


def calculate_skill_score(required_skills: list[str], candidate_skills: list[str]) -> tuple[float, list[str], list[str]]:
    required = {skill.lower() for skill in required_skills if skill}
    candidate = {skill.lower() for skill in candidate_skills if skill}
    if not required:
        return 100.0, [], []
    matched = sorted(required.intersection(candidate))
    missing = sorted(required.difference(candidate))
    score = (len(matched) / len(required)) * 100
    return round(score, 2), matched, missing


def calculate_experience_score(candidate_exp: float, required_exp: int) -> float:
    if required_exp <= 0:
        return 100.0
    if candidate_exp >= required_exp:
        return 100.0
    return round((candidate_exp / required_exp) * 100, 2)


def calculate_education_score(required_qualifications, candidate_education: str) -> float:
    required = [item.lower() for item in split_multi_value(required_qualifications)]
    candidate = (candidate_education or "").lower()
    if not required:
        return 100.0
    if any(item in candidate for item in required):
        return 100.0
    related_degrees = {"bca", "bsc", "b.tech", "btech", "mca", "m.tech", "computer science"}
    if any(item in candidate for item in related_degrees):
        return 70.0
    return 30.0


def get_similarity_score(job_text: str, resume_text: str) -> float:
    cleaned_job = remove_bias_terms(job_text or "")
    cleaned_resume = remove_bias_terms(resume_text or "")
    if not cleaned_job.strip() or not cleaned_resume.strip():
        return 0.0
    if TfidfVectorizer is None or cosine_similarity is None:
        job_terms = set(cleaned_job.lower().split())
        resume_terms = set(cleaned_resume.lower().split())
        if not job_terms:
            return 0.0
        return round((len(job_terms.intersection(resume_terms)) / len(job_terms)) * 100, 2)
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([cleaned_job, cleaned_resume])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(score * 100, 2)


def calculate_final_score(
    skill_score: float,
    experience_score: float,
    education_score: float,
    similarity_score: float,
) -> float:
    score = (
        skill_score * 0.50
        + experience_score * 0.20
        + education_score * 0.15
        + similarity_score * 0.15
    )
    return round(score, 2)


def get_recommendation(final_score: float) -> str:
    if final_score >= 80:
        return "Strong Match"
    if final_score >= 60:
        return "Moderate Match"
    return "Weak Match"


def build_notes(matched_skills: list[str], missing_skills: list[str], final_score: float) -> str:
    return (
        f"Matched {len(matched_skills)} required skills. "
        f"Missing {len(missing_skills)} required skills. "
        f"Final suitability score is {final_score}."
    )


def score_resume_against_job(resume, job) -> dict:
    required_skills = getattr(job, "required_skill_list", split_multi_value(job.required_skills))
    candidate_skills = getattr(resume, "skill_list", split_multi_value(resume.skills))

    skill_score, matched, missing = calculate_skill_score(required_skills, candidate_skills)
    experience_score = calculate_experience_score(float(resume.experience_years or 0), job.min_experience)
    education_score = calculate_education_score(job.qualifications, resume.education or "")

    job_text = " ".join(
        [
            job.title or "",
            job.description_text or "",
            job.required_skills or "",
            job.keywords or "",
            job.qualifications or "",
        ]
    )
    resume_text = " ".join(
        [
            resume.raw_text or "",
            resume.skills or "",
            resume.education or "",
            resume.experience_text or "",
        ]
    )
    similarity_score = get_similarity_score(job_text, resume_text)
    final_score = calculate_final_score(
        skill_score,
        experience_score,
        education_score,
        similarity_score,
    )
    return {
        "skill_score": skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "similarity_score": similarity_score,
        "suitability_score": final_score,
        "recommendation": get_recommendation(final_score),
        "matched_skills": ", ".join(matched),
        "missing_skills": ", ".join(missing),
        "notes": build_notes(matched, missing, final_score),
    }
