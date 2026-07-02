def classify_risk(score):

    if score >= 85:
        return "Critical"

    elif score >= 60:
        return "High"

    return "Review"