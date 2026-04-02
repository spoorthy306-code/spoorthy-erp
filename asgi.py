import time
import random
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, Header, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from services.erp_api import (
    post_ledger_entry,
    get_balance_sheet,
    run_warehouse_etl,
    calculate_inventory_turnover,
    schedule_report_generation,
    create_workflow_definition,
    create_workflow_instance,
    list_pending_tasks,
    process_incoming_webhook,
    notify_outgoing_webhook,
    anonymize_user_data,
    list_inventory_products,
    create_inventory_product,
    update_inventory_product,
    delete_inventory_product,
    api_metrics,
)
from services.ledger.reconciliation import reconcile_bank_statement
from services.ledger.period_close import period_close
from services.ledger.reversal import reverse_entry
from services.ledger.multi_currency import get_exchange_rates, set_exchange_rate
from services.ledger.chart_of_accounts_import_export import import_coa_csv, export_coa_csv
from services.workflow.parallel_gateways import define_parallel_workflow, fork_join_instance
from services.workflow.subworkflows import spawn_subworkflow
from services.workflow.escalations import check_escalations
from services.workflow.workflow_metrics import workflow_metrics
from services.workflow.timer_events import schedule_workflow_start
from services.workflow.ui_designer_json import validate_workflow_json
from services.warehouse.export_endpoints import export_sales, export_inventory
from services.warehouse.dashboard_api import dashboard_kpis, sales_trend
from services.ai.train_pipeline import train_pipeline
from services.ai.feature_store import compute_features
from services.ai.inference_cache import inference_cache
from services.ai.anomaly_explanation import anomaly_explanation
from services.ai.ab_testing import ab_test_predict
from services.integration.dead_letter_ui import list_dead_letter, replay_dead_letter, delete_dead_letter
from services.integration.sla_monitoring import integration_metrics
from shared.libs.security.mfa import enable_mfa, verify_mfa
from shared.libs.security.sso import login_redirect, auth_callback
from shared.libs.security.password_policy import change_password
from shared.libs.security.brute_force import check_login_attempts, record_failed_attempt
from shared.libs.security.csp_headers import add_csp_header
from shared.libs.security.gdpr_auto_purge import purge_old_user_data
from services.finance.invoicing import create_invoice, list_invoices, match_payment
from services.finance.tax_calculation import calculate_tax
from services.finance.budget_vs_actual import budget_variances
from services.inventory.serial_lot_tracking import add_serial_lot
from services.inventory.bin_locations import set_bin_location
from services.inventory.transfer_orders import create_transfer, complete_transfer
from services.inventory.cycle_count import schedule_cycle_count, record_count
from services.hr.leave_management import request_leave, get_leave_balance
from services.hr.payroll_stub import calculate_payroll
from services.hr.performance_reviews import create_review, list_reviews
from services.hr.onboarding_workflow import start_onboarding
from services.sales.quote_to_order import convert_quote_to_order
from services.sales.discount_engine import apply_discount
from services.sales.customer_credit_limit import check_credit_limit
from services.manufacturing.mrp import explode_bom
from services.manufacturing.capacity_planning import get_capacity_load
from services.manufacturing.quality_control import create_inspection

app = FastAPI(
    title="Spoorthy ERP (Streamlit + FastAPI bridge)",
    description="FastAPI gateway combining ERP modules, analytics, and workflow services.",
    version="1.0.1",
)

logger = logging.getLogger("asgi")
logging.basicConfig(level=logging.INFO)

rate_limits_user: Dict[str, List[float]] = {}
rate_limits_api: Dict[str, List[float]] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


@app.middleware("http")
async def audit_and_rate_limit(request: Request, call_next):
    start = time.time()
    user = request.headers.get("X-User", "anonymous")
    api_key = request.headers.get("X-API-Key", "anon")

    # user-based rate limit 100/min
    count_user = rate_limits_user.get(user, [])
    count_user = [t for t in count_user if t > start - 60]
    if len(count_user) >= 100:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded for user"})
    count_user.append(start)
    rate_limits_user[user] = count_user

    # api-key rate limit 1000/min
    count_key = rate_limits_api.get(api_key, [])
    count_key = [t for t in count_key if t > start - 60]
    if len(count_key) >= 1000:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded for api key"})
    count_key.append(start)
    rate_limits_api[api_key] = count_key

    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000.0
    api_metrics["request_count"] += 1
    api_metrics["latency_ms"].append(duration_ms)
    if response.status_code >= 400:
        api_metrics["error_count"] += 1

    response = add_csp_header(request, response)
    return response


