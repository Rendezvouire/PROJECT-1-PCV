import cv2
import time
from config import zones_config, zone_keys, dwell_time, HEADER_HEIGHT, MENU_BUTTONS, ROUND_TIME_LIMIT
from tracker import hand_recognition, get_zone_from_point, get_menu_button_from_point
from game_logic import SimonSaysGame
DELAY_TIME = 1.5

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

    sub_text = "Use your mythical GREEN hand to play!"
    sub_scale = 0.55
    sub_thickness = 1
    (sub_w, sub_h), _ = cv2.getTextSize(sub_text, font, sub_scale, sub_thickness)
    sub_x = (w - sub_w) // 2
    cv2.putText(frame, sub_text, (sub_x, 125), font, sub_scale, (200, 200, 200), sub_thickness, cv2.LINE_AA)

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

def draw_game_over(frame):
    h, w, _ = frame.shape
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (10, 10, 10), -1)
    cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)

    font = cv2.FONT_HERSHEY_SIMPLEX

    msg1 = "Game Over!"
    (w1, h1), _ = cv2.getTextSize(msg1, font, 1.5, 3)
    cv2.putText(frame, msg1, ((w - w1) // 2, h // 2 - 20), font, 1.5, (0, 0, 255), 3)

    msg2 = "Try Again!"
    (w2, h2), _ = cv2.getTextSize(msg2, font, 1.1, 2)
    cv2.putText(frame, msg2, ((w - w2) // 2, h // 2 + 30), font, 1.1, (255, 255, 255), 2)

    msg3 = "Hover anywhere with your mythical GREEN hand or press ESC for Menu"
    (w3, h3), _ = cv2.getTextSize(msg3, font, 0.6, 1)
    cv2.putText(frame, msg3, ((w - w3) // 2, h // 2 + 80), font, 0.6, (200, 200, 200), 1)

def draw_you_win(frame):
    h, w, _ = frame.shape
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (10, 30, 10), -1)
    cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)

    font = cv2.FONT_HERSHEY_SIMPLEX

    msg1 = "You Win!"
    (w1, h1), _ = cv2.getTextSize(msg1, font, 1.6, 3)
    cv2.putText(frame, msg1, ((w - w1) // 2, h // 2 - 20), font, 1.6, (0, 255, 0), 3)

    msg2 = "Congratulations!"
    (w2, h2), _ = cv2.getTextSize(msg2, font, 1.1, 2)
    cv2.putText(frame, msg2, ((w - w2) // 2, h // 2 + 30), font, 1.1, (255, 255, 255), 2)

    msg3 = "Hover anywhere with your mythical GREEN hand or press ESC for Menu"
    (w3, h3), _ = cv2.getTextSize(msg3, font, 0.6, 1)
    cv2.putText(frame, msg3, ((w - w3) // 2, h // 2 + 80), font, 0.6, (200, 200, 200), 1)

def main():
    cap = cv2.VideoCapture(0)
    game = SimonSaysGame(zone_keys, zones_config, time_limit=ROUND_TIME_LIMIT)

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

                if detected_button == current_hover_zone and detected_button is not None:
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
                    current_hover_zone = detected_button
                    dwell_start_time = time.time()
            else:
                current_hover_zone = None
                dwell_start_time = None

        elif game_state == "PLAYING":
            if game.is_time_up():
                game_over = game.handle_time_up()
                if game_over:
                    game_state = "GAME_OVER"
                    dwell_start_time = time.time()
                    continue
            
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

            cv2.rectangle(frame, (0, 0), (w, HEADER_HEIGHT), (0, 0, 0), -1)
            cv2.putText(frame, game.get_instruction_text(), (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

            time_remaining = game.get_remaining_time()
            timer_color = (0, 255, 0) if time_remaining <= 2.0 else (0, 255, 255)
            cv2.putText(frame, f"Time: {time_remaining:.1f}s", (w - 280, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, timer_color, 2)
            cv2.putText(frame, f"Score: {game.score}", (w - 130, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

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
                            is_correct, status = game.check_answer(detected_zone)
                            
                            if status == "You Win!":
                                game_state = "YOU_WIN"
                            elif status == "You Lose!":
                                game_state = "GAME_OVER"
                            dwell_start_time = None
                                            
                else:
                    current_hover_zone = detected_zone
                    dwell_start_time = time.time()
            else:
                current_hover_zone = None
                dwell_start_time = None

        elif game_state == "YOU_WIN":
            draw_you_win(frame)

            if centroid:
                cx, cy = centroid
                cv2.circle(frame, (cx, cy), 12, (0, 255, 0), -1)

                if dwell_start_time is not None:
                    elapsed = time.time() - dwell_start_time

                    if elapsed >= DELAY_TIME:
                        hover_time = elapsed - DELAY_TIME
                        angle = int((hover_time / dwell_time) * 360)
                        cv2.ellipse(frame, (cx, cy), (25, 25), 0, 0, min(angle, 360), (0, 255, 255), 3)

                        if hover_time >= dwell_time:
                            game_state = "PLAYING"
                            game.start_new_game()
                            dwell_start_time = None
                else:
                    dwell_start_time = time.time()
            else:
                dwell_start_time = None

        elif game_state == "GAME_OVER":
            draw_game_over(frame)

            if centroid:
                cx, cy = centroid
                cv2.circle(frame, (cx, cy), 12, (0, 0, 255), -1)

                if dwell_start_time is not None:
                    elapsed = time.time() - dwell_start_time

                    if elapsed >= DELAY_TIME:
                        hover_time = elapsed - DELAY_TIME
                        angle = int((hover_time / dwell_time) * 360)
                        cv2.ellipse(frame, (cx, cy), (25, 25), 0, 0, min(angle, 360), (0, 255, 255), 3)

                        if hover_time >= dwell_time:
                            game_state = "PLAYING"
                            game.start_new_game()
                            dwell_start_time = None
                else:
                    dwell_start_time = time.time()
            else:
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