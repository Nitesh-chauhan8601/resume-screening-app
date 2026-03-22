from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request

from backend.extensions import db
from backend.models import IssueTicket, SystemLog
from backend.services.auth_service import get_current_user, role_required
from backend.services.monitoring_service import get_system_health


admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/health")
@role_required("admin")
def health():
    payload = get_system_health(
        current_app.config["UPLOAD_FOLDER"],
        current_app.config["REPORT_FOLDER"],
    )
    return jsonify({"success": True, "health": payload})


@admin_bp.get("/logs")
@role_required("admin")
def logs():
    level = (request.args.get("level") or "").strip().upper()
    limit = request.args.get("limit", default=20, type=int)
    query = SystemLog.query
    if level:
        query = query.filter_by(level=level)
    logs = query.order_by(SystemLog.created_at.desc()).limit(limit).all()
    return jsonify({"success": True, "logs": [log.to_dict() for log in logs]})


@admin_bp.get("/tickets")
@role_required("admin")
def list_tickets():
    tickets = IssueTicket.query.order_by(IssueTicket.created_at.desc()).all()
    return jsonify({"success": True, "tickets": [ticket.to_dict() for ticket in tickets]})


@admin_bp.post("/tickets")
@role_required("admin")
def create_ticket():
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    severity = (data.get("severity") or "medium").strip().lower()

    if not title or not description:
        return jsonify({"success": False, "message": "Title and description are required"}), 400

    ticket = IssueTicket(
        title=title,
        description=description,
        severity=severity,
        status="open",
        created_by=user.id,
    )
    db.session.add(ticket)
    db.session.commit()
    return jsonify({"success": True, "message": "Ticket created", "ticket": ticket.to_dict()}), 201


@admin_bp.put("/tickets/<int:ticket_id>")
@role_required("admin")
def update_ticket(ticket_id: int):
    user = get_current_user()
    ticket = IssueTicket.query.get_or_404(ticket_id)
    data = request.get_json(silent=True) or {}

    status = (data.get("status") or ticket.status).strip().lower()
    severity = (data.get("severity") or ticket.severity).strip().lower()
    assigned_to = data.get("assigned_to", ticket.assigned_to)

    ticket.status = status
    ticket.severity = severity
    ticket.assigned_to = assigned_to or user.id
    if status == "resolved" and ticket.resolved_at is None:
        ticket.resolved_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"success": True, "message": "Ticket updated", "ticket": ticket.to_dict()})
