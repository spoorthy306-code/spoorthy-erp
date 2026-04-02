from typing import Dict, Any

def apply_discount(amount: float, volume: int=1, coupon: str=None) -> Dict[str, Any]:
    discount = 0.0
    if volume > 50:
        discount += amount * 0.1
    if coupon == 'SAVE20':
        discount += amount * 0.2
    final = amount - discount
    return {'amount': amount, 'discount': round(discount,2), 'net': round(final,2)}
