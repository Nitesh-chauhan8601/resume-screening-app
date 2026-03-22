from backend.extensions import db


class SystemLog(db.Model):
    __tablename__ = "system_logs"

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), nullable=False)
    module = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    error_trace = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "level": self.level,
            "module": self.module,
            "message": self.message,
            "error_trace": self.error_trace,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
