import os
import json
import time
import uuid
import logging
import hashlib
import random
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional

import requests
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from db import schema
from db.schema import (
    SessionLocal,
    Ledger,
    AccountGroup,
    Transaction,
    Voucher,
    Party,
    AppUser,
    WorkflowDefinition,
    WorkflowInstance,
    Task,
    Webhook,
    IntegrationLog,
    IdempotencyKey,
    WarehouseSalesFact,
    ManufacturingBOM,
    WorkOrder,
)

logger = logging.getLogger("erp_api")
logging.basicConfig(level=logging.INFO)

AES_AVAILABLE = False
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    AES_AVAILABLE = True
except ImportError:
    logger.warning("cryptography not installed - AES encryption will use dummy obfuscation")

# Prometheus metrics storage (simple, no external dependency if prometheus_client absent)
api_metrics = {
    "request_count": 0,
    "error_count": 0,
    "latency_ms": []
}

# Simple in-memory rate limiter for demo
rate_limits = {
    "user": {},
    "api_key": {}
}


def current_millis() -> int:
    return int(time.time() * 1000)


def track_metric(status_code: int, latency_ms: float):
    api_metrics["request_count"] += 1
    api_metrics["latency_ms"].append(latency_ms)
    if status_code >= 400:
        api_metrics["error_count"] += 1


def encrypt_sensitive(value: str, key: Optional[bytes] = None) -> str:
    if not key:
        key = os.environ.get("AES_KEY", "0123456789abcdef0123456789abcdef").encode()[:32]
    if AES_AVAILABLE:
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, value.encode(), None)
        return (nonce + ct).hex()
    return hashlib.sha256(value.encode()).hexdigest()


def decrypt_sensitive(value: str, key: Optional[bytes] = None) -> str:
    if not key:
        key = os.environ.get("AES_KEY", "0123456789abcdef0123456789abcdef").encode()[:32]
    if AES_AVAILABLE:
        raw = bytes.fromhex(value)
        nonce = raw[:12]
        ct = raw[12:]
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ct, None).decode()
    return "[encrypted]"


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_idempotency(db: Session, key_value: str, endpoint: str, request_hash: Optional[str] = None):
    record = db.query(IdempotencyKey).filter_by(key=key_value).first()
    if record:
        return record
    new = IdempotencyKey(key=key_value, endpoint=endpoint, request_hash=request_hash or "")
    db.add(new)
    db.commit()
    return new


def post_ledger_entry(body: Dict[str, Any], idempotency_key: Optional[str] = None, user: str = "system") -> Dict[str, Any]:
    schema.create_all_tables()
    db = SessionLocal()
    try:
        if not idempotency_key:
            raise HTTPException(status_code=400, detail="idempotency_key header is required")

        existing = db.query(IdempotencyKey).filter_by(key=idempotency_key).first()
        if existing and existing.response_json:
            return json.loads(existing.response_json)

        entry = body
        lines = entry.get("lines", [])
        if not lines or not isinstance(lines, list):
            raise HTTPException(status_code=422, detail="Entry must include lines")

        total_dr = sum(float(l.get("debit", 0)) for l in lines)
        total_cr = sum(float(l.get("credit", 0)) for l in lines)
        if abs(total_dr - total_cr) > 0.01:
            raise HTTPException(status_code=422, detail="Entry is not balanced")

        raw_date = entry.get("date", date.today())
        if isinstance(raw_date, str):
            raw_date = date.fromisoformat(raw_date)

        v = Voucher(
            voucher_no=entry.get("voucher_no", f"IDX-{uuid.uuid4().hex[:8]}"),
            voucher_type_id=entry.get("voucher_type_id", 1),
            voucher_date=raw_date,
            fiscal_year=entry.get("fiscal_year", "2025-26"),
            narration=entry.get("narration", "Ledger Entry"),
            total_amount=entry.get("total_amount", total_dr),
            status="POSTED",
            created_by=user,
        )
        db.add(v)
        db.flush()

        for line in lines:
            ledger_code = line.get("ledger_code")
            if not ledger_code:
                raise HTTPException(status_code=422, detail="Each line needs ledger_code")
            ledger = db.query(Ledger).filter_by(code=ledger_code).first()
            if not ledger:
                raise HTTPException(status_code=404, detail=f"Ledger {ledger_code} not found")
            db.add(Transaction(
                voucher_id=v.id,
                ledger_id=ledger.id,
                debit=float(line.get("debit", 0)),
                credit=float(line.get("credit", 0)),
                narration=line.get("narration", entry.get("narration")),
            ))

        db.commit()

        # record idempotency for future
        existing = ensure_idempotency(db, idempotency_key, "/ledger/post", str(hash(json.dumps(entry, sort_keys=True))))
        existing.response_json = json.dumps({"voucher_id": v.id, "voucher_no": v.voucher_no})
        existing.created_by = user
        db.commit()

        return {"voucher_id": v.id, "voucher_no": v.voucher_no}

    finally:
        db.close()


