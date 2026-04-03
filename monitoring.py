# SPOORTHY QUANTUM OS — Monitoring & Observability
# monitoring.py

import time
from typing import Dict, Any, List
from dataclasses import dataclass
from prometheus_client import (
    Counter, Histogram, Gauge, CollectorRegistry,
    generate_latest, CONTENT_TYPE_LATEST
)
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily
import structlog
import asyncio
from datetime import datetime, timedelta
import json

logger = structlog.get_logger()

@dataclass
class QuantumJobMetrics:
    """Metrics for quantum job execution"""
    job_id: str
    job_type: str
    start_time: float
    end_time: float
    energy: float
    qubits_used: int
    solve_time_ms: float
    confidence: float
    success: bool

@dataclass
class BusinessMetrics:
    """Business-level metrics"""
    entity_id: str
    period: str
    revenue: float
    expenses: float
    profit: float
    gst_liability: float
    compliance_score: float

class SpoorthyMetricsCollector:
    """Custom Prometheus metrics collector for Spoorthy Quantum OS"""

    def __init__(self):
        self.quantum_jobs_total = Counter(
            'spoorthy_quantum_jobs_total',
            'Total number of quantum jobs executed',
            ['job_type', 'status']
        )

        self.quantum_solve_time = Histogram(
            'spoorthy_quantum_solve_time_seconds',
            'Time taken for quantum solves',
            ['job_type'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        )

        self.quantum_energy = Gauge(
            'spoorthy_quantum_energy',
            'Ground state energy from quantum optimization',
            ['job_type']
        )

        self.business_revenue = Gauge(
            'spoorthy_business_revenue_total',
            'Total revenue by entity and period',
            ['entity_id', 'period']
        )

        self.business_profit = Gauge(
            'spoorthy_business_profit_total',
            'Total profit by entity and period',
            ['entity_id', 'period']
        )

        self.gst_liability = Gauge(
            'spoorthy_gst_liability_total',
            'GST liability by entity and period',
            ['entity_id', 'period']
        )

        self.compliance_score = Gauge(
            'spoorthy_compliance_score',
            'Compliance score (0-100) by entity',
            ['entity_id']
        )

        self.api_requests_total = Counter(
            'spoorthy_api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status']
        )

        self.api_request_duration = Histogram(
            'spoorthy_api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
        )

        self.database_connections = Gauge(
            'spoorthy_database_connections_active',
            'Number of active database connections'
        )

        self.cache_hit_ratio = Gauge(
            'spoorthy_cache_hit_ratio',
            'Cache hit ratio (0-1)'
        )

        # Custom metrics storage
        self._quantum_jobs: List[QuantumJobMetrics] = []
        self._business_metrics: List[BusinessMetrics] = []

    def record_quantum_job(self, job: QuantumJobMetrics):
        """Record quantum job metrics"""
        self._quantum_jobs.append(job)

        status = 'success' if job.success else 'failure'
        self.quantum_jobs_total.labels(job_type=job.job_type, status=status).inc()

        if job.success:
            self.quantum_solve_time.labels(job_type=job.job_type).observe(job.solve_time_ms / 1000)
            self.quantum_energy.labels(job_type=job.job_type).set(job.energy)

        logger.info(
            "quantum_job_completed",
            job_id=job.job_id,
            job_type=job.job_type,
            solve_time_ms=job.solve_time_ms,
            energy=job.energy,
            success=job.success
        )

    def record_business_metrics(self, metrics: BusinessMetrics):
        """Record business-level metrics"""
        self._business_metrics.append(metrics)

        self.business_revenue.labels(
            entity_id=metrics.entity_id,
            period=metrics.period
        ).set(metrics.revenue)

        self.business_profit.labels(
            entity_id=metrics.entity_id,
            period=metrics.period
        ).set(metrics.profit)

        self.gst_liability.labels(
            entity_id=metrics.entity_id,
            period=metrics.period
        ).set(metrics.gst_liability)

        self.compliance_score.labels(entity_id=metrics.entity_id).set(metrics.compliance_score)

    def record_api_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record API request metrics"""
        self.api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status)
        ).inc()

        self.api_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    def update_system_metrics(self, db_connections: int, cache_hit_ratio: float):
        """Update system-level metrics"""
        self.database_connections.set(db_connections)
        self.cache_hit_ratio.set(cache_hit_ratio)

    def get_metrics_json(self) -> Dict[str, Any]:
        """Get all metrics as JSON for custom endpoints"""
        return {
            'quantum_jobs': [
                {
                    'job_id': job.job_id,
                    'job_type': job.job_type,
                    'solve_time_ms': job.solve_time_ms,
                    'energy': job.energy,
                    'qubits_used': job.qubits_used,
                    'confidence': job.confidence,
                    'success': job.success,
                    'timestamp': job.end_time
                }
                for job in self._quantum_jobs[-100:]  # Last 100 jobs
            ],
            'business_metrics': [
                {
                    'entity_id': metric.entity_id,
                    'period': metric.period,
                    'revenue': metric.revenue,
                    'expenses': metric.expenses,
                    'profit': metric.profit,
                    'gst_liability': metric.gst_liability,
                    'compliance_score': metric.compliance_score
                }
                for metric in self._business_metrics[-50:]  # Last 50 records
            ],
            'timestamp': time.time()
        }

class AlertManager:
    """Alert management for Spoorthy Quantum OS"""

    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
        self.alert_rules = {
            'quantum_job_failure_rate': {
                'threshold': 0.1,  # 10% failure rate
                'window_minutes': 60,
                'severity': 'critical'
            },
            'api_error_rate': {
                'threshold': 0.05,  # 5% error rate
                'window_minutes': 15,
                'severity': 'warning'
            },
            'compliance_score_low': {
                'threshold': 80,  # Below 80%
                'severity': 'warning'
            },
            'database_connections_high': {
                'threshold': 50,  # Above 50 connections
                'severity': 'warning'
            }
        }

    def check_quantum_job_failure_rate(self, metrics_collector: SpoorthyMetricsCollector) -> List[Dict]:
        """Check quantum job failure rate"""
        alerts = []
        window_start = time.time() - (self.alert_rules['quantum_job_failure_rate']['window_minutes'] * 60)

        recent_jobs = [job for job in metrics_collector._quantum_jobs if job.end_time > window_start]
        if not recent_jobs:
            return alerts

        failure_rate = sum(1 for job in recent_jobs if not job.success) / len(recent_jobs)

        if failure_rate > self.alert_rules['quantum_job_failure_rate']['threshold']:
            alerts.append({
                'alertname': 'QuantumJobFailureRateHigh',
                'severity': self.alert_rules['quantum_job_failure_rate']['severity'],
                'description': f'Quantum job failure rate is {failure_rate:.2%} (threshold: {self.alert_rules["quantum_job_failure_rate"]["threshold"]:.0%})',
                'value': failure_rate,
                'timestamp': time.time()
            })

        return alerts

    def check_compliance_scores(self, metrics_collector: SpoorthyMetricsCollector) -> List[Dict]:
        """Check compliance scores"""
        alerts = []

        # Get latest compliance scores
        compliance_scores = {}
        for metric in metrics_collector._business_metrics:
            compliance_scores[metric.entity_id] = metric.compliance_score

        for entity_id, score in compliance_scores.items():
            if score < self.alert_rules['compliance_score_low']['threshold']:
                alerts.append({
                    'alertname': 'ComplianceScoreLow',
                    'severity': self.alert_rules['compliance_score_low']['severity'],
                    'description': f'Compliance score for entity {entity_id} is {score:.1f}% (threshold: {self.alert_rules["compliance_score_low"]["threshold"]}%)',
                    'entity_id': entity_id,
                    'value': score,
                    'timestamp': time.time()
                })

        return alerts

    def generate_alerts(self, metrics_collector: SpoorthyMetricsCollector) -> List[Dict]:
        """Generate all alerts"""
        all_alerts = []

        all_alerts.extend(self.check_quantum_job_failure_rate(metrics_collector))
        all_alerts.extend(self.check_compliance_scores(metrics_collector))

        # Add new alerts to history
        for alert in all_alerts:
            if alert not in self.alerts:
                self.alerts.append(alert)
                logger.warning(
                    "alert_triggered",
                    alertname=alert['alertname'],
                    severity=alert['severity'],
                    description=alert['description']
                )

        # Keep only recent alerts (last 24 hours)
        cutoff = time.time() - (24 * 60 * 60)
        self.alerts = [alert for alert in self.alerts if alert['timestamp'] > cutoff]

        return all_alerts

class HealthChecker:
    """Health check endpoints for Spoorthy Quantum OS"""

    def __init__(self, metrics_collector: SpoorthyMetricsCollector):
        self.metrics_collector = metrics_collector
        self.start_time = time.time()

    def database_health_check(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            # Simulate database check
            db_status = "healthy"
            response_time = 0.023  # seconds
            connection_count = 5

            return {
                'status': db_status,
                'response_time_seconds': response_time,
                'active_connections': connection_count,
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error("database_health_check_failed", error=str(e))
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }

    def quantum_engine_health_check(self) -> Dict[str, Any]:
        """Check quantum engine availability"""
        try:
            # Simulate quantum engine check
            engine_status = "healthy"
            last_solve_time = time.time() - 300  # 5 minutes ago
            available_qubits = 512

            return {
                'status': engine_status,
                'last_solve_timestamp': last_solve_time,
                'available_qubits': available_qubits,
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error("quantum_engine_health_check_failed", error=str(e))
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }

    def gstn_api_health_check(self) -> Dict[str, Any]:
        """Check GSTN API connectivity"""
        try:
            # Simulate GSTN API check
            api_status = "healthy"
            last_sync = time.time() - 1800  # 30 minutes ago

            return {
                'status': api_status,
                'last_sync_timestamp': last_sync,
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error("gstn_api_health_check_failed", error=str(e))
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }

    def overall_health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        checks = {
            'database': self.database_health_check(),
            'quantum_engine': self.quantum_engine_health_check(),
            'gstn_api': self.gstn_api_health_check()
        }

        overall_status = 'healthy'
        for check_name, check_result in checks.items():
            if check_result['status'] != 'healthy':
                overall_status = 'unhealthy'
                break

        return {
            'status': overall_status,
            'uptime_seconds': time.time() - self.start_time,
            'checks': checks,
            'timestamp': time.time()
        }

# Global instances
metrics_collector = SpoorthyMetricsCollector()
alert_manager = AlertManager()
health_checker = HealthChecker(metrics_collector)

# Alertmanager configuration (YAML format as string)
ALERTMANAGER_CONFIG = """
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'spoorthy306@gmail.com'
  smtp_auth_username: 'spoorthy306@gmail.com'
  smtp_auth_password: 'your_password_here'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'spoorthy-team'
  routes:
  - match:
      severity: critical
    receiver: 'spoorthy-critical'

