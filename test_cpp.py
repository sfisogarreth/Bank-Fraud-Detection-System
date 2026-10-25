import fast_math

# Test single transaction risk scoring
score = fast_math.calculate_risk_score(5000.0, 3)
print(f"✅ Single C++ Risk Score Calculation Result: {score}")

# Test batch multi-transaction array processing
batch_scores = fast_math.batch_calculate_risk([1500.0, 25000.0, 3200.0], [1, 8, 2])
print(f"✅ Batch C++ Risk Scores Result: {batch_scores}")

total_sum = fast_math.batch_process([100.0, 250.0, 50.0])
print(f"✅ Batch Amount Sum Result: {total_sum}")