import cv2
import numpy as np
from config import lower_glove, upper_glove 

def hand_recognition(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_glove, upper_glove)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) > 800:
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                return (cx, cy), mask
    return None, mask

def get_zone_from_point(x, y, width, height):
    HEADER_HEIGHT = 50
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