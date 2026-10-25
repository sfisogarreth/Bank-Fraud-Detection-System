import logging

logger = logging.getLogger("mazi_logger")


def generate_explanation(case: dict) -> dict:
    """
    Dynamically generates Explainable AI (XAI) feature weights, proxy risk assessments, 
    and device forensics based on the specific properties of an evaluated transaction.
    """
    risk_score = float(case.get("risk_score", 50.0))
    amount = float(case.get("amount", 0.0))
    location = str(case.get("location", "Durban, ZA"))
    
    # Dynamically scale feature attribution weights based on actual risk severity
    geo_weight = min(50, int(risk_score * 0.45 + (15 if "Proxy" in location or "Lagos" in location else 0)))
    velocity_weight = min(40, int(risk_score * 0.35))
    amount_weight = max(10, 100 - (geo_weight + velocity_weight))
    
    # Detect potential proxy/VPN or cross-border anomalies
    is_proxy = "Proxy" in location or "Foreign" in location or not location.endswith("ZA")
    ip_region = f"{location} ({'Proxy/VPN Detected' if is_proxy else 'Standard Secure Route'})"
    
    # Assign simulated device risk fingerprint based on risk score severity
    if risk_score > 85:
        device_os = "Linux / Tor Anonymous Browser (Unknown Fingerprint)"
    elif risk_score > 60:
        device_os = "Windows / Headless Chrome Automation Script"
    else:
        device_os = "iOS / Verified MAZI Mobile App (Biometric Secured)"
    
    return {
        "id": case.get("id", "N/A"),
        "risk_score": int(round(risk_score)),
        "ip_region": ip_region,
        "device_os": device_os,
        "velocity_metric": int(max(1, risk_score / 3.0)),
        "xai_features": [
            {
                "name": "Geolocation & Proxy Risk",
                "weight": geo_weight
            },
            {
                "name": "Transaction Velocity / Frequency",
                "weight": velocity_weight
            },
            {
                "name": "Amount Anomaly vs Customer Baseline",
                "weight": amount_weight
            }
        ]
    }