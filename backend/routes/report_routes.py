from flask import Blueprint, current_app, jsonify, request, send_file

from backend.models import JobDescription
from backend.services.auth_service import get_current_user, login_required
from backend.services.report_service import build_summary, export_results_csv, save_report_record


report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def _authorize(job, user) -> bool:
    return user.role == "admin" or job.recruiter_id == user.id


@report_bp.get("/<int:jd_id>/summary")
@login_required
def summary(jd_id: int):
    user = get_current_user()
    job = JobDescription.query.get_or_404(jd_id)
    if not _authorize(job, user):
        return jsonify({"success": False, "message": "Access denied"}), 403
    return jsonify({"success": True, "summary": build_summary(job)})


@report_bp.get("/export/<int:jd_id>")
@login_required
def export_report(jd_id: int):
    user = get_current_user()
    job = JobDescription.query.get_or_404(jd_id)
    if not _authorize(job, user):
        return jsonify({"success": False, "message": "Access denied"}), 403

    output_format = (request.args.get("format") or "csv").lower()
    if output_format != "csv":
        return jsonify({"success": False, "message": "Only CSV export is supported in this project"}), 400

    file_path = export_results_csv(job, current_app.config["REPORT_FOLDER"])
    save_report_record(user.id, job.id, "Ranking Export", file_path)
    return send_file(file_path, as_attachment=True)