receivers:
- name: 'spoorthy-team'
  email_configs:
  - to: 'spoorthy306@gmail.com'
    subject: 'Spoorthy Quantum OS Alert: {{ .GroupLabels.alertname }}'
    body: |
      Alert: {{ .GroupLabels.alertname }}
      Severity: {{ .CommonLabels.severity }}
      Description: {{ .CommonAnnotations.description }}
      Value: {{ .CommonLabels.value }}
      Time: {{ .StartsAt }}

- name: 'spoorthy-critical'
  email_configs:
  - to: 'spoorthy306@gmail.com'
    subject: 'CRITICAL: Spoorthy Quantum OS Alert: {{ .GroupLabels.alertname }}'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#critical-alerts'
    title: 'CRITICAL ALERT: {{ .GroupLabels.alertname }}'
    text: |
      *Alert:* {{ .GroupLabels.alertname }}
      *Severity:* {{ .CommonLabels.severity }}
      *Description:* {{ .CommonAnnotations.description }}
      *Value:* {{ .CommonLabels.value }}
"""

# Prometheus alerting rules
PROMETHEUS_ALERT_RULES = """
groups:
- name: spoorthy_alerts
  rules:
  - alert: QuantumJobFailureRateHigh
    expr: rate(spoorthy_quantum_jobs_total{status="failure"}[5m]) / rate(spoorthy_quantum_jobs_total[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High quantum job failure rate"
      description: "Quantum job failure rate is {{ $value }}% (threshold: 10%)"

  - alert: APIErrorRateHigh
    expr: rate(spoorthy_api_requests_total{status=~"5.."}[5m]) / rate(spoorthy_api_requests_total[5m]) > 0.05
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High API error rate"
      description: "API error rate is {{ $value }}% (threshold: 5%)"

  - alert: ComplianceScoreLow
    expr: spoorthy_compliance_score < 80
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Low compliance score"
      description: "Compliance score for entity {{ $labels.entity_id }} is {{ $value }}% (threshold: 80%)"

  - alert: DatabaseConnectionsHigh
    expr: spoorthy_database_connections_active > 50
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High database connections"
      description: "Active database connections: {{ $value }} (threshold: 50)"

  - alert: QuantumSolveTimeHigh
    expr: histogram_quantile(0.95, rate(spoorthy_quantum_solve_time_seconds_bucket[5m])) > 30
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High quantum solve time"
      description: "95th percentile quantum solve time is {{ $value }}s (threshold: 30s)"
"""

def get_prometheus_metrics() -> str:
    """Get Prometheus metrics output"""
    return generate_latest(metrics_collector).decode('utf-8')

def get_metrics_json() -> Dict[str, Any]:
    """Get metrics as JSON"""
    return metrics_collector.get_metrics_json()

def get_alerts() -> List[Dict]:
    """Get current alerts"""
    return alert_manager.generate_alerts(metrics_collector)

def get_health_status() -> Dict[str, Any]:
    """Get overall health status"""
    return health_checker.overall_health_check()

# Example usage functions
async def demo_monitoring():
    """Demo function showing monitoring capabilities"""

    # Record some quantum jobs
    job1 = QuantumJobMetrics(
        job_id="qjob_001",
        job_type="reconciliation",
        start_time=time.time() - 2.5,
        end_time=time.time(),
        energy=-45.67,
        qubits_used=256,
        solve_time_ms=1200,
        confidence=0.95,
        success=True
    )
    metrics_collector.record_quantum_job(job1)

    job2 = QuantumJobMetrics(
        job_id="qjob_002",
        job_type="portfolio_optimization",
        start_time=time.time() - 1.8,
        end_time=time.time(),
        energy=-125.34,
        qubits_used=512,
        solve_time_ms=850,
        confidence=0.92,
        success=True
    )
    metrics_collector.record_quantum_job(job2)

    # Record business metrics
    biz_metrics = BusinessMetrics(
        entity_id="SPOORTHY_TECH",
        period="2024-03",
        revenue=12500000,
        expenses=7500000,
        profit=5000000,
        gst_liability=450000,
        compliance_score=95.5
    )
    metrics_collector.record_business_metrics(biz_metrics)

    # Update system metrics
    metrics_collector.update_system_metrics(db_connections=8, cache_hit_ratio=0.87)

    # Check for alerts
    alerts = alert_manager.generate_alerts(metrics_collector)
    print(f"Active alerts: {len(alerts)}")

    # Get health status
    health = health_checker.overall_health_check()
    print(f"System health: {health['status']}")

    # Get metrics JSON
    metrics_json = metrics_collector.get_metrics_json()
    print(f"Recorded {len(metrics_json['quantum_jobs'])} quantum jobs")
    print(f"Recorded {len(metrics_json['business_metrics'])} business metrics")

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_monitoring())

    # Print Prometheus metrics
    print("\nPrometheus Metrics:")
    print(get_prometheus_metrics())
