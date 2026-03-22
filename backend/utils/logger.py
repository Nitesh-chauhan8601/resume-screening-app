import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(app) -> None:
    log_dir = Path(app.root_path).parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_dir / "app.log", maxBytes=1_000_000, backupCount=3)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )
    handler.setLevel(logging.INFO)
    if not any(isinstance(existing, RotatingFileHandler) for existing in app.logger.handlers):
        app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
