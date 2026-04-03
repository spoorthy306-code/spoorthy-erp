# SPOORTHY QUANTUM OS — Financial Services
# Financial statement generation and analysis

import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession


class FinancialStatementGenerator:
    """Generate financial statements"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_trial_balance(
        self, entity_id: str, period: str
    ) -> Dict[str, Any]:
        """Generate trial balance for entity and period"""
        # In real implementation, would query database
        # For demo, return mock data
        return {
            "entity_id": entity_id,
            "period": period,
            "accounts": [
                {
                    "code": "1001",
                    "name": "Cash",
                    "debit": 500000,
                    "credit": 0,
                    "balance": 500000,
                },
                {
                    "code": "1101",
                    "name": "Accounts Receivable",
                    "debit": 200000,
                    "credit": 0,
                    "balance": 200000,
                },
                {
                    "code": "2001",
                    "name": "Accounts Payable",
                    "debit": 0,
                    "credit": 150000,
                    "balance": -150000,
                },
                {
                    "code": "4001",
                    "name": "Revenue",
                    "debit": 0,
                    "credit": 1000000,
                    "balance": -1000000,
                },
                {
                    "code": "5001",
                    "name": "Salaries",
                    "debit": 300000,
                    "credit": 0,
                    "balance": 300000,
                },
            ],
            "total_debit": 1000000,
            "total_credit": 1150000,
            "difference": 150000,
        }

    async def generate_pl(self, entity_id: str, period: str) -> Dict[str, Any]:
        """Generate profit & loss statement"""
        return {
            "entity_id": entity_id,
            "period": period,
            "revenue": {
                "software_services": 800000,
                "consulting": 200000,
                "total_revenue": 1000000,
            },
            "expenses": {
                "salaries": 300000,
                "rent": 50000,
                "utilities": 25000,
                "depreciation": 30000,
                "professional_fees": 50000,
                "total_expenses": 455000,
            },
            "profit_before_tax": 545000,
            "tax": 109000,
            "net_profit": 436000,
        }

    async def generate_balance_sheet(
        self, entity_id: str, as_of_date: date
    ) -> Dict[str, Any]:
        """Generate balance sheet"""
        return {
            "entity_id": entity_id,
            "as_of_date": as_of_date.isoformat(),
            "assets": {
                "current_assets": {
                    "cash": 500000,
                    "accounts_receivable": 200000,
                    "inventory": 100000,
                    "total_current_assets": 800000,
                },
                "fixed_assets": {
                    "computers": 300000,
                    "furniture": 100000,
                    "accumulated_depreciation": -60000,
                    "net_fixed_assets": 340000,
                },
                "total_assets": 1140000,
            },
            "liabilities": {
                "current_liabilities": {
                    "accounts_payable": 150000,
                    "tax_payable": 50000,
                    "total_current_liabilities": 200000,
                },
                "long_term_liabilities": {
                    "loans": 400000,
                    "total_long_term_liabilities": 400000,
                },
                "total_liabilities": 600000,
            },
            "equity": {
                "share_capital": 500000,
                "retained_earnings": 40000,
                "total_equity": 540000,
            },
            "total_liabilities_equity": 1140000,
        }

    async def generate_cash_flow(
        self, entity_id: str, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Generate cash flow statement"""
        return {
            "entity_id": entity_id,
            "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
            "operating_activities": {
                "net_profit": 436000,
                "depreciation": 30000,
                "changes_in_working_capital": -50000,
                "net_cash_operating": 416000,
            },
            "investing_activities": {
                "fixed_asset_purchases": -100000,
                "net_cash_investing": -100000,
            },
            "financing_activities": {
                "loan_proceeds": 200000,
                "dividends_paid": -50000,
                "net_cash_financing": 150000,
            },
            "net_cash_flow": 466000,
            "opening_cash": 34000,
            "closing_cash": 500000,
        }

    async def generate_aging_report(
        self, entity_id: str, as_of_date: date
    ) -> Dict[str, Any]:
        """Generate receivables aging report"""
        return {
            "entity_id": entity_id,
            "as_of_date": as_of_date.isoformat(),
            "aging_buckets": {
                "current": 150000,
                "1_30_days": 30000,
                "31_60_days": 15000,
                "61_90_days": 5000,
                "over_90_days": 0,
            },
            "total_outstanding": 200000,
            "total_overdue": 50000,
        }


class BudgetActualEngine:
    """Budget vs actual analysis"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def variance_report(self, entity_id: str, period: str) -> Dict[str, Any]:
        """Generate budget vs actual variance report"""
        return {
            "entity_id": entity_id,
            "period": period,
            "variances": [
                {
                    "account": "Salaries",
                    "budget": 350000,
                    "actual": 300000,
                    "variance": 50000,
                    "variance_pct": 14.29,
                    "favorable": True,
                },
                {
                    "account": "Revenue",
                    "budget": 900000,
                    "actual": 1000000,
                    "variance": 100000,
                    "variance_pct": 11.11,
                    "favorable": True,
                },
                {
                    "account": "Rent",
                    "budget": 45000,
                    "actual": 50000,
                    "variance": -5000,
                    "variance_pct": -11.11,
                    "favorable": False,
                },
            ],
            "summary": {
                "total_budget": 1295000,
                "total_actual": 1350000,
                "total_variance": 55000,
                "total_variance_pct": 4.25,
            },
        }


class CashFlowForecaster:
    """Cash flow forecasting"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def forecast_cash_flow(
        self, entity_id: str, periods: int = 6
    ) -> Dict[str, Any]:
        """Forecast cash flow for future periods"""
        forecast = []
        current_cash = 500000

        for i in range(periods):
            period_date = date.today() + timedelta(days=30 * (i + 1))
            inflows = 200000 + random.randint(-20000, 20000)
            outflows = 150000 + random.randint(-15000, 15000)
            net_flow = inflows - outflows
            current_cash += net_flow

            forecast.append(
                {
                    "period": period_date.strftime("%Y-%m"),
                    "opening_cash": current_cash - net_flow,
                    "inflows": inflows,
                    "outflows": outflows,
                    "net_flow": net_flow,
                    "closing_cash": current_cash,
                }
            )

        return {
            "entity_id": entity_id,
            "forecast_periods": periods,
            "forecast": forecast,
        }
