from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Blueprint, current_app, jsonify, request

from backend.extensions import db
from backend.models import Resume
from backend.services.auth_service import get_current_user, login_required, role_required
from backend.services.monitoring_service import log_system_event
from backend.services.resume_parser import parse_resume_file
from backend.utils.file_utils import save_uploaded_file
from backend.utils.validators import allowed_file


resume_bp = Blueprint("resumes", __name__, url_prefix="/api/resumes")


def _get_resume(resume_id: int):
    return Resume.query.get_or_404(resume_id)


def _serialize_resume(resume: Resume) -> dict:
    payload = resume.to_dict()
    payload["raw_text"] = resume.raw_text or ""
    return payload


@resume_bp.get("")
@login_required
def list_resumes():
    user = get_current_user()
    query = Resume.query
    if user.role != "admin":
        query = query.filter_by(recruiter_id=user.id)
    resumes = query.order_by(Resume.uploaded_at.desc()).all()
    return jsonify({"success": True, "resumes": [resume.to_dict() for resume in resumes]})


@resume_bp.post("/upload")
@role_required("recruiter")
def upload_single_resume():
    return _handle_resume_upload(single_only=True)


@resume_bp.post("/upload-bulk")
@role_required("recruiter")
def upload_bulk_resumes():
    return _handle_resume_upload(single_only=False)


def _handle_resume_upload(single_only: bool):
    user = get_current_user()
    files = request.files.getlist("resumes")
    single_file = request.files.get("resume")
    if single_file:
        files.append(single_file)
    if single_only and len(files) > 1:
        return jsonify({"success": False, "message": "Please upload only one resume"}), 400
    if not files:
        return jsonify({"success": False, "message": "No resume files provided"}), 400

    uploaded_items = []
    failed_items = []

    def _process_file(file_storage, upload_folder):
        filename = file_storage.filename or ""
        original_name, saved_path = save_uploaded_file(file_storage, upload_folder)
        try:
            parsed = parse_resume_file(saved_path)
            return True, original_name, saved_path, parsed, None
        except Exception as exc:
            return False, original_name, saved_path, None, str(exc)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for file_storage in files:
            filename = file_storage.filename or ""
            if not allowed_file(filename, current_app.config["ALLOWED_EXTENSIONS"]):
                failed_items.append({"file_name": filename, "reason": "Unsupported file type"})
                continue
            futures.append(executor.submit(_process_file, file_storage, current_app.config["UPLOAD_FOLDER"]))
        
        for future in as_completed(futures):
            success, original_name, saved_path, parsed, error_msg = future.result()
            if success:
                resume = Resume(
                    recruiter_id=user.id,
                    file_name=original_name,
                    file_path=saved_path,
                    parse_status="success",
                    **parsed,
                )
                db.session.add(resume)
                try:
                    db.session.commit()
                    uploaded_items.append(resume.to_dict())
                except Exception as db_exc:
                    db.session.rollback()
                    failed_items.append({"file_name": original_name, "reason": "Database insertion error"})
            else:
                resume = Resume(
                    recruiter_id=user.id,
                    candidate_name="Unknown Candidate",
                    file_name=original_name,
                    file_path=saved_path,
                    parse_status="failed",
                    raw_text="",
                )
                db.session.add(resume)
                db.session.commit()
                failed_items.append({"file_name": original_name, "reason": error_msg})
                log_system_event(
                    "ERROR",
                    "resume_parser",
                    f"Resume parsing failed for {original_name}",
                    error_trace=error_msg,
                    create_ticket=True,
                    ticket_title="Resume parsing failure",
                    severity="medium",
                    created_by=user.id,
                )

    status_code = 201 if uploaded_items else 400
    return (
        jsonify(
            {
                "success": bool(uploaded_items),
                "message": f"Processed {len(uploaded_items)} resumes",
                "uploaded": uploaded_items,
                "failed": failed_items,
            }
        ),
        status_code,
    )


@resume_bp.get("/<int:resume_id>")
@login_required
def get_resume(resume_id: int):
    user = get_current_user()
    resume = _get_resume(resume_id)
    if user.role != "admin" and resume.recruiter_id != user.id:
        return jsonify({"success": False, "message": "Access denied"}), 403
    return jsonify({"success": True, "resume": _serialize_resume(resume)})


@resume_bp.delete("/<int:resume_id>")
@role_required("recruiter")
def delete_resume(resume_id: int):
    user = get_current_user()
    resume = _get_resume(resume_id)
    if resume.recruiter_id != user.id:
        return jsonify({"success": False, "message": "Access denied"}), 403
    db.session.delete(resume)
    db.session.commit()
    return jsonify({"success": True, "message": "Resume deleted"})
