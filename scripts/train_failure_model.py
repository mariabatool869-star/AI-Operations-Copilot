"""
Train the Random Forest failure classifier on the public AI4I 2020 dataset
and save it to data/failure_classifier.joblib.
"""

import os
import urllib.request

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score
from sklearn.model_selection import train_test_split

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
CSV_PATH = os.path.join(DATA_DIR, "ai4i2020.csv")
MODEL_PATH = os.path.join(DATA_DIR, "failure_classifier.joblib")

# Official UCI mirror of AI4I 2020 Predictive Maintenance Dataset
CSV_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv"


def download_dataset() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(CSV_PATH):
        print(f"Dataset already present: {CSV_PATH}")
        return
    print("Downloading AI4I 2020 dataset...")
    urllib.request.urlretrieve(CSV_URL, CSV_PATH)
    print(f"Saved to {CSV_PATH}")


def train() -> None:
    download_dataset()
    df = pd.read_csv(CSV_PATH)

    # One-hot encode product type (L/M/H) to match the tool's expected columns
    type_dummies = pd.get_dummies(df["Type"], prefix="type")
    for col in ("type_H", "type_L", "type_M"):
        if col not in type_dummies.columns:
            type_dummies[col] = 0

    feature_columns = [
        "type_H",
        "type_L",
        "type_M",
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]",
    ]
    X = pd.concat(
        [
            type_dummies[["type_H", "type_L", "type_M"]],
            df[
                [
                    "Air temperature [K]",
                    "Process temperature [K]",
                    "Rotational speed [rpm]",
                    "Torque [Nm]",
                    "Tool wear [min]",
                ]
            ],
        ],
        axis=1,
    )[feature_columns]
    y = df["Machine failure"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_proba = model.predict_proba(X_test)[:, 1]
    pr_auc = average_precision_score(y_test, y_proba)
    print(f"PR-AUC on holdout set: {pr_auc:.3f}")

    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