def get_balance_sheet(as_of: Optional[str] = None) -> Dict[str, float]:
    db = SessionLocal()
    try:
        cutoff = date.fromisoformat(as_of) if as_of else date.today()
        assets = liabilities = equity = 0.0

        ledgers = db.query(Ledger).join(AccountGroup).all()
        for ledger in ledgers:
            txns = (
                db.query(Transaction)
                  .join(Voucher)
                  .filter(Transaction.ledger_id == ledger.id)
                  .filter(Voucher.voucher_date <= cutoff)
                  .all()
            )
            dr = sum(float(t.debit or 0) for t in txns)
            cr = sum(float(t.credit or 0) for t in txns)
            bal = dr - cr if ledger.group.group_type in ["ASSET", "EXPENSE"] else cr - dr
            if ledger.group.group_type == "ASSET":
                assets += bal
            elif ledger.group.group_type == "LIABILITY":
                liabilities += bal
            elif ledger.group.group_type == "INCOME":
                equity += cr - dr
            elif ledger.group.group_type == "EXPENSE":
                equity -= dr - cr

        return {
            "as_of": cutoff.isoformat(),
            "assets": round(assets, 2),
            "liabilities": round(liabilities, 2),
            "equity": round(assets - liabilities, 2),
            "retained_earnings_estimate": round(equity, 2),
        }

    finally:
        db.close()


def run_warehouse_etl() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(hours=1)
        txns = db.query(Transaction).join(Voucher).filter(Voucher.voucher_date >= since.date()).all()
        inserted = 0
        for txn in txns:
            db.add(WarehouseSalesFact(
                transaction_date=txn.voucher.voucher_date,
                voucher_id=txn.voucher_id,
                ledger_id=txn.ledger_id,
                item_id=None,
                quantity=0,
                amount=float(txn.debit or 0) + float(txn.credit or 0)
            ))
            inserted += 1
        db.commit()
        return {"processed": inserted, "since": since.isoformat()}
    finally:
        db.close()


def calculate_inventory_turnover() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        total_sales = sum(float(f.amount or 0) for f in db.query(WarehouseSalesFact).all())
        avg_inventory = sum(float(i.current_stock or 0) * float(i.cost_price or 0) for i in db.query(schema.StockItem).all())
        turnover = (total_sales / avg_inventory) if avg_inventory > 0 else 0.0
        return {"total_sales": total_sales, "avg_inventory": avg_inventory, "inventory_turnover": round(turnover, 3)}
    finally:
        db.close()


def schedule_report_generation(report_data: Dict[str, Any]) -> Dict[str, Any]:
    job_id = uuid.uuid4().hex
    # nop: in production this should be queued into Celery/RQ
    logger.info("queued report job %s", job_id)
    return {"job_id": job_id, "status": "queued", "started_at": datetime.utcnow().isoformat()}


def create_workflow_definition(body: Dict[str, Any]) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        wf = WorkflowDefinition(
            name=body.get("name"),
            description=body.get("description", ""),
            rule_json=json.dumps(body.get("rule", {})),
            created_by=body.get("created_by", "system")
        )
        db.add(wf)
        db.commit()
        return {"id": wf.id, "name": wf.name}
    finally:
        db.close()


def create_workflow_instance(body: Dict[str, Any]) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        instance = WorkflowInstance(
            definition_id=body.get("definition_id"),
            context_json=json.dumps(body.get("context", {})),
            status="RUNNING"
        )
        db.add(instance)
        db.commit()
        return {"id": instance.id, "status": instance.status}
    finally:
        db.close()


