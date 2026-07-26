"""
Tool: check_sensor_status

This is a TOOL FUNCTION - a plain Python function that the agent will be
told about (name, description, inputs) and will decide, on its own, when
to call. Notice this function itself is completely ordinary code - there
is nothing "AI" about it. The intelligence is entirely in the agent
deciding WHEN and WHY to call it, which we build next.

Reuses the exact IsolationForest detection pattern from Project 1 - same
baseline training approach, same risk-level logic - because good tools
are built from logic you already trust, not reinvented from scratch.
"""

import numpy as np
from sklearn.ensemble import IsolationForest

from data.asset_database import ASSET_DATABASE

# Simulated healthy baseline readings used to "train" what normal looks
# like, same idea as Project 1's healthy training window.
_BASELINE_READINGS = [
    {"vibration": v, "bearing_temp": t, "pressure": p}
    for v, t, p in zip(
        np.random.default_rng(42).normal(2.4, 0.15, 200),
        np.random.default_rng(1).normal(60.0, 1.5, 200),
        np.random.default_rng(2).normal(5.0, 0.1, 200),
    )
]

import pandas as pd
_baseline_df = pd.DataFrame(_BASELINE_READINGS)
_detector = IsolationForest(contamination=0.02, random_state=42, n_estimators=200)
_detector.fit(_baseline_df[["vibration", "bearing_temp", "pressure"]])


def score_to_risk_level(score: float) -> str:
    if score > 0.05:
        return "normal"
    elif score > -0.05:
        return "watch"
    elif score > -0.15:
        return "warning"
    return "critical"


def check_sensor_status(asset_id: str) -> dict:
    """
    Looks up an asset's current sensor reading and evaluates it against
    the trained baseline. Returns a self-contained result including the
    asset_id, so the agent can track which result belongs to which asset
    even when checking multiple assets in one conversation.
    """
    if asset_id not in ASSET_DATABASE:
        return {
            "asset_id": asset_id,
            "error": f"No asset found with ID '{asset_id}'. Known assets: {list(ASSET_DATABASE.keys())}",
        }

    reading = ASSET_DATABASE[asset_id]["current_reading"]
    input_df = pd.DataFrame([reading])
    flag = _detector.predict(input_df[["vibration", "bearing_temp", "pressure"]])[0]
    score = _detector.decision_function(input_df[["vibration", "bearing_temp", "pressure"]])[0]
    risk_level = score_to_risk_level(score)

    explanation_parts = []
    if reading["vibration"] > 2.7:
        explanation_parts.append(f"vibration elevated ({reading['vibration']} mm/s, baseline ~2.4)")
    if reading["bearing_temp"] > 62:
        explanation_parts.append(f"bearing temp elevated ({reading['bearing_temp']}°C, baseline ~60°C)")
    if reading["pressure"] < 4.9:
        explanation_parts.append(f"pressure below normal ({reading['pressure']} bar, baseline ~5.0 bar)")
    explanation = "; ".join(explanation_parts) if explanation_parts else (
        "No single sensor is individually out of range, but the combination of readings "
        "is slightly unusual compared to normal operation."
        if risk_level != "normal" else
        "Readings within expected range."
    )

    return {
        "asset_id": asset_id,
        "is_anomaly": bool(flag == -1),
        "anomaly_score": round(float(score), 4),
        "risk_level": risk_level,
        "explanation": explanation,
    }


if __name__ == "__main__":
    for asset_id in ["P-104", "C-7", "P-22", "T-12", "UNKNOWN-99"]:
        print(check_sensor_status(asset_id))
