from flask import Blueprint, jsonify, request

from backend.extensions import db
from backend.models import JobDescription, Resume, ScreeningResult
from backend.services.auth_service import get_current_user, login_required, role_required
from backend.services.jd_service import prepare_job_payload
from backend.services.monitoring_service import log_system_event


job_bp = Blueprint("jobs", __name__, url_prefix="/api")


def _job_or_404(job_id: int):
    return JobDescription.query.get_or_404(job_id)


def _authorize_job_access(job: JobDescription, user) -> bool:
    return user.role == "admin" or job.recruiter_id == user.id


@job_bp.get("/dashboard/stats")
@login_required
def dashboard_stats():
    user = get_current_user()
    if user.role == "admin":
        payload = {
            "total_jobs": JobDescription.query.count(),
            "total_resumes": Resume.query.count(),
            "screened_candidates": ScreeningResult.query.count(),
            "recent_jobs": [
                job.to_dict()
                for job in JobDescription.query.order_by(JobDescription.created_at.desc()).limit(5)
            ],
        }
    else:
        recruiter_jobs = JobDescription.query.filter_by(recruiter_id=user.id)
        payload = {
            "total_jobs": recruiter_jobs.count(),
            "total_resumes": Resume.query.filter_by(recruiter_id=user.id).count(),
            "screened_candidates": (
                ScreeningResult.query.join(JobDescription, ScreeningResult.jd_id == JobDescription.id)
                .filter(JobDescription.recruiter_id == user.id)
                .count()
            ),
            "recent_jobs": [
                job.to_dict()
                for job in recruiter_jobs.order_by(JobDescription.created_at.desc()).limit(5)
            ],
        }
    return jsonify({"success": True, "stats": payload})


@job_bp.post("/jobs")
@role_required("recruiter")
def create_job():
    user = get_current_user()
    payload = prepare_job_payload(request.get_json(silent=True) or {})
    if not payload["title"] or not payload["description_text"]:
        return jsonify({"success": False, "message": "Job title and description are required"}), 400

    job = JobDescription(recruiter_id=user.id, **payload)
    db.session.add(job)
    db.session.commit()
    log_system_event("INFO", "jobs", f"Job profile created: {job.title}", created_by=user.id)
    return jsonify({"success": True, "message": "Job profile created", "job": job.to_dict()}), 201


@job_bp.get("/jobs")
@login_required
def list_jobs():
    user = get_current_user()
    query = JobDescription.query
    if user.role != "admin":
        query = query.filter_by(recruiter_id=user.id)
    jobs = query.order_by(JobDescription.created_at.desc()).all()
    return jsonify({"success": True, "jobs": [job.to_dict() for job in jobs]})


@job_bp.get("/jobs/<int:job_id>")
@login_required
def get_job(job_id: int):
    user = get_current_user()
    job = _job_or_404(job_id)
    if not _authorize_job_access(job, user):
        return jsonify({"success": False, "message": "Access denied"}), 403
    return jsonify({"success": True, "job": job.to_dict()})


@job_bp.put("/jobs/<int:job_id>")
@role_required("recruiter")
def update_job(job_id: int):
    user = get_current_user()
    job = _job_or_404(job_id)
    if job.recruiter_id != user.id:
        return jsonify({"success": False, "message": "Access denied"}), 403

    payload = prepare_job_payload(request.get_json(silent=True) or {})
    for field, value in payload.items():
        setattr(job, field, value)
    db.session.commit()
    return jsonify({"success": True, "message": "Job profile updated", "job": job.to_dict()})


@job_bp.delete("/jobs/<int:job_id>")
@role_required("recruiter")
def delete_job(job_id: int):
    user = get_current_user()
    job = _job_or_404(job_id)
    if job.recruiter_id != user.id:
        return jsonify({"success": False, "message": "Access denied"}), 403

    title = job.title
    db.session.delete(job)
    db.session.commit()
    log_system_event("INFO", "jobs", f"Job profile deleted: {title}", created_by=user.id)
    return jsonify({"success": True, "message": "Job profile deleted"})