@app.on_event("startup")
async def startup_tasks():
    # ensure database schema is created before first request
    try:
        schema.create_all_tables()
    except Exception as exc:
        logger.warning("Schema creation on startup failed: %s", exc)

    # immediately run ETL once at startup
    try:
        run_warehouse_etl()
    except Exception as exc:
        logger.warning("Initial warehouse ETL failed: %s", exc)

    # schedule hourly warehouse ETL
    import threading

    def cascade_etl():
        try:
            run_warehouse_etl()
            logger.info("warehouse ETL completed")
        except Exception as exc:
            logger.warning("warehouse ETL failed: %s", exc)
        threading.Timer(3600, cascade_etl).start()

    threading.Timer(3600, cascade_etl).start()


@app.get("/", summary="Root")
async def root():
    return {
        "message": "Spoorthy ERP is a Streamlit app. Run streamlit run ui/app.py for the UI.",
        "info": "Use /health for readiness checks.",
    }


@app.get("/health", summary="Health check")
async def health_check():
    return JSONResponse(content={"status": "ok"})


@app.get("/metrics", summary="Prometheus metrics")
async def metrics():
    avg_latency = (
        sum(api_metrics["latency_ms"]) / len(api_metrics["latency_ms"]) if api_metrics["latency_ms"] else 0
    )
    return {
        "request_count": api_metrics["request_count"],
        "error_count": api_metrics["error_count"],
        "avg_latency_ms": round(avg_latency, 2),
    }


@app.post("/ledger/post-entry")
async def ledger_post_entry(request: Request, idempotency_key: Optional[str] = Header(None)):
    payload = await request.json()
    return post_ledger_entry(payload, idempotency_key=idempotency_key, user=request.headers.get("X-User", "system"))


@app.get("/ledger/balance-sheet")
async def ledger_balance_sheet(date: Optional[str] = None):
    return get_balance_sheet(date)


@app.get("/analytics/sales/forecast")
async def analytics_sales_forecast():
    return {
        "forecast": round(random.uniform(100000, 500000), 2),
        "model": "ai-placeholder-v1",
        "as_of": datetime.utcnow().isoformat(),
    }


@app.get("/analytics/inventory/turnover")
async def analytics_inventory_turnover():
    return calculate_inventory_turnover()


@app.post("/ledger/reconcile")
async def ledger_reconcile(body: Dict[str, Any]):
    csv_text = body.get("csv","")
    return reconcile_bank_statement(csv_text)


@app.post("/ledger/period/close")
async def ledger_period_close(body: Dict[str, Any]):
    return period_close(body.get("period_end", ""))


@app.post("/ledger/entries/reverse")
async def ledger_entries_reverse(body: Dict[str, Any]):
    return reverse_entry(int(body.get("voucher_id", 0)))


@app.get("/ledger/rates")
async def ledger_rates():
    return get_exchange_rates()


@app.post("/ledger/rates")
async def ledger_set_rate(body: Dict[str, Any]):
    return set_exchange_rate(body.get("from"), body.get("to"), float(body.get("rate", 1.0)))


@app.post("/coa/import")
async def coa_import(body: Dict[str, Any]):
    return import_coa_csv(body.get("csv", ""))


@app.get("/coa/export")
async def coa_export():
    return {"csv": export_coa_csv()}


@app.post("/workflow/parallel/define")
async def workflow_parallel_define(body: Dict[str, Any]):
    return define_parallel_workflow(body.get("name", ""), body.get("nodes", {}), body.get("branches", {}))


@app.post("/workflow/parallel/start")
async def workflow_parallel_start(body: Dict[str, Any]):
    return fork_join_instance(int(body.get("workflow_id", 0)), body)


@app.post("/workflow/subworkflow")
async def workflow_subworkflow(body: Dict[str, Any]):
    return spawn_subworkflow(int(body.get("parent_instance_id", 0)), int(body.get("sub_definition_id", 0)))


@app.get("/workflow/escalations/check")
async def workflow_escalations():
    return check_escalations()


@app.get("/workflow/metrics")
async def workflow_metrics_endpoint():
    return workflow_metrics()


