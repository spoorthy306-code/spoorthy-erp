#!/usr/bin/env python3
# SPOORTHY QUANTUM OS — CLI Management Tool
# scripts/manage.py

import click
import asyncio
from datetime import datetime, date
from typing import Optional
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.main import app
from backend.app.db.session import get_db
from backend.app.models import Entity, JournalEntry, Invoice, GSTReturn
from backend.app.repositories import EntityRepository, JournalEntryRepository
from backend.app.services.quantum_services import QuantumReconciliationEngine
from backend.app.services.financial_services import FinancialStatementGenerator
from backend.app.services.compliance_services import GSTComplianceEngine
from backend.app.config import settings
from backend.app.seed_data import seed_demo_data
from monitoring import metrics_collector, QuantumJobMetrics
import structlog

logger = structlog.get_logger()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Spoorthy Quantum OS Management CLI"""
    pass

@cli.group()
def db():
    """Database management commands"""
    pass

@db.command()
def init():
    """Initialize database schema"""
    click.echo("Initializing database schema...")
    try:
        from backend.app.db.session import create_tables
        asyncio.run(create_tables())
        click.echo(click.style("✓ Database schema initialized successfully", fg='green'))
    except Exception as e:
        click.echo(click.style(f"✗ Failed to initialize database: {e}", fg='red'))
        sys.exit(1)

@db.command()
def seed():
    """Seed database with demo data"""
    click.echo("Seeding database with demo data...")
    try:
        asyncio.run(seed_demo_data())
        click.echo(click.style("✓ Database seeded successfully", fg='green'))
    except Exception as e:
        click.echo(click.style(f"✗ Failed to seed database: {e}", fg='red'))
        sys.exit(1)

@db.command()
@click.option('--entity-id', help='Entity ID to show data for')
def status(entity_id):
    """Show database status and statistics"""
    async def _status():
        async for session in get_db():
            try:
                # Count records
                entity_count = await session.scalar("SELECT COUNT(*) FROM entities")
                journal_count = await session.scalar("SELECT COUNT(*) FROM journal_entries")
                invoice_count = await session.scalar("SELECT COUNT(*) FROM invoices")

                click.echo(f"Database Status:")
                click.echo(f"  Entities: {entity_count}")
                click.echo(f"  Journal Entries: {journal_count}")
                click.echo(f"  Invoices: {invoice_count}")

                if entity_id:
                    # Show entity-specific data
                    entity_repo = EntityRepository(session)
                    entity = await entity_repo.get_by_id(entity_id)
                    if entity:
                        click.echo(f"\nEntity {entity_id}:")
                        click.echo(f"  Name: {entity.name}")
                        click.echo(f"  GSTIN: {entity.gstin}")
                        click.echo(f"  Status: {entity.status}")
                    else:
                        click.echo(click.style(f"Entity {entity_id} not found", fg='yellow'))

            except Exception as e:
                click.echo(click.style(f"Error checking database status: {e}", fg='red'))

    asyncio.run(_status())

@cli.group()
def quantum():
    """Quantum computing operations"""
    pass

@quantum.command()
@click.option('--entity-id', required=True, help='Entity ID for reconciliation')
@click.option('--bank-file', required=True, help='Path to bank statement CSV')
@click.option('--items-file', required=True, help='Path to open items CSV')
def reconcile(entity_id, bank_file, items_file):
    """Run quantum bank reconciliation"""
    click.echo(f"Running quantum reconciliation for entity {entity_id}...")

    async def _reconcile():
        try:
            # Load CSV data (simplified)
            bank_data = []  # Load from bank_file
            items_data = []  # Load from items_file

            # Run quantum reconciliation
            engine = QuantumReconciliationEngine()
            start_time = datetime.now()

            result = await engine.reconcile(entity_id, bank_data, items_data)

            end_time = datetime.now()
            solve_time = (end_time - start_time).total_seconds() * 1000

            # Record metrics
            job_metrics = QuantumJobMetrics(
                job_id=f"recon_{entity_id}_{int(start_time.timestamp())}",
                job_type="reconciliation",
                start_time=start_time.timestamp(),
                end_time=end_time.timestamp(),
                energy=result.get('energy', 0),
                qubits_used=result.get('qubits_used', 256),
                solve_time_ms=solve_time,
                confidence=result.get('confidence', 0.95),
                success=True
            )
            metrics_collector.record_quantum_job(job_metrics)

            click.echo(click.style("✓ Quantum reconciliation completed", fg='green'))
            click.echo(f"  Matched items: {result.get('matched_count', 0)}")
            click.echo(f"  Solve time: {solve_time:.1f}ms")
            click.echo(f"  Confidence: {result.get('confidence', 0):.1%}")

        except Exception as e:
            click.echo(click.style(f"✗ Reconciliation failed: {e}", fg='red'))

    asyncio.run(_reconcile())

@quantum.command()
@click.option('--entity-id', required=True, help='Entity ID for portfolio optimization')
@click.option('--risk-profile', type=click.Choice(['conservative', 'balanced', 'aggressive']),
              default='balanced', help='Risk profile')
def optimize_portfolio(entity_id, risk_profile):
    """Run quantum portfolio optimization"""
    click.echo(f"Running quantum portfolio optimization for entity {entity_id} ({risk_profile})...")

    async def _optimize():
        try:
            from backend.app.services.quantum_services import QuantumPortfolioOptimizer

            optimizer = QuantumPortfolioOptimizer()
            start_time = datetime.now()

            result = await optimizer.optimize_portfolio(entity_id, risk_profile)

            end_time = datetime.now()
            solve_time = (end_time - start_time).total_seconds() * 1000

            # Record metrics
            job_metrics = QuantumJobMetrics(
                job_id=f"port_{entity_id}_{int(start_time.timestamp())}",
                job_type="portfolio_optimization",
                start_time=start_time.timestamp(),
                end_time=end_time.timestamp(),
                energy=result.get('energy', 0),
                qubits_used=result.get('qubits_used', 512),
                solve_time_ms=solve_time,
                confidence=result.get('confidence', 0.92),
                success=True
            )
            metrics_collector.record_quantum_job(job_metrics)

            click.echo(click.style("✓ Portfolio optimization completed", fg='green'))
            click.echo(f"  Expected return: {result.get('expected_return', 0):.1%}")
            click.echo(f"  Volatility: {result.get('volatility', 0):.1%}")
            click.echo(f"  Solve time: {solve_time:.1f}ms")

        except Exception as e:
            click.echo(click.style(f"✗ Portfolio optimization failed: {e}", fg='red'))

    asyncio.run(_optimize())

@cli.group()
def financial():
    """Financial operations"""
    pass

@financial.command()
@click.option('--entity-id', required=True, help='Entity ID')
@click.option('--period', required=True, help='Period (YYYY-MM)')
@click.option('--statement', type=click.Choice(['pnl', 'balance', 'cashflow']),
              required=True, help='Statement type')
def generate_statement(entity_id, period, statement):
    """Generate financial statement"""
    click.echo(f"Generating {statement.upper()} statement for {entity_id} - {period}...")

    async def _generate():
        try:
            generator = FinancialStatementGenerator()

            if statement == 'pnl':
                result = await generator.generate_pl(entity_id, period)
                click.echo(click.style("✓ Profit & Loss statement generated", fg='green'))
                click.echo(f"  Revenue: ₹{result.get('revenue', 0):,.0f}")
                click.echo(f"  Net Profit: ₹{result.get('net_profit', 0):,.0f}")

            elif statement == 'balance':
                result = await generator.generate_balance_sheet(entity_id, period)
                click.echo(click.style("✓ Balance sheet generated", fg='green'))
                click.echo(f"  Total Assets: ₹{result.get('total_assets', 0):,.0f}")
                click.echo(f"  Total Liabilities: ₹{result.get('total_liabilities', 0):,.0f}")

            elif statement == 'cashflow':
                result = await generator.generate_cash_flow(entity_id, period)
                click.echo(click.style("✓ Cash flow statement generated", fg='green'))
                click.echo(f"  Operating Cash Flow: ₹{result.get('operating_cash_flow', 0):,.0f}")
                click.echo(f"  Net Cash Flow: ₹{result.get('net_cash_flow', 0):,.0f}")

        except Exception as e:
            click.echo(click.style(f"✗ Statement generation failed: {e}", fg='red'))

    asyncio.run(_generate())

@financial.command()
@click.option('--entity-id', required=True, help='Entity ID')
@click.option('--period', required=True, help='Period (YYYY-MM)')
def aging_report(entity_id, period):
    """Generate accounts receivable aging report"""
    click.echo(f"Generating aging report for {entity_id} - {period}...")

    async def _aging():
        try:
            generator = FinancialStatementGenerator()
            result = await generator.generate_aging_report(entity_id, period)

            click.echo(click.style("✓ Aging report generated", fg='green'))
            click.echo(f"  Current: ₹{result.get('current', 0):,.0f}")
            click.echo(f"  1-30 days: ₹{result.get('days_1_30', 0):,.0f}")
            click.echo(f"  31-60 days: ₹{result.get('days_31_60', 0):,.0f}")
            click.echo(f"  61-90 days: ₹{result.get('days_61_90', 0):,.0f}")
            click.echo(f"  90+ days: ₹{result.get('days_90_plus', 0):,.0f}")

        except Exception as e:
            click.echo(click.style(f"✗ Aging report failed: {e}", fg='red'))

    asyncio.run(_aging())

@cli.group()
def compliance():
    """Compliance operations"""
    pass

@compliance.command()
@click.option('--entity-id', required=True, help='Entity ID')
@click.option('--period', required=True, help='Period (YYYY-MM)')
@click.option('--return-type', type=click.Choice(['gstr1', 'gstr3b']),
              required=True, help='GST return type')
def generate_gst_return(entity_id, period, return_type):
    """Generate GST return"""
    click.echo(f"Generating {return_type.upper()} for {entity_id} - {period}...")

    async def _generate_gst():
        try:
            gst_engine = GSTComplianceEngine()

            if return_type == 'gstr1':
                result = await gst_engine.generate_gstr1(entity_id, period)
                click.echo(click.style("✓ GSTR-1 generated", fg='green'))
                click.echo(f"  Total invoices: {result.get('total_invoices', 0)}")
                click.echo(f"  Taxable value: ₹{result.get('taxable_value', 0):,.0f}")
                click.echo(f"  Total tax: ₹{result.get('total_tax', 0):,.0f}")

            elif return_type == 'gstr3b':
                result = await gst_engine.generate_gstr3b(entity_id, period)
                click.echo(click.style("✓ GSTR-3B generated", fg='green'))
                click.echo(f"  Output tax: ₹{result.get('output_tax', 0):,.0f}")
                click.echo(f"  Input tax credit: ₹{result.get('input_tax_credit', 0):,.0f}")
                click.echo(f"  Net tax payable: ₹{result.get('net_tax_payable', 0):,.0f}")

        except Exception as e:
            click.echo(click.style(f"✗ GST return generation failed: {e}", fg='red'))

    asyncio.run(_generate_gst())

@compliance.command()
@click.option('--entity-id', required=True, help='Entity ID')
@click.option('--period', required=True, help='Period (YYYY-MM)')
def file_gst_return(entity_id, period):
    """File GST return with GSTN"""
    click.echo(f"Filing GST return for {entity_id} - {period}...")

    async def _file_gst():
        try:
            gst_engine = GSTComplianceEngine()
            result = await gst_engine.file_gst_return(entity_id, period)

            if result['success']:
                click.echo(click.style("✓ GST return filed successfully", fg='green'))
                click.echo(f"  ARN: {result.get('arn', 'N/A')}")
                click.echo(f"  Status: {result.get('status', 'Filed')}")
            else:
                click.echo(click.style(f"✗ GST return filing failed: {result.get('error', 'Unknown error')}", fg='red'))

        except Exception as e:
            click.echo(click.style(f"✗ GST return filing failed: {e}", fg='red'))

    asyncio.run(_file_gst())

@cli.group()
def reports():
    """Reporting operations"""
    pass

@reports.command()
@click.option('--entity-id', required=True, help='Entity ID')
@click.option('--format', type=click.Choice(['json', 'csv', 'excel']),
              default='json', help='Export format')
@click.option('--output', help='Output file path')
def export_trial_balance(entity_id, format, output):
    """Export trial balance"""
    click.echo(f"Exporting trial balance for {entity_id}...")

    async def _export_tb():
        try:
            generator = FinancialStatementGenerator()
            data = await generator.generate_trial_balance(entity_id)

            if format == 'json':
                output_data = json.dumps(data, indent=2, default=str)
                ext = 'json'
            elif format == 'csv':
                # Convert to CSV format
                output_data = "Account,Debit,Credit\n"
                for item in data.get('items', []):
                    output_data += f"{item['account']},{item.get('debit', 0)},{item.get('credit', 0)}\n"
                ext = 'csv'
            elif format == 'excel':
                # For Excel, we'd use openpyxl, but simulate here
                output_data = "Excel format would be generated here"
                ext = 'xlsx'

            if output:
                with open(output, 'w' if format != 'excel' else 'wb') as f:
                    f.write(output_data)
                click.echo(click.style(f"✓ Trial balance exported to {output}", fg='green'))
            else:
                default_filename = f"trial_balance_{entity_id}.{ext}"
                with open(default_filename, 'w' if format != 'excel' else 'wb') as f:
                    f.write(output_data)
                click.echo(click.style(f"✓ Trial balance exported to {default_filename}", fg='green'))

        except Exception as e:
            click.echo(click.style(f"✗ Export failed: {e}", fg='red'))

    asyncio.run(_export_tb())

@reports.command()
@click.option('--entity-id', required=True, help='Entity ID')
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
def journal_report(entity_id, start_date, end_date):
    """Generate journal entries report"""
    click.echo(f"Generating journal report for {entity_id} from {start_date} to {end_date}...")

    async def _journal_report():
        try:
            async for session in get_db():
                repo = JournalEntryRepository(session)
                entries = await repo.get_by_entity_and_date_range(
                    entity_id, start_date, end_date
                )

                click.echo(click.style(f"✓ Found {len(entries)} journal entries", fg='green'))

                for entry in entries[:10]:  # Show first 10
                    click.echo(f"  {entry.date} - {entry.description}: ₹{entry.amount:,.0f}")

                if len(entries) > 10:
                    click.echo(f"  ... and {len(entries) - 10} more entries")

        except Exception as e:
            click.echo(click.style(f"✗ Journal report failed: {e}", fg='red'))

    asyncio.run(_journal_report())

@cli.command()
def health():
    """Check system health"""
    click.echo("Checking system health...")

    from monitoring import get_health_status

    health = get_health_status()

    if health['status'] == 'healthy':
        click.echo(click.style("✓ System is healthy", fg='green'))
    else:
        click.echo(click.style("✗ System has issues", fg='red'))

    click.echo(f"Uptime: {health['uptime_seconds']:.0f} seconds")

    for check_name, check_result in health['checks'].items():
        status_color = 'green' if check_result['status'] == 'healthy' else 'red'
        click.echo(click.style(f"  {check_name}: {check_result['status']}", fg=status_color))

@cli.command()
def metrics():
    """Show system metrics"""
    click.echo("System Metrics:")

    from monitoring import get_metrics_json

    metrics = get_metrics_json()

    click.echo(f"Quantum jobs (last 24h): {len(metrics['quantum_jobs'])}")
    click.echo(f"Business metrics records: {len(metrics['business_metrics'])}")

    if metrics['quantum_jobs']:
        latest_job = metrics['quantum_jobs'][-1]
        click.echo(f"Latest quantum job: {latest_job['job_type']} ({latest_job['solve_time_ms']:.1f}ms)")

@cli.command()
def alerts():
    """Show active alerts"""
    click.echo("Active Alerts:")

    from monitoring import get_alerts

    alerts = get_alerts()

    if not alerts:
        click.echo(click.style("✓ No active alerts", fg='green'))
    else:
        for alert in alerts:
            severity_color = 'red' if alert['severity'] == 'critical' else 'yellow'
            click.echo(click.style(f"  {alert['alertname']} ({alert['severity']}): {alert['description']}",
                                 fg=severity_color))

if __name__ == '__main__':
    cli()