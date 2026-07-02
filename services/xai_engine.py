def generate_explanation(case):

    return {
        "id": case["id"],
        "risk_score": case["risk_score"],
        "ip_region": "Durban, ZA (Proxy Detected)",
        "device_os": "Linux / Firefox (Unknown Fingerprint)",
        "velocity_metric": 24,
        "xai_features": [
            {
                "name": "Geolocation Mismatch",
                "weight": 42
            },
            {
                "name": "High Velocity Transfers",
                "weight": 35
            },
            {
                "name": "New Device Login",
                "weight": 23
            }
        ]
    }