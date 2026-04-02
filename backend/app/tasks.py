# SPOORTHY QUANTUM OS — Celery Tasks
import os

from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "spoorthy_erp", broker=REDIS_URL, backend=REDIS_URL, include=["backend.app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    beat_schedule={
        "daily-bank-reconciliation": {
            "task": "backend.app.tasks.run_bank_reconciliation",
            "schedule": crontab(hour=1, minute=0),
        },
        "monthly-gst-reminder": {
            "task": "backend.app.tasks.send_gst_reminder",
            "schedule": crontab(day_of_month=10, hour=9, minute=0),
        },
        "daily-depreciation": {
            "task": "backend.app.tasks.run_daily_depreciation",
            "schedule": crontab(hour=2, minute=30),
        },
    },
)


@celery_app.task(name="backend.app.tasks.run_bank_reconciliation")
def run_bank_reconciliation():
    """Daily quantum bank reconciliation task"""
    return {"status": "completed", "task": "bank_reconciliation"}


@celery_app.task(name="backend.app.tasks.send_gst_reminder")
def send_gst_reminder():
    """Monthly GST filing reminder"""
    return {"status": "completed", "task": "gst_reminder"}


@celery_app.task(name="backend.app.tasks.run_daily_depreciation")
def run_daily_depreciation():
    """Daily fixed asset depreciation calculation"""
    return {"status": "completed", "task": "depreciation"}
