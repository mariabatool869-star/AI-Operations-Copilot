"""
Tool: predict_failure_risk

WHAT THIS TOOL DOES, IN PLAIN TERMS:
It loads the real machine-learning model you already trained on the real
AI4I 2020 dataset (10,000 real machine records), and uses it to answer:
"given these operating conditions - temperature, speed, torque, tool wear
- how likely is a failure?"

WHY THIS IS DIFFERENT FROM THE SENSOR TOOL:
The sensor tool (check_sensor_status) asks "does this reading LOOK unusual
compared to normal?" - it has no idea what a real failure looks like, it
only knows what "normal" looks like.
This tool asks a different, more specific question: "based on real,
labeled failure examples we trained on, what is the PROBABILITY of an
actual failure?" - it directly learned from real failure/no-failure
outcomes, not just "is this different from usual."
Having both gives the agent two genuinely different lenses to reason
with, which is exactly what a senior engineer does: cross-check one
signal against another before concluding something is wrong.
"""

import joblib
import pandas as pd
import os

_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "failure_classifier.joblib")
_model = joblib.load(_MODEL_PATH)

# The exact feature columns the model was trained on (must match training exactly)
_FEATURE_COLUMNS = [
    "type_H", "type_L", "type_M",
    "Air temperature [K]", "Process temperature [K]",
    "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]",
]


def predict_failure_risk(
    product_type: str,
    air_temp_k: float,
    process_temp_k: float,
    rotational_speed_rpm: float,
    torque_nm: float,
    tool_wear_min: float,
) -> dict:
    """
    product_type must be one of "L", "M", "H" (low/medium/high quality
    variant, matching the real dataset's categories).
    """
    if product_type not in ("L", "M", "H"):
        return {"error": f"product_type must be L, M, or H - got '{product_type}'"}

    row = {col: 0 for col in _FEATURE_COLUMNS}
    row[f"type_{product_type}"] = 1
    row["Air temperature [K]"] = air_temp_k
    row["Process temperature [K]"] = process_temp_k
    row["Rotational speed [rpm]"] = rotational_speed_rpm
    row["Torque [Nm]"] = torque_nm
    row["Tool wear [min]"] = tool_wear_min

    input_df = pd.DataFrame([row])[_FEATURE_COLUMNS]
    failure_probability = float(_model.predict_proba(input_df)[0][1])

    if failure_probability >= 0.5:
        risk_level = "high"
    elif failure_probability >= 0.2:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "failure_probability": round(failure_probability, 4),
        "risk_level": risk_level,
        "model_source": "Random Forest trained on AI4I 2020 real published dataset (PR-AUC 0.776)",
    }


if __name__ == "__main__":
    print("Normal operating conditions:")
    print(predict_failure_risk("M", 298.1, 308.6, 1551, 42.8, 0))

    print("\nHigh tool wear + high torque (known real risk pattern):")
    print(predict_failure_risk("L", 300.5, 311.0, 1350, 65.0, 220))
