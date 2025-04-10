from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def format_price(value):
    """Format price with commas and 2 decimal places"""
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return value 