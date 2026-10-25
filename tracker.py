import json
import os

import cv2
import numpy as np
from config import (LOWER_GLOVE, UPPER_GLOVE, HEADER_HEIGHT, CALIBRATION_FILE, BLUR_KERNEL_SIZE, 
                    MORPH_KERNEL_SIZE, MIN_CONTOUR_AREA, SMOOTHING_ALPHA)

CALIB_WINDOW = "HSV Calibration"
DEBUG_WINDOW = "Image Processing Pipeline"
TRACKBARS = ["H min", "S min", "V min", "H max", "S max", "V max"]

class HandTracker:
    def __init__(self):
        self.lower = LOWER_GLOVE.copy()
        self.upper = UPPER_GLOVE.copy()
        self.kernel = np.ones((MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE), np.uint8)
        
        self.smoothed = None
        self.raw_mask = None
        self.clean_mask = None
        self.contour = None
        self.calibrating = False

        self.load_calibration()
        
    def detect(self, frame):
        blurred = cv2.GaussianBlur(frame, (BLUR_KERNEL_SIZE, BLUR_KERNEL_SIZE), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        
        self.raw_mask = cv2.inRange(hsv, self.lower, self.upper)
        mask = cv2.morphologyEx(self.raw_mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)
        self.clean_mask = mask

        self.contour = None
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > MIN_CONTOUR_AREA:
                M = cv2.moments(largest)
                if M["m00"] != 0:
                    self.contour = largest
                    raw = np.array([M["m10"] / M["m00"], M["m01"] / M["m00"]])
                    return self._smooth(raw), mask
                
        self.smoothed = None
        return None, mask
    
    def _smooth(self, point):
        if self.smoothed is None:
            self.smoothed = point
        else:
            self.smoothed = SMOOTHING_ALPHA * point + (1 - SMOOTHING_ALPHA) * self.smoothed
        return int(self.smoothed[0]), int(self.smoothed[1])

    def show_debug(self, frame):
        if self.raw_mask is None:
            return
        result = frame.copy()
        if self.contour is not None:
            cv2.drawContours(result, [self.contour], -1, (0, 255, 0), 2)
            x, y, w, h = cv2.boundingRect(self.contour)
            cv2.rectangle(result, (x, y), (x + w, y + h), (255, 0, 0), 2)
            area = int(cv2.contourArea(self.contour))
            cv2.putText(result, f"Area: {area}", (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        if self.smoothed is not None:
            cv2.circle(result, (int(self.smoothed[0]), int(self.smoothed[1])), 6, (0, 0, 255), -1)

        panels = [
            (cv2.cvtColor(self.raw_mask, cv2.COLOR_GRAY2BGR), "Threshold HSV"),
            (cv2.cvtColor(self.clean_mask, cv2.COLOR_GRAY2BGR), "Opening + Closing"),
            (result, "Contour + Centroid"),
        ]
        small = []
        for img, label in panels:
            img = cv2.resize(img, (320, 240))
            cv2.rectangle(img, (0, 0), (320, 24), (0, 0, 0), -1)
            cv2.putText(img, label, (6, 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            small.append(img)
        cv2.imshow(DEBUG_WINDOW, np.hstack(small))

    def hide_debug(self):
        _destroy_window(DEBUG_WINDOW)

    def toggle_calibration(self):
        self.calibrating = not self.calibrating
        if self.calibrating:
            cv2.namedWindow(CALIB_WINDOW)
            values = list(self.lower) + list(self.upper)
            for name, val in zip(TRACKBARS, values):
                max_val = 179 if name.startswith("H") else 255
                cv2.createTrackbar(name, CALIB_WINDOW, val, max_val, lambda x: None)
        else:
            _destroy_window(CALIB_WINDOW)
            self.save_calibration()

    def update_from_trackbars(self):
        if not self.calibrating:
            return
        vals = [cv2.getTrackbarPos(name, CALIB_WINDOW) for name in TRACKBARS]
        self.lower = np.array(vals[:3], dtype=np.uint8)
        self.upper = np.array(vals[3:], dtype=np.uint8)

    def save_calibration(self):
        data = {
            "lower": self.lower.tolist(),
            "upper": self.upper.tolist()
        }
        with open(CALIBRATION_FILE, "w") as f:
            json.dump(data, f)
        print(f"HSV Calibration is saved: {data}")

    def load_calibration(self):
        if os.path.exists(CALIBRATION_FILE):
            try:
                with open(CALIBRATION_FILE) as f:
                    data = json.load(f)
                self.lower = np.array(data["lower"], dtype=np.uint8)
                self.upper = np.array(data["upper"], dtype=np.uint8)
                print(f"HSV Calibration is loaded: {data}")
            except (ValueError, KeyError):
                print("Error loading calibration file.")
        else:
            print("No calibration file found.")
def _destroy_window(name):
    try:
        cv2.destroyWindow(name)
    except cv2.error:
        pass

def get_zone_from_point(x, y, width, height):
    game_height = height - HEADER_HEIGHT

    mid_x = width // 2
    mid_y = HEADER_HEIGHT + (game_height // 2)

    if y < HEADER_HEIGHT:
        return None

    if x < mid_x and y < mid_y:
        return "TL"
    elif x >= mid_x and y < mid_y:
        return "TR"
    elif x < mid_x and y >= mid_y:
        return "BL"
    else:
        return "BR"

def get_menu_button_from_point(x, y, menu_buttons):
    for button_key, button_info in menu_buttons.items():
        x1, y1, x2, y2 = button_info["box"]
        if x1 <= x <= x2 and y1 <= y <= y2:
            return button_key
    return None