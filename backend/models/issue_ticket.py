from backend.extensions import db


class IssueTicket(db.Model):
    __tablename__ = "issue_tickets"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False, default="medium")
    status = db.Column(db.String(20), nullable=False, default="open")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    resolved_at = db.Column(db.DateTime)

    creator = db.relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_tickets",
    )
    assignee = db.relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_tickets",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "status": self.status,
            "created_by": self.created_by,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }
