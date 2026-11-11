"""CAGR calculation helpers."""
from .ratios import calculate_cagr

def cagr_for_window(values, years):
    if len(values) < 2:
        return None, "INSUFFICIENT_DATA"
    return calculate_cagr(values[0], values[-1], years)
