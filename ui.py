import cv2
import numpy as np
from config import HEADER_HEIGHT

FONT = cv2.FONT_HERSHEY_SIMPLEX
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
YELLOW = (0, 255, 255)
RED = (0, 0, 255)
GREEN = (0, 255, 0)

def draw_text_centered(frame, text, center_x, y, scale, color, thickness, line_type=cv2.LINE_8):
    (text_w, _), _ = cv2.getTextSize(text, FONT, scale, thickness)
    cv2.putText(frame, text, (center_x - text_w // 2, y), FONT, scale, color, thickness, line_type)

def draw_text_in_box(frame, text, box, scale, color, thickness, line_type=cv2.LINE_8):
    x1, y1, x2, y2 = box
    (text_w, text_h), _ = cv2.getTextSize(text, FONT, scale, thickness)
    text_x = x1 + ((x2 - x1) - text_w) // 2
    text_y = y1 + ((y2 - y1) + text_h) // 2
    cv2.putText(frame, text, (text_x, text_y), FONT, scale, color, thickness, line_type)

def draw_dark_overlay(frame, bg_color, alpha):
    h, w, _ = frame.shape
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), bg_color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

def get_zone_bounds(w, h):
    game_height = h - HEADER_HEIGHT
    mid_x = w // 2
    mid_y = HEADER_HEIGHT + (game_height // 2)
    return {
        "TL": (0, HEADER_HEIGHT, mid_x, mid_y),
        "TR": (mid_x, HEADER_HEIGHT, w, mid_y),
        "BL": (0, mid_y, mid_x, h),
        "BR": (mid_x, mid_y, w, h),
    }

def draw_cursor(frame, centroid, color=GREEN):
    cv2.circle(frame, centroid, 12, color, -1)

def draw_dwell_progress(frame, centroid, progress):
    angle = int(min(max(progress, 0.0), 1.0) * 360)
    cv2.ellipse(frame, centroid, (25, 25), 0, 0, angle, YELLOW, 3)

def draw_menu(frame, menu_buttons):
    h, w, _ = frame.shape
    draw_dark_overlay(frame, (30, 30, 30), 0.6)

    draw_text_centered(frame, "Hand Color Simon Says", w // 2, 100, 1.1, WHITE, 3)
    draw_text_centered(frame, "Use your mythical GREEN hand to play!", w // 2, 125,
                       0.55, GREY, 1, cv2.LINE_AA)

    for button_info in menu_buttons.values():
        x1, y1, x2, y2 = button_info["box"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), button_info["color"], -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), WHITE, 2)
        draw_text_in_box(frame, button_info["text"], button_info["box"], 0.9, WHITE, 2)

def draw_heart(frame, center, size, filled):
    cx, cy = center
    r = size // 4
    color = (60, 60, 230) if filled else (90, 90, 90)
    thickness = -1 if filled else 2

    pts = np.array([[cx - 2 * r + 1, cy + r // 2],
                    [cx + 2 * r - 1, cy + r // 2],
                    [cx, cy + 2 * r + r // 2]], np.int32)
    
    if filled:
        cv2.circle(frame, (cx - r, cy), r, color, -1, cv2.LINE_AA)
        cv2.circle(frame, (cx + r, cy), r, color, -1, cv2.LINE_AA)
        cv2.fillPoly(frame, [pts], color, cv2.LINE_AA)
    else:
        cv2.ellipse(frame, (cx - r, cy), (r, r), 0, 150, 360, color, thickness, cv2.LINE_AA)
        cv2.ellipse(frame, (cx + r, cy), (r, r), 0, 180, 390, color, thickness, cv2.LINE_AA)
        cv2.line(frame, (cx - 2 * r + 1, cy + r // 2), (cx, cy + 2 * r + r // 2), color, thickness, cv2.LINE_AA)
        cv2.line(frame, (cx + 2 * r - 1, cy + r // 2), (cx, cy + 2 * r + r // 2), color, thickness, cv2.LINE_AA)

def draw_lives(frame, lives, max_lives, start_x, center_y, size=20, gap=8):
    for i in range(max_lives):
        cx = start_x + i * (size + gap) + size // 2
        draw_heart(frame, (cx, center_y - size // 4), size, filled=(i < lives))

def draw_header(frame, game):
    h, w, _ = frame.shape
    cv2.rectangle(frame, (0, 0), (w, HEADER_HEIGHT), (0, 0, 0), -1)
    cv2.putText(frame, game.get_instruction_text(), (15, 35), FONT, 0.65, WHITE, 2)

    time_remaining = game.get_remaining_time()
    timer_color = RED if time_remaining <= 2.0 else YELLOW
    cv2.putText(frame, f"Time: {time_remaining:.1f}s", (w - 280, 35), FONT, 0.7, timer_color, 2)
    cv2.putText(frame, f"Score: {game.score}", (w - 130, 35), FONT, 0.7, YELLOW, 2)
    draw_lives(frame, game.lives, game.max_lives, w - 375, HEADER_HEIGHT // 2)

def draw_playing(frame, game):
    h, w, _ = frame.shape
    zone_bounds = get_zone_bounds(w, h)

    mid_x = zone_bounds["TL"][2]
    mid_y = zone_bounds["TL"][3]
    cv2.line(frame, (mid_x, HEADER_HEIGHT), (mid_x, h), WHITE, 2)
    cv2.line(frame, (0, mid_y), (w, mid_y), WHITE, 2)

    for zone_key, box in zone_bounds.items():
        cfg = game.layout[zone_key]
        draw_text_in_box(frame, cfg["text"], box, 1.2, cfg["color"], 3, cv2.LINE_AA)

    draw_header(frame, game)

def draw_end_screen(frame, title, title_color, subtitle, bg_color, title_scale=1.5):
    h, w, _ = frame.shape
    draw_dark_overlay(frame, bg_color, 0.8)

    draw_text_centered(frame, title, w // 2, h // 2 - 20, title_scale, title_color, 3)
    draw_text_centered(frame, subtitle, w // 2, h // 2 + 30, 1.1, WHITE, 2)
    draw_text_centered(frame, "Hover anywhere with your mythical GREEN hand or press ESC for Menu",
                       w // 2, h // 2 + 80, 0.6, GREY, 1)

def draw_game_over(frame):
    draw_end_screen(frame, "Game Over!", RED, "Try Again!", (10, 10, 10), 1.5)

def draw_you_win(frame):
    draw_end_screen(frame, "You Win!", GREEN, "Congratulations!", (10, 30, 10), 1.6)