from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError

from backend.extensions import db
from backend.models import IssueTicket, SystemLog, User


def _fallback_user_id() -> Optional[int]:
    admin = User.query.filter_by(role="admin").order_by(User.id.asc()).first()
    if admin:
        return admin.id
    user = User.query.order_by(User.id.asc()).first()
    return user.id if user else None


def log_system_event(
    level: str,
    module: str,
    message: str,
    error_trace: Optional[str] = None,
    create_ticket: bool = False,
    ticket_title: Optional[str] = None,
    severity: str = "medium",
    created_by: Optional[int] = None,
):
    log = SystemLog(
        level=level.upper(),
        module=module,
        message=message,
        error_trace=error_trace,
    )
    db.session.add(log)
    db.session.flush()

    ticket = None
    if create_ticket:
        creator_id = created_by or _fallback_user_id()
        if creator_id:
            ticket = IssueTicket(
                title=ticket_title or message[:150],
                description=message if not error_trace else f"{message}\n\n{error_trace}",
                severity=severity,
                status="open",
                created_by=creator_id,
            )
            db.session.add(ticket)

    db.session.commit()
    return log, ticket


def get_system_health(upload_folder: str, report_folder: str) -> dict:
    database_status = "connected"
    try:
        db.session.execute(db.text("SELECT 1"))
    except SQLAlchemyError:
        database_status = "disconnected"
    return {
        "database": database_status,
        "upload_folder": "available" if Path(upload_folder).exists() else "missing",
        "report_folder": "available" if Path(report_folder).exists() else "missing",
        "errors_today": SystemLog.query.filter_by(level="ERROR").count(),
        "open_tickets": IssueTicket.query.filter(IssueTicket.status != "resolved").count(),
        "server_time": datetime.utcnow().isoformat(),
    }
