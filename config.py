import numpy as np

lower_glove = np.array([35, 100, 100], dtype=np.uint8)
upper_glove = np.array([85, 255, 255], dtype=np.uint8)

dwell_time = 0.8
ROUND_TIME_LIMIT = 5.0
HEADER_HEIGHT = 50

zones_config = {
    "TL": {"text": "Yellow", "color": (0, 0, 255), "bg_name": "Red"},
    "TR": {"text": "Blue", "color": (0, 255, 255), "bg_name": "Yellow"},
    "BL": {"text": "Red", "color": (0, 255, 0), "bg_name": "Green"},
    "BR": {"text": "Green", "color": (255, 0, 0), "bg_name": "Blue"}
}

zone_keys = ["TL", "TR", "BL", "BR"]

MENU_BUTTONS = {
    "START": {"text": "Start Game", "color": (0, 180, 0), "box": (200, 180, 440, 250)},
    "EXIT": {"text": "Exit", "color": (0, 0, 180), "box": (200, 280, 440, 350)}
}