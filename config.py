import numpy as np

LOWER_GLOVE = np.array([35, 100, 100], dtype=np.uint8)
UPPER_GLOVE = np.array([85, 255, 255], dtype=np.uint8)

DWELL_TIME = 0.8
ROUND_TIME_LIMIT = 5.0
HEADER_HEIGHT = 50
DELAY_TIME = 1.5

zones_config = {
    "TL": {"text": "Yellow", "color": (0, 0, 255), "ink_name": "Red"},
    "TR": {"text": "Blue", "color": (0, 255, 255), "ink_name": "Yellow"},
    "BL": {"text": "Red", "color": (0, 255, 0), "ink_name": "Green"},
    "BR": {"text": "Green", "color": (255, 0, 0), "ink_name": "Blue"}
}

zone_keys = ["TL", "TR", "BL", "BR"]

MENU_BUTTONS = {
    "START": {"text": "Start Game", "color": (0, 180, 0), "box": (200, 180, 440, 250)},
    "EXIT": {"text": "Exit", "color": (0, 0, 180), "box": (200, 280, 440, 350)}
}