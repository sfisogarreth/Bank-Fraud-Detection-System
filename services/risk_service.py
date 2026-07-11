import fast_math
print(fast_math.calculate_risk_score(5000, 3))  # Should output a number
try:
    import fast_math
    CPP_AVAILABLE = True
except ImportError:
    CPP_AVAILABLE = False
    print("⚠️ fast_math C++ module not compiled. Run: python setup.py build_ext --inplace")

def get_risk_score(amount, velocity):
    if CPP_AVAILABLE:
        return fast_math.calculate_risk_score(amount, velocity)
    # Pure Python fallback
    return min(100, (amount / 1000) * 2.5 * (1 + velocity * 0.15))