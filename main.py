import cv2
import time
from config import zones_config, zone_keys, dwell_time, HEADER_HEIGHT, MENU_BUTTONS
from tracker import hand_recognition, get_zone_from_point, get_menu_button_from_point
from game_logic import SimonSaysGame

def draw_menu(frame, menu_buttons):
    h, w, _ = frame.shape
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (30, 30, 30), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    title_text = "Hand Color Simon Says"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.1
    font_thickness = 3
    (title_w, title_h), _ = cv2.getTextSize(title_text, font, font_scale, font_thickness)
    title_x = (w - title_w) // 2
    cv2.putText(frame, title_text, (title_x, 100), font, font_scale, (255, 255, 255), font_thickness)

    for button_key, button_info in menu_buttons.items():
        x1, y1, x2, y2 = button_info["box"]
        color = button_info["color"]
        text = button_info["text"]

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)

        button_font_scale = 0.9
        button_font_thickness = 2
        (text_w, text_h), baseline = cv2.getTextSize(text, font, button_font_scale, button_font_thickness)

        button_w = x2 - x1
        button_h = y2 - y1
        text_x = x1 + (button_w - text_w) // 2
        text_y = y1 + (button_h + text_h) // 2
        cv2.putText(frame, text, (text_x, text_y), font, button_font_scale, (255, 255, 255), button_font_thickness)

def main():
    cap = cv2.VideoCapture(0)
    game = SimonSaysGame(zone_keys, zones_config)

    game_state = "MENU"
    
    dwell_start_time = None
    current_hover_zone = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame from camera. Exiting...")
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        centroid, _ = hand_recognition(frame)

        if game_state == "MENU":
            draw_menu(frame, MENU_BUTTONS)
            
            if centroid:
                cx, cy = centroid
                cv2.circle(frame, (cx, cy), 12, (0, 255, 0), -1)

                detected_button = get_menu_button_from_point(cx, cy, MENU_BUTTONS)

                if detected_button == current_target_zone and detected_button is not None:
                    if dwell_start_time is not None:
                        elapsed = time.time() - dwell_start_time
                        angle = int((elapsed / dwell_time) * 360)
                        cv2.ellipse(frame, (cx, cy), (25, 25), 0, 0, min(angle, 360), (0, 255, 255), 3)

                        if elapsed >= dwell_time:
                            if detected_button in ["PLAY", "START"]:
                                game_state = "PLAYING"
                                game.score = 0
                                game.generate_new_target()
                            elif detected_button == "EXIT":
                                break
                            dwell_start_time = None
                else:
                    current_target_zone = detected_button
                    dwell_start_time = time.time()
            else:
                current_target_zone = None
                dwell_start_time = None

        elif game_state == "PLAYING":
            game_height = h - HEADER_HEIGHT
            mid_x = w // 2
            mid_y = HEADER_HEIGHT + (game_height // 2)

            cv2.line(frame, (mid_x, HEADER_HEIGHT), (mid_x, h), (255, 255, 255), 2)
            cv2.line(frame, (0, mid_y), (w, mid_y), (255, 255, 255), 2)

            zone_bounds = {
                "TL": (0, HEADER_HEIGHT, mid_x, mid_y),
                "TR": (mid_x, HEADER_HEIGHT, w, mid_y),
                "BL": (0, mid_y, mid_x, h),
                "BR": (mid_x, mid_y, w, h)
            }

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.2
            font_thickness = 3

            for zone_key, bounds in zone_bounds.items():
                cfg = zones_config[zone_key]
                text = cfg["text"]
                color = cfg["color"]

                x1, y1, x2, y2 = bounds
                zone_w = x2 - x1
                zone_h = y2 - y1

                (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, font_thickness)

                text_x = x1 + (zone_w - text_w) // 2
                text_y = y1 + (zone_h + text_h) // 2
                
                cv2.putText(frame, cfg["text"], (text_x, text_y), font, font_scale, color, font_thickness, cv2.LINE_AA)

            cv2.rectangle(frame, (0, 0), (w, 50), (0, 0, 0), -1)
            cv2.putText(frame, game.get_instruction_text(), (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Score: {game.score}", (w - 150, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            if centroid:
                cx, cy = centroid
                cv2.circle(frame, (cx, cy), 12, (0, 255, 0), -1)

                detected_zone = get_zone_from_point(cx, cy, w, h)

                if detected_zone == current_hover_zone and detected_zone is not None:
                    if dwell_start_time is not None:
                        elapsed = time.time() - dwell_start_time
                        angle = int((elapsed / dwell_time) * 360)
                        cv2.ellipse(frame, (cx, cy), (25, 25), 0, 0, min(angle, 360), (0, 255, 255), 3)

                        if elapsed >= dwell_time:
                            game.check_answer(detected_zone)
                            dwell_start_time = None
                else:
                    current_hover_zone = detected_zone
                    dwell_start_time = time.time()
            else:
                current_hover_zone = None
                dwell_start_time = None

        cv2.imshow("Hand Color Simon Says", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == 27:
            game_state = "MENU"

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()