@app.post("/workflow/schedule")
async def workflow_schedule(body: Dict[str, Any]):
    from datetime import datetime
    start_at = datetime.fromisoformat(body.get("start_at"))
    return schedule_workflow_start(int(body.get("definition_id", 0)), start_at)


@app.post("/workflow/validate")
async def workflow_validate(body: Dict[str, Any]):
    return validate_workflow_json(body)


@app.get("/analytics/sales/export")
async def analytics_sales_export(format: str = "csv"):
    return {"data": export_sales(format)}


@app.get("/analytics/inventory/export")
async def analytics_inventory_export(format: str = "xlsx"):
    return {"data": export_inventory(format)}


@app.get("/dashboard/kpis")
async def dashboard_kpis_endpoint():
    return dashboard_kpis()


@app.get("/dashboard/sales_trend")
async def dashboard_sales_trend(days: int = 30):
    return sales_trend(days)


@app.post("/ai/train")
async def ai_train():
    return train_pipeline()


@app.post("/ai/feature-store")
async def ai_feature_store():
    return compute_features()


@app.post("/ai/infer")
async def ai_infer(body: Dict[str, Any]):
    return inference_cache(body)


@app.post("/detect/anomaly")
async def detect_anomaly(body: Dict[str, Any]):
    return anomaly_explanation(body)


@app.post("/predict/sales/ab")
async def predict_sales_ab(body: Dict[str, Any]):
    return ab_test_predict(body)


@app.get("/dead-letter")
async def dead_letter_list():
    return list_dead_letter()


@app.post("/dead-letter/{record_id}/replay")
async def dead_letter_replay(record_id: int):
    return replay_dead_letter(record_id)


@app.delete("/dead-letter/{record_id}")
async def dead_letter_delete(record_id: int):
    return delete_dead_letter(record_id)


@app.get("/integration/metrics")
async def integration_metrics_endpoint():
    return integration_metrics()


@app.post("/auth/mfa/enable")
async def auth_mfa_enable(body: Dict[str, Any]):
    return enable_mfa(int(body.get("user_id", 0)))


@app.post("/auth/mfa/verify")
async def auth_mfa_verify(body: Dict[str, Any]):
    return {"valid": verify_mfa(int(body.get("user_id", 0)), body.get("code", ""))}


@app.get("/auth/login/{provider}")
async def auth_login(provider: str):
    return login_redirect(provider)


@app.get("/auth/callback")
async def auth_callback_endpoint(request: Request):
    return await auth_callback(request)


@app.post("/auth/change-password")
async def auth_change_password(body: Dict[str, Any]):
    return change_password(int(body.get("user_id", 0)), body.get("new_password", ""))


@app.post("/auth/login")
async def auth_login_enhanced(body: Dict[str, Any], request: Request):
    ip = request.client.host if request.client else 'unknown'
    check = check_login_attempts(body.get('username', ''), ip)
    if check.get('blocked'):
        return {'error': 'blocked'}
    # simple credentials check stub
    if body.get('username') == 'admin' and body.get('password') == 'admin':
        return {'token': 'fake-token'}
    record_failed_attempt(body.get('username', ''), ip)
    return {'error': 'invalid_credentials'}


@app.post("/auth/purge-gdpr")
async def auth_purge_gdpr():
    return purge_old_user_data()


@app.post("/finance/invoices")
async def finance_create_invoice(body: Dict[str, Any]):
    return create_invoice(body.get('order_id',0), body.get('customer_id',0), body.get('lines',[]))


@app.get("/finance/invoices")
async def finance_list_invoices():
    return list_invoices()


@app.post("/finance/payments/match")
async def finance_match_payment(body: Dict[str, Any]):
    return match_payment(body.get('payment_id',0), body.get('invoice_id',0))


@app.get("/finance/budget/variances")
async def finance_budget_variances():
    return budget_variances()


@app.post("/inventory/serial-lot")
async def inventory_serial_lot(body: Dict[str, Any]):
    return add_serial_lot(body.get('item_id',0), body.get('serial_number',''), body.get('lot_number',''), body.get('expiry_date',''))


@app.post("/inventory/bin-location")
async def inventory_bin_location(body: Dict[str, Any]):
    return set_bin_location(body.get('item_id',0), body.get('warehouse',''), body.get('zone',''), body.get('rack',''), body.get('bin_code',''))


@app.post("/inventory/transfers")
async def inventory_create_transfer(body: Dict[str, Any]):
    return create_transfer(body.get('source_warehouse',''), body.get('target_warehouse',''), body.get('item_id',0), body.get('quantity',0))


@app.post("/inventory/transfers/{transfer_id}/complete")
async def inventory_complete_transfer(transfer_id: int):
    return complete_transfer(transfer_id)


@app.post("/inventory/cycle-count")
async def inventory_cycle_count(body: Dict[str, Any]):
    return schedule_cycle_count(body.get('item_id',0), body.get('count_date',''))


@app.post("/inventory/cycle-count/{cycle_id}/record")
async def inventory_record_count(cycle_id: int, body: Dict[str, Any]):
    return record_count(cycle_id, body.get('counted_qty',0))


@app.post("/hr/leave")
async def hr_leave_request(body: Dict[str, Any]):
    return request_leave(body.get('employee_id',0), body.get('from_date',''), body.get('to_date',''), body.get('reason',''))


@app.get("/hr/leave/{employee_id}/balance")
async def hr_leave_balance(employee_id: int):
    return get_leave_balance(employee_id)


@app.post("/hr/payroll/calculate")
async def hr_payroll(body: Dict[str, Any]):
    return calculate_payroll(body.get('gross',0), body.get('deductions',0), body.get('tax_pct',0.1))


@app.post("/hr/performance")
async def hr_performance(body: Dict[str, Any]):
    return create_review(body.get('employee_id',0), body.get('score',0), body.get('comments',''))


@app.get("/hr/performance/{employee_id}")
async def hr_performance_list(employee_id: int):
    return list_reviews(employee_id)


@app.post("/hr/onboarding")
async def hr_onboarding(body: Dict[str, Any]):
    return start_onboarding(body.get('employee_id',0))


@app.post("/sales/quote-to-order")
async def sales_quote_to_order(body: Dict[str, Any]):
    return convert_quote_to_order(body.get('quote_id',0))


@app.post("/sales/discount")
async def sales_discount(body: Dict[str, Any]):
    return apply_discount(body.get('amount',0), body.get('volume',1), body.get('coupon',None))


@app.post("/sales/credit-check")
async def sales_credit_check(body: Dict[str, Any]):
    return check_credit_limit(body.get('customer_id',0), body.get('order_amount',0))


@app.get("/manufacturing/mrp")
async def manufacturing_mrp(product_id: int, demand_qty: float):
    return explode_bom(product_id, demand_qty)


@app.get("/manufacturing/capacity")
async def manufacturing_capacity(workcenter_id: int):
    return get_capacity_load(workcenter_id)


@app.post("/manufacturing/quality")
async def manufacturing_quality(body: Dict[str, Any]):
    return create_inspection(body.get('order_id',0), body.get('results', {}))


@app.post("/analytics/reports/generate")
async def analytics_reports_generate(body: Dict[str, Any], background_tasks: BackgroundTasks):
    job = schedule_report_generation(body)
    background_tasks.add_task(lambda: logger.info("Report job completed: %s", job["job_id"]))
    return job


@app.post("/workflows/definitions")
async def workflows_definitions(body: Dict[str, Any]):
    return create_workflow_definition(body)


@app.post("/workflows/instances")
async def workflows_instances(body: Dict[str, Any]):
    return create_workflow_instance(body)


@app.get("/tasks/pending")
async def tasks_pending():
    return list_pending_tasks()


@app.get("/inventory/products")
async def inventory_products():
    return list_inventory_products()


@app.post("/inventory/products")
async def inventory_products_create(body: Dict[str, Any]):
    return create_inventory_product(body)


@app.put("/inventory/products/{product_id}")
async def inventory_products_update(product_id: int, body: Dict[str, Any]):
    return update_inventory_product(product_id, body)


@app.delete("/inventory/products/{product_id}")
async def inventory_products_delete(product_id: int):
    return delete_inventory_product(product_id)


@app.post("/integration/webhooks/incoming")
async def integration_webhook_incoming(request: Request):
    headers = dict(request.headers)
    body = await request.json()
    return process_incoming_webhook(headers, body)


@app.post("/integration/webhooks/outgoing")
async def integration_webhook_outgoing(body: Dict[str, Any]):
    return notify_outgoing_webhook(body.get("url"), body.get("payload", {}))


@app.delete("/user/data/{user_id}")
async def user_delete_data(user_id: int):
    return anonymize_user_data(user_id)

