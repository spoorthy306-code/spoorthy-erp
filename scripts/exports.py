#!/usr/bin/env python3
# SPOORTHY QUANTUM OS — Export Scripts
# scripts/exports.py

import asyncio
import csv
import json
import sys
import os
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import pandas as pd
from io import StringIO, BytesIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.db.session import get_db
from backend.app.services.financial_services import FinancialStatementGenerator
from backend.app.services.compliance_services import GSTComplianceEngine
from backend.app.repositories import EntityRepository, JournalEntryRepository
import structlog

logger = structlog.get_logger()

class ExportManager:
    """Export manager for various data formats"""

    def __init__(self):
        self.exports_dir = "exports"
        os.makedirs(self.exports_dir, exist_ok=True)

    async def export_trial_balance(self, entity_id: str, period: str,
                                 format: str = 'excel') -> str:
        """Export trial balance"""
        logger.info("exporting_trial_balance", entity_id=entity_id, period=period, format=format)

        generator = FinancialStatementGenerator()
        data = await generator.generate_trial_balance(entity_id, period)

        filename = f"trial_balance_{entity_id}_{period}.{format}"
        filepath = os.path.join(self.exports_dir, filename)

        if format == 'excel':
            await self._export_trial_balance_excel(data, filepath)
        elif format == 'csv':
            await self._export_trial_balance_csv(data, filepath)
        elif format == 'json':
            await self._export_json(data, filepath)

        return filepath

    async def export_profit_loss(self, entity_id: str, period: str,
                               format: str = 'excel') -> str:
        """Export profit & loss statement"""
        logger.info("exporting_profit_loss", entity_id=entity_id, period=period, format=format)

        generator = FinancialStatementGenerator()
        data = await generator.generate_pl(entity_id, period)

        filename = f"profit_loss_{entity_id}_{period}.{format}"
        filepath = os.path.join(self.exports_dir, filename)

        if format == 'excel':
            await self._export_pl_excel(data, filepath)
        elif format == 'csv':
            await self._export_pl_csv(data, filepath)
        elif format == 'json':
            await self._export_json(data, filepath)

        return filepath

    async def export_balance_sheet(self, entity_id: str, period: str,
                                 format: str = 'excel') -> str:
        """Export balance sheet"""
        logger.info("exporting_balance_sheet", entity_id=entity_id, period=period, format=format)

        generator = FinancialStatementGenerator()
        data = await generator.generate_balance_sheet(entity_id, period)

        filename = f"balance_sheet_{entity_id}_{period}.{format}"
        filepath = os.path.join(self.exports_dir, filename)

        if format == 'excel':
            await self._export_balance_sheet_excel(data, filepath)
        elif format == 'csv':
            await self._export_balance_sheet_csv(data, filepath)
        elif format == 'json':
            await self._export_json(data, filepath)

        return filepath

    async def export_gst_return(self, entity_id: str, period: str,
                              return_type: str, format: str = 'excel') -> str:
        """Export GST return"""
        logger.info("exporting_gst_return", entity_id=entity_id, period=period,
                   return_type=return_type, format=format)

        gst_engine = GSTComplianceEngine()

        if return_type == 'gstr1':
            data = await gst_engine.generate_gstr1(entity_id, period)
        elif return_type == 'gstr3b':
            data = await gst_engine.generate_gstr3b(entity_id, period)
        else:
            raise ValueError(f"Unknown return type: {return_type}")

        filename = f"{return_type}_{entity_id}_{period}.{format}"
        filepath = os.path.join(self.exports_dir, filename)

        if format == 'excel':
            await self._export_gst_excel(data, return_type, filepath)
        elif format == 'json':
            await self._export_json(data, filepath)

        return filepath

    async def export_journal_entries(self, entity_id: str, start_date: str,
                                   end_date: str, format: str = 'excel') -> str:
        """Export journal entries"""
        logger.info("exporting_journal_entries", entity_id=entity_id,
                   start_date=start_date, end_date=end_date, format=format)

        async for session in get_db():
            repo = JournalEntryRepository(session)
            entries = await repo.get_by_entity_and_date_range(entity_id, start_date, end_date)

            data = {
                'entries': [
                    {
                        'id': entry.id,
                        'date': entry.date.isoformat(),
                        'description': entry.description,
                        'amount': entry.amount,
                        'type': entry.type,
                        'reference': entry.reference,
                        'period': entry.period
                    }
                    for entry in entries
                ]
            }

            filename = f"journal_entries_{entity_id}_{start_date}_{end_date}.{format}"
            filepath = os.path.join(self.exports_dir, filename)

            if format == 'excel':
                await self._export_journal_excel(data, filepath)
            elif format == 'csv':
                await self._export_journal_csv(data, filepath)
            elif format == 'json':
                await self._export_json(data, filepath)

            return filepath

    async def export_aging_report(self, entity_id: str, period: str,
                                format: str = 'excel') -> str:
        """Export aging report"""
        logger.info("exporting_aging_report", entity_id=entity_id, period=period, format=format)

        generator = FinancialStatementGenerator()
        data = await generator.generate_aging_report(entity_id, period)

        filename = f"aging_report_{entity_id}_{period}.{format}"
        filepath = os.path.join(self.exports_dir, filename)

        if format == 'excel':
            await self._export_aging_excel(data, filepath)
        elif format == 'csv':
            await self._export_aging_csv(data, filepath)
        elif format == 'json':
            await self._export_json(data, filepath)

        return filepath

    async def export_comprehensive_report(self, entity_id: str, period: str) -> str:
        """Export comprehensive financial report (Excel with multiple sheets)"""
        logger.info("exporting_comprehensive_report", entity_id=entity_id, period=period)

        generator = FinancialStatementGenerator()
        gst_engine = GSTComplianceEngine()

        # Generate all data
        trial_balance = await generator.generate_trial_balance(entity_id, period)
        pl_statement = await generator.generate_pl(entity_id, period)
        balance_sheet = await generator.generate_balance_sheet(entity_id, period)
        cash_flow = await generator.generate_cash_flow(entity_id, period)
        aging = await generator.generate_aging_report(entity_id, period)
        gstr3b = await gst_engine.generate_gstr3b(entity_id, period)

        filename = f"comprehensive_report_{entity_id}_{period}.xlsx"
        filepath = os.path.join(self.exports_dir, filename)

        await self._export_comprehensive_excel({
            'trial_balance': trial_balance,
            'profit_loss': pl_statement,
            'balance_sheet': balance_sheet,
            'cash_flow': cash_flow,
            'aging': aging,
            'gstr3b': gstr3b
        }, filepath)

        return filepath

    # Excel export methods
    async def _export_trial_balance_excel(self, data: Dict, filepath: str):
        """Export trial balance to Excel"""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Prepare data
            rows = []
            for item in data.get('items', []):
                rows.append({
                    'Account': item['account'],
                    'Debit': item.get('debit', 0),
                    'Credit': item.get('credit', 0)
                })

            df = pd.DataFrame(rows)
            df.to_excel(writer, sheet_name='Trial Balance', index=False)

            # Add summary
            summary_df = pd.DataFrame([{
                'Total Debit': data.get('total_debit', 0),
                'Total Credit': data.get('total_credit', 0),
                'Difference': abs(data.get('total_debit', 0) - data.get('total_credit', 0))
            }])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

    async def _export_pl_excel(self, data: Dict, filepath: str):
        """Export P&L to Excel"""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            rows = []
            for item in data.get('items', []):
                rows.append({
                    'Account': item['account'],
                    'Amount': item['amount']
                })

            df = pd.DataFrame(rows)
            df.to_excel(writer, sheet_name='Profit & Loss', index=False)

    async def _export_balance_sheet_excel(self, data: Dict, filepath: str):
        """Export balance sheet to Excel"""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Assets
            asset_rows = []
            for item in data.get('assets', []):
                asset_rows.append({
                    'Asset': item['account'],
                    'Amount': item['amount']
                })

            assets_df = pd.DataFrame(asset_rows)
            assets_df.to_excel(writer, sheet_name='Assets', index=False)

            # Liabilities & Equity
            liability_rows = []
            for item in data.get('liabilities', []):
                liability_rows.append({
                    'Liability/Equity': item['account'],
                    'Amount': item['amount']
                })

            liabilities_df = pd.DataFrame(liability_rows)
            liabilities_df.to_excel(writer, sheet_name='Liabilities & Equity', index=False)

    async def _export_gst_excel(self, data: Dict, return_type: str, filepath: str):
        """Export GST return to Excel"""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            if return_type == 'gstr1':
                # B2B invoices
                b2b_rows = []
                for invoice in data.get('b2b', []):
                    b2b_rows.append({
                        'GSTIN': invoice['gstin'],
                        'Invoice No': invoice['invoice_no'],
                        'Date': invoice['date'],
                        'Value': invoice['value'],
                        'Rate': invoice['rate'],
                        'Tax': invoice['tax']
                    })

                b2b_df = pd.DataFrame(b2b_rows)
                b2b_df.to_excel(writer, sheet_name='B2B Invoices', index=False)

                # Summary
                summary_df = pd.DataFrame([{
                    'Total Invoices': data.get('total_invoices', 0),
                    'Total Value': data.get('total_value', 0),
                    'Taxable Value': data.get('taxable_value', 0),
                    'IGST': data.get('igst', 0),
                    'CGST': data.get('cgst', 0),
                    'SGST': data.get('sgst', 0),
                    'Total Tax': data.get('total_tax', 0)
                }])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

            elif return_type == 'gstr3b':
                summary_df = pd.DataFrame([{
                    'Outward Taxable': data.get('outward_taxable', 0),
                    'Outward Exempted': data.get('outward_exempted', 0),
                    'Inward Taxable': data.get('inward_taxable', 0),
                    'Inward Exempted': data.get('inward_exempted', 0),
                    'ITC IGST': data.get('itc_igst', 0),
                    'ITC CGST': data.get('itc_cgst', 0),
                    'ITC SGST': data.get('itc_sgst', 0),
                    'Tax Payable IGST': data.get('tax_payable_igst', 0),
                    'Tax Payable CGST': data.get('tax_payable_cgst', 0),
                    'Tax Payable SGST': data.get('tax_payable_sgst', 0)
                }])
                summary_df.to_excel(writer, sheet_name='GSTR-3B', index=False)

    async def _export_journal_excel(self, data: Dict, filepath: str):
        """Export journal entries to Excel"""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            rows = []
            for entry in data.get('entries', []):
                rows.append({
                    'ID': entry['id'],
                    'Date': entry['date'],
                    'Description': entry['description'],
                    'Amount': entry['amount'],
                    'Type': entry['type'],
                    'Reference': entry['reference'],
                    'Period': entry['period']
                })

            df = pd.DataFrame(rows)
            df.to_excel(writer, sheet_name='Journal Entries', index=False)

    async def _export_aging_excel(self, data: Dict, filepath: str):
        """Export aging report to Excel"""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            rows = []
            for customer in data.get('customers', []):
                rows.append({
                    'Customer': customer['name'],
                    'Current': customer.get('current', 0),
                    '1-30 Days': customer.get('days_1_30', 0),
                    '31-60 Days': customer.get('days_31_60', 0),
                    '61-90 Days': customer.get('days_61_90', 0),
                    '90+ Days': customer.get('days_90_plus', 0),
                    'Total': customer.get('total', 0)
                })

            df = pd.DataFrame(rows)
            df.to_excel(writer, sheet_name='Aging Report', index=False)

    async def _export_comprehensive_excel(self, data: Dict, filepath: str):
        """Export comprehensive report to Excel"""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Trial Balance
            tb_rows = []
            for item in data['trial_balance'].get('items', []):
                tb_rows.append({
                    'Account': item['account'],
                    'Debit': item.get('debit', 0),
                    'Credit': item.get('credit', 0)
                })
            pd.DataFrame(tb_rows).to_excel(writer, sheet_name='Trial Balance', index=False)

            # P&L
            pl_rows = []
            for item in data['profit_loss'].get('items', []):
                pl_rows.append({
                    'Account': item['account'],
                    'Amount': item['amount']
                })
            pd.DataFrame(pl_rows).to_excel(writer, sheet_name='Profit & Loss', index=False)

            # Balance Sheet
            bs_assets = []
            for item in data['balance_sheet'].get('assets', []):
                bs_assets.append({
                    'Asset': item['account'],
                    'Amount': item['amount']
                })
            pd.DataFrame(bs_assets).to_excel(writer, sheet_name='Assets', index=False)

            bs_liabilities = []
            for item in data['balance_sheet'].get('liabilities', []):
                bs_liabilities.append({
                    'Liability/Equity': item['account'],
                    'Amount': item['amount']
                })
            pd.DataFrame(bs_liabilities).to_excel(writer, sheet_name='Liabilities', index=False)

            # Cash Flow
            cf_rows = []
            for item in data['cash_flow'].get('items', []):
                cf_rows.append({
                    'Category': item['category'],
                    'Amount': item['amount']
                })
            pd.DataFrame(cf_rows).to_excel(writer, sheet_name='Cash Flow', index=False)

            # Aging
            aging_rows = []
            for customer in data['aging'].get('customers', []):
                aging_rows.append({
                    'Customer': customer['name'],
                    'Current': customer.get('current', 0),
                    '1-30 Days': customer.get('days_1_30', 0),
                    '31-60 Days': customer.get('days_31_60', 0),
                    '61-90 Days': customer.get('days_61_90', 0),
                    '90+ Days': customer.get('days_90_plus', 0),
                    'Total': customer.get('total', 0)
                })
            pd.DataFrame(aging_rows).to_excel(writer, sheet_name='Aging', index=False)

            # GST
            gst_df = pd.DataFrame([{
                'Outward Taxable': data['gstr3b'].get('outward_taxable', 0),
                'ITC Available': data['gstr3b'].get('itc_available', 0),
                'Tax Payable': data['gstr3b'].get('tax_payable', 0)
            }])
            gst_df.to_excel(writer, sheet_name='GST Summary', index=False)

    # CSV export methods
    async def _export_trial_balance_csv(self, data: Dict, filepath: str):
        """Export trial balance to CSV"""
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Account', 'Debit', 'Credit'])

            for item in data.get('items', []):
                writer.writerow([
                    item['account'],
                    item.get('debit', 0),
                    item.get('credit', 0)
                ])

    async def _export_pl_csv(self, data: Dict, filepath: str):
        """Export P&L to CSV"""
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Account', 'Amount'])

            for item in data.get('items', []):
                writer.writerow([
                    item['account'],
                    item['amount']
                ])

    async def _export_balance_sheet_csv(self, data: Dict, filepath: str):
        """Export balance sheet to CSV"""
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Type', 'Account', 'Amount'])

            for item in data.get('assets', []):
                writer.writerow(['Asset', item['account'], item['amount']])

            for item in data.get('liabilities', []):
                writer.writerow(['Liability/Equity', item['account'], item['amount']])

    async def _export_journal_csv(self, data: Dict, filepath: str):
        """Export journal entries to CSV"""
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Date', 'Description', 'Amount', 'Type', 'Reference', 'Period'])

            for entry in data.get('entries', []):
                writer.writerow([
                    entry['id'],
                    entry['date'],
                    entry['description'],
                    entry['amount'],
                    entry['type'],
                    entry['reference'],
                    entry['period']
                ])

    async def _export_aging_csv(self, data: Dict, filepath: str):
        """Export aging report to CSV"""
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Customer', 'Current', '1-30 Days', '31-60 Days', '61-90 Days', '90+ Days', 'Total'])

            for customer in data.get('customers', []):
                writer.writerow([
                    customer['name'],
                    customer.get('current', 0),
                    customer.get('days_1_30', 0),
                    customer.get('days_31_60', 0),
                    customer.get('days_61_90', 0),
                    customer.get('days_90_plus', 0),
                    customer.get('total', 0)
                ])

    async def _export_json(self, data: Dict, filepath: str):
        """Export data to JSON"""
        with open(filepath, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=2, default=str)

