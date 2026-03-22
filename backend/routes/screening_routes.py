from flask import Blueprint, jsonify, request
from sqlalchemy import desc

from backend.extensions import db
from backend.models import JobDescription, Resume, ScreeningResult
from backend.services.auth_service import get_current_user, login_required, role_required
from backend.services.matching_service import score_resume_against_job


screening_bp = Blueprint("screening", __name__, url_prefix="/api/screening")


def _get_job(job_id: int):
    return JobDescription.query.get_or_404(job_id)


def _authorize_job(job, user) -> bool:
    return user.role == "admin" or job.recruiter_id == user.id


def _apply_rankings(jd_id: int) -> None:
    ordered_results = (
        ScreeningResult.query.join(Resume, ScreeningResult.resume_id == Resume.id)
        .filter(ScreeningResult.jd_id == jd_id)
        .order_by(
            desc(ScreeningResult.suitability_score),
            desc(ScreeningResult.skill_score),
            desc(Resume.experience_years),
        )
        .all()
    )
    for index, result in enumerate(ordered_results, start=1):
        result.ranking = index
    db.session.commit()


@screening_bp.post("/run/<int:jd_id>")
@role_required("recruiter")
def run_screening(jd_id: int):
    user = get_current_user()
    job = _get_job(jd_id)
    if job.recruiter_id != user.id:
        return jsonify({"success": False, "message": "Access denied"}), 403

    data = request.get_json(silent=True) or {}
    resume_ids = data.get("resume_ids") or []
    query = Resume.query.filter_by(recruiter_id=user.id, parse_status="success")
    if resume_ids:
        query = query.filter(Resume.id.in_(resume_ids))
    resumes = query.all()

    if not resumes:
        return jsonify({"success": False, "message": "No parsed resumes available for screening"}), 400

    processed = []
    for resume in resumes:
        scoring = score_resume_against_job(resume, job)
        result = ScreeningResult.query.filter_by(resume_id=resume.id, jd_id=jd_id).first()
        if result is None:
            result = ScreeningResult(resume_id=resume.id, jd_id=jd_id)
            db.session.add(result)
        for field, value in scoring.items():
            setattr(result, field, value)
        processed.append(
            {
                "resume_id": resume.id,
                "candidate_name": resume.candidate_name,
                "suitability_score": scoring["suitability_score"],
            }
        )
    db.session.commit()
    _apply_rankings(jd_id)
    return jsonify({"success": True, "message": "Screening completed", "processed": processed})


@screening_bp.get("/results/<int:jd_id>")
@login_required
def get_results(jd_id: int):
    user = get_current_user()
    job = _get_job(jd_id)
    if not _authorize_job(job, user):
        return jsonify({"success": False, "message": "Access denied"}), 403

    sort = (request.args.get("sort") or "highest").lower()
    qualification = (request.args.get("qualification") or "").strip().lower()
    min_experience = request.args.get("min_experience", type=float)
    recommendation = (request.args.get("recommendation") or "").strip().lower()

    query = ScreeningResult.query.join(Resume, ScreeningResult.resume_id == Resume.id).filter(
        ScreeningResult.jd_id == jd_id
    )
    if qualification:
        query = query.filter(Resume.education.ilike(f"%{qualification}%"))
    if min_experience is not None:
        query = query.filter(Resume.experience_years >= min_experience)
    if recommendation:
        query = query.filter(ScreeningResult.recommendation.ilike(f"%{recommendation}%"))

    if sort == "lowest":
        query = query.order_by(ScreeningResult.suitability_score.asc())
    else:
        query = query.order_by(
            ScreeningResult.ranking.is_(None),
            ScreeningResult.ranking.asc(),
            ScreeningResult.suitability_score.desc(),
        )

    results = query.all()
    return jsonify(
        {
            "success": True,
            "job": job.to_dict(),
            "count": len(results),
            "results": [result.to_dict() for result in results],
        }
    )


@screening_bp.get("/result/<int:result_id>")
@login_required
def get_result_detail(result_id: int):
    user = get_current_user()
    result = ScreeningResult.query.get_or_404(result_id)
    job = result.job_description
    if not _authorize_job(job, user):
        return jsonify({"success": False, "message": "Access denied"}), 403
    payload = result.to_dict()
    payload["job"] = job.to_dict()
    return jsonify({"success": True, "result": payload})
