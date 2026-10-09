import numpy as np

lower_glove = np.array([35, 100, 100], dtype=np.uint8)
upper_glove = np.array([85, 255, 255], dtype=np.uint8)

dwell_time = 0.8

zones_config = {
    "TL": {"text": "Kuning", "color": (0, 0, 255), "bg_name": "Merah"},
    "TR": {"text": "Biru", "color": (0, 255, 255), "bg_name": "Kuning"},
    "BL": {"text": "Merah", "color": (0, 255, 0), "bg_name": "Hijau"},
    "BR": {"text": "Hijau", "color": (255, 0, 0), "bg_name": "Biru"}
}

zone_keys = ["TL", "TR", "BL", "BR"]