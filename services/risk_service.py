try:
    import fast_math
    FAST_MATH_AVAILABLE = True
except ImportError:
    FAST_MATH_AVAILABLE = False


def calculate_risk_score(amount, transaction_count):
    if FAST_MATH_AVAILABLE:
        return fast_math.calculate_risk_score(amount, transaction_count)
    else:
        base_risk = (amount / 1000) * 2.5
        velocity_multiplier = 1 + (transaction_count * 0.15)
        risk = base_risk * velocity_multiplier
        return min(100, risk)


def get_risk_score(amount, velocity):
    if FAST_MATH_AVAILABLE:
        return fast_math.calculate_risk_score(amount, velocity)
    # Pure Python fallback
    return min(100, (amount / 1000) * 2.5 * (1 + velocity * 0.15))


# REMOVED: The module-level print that crashed on import
# If you want to test, do it in __main__:
if __name__ == '__main__':
    print(calculate_risk_score(5000, 3))