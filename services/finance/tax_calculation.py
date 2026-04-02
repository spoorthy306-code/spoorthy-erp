from typing import Dict, Any


def calculate_tax(amount: float, tax_code: str, country: str) -> Dict[str, Any]:
    rate = 0.18 if country.lower() == 'india' else 0.20
    tax = amount * rate
    return {'amount': amount, 'tax': round(tax,2), 'tax_rate': rate}