def list_pending_tasks() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        tasks = db.query(Task).filter(Task.status == "PENDING").all()
        pending = []
        for t in tasks:
            if t.due_date and datetime.utcnow() > t.due_date and not t.escalated:
                t.escalated = True
                webhook = db.query(Webhook).filter_by(event_code="task.overdue").first()
                if webhook and webhook.is_active:
                    notify_outgoing_webhook(webhook.url, {"task_id": t.id, "issue": "deadline_missed"})
            pending.append({
                "id": t.id,
                "title": t.title,
                "assigned_to": t.assigned_to,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "status": t.status,
                "escalated": t.escalated,
            })
        db.commit()
        return pending
    finally:
        db.close()


def notify_outgoing_webhook(url: str, payload: Dict[str, Any], retries: int = 5) -> Dict[str, Any]:
    backoff = 1
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(url, json=payload, timeout=10)
            status = resp.status_code
            schema_ = IntegrationLog(
                source="outgoing", event_type="webhook", request_body=json.dumps(payload),
                response_body=resp.text, status_code=status
            )
            db = SessionLocal(); db.add(schema_); db.commit(); db.close()
            if 200 <= status < 300:
                return {"status": "sent", "http_status": status}
            raise RuntimeError(f"HTTP {status}")
        except Exception as exc:
            logger.warning("webhook attempt %s failed: %s", attempt, exc)
            if attempt == retries:
                # dead-letter placeholder
                msg = {"status": "dead_letter", "reason": str(exc)}
                return msg
            time.sleep(backoff)
            backoff *= 2


def process_incoming_webhook(headers: Dict[str, str], body: Dict[str, Any]) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        key = headers.get("Idempotency-Key") or headers.get("idempotency-key")
        if not key:
            raise HTTPException(status_code=400, detail="Idempotency-Key header required")

        existing = db.query(IdempotencyKey).filter_by(key=key).first()
        if existing:
            raise HTTPException(status_code=409, detail="Webhook already processed")

        ensure_idempotency(db, key, "/webhooks/incoming")
        event_type = body.get("event_type", "incoming")
        ilog = IntegrationLog(source="incoming", event_type=event_type,
                              request_body=json.dumps(body), response_body="", status_code=200)
        db.add(ilog)
        db.commit()
        return {"status": "processed", "event_type": event_type}
    finally:
        db.close()


def anonymize_user_data(user_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        user = db.query(AppUser).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.full_name = "ANONYMIZED"
        user.email = f"anonymous-{user_id}@example.com"
        user.password_hash = ""
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()
        return {"status": "anonymized", "user_id": user_id}
    finally:
        db.close()


def list_inventory_products() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        items = db.query(schema.StockItem).filter(schema.StockItem.is_active == True).all()
        return [{
            "id": i.id,
            "code": i.code,
            "name": i.name,
            "current_stock": float(i.current_stock or 0),
            "cost_price": float(i.cost_price or 0),
            "sale_price": float(i.sale_price or 0),
            "is_active": i.is_active,
        } for i in items]
    finally:
        db.close()


def create_inventory_product(payload: Dict[str, Any]) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        item = schema.StockItem(
            code=payload["code"],
            name=payload["name"],
            current_stock=payload.get("current_stock", 0),
            cost_price=payload.get("cost_price", 0),
            sale_price=payload.get("sale_price", 0),
            is_active=payload.get("is_active", True),
        )
        db.add(item)
        db.commit()
        return {"id": item.id, "code": item.code}
    finally:
        db.close()


def update_inventory_product(product_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        item = db.query(schema.StockItem).filter_by(id=product_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Product not found")
        for field in ["name", "current_stock", "cost_price", "sale_price", "is_active"]:
            if field in payload:
                setattr(item, field, payload[field])
        db.commit()
        return {"id": item.id, "updated": True}
    finally:
        db.close()


def delete_inventory_product(product_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        item = db.query(schema.StockItem).filter_by(id=product_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Product not found")
        item.is_active = False
        db.commit()
        return {"id": item.id, "deleted": True}
    finally:
        db.close()


def paginate(query, page: int = 1, page_size: int = 100):
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size).all()
