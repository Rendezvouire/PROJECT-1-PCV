import cv2
import numpy as np
from config import lower_skin, upper_skin 

def hand_recognition(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) > 2000:
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                return (cx, cy), mask
    return None, mask

def get_zone_from_point(x, y, width, height):
    mid_x, mid_y = width // 2, height // 2
    if x < mid_x and y < mid_y:
        return "TL"
    elif x >= mid_x and y < mid_y:
        return "TR"
    elif x < mid_x and y >= mid_y:
        return "BL"
    else:
        return "BR"