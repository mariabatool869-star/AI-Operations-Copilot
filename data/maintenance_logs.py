"""
Small sample set of maintenance log entries the agent can search through.
Deliberately worded differently from how a user might ask about them, to
prove the search is working by MEANING, not exact word matching.
"""

MAINTENANCE_LOGS = [
    {"id": "LOG-01", "asset_id": "C-7", "text": "Steady drip observed near the flange connection during routine walkdown, isolated area, informed shift lead."},
    {"id": "LOG-02", "asset_id": "P-104", "text": "Bearing running warmer than usual, nothing alarming, will keep an eye on it next shift."},
    {"id": "LOG-03", "asset_id": "T-12", "text": "Surface pitting and rust noted on the tank exterior near the base weld, recommend recoating."},
    {"id": "LOG-04", "asset_id": "P-22", "text": "Guard was missing near the rotating shaft, replaced immediately per safety procedure."},
    {"id": "LOG-05", "asset_id": "C-7", "text": "Discharge reading briefly exceeded the normal operating band this morning, returned to normal after restart."},
    {"id": "LOG-06", "asset_id": "P-104", "text": "Routine walkdown completed, all readings nominal, no concerns."},
]