# CLI interface
async def export_trial_balance(entity_id: str, period: str, format: str = 'excel'):
    """CLI function to export trial balance"""
    exporter = ExportManager()
    filepath = await exporter.export_trial_balance(entity_id, period, format)
    print(f"Trial balance exported to: {filepath}")

async def export_profit_loss(entity_id: str, period: str, format: str = 'excel'):
    """CLI function to export profit & loss"""
    exporter = ExportManager()
    filepath = await exporter.export_profit_loss(entity_id, period, format)
    print(f"Profit & Loss exported to: {filepath}")

async def export_balance_sheet(entity_id: str, period: str, format: str = 'excel'):
    """CLI function to export balance sheet"""
    exporter = ExportManager()
    filepath = await exporter.export_balance_sheet(entity_id, period, format)
    print(f"Balance sheet exported to: {filepath}")

async def export_gst_return(entity_id: str, period: str, return_type: str, format: str = 'excel'):
    """CLI function to export GST return"""
    exporter = ExportManager()
    filepath = await exporter.export_gst_return(entity_id, period, return_type, format)
    print(f"GST return exported to: {filepath}")

async def export_journal_entries(entity_id: str, start_date: str, end_date: str, format: str = 'excel'):
    """CLI function to export journal entries"""
    exporter = ExportManager()
    filepath = await exporter.export_journal_entries(entity_id, start_date, end_date, format)
    print(f"Journal entries exported to: {filepath}")

async def export_aging_report(entity_id: str, period: str, format: str = 'excel'):
    """CLI function to export aging report"""
    exporter = ExportManager()
    filepath = await exporter.export_aging_report(entity_id, period, format)
    print(f"Aging report exported to: {filepath}")

async def export_comprehensive(entity_id: str, period: str):
    """CLI function to export comprehensive report"""
    exporter = ExportManager()
    filepath = await exporter.export_comprehensive_report(entity_id, period)
    print(f"Comprehensive report exported to: {filepath}")

if __name__ == "__main__":
    # Example usage
    async def demo_exports():
        """Demo export functionality"""
        try:
            # Export trial balance
            await export_trial_balance("SPOORTHY_TECH", "2024-03", "excel")

            # Export P&L
            await export_profit_loss("SPOORTHY_TECH", "2024-03", "excel")

            # Export GST return
            await export_gst_return("SPOORTHY_TECH", "2024-03", "gstr3b", "excel")

            # Export comprehensive report
            await export_comprehensive("SPOORTHY_TECH", "2024-03")

            print("All exports completed successfully!")

        except Exception as e:
            print(f"Export demo failed: {e}")

    asyncio.run(demo_exports())