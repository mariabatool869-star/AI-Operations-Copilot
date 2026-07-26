"""
A small simulated fleet of industrial assets - simplified stand-in for a
real plant's asset database. Each asset has a 'current reading' that the
sensor tool will evaluate. Values are hand-picked to represent a mix of
normal, borderline, and clearly-anomalous readings, so the agent has
genuinely different situations to reason about.
"""

ASSET_DATABASE = {
    "P-104": {
        "type": "pump",
        "current_reading": {"vibration": 2.4, "bearing_temp": 60.0, "pressure": 5.0},
    },
    "C-7": {
        "type": "compressor",
        "current_reading": {"vibration": 2.9, "bearing_temp": 64.5, "pressure": 4.82},
    },
    "P-22": {
        "type": "pump",
        "current_reading": {"vibration": 2.3, "bearing_temp": 59.0, "pressure": 5.05},
    },
    "T-12": {
        "type": "tank",
        "current_reading": {"vibration": 0.0, "bearing_temp": 58.0, "pressure": 5.1},
    },
}
