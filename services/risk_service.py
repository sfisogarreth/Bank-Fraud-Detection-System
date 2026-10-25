import logging

logger = logging.getLogger("mazi_logger")

# Attempt binding to native C++ compiled extension module
try:
    import fast_math
    FAST_MATH_AVAILABLE = True
    logger.info("Native C++ 'fast_math' extension successfully loaded and verified.")
except ImportError as err:
    FAST_MATH_AVAILABLE = False
    logger.warning(f"Native C++ 'fast_math' extension unavailable ({err}); falling back to Python math engine.")


def calculate_risk_score(amount: float, transaction_count: int) -> float:
    """
    Calculates velocity and amount risk using native C++ code if available, 
    otherwise falls back to optimized Python arithmetic.
    """
    amt = float(amount)
    count = int(transaction_count)

    if FAST_MATH_AVAILABLE:
        try:
            return float(fast_math.calculate_risk_score(amt, count))
        except Exception as exc:
            logger.error(f"Runtime exception in C++ fast_math execution: {exc}")
    
    # Pure Python High-Performance Fallback Calculation
    if amt < 0.0:
        return 0.0
    base_risk = (amt / 1000.0) * 2.5
    velocity_multiplier = 1.0 + (float(count) * 0.15)
    risk = base_risk * velocity_multiplier
    return round(min(100.0, max(0.0, risk)), 2)


def get_risk_score(amount: float, velocity: int) -> float:
    """Convenience alias for calculate_risk_score."""
    return calculate_risk_score(amount, velocity)


if __name__ == '__main__':
    test_score = calculate_risk_score(15000.0, 4)
    print(f"Risk Service Diagnostic Result: {test_score}")