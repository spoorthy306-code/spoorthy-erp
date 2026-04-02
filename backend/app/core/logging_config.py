# SPOORTHY QUANTUM OS — Logging Configuration
# Structured logging with PII masking and 4 rotating file handlers

import logging
import logging.handlers
import os
import re
import sys
from typing import Any, Dict

import structlog
from pythonjsonlogger import jsonlogger

# Log directory
LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# ── PII masking patterns ──────────────────────────────────────────────────────
_PAN_RE = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
_GSTIN_RE = re.compile(r"\b\d{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b")
_ACCOUNT_RE = re.compile(r"\b\d{9,18}\b")  # bank account numbers
_CARD_RE = re.compile(r"\b(?:\d[ -]?){13,16}\b")


def _redact_string(s: str) -> str:
    """Apply all PII regex redactions to a string value."""
    s = _PAN_RE.sub(lambda m: m.group()[:2] + "***" + m.group()[-1], s)
    s = _GSTIN_RE.sub(lambda m: m.group()[:4] + "***" + m.group()[-3:], s)
    s = _ACCOUNT_RE.sub(lambda m: m.group()[:3] + "****" + m.group()[-2:], s)
    return s


def mask_pii(
    logger: Any, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Mask PII data in log event dicts."""
    sensitive_keys = {
        "password",
        "token",
        "api_key",
        "secret",
        "pan",
        "gstin",
        "email",
        "account_no",
        "card_no",
        "otp",
        "pin",
    }

    for key in list(event_dict.keys()):
        val = event_dict[key]
        lkey = key.lower()

        if any(s in lkey for s in sensitive_keys):
            if isinstance(val, str) and len(val) > 4:
                event_dict[key] = val[:2] + "*" * (len(val) - 4) + val[-2:]
            else:
                event_dict[key] = "***MASKED***"
        elif isinstance(val, str) and len(val) > 8:
            event_dict[key] = _redact_string(val)

    return event_dict


# ── JSON formatter for file handlers ─────────────────────────────────────────
class _PIIJsonFormatter(jsonlogger.JsonFormatter):
    """JSON log formatter that also redacts PII from message strings."""

    def add_fields(
        self, log_record: Dict, record: logging.LogRecord, message_dict: Dict
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["service"] = "spoorthy-erp"
        # Redact PII from the message field
        if "message" in log_record and isinstance(log_record["message"], str):
            log_record["message"] = _redact_string(log_record["message"])


# ── Audit log filter ──────────────────────────────────────────────────────────
class _AuditFilter(logging.Filter):
    """Pass only records that have audit=True in their extra dict."""

    def filter(self, record: logging.LogRecord) -> bool:
        return getattr(record, "audit", False)


# ── HTTP access log filter ────────────────────────────────────────────────────
class _AccessFilter(logging.Filter):
    """Pass only records from the 'access' logger namespace."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith("access") or getattr(record, "access", False)


# ── Build rotating file handler helper ───────────────────────────────────────
def _make_rotating_handler(
    filename: str,
    max_bytes: int = 100 * 1024 * 1024,  # 100 MB
    backup_count: int = 30,
    level: int = logging.DEBUG,
    log_filter: logging.Filter = None,
) -> logging.handlers.RotatingFileHandler:
    handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOG_DIR, filename),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(
        _PIIJsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )
    if log_filter:
        handler.addFilter(log_filter)
    return handler


def setup_logging() -> None:
    """Configure 4 rotating file handlers + stdout + structlog."""

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Remove any existing handlers to avoid duplication on re-import
    root.handlers.clear()

    # 1. stdout — human-readable for Docker / dev
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s — %(message)s", "%H:%M:%S"
        )
    )
    root.addHandler(stdout_handler)

    # 2. app.log — ALL levels, rotating at 100 MB, 30 backups (~30 days)
    root.addHandler(_make_rotating_handler("app.log", level=logging.DEBUG))

    # 3. errors.log — ERROR and above only
    root.addHandler(_make_rotating_handler("errors.log", level=logging.ERROR))

    # 4. audit.log — compliance events only (records with extra={'audit': True})
    audit_handler = _make_rotating_handler("audit.log", level=logging.INFO)
    audit_handler.addFilter(_AuditFilter())
    root.addHandler(audit_handler)

    # 5. access.log — HTTP access log only
    access_handler = _make_rotating_handler("access.log", level=logging.INFO)
    access_handler.addFilter(_AccessFilter())
    root.addHandler(access_handler)

    # ── structlog configuration ───────────────────────────────────────────────
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            mask_pii,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structlog bound logger for the given name."""
    return structlog.get_logger(name)


def audit_log(event: str, **kwargs: Any) -> None:
    """
    Emit a compliance-relevant audit event.
    These records pass through the AuditFilter to audit.log.
    """
    logger = logging.getLogger("audit")
    logger.info(event, extra={"audit": True, **kwargs})


def access_log(
    method: str, path: str, status: int, duration_ms: float, **kwargs: Any
) -> None:
    """Emit an HTTP access log record that goes to access.log."""
    logger = logging.getLogger("access")
    logger.info(
        f"{method} {path} {status} {duration_ms:.1f}ms",
        extra={
            "access": True,
            "method": method,
            "path": path,
            "status": status,
            "duration_ms": duration_ms,
            **kwargs,
        },
    )


# Initialise on import
setup_logging()
