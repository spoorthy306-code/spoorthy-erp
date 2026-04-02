from typing import Dict, Any


def calculate_payroll(gross: float, deductions: float, tax_pct: float = 0.1) -> Dict[str, Any]:
    tax = gross * tax_pct
    net = gross - deductions - tax
    return {'gross': gross, 'deductions': deductions, 'tax': round(tax,2), 'net': round(net,2)}
