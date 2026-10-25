import cv2
import time
from config import zones_config, zone_keys, DWELL_TIME, MENU_BUTTONS, ROUND_TIME_LIMIT, DELAY_TIME
from tracker import HandTracker, get_zone_from_point, get_menu_button_from_point
from game_logic import SimonSaysGame
import ui

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera could not be opened. Check your webcam.")
        return

    game = SimonSaysGame(zone_keys, zones_config, time_limit=ROUND_TIME_LIMIT)
    tracker = HandTracker()
    debug_mode = False

    game_state = "MENU"
    dwell_start_time = None
    current_hover_zone = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame from camera. Exiting...")
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        tracker.update_from_trackbars()
        centroid, _ = tracker.detect(frame)
        if debug_mode or tracker.calibrating:
            tracker.show_debug(frame)

        if game_state == "MENU":
            ui.draw_menu(frame, MENU_BUTTONS)

            if centroid:
                cx, cy = centroid
                ui.draw_cursor(frame, centroid)
                detected_button = get_menu_button_from_point(cx, cy, MENU_BUTTONS)

                if detected_button == current_hover_zone and detected_button is not None:
                    if dwell_start_time is not None:
                        elapsed = time.time() - dwell_start_time
                        ui.draw_dwell_progress(frame, centroid, elapsed / DWELL_TIME)

                        if elapsed >= DWELL_TIME:
                            if detected_button == "START":
                                game_state = "PLAYING"
                                game.start_new_game()
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
                is_over, _ = game.handle_time_up()
                if is_over:
                    game_state = "GAME_OVER"
                    dwell_start_time = time.time()
                    continue

            ui.draw_playing(frame, game, zones_config)

            if centroid:
                cx, cy = centroid
                ui.draw_cursor(frame, centroid)
                detected_zone = get_zone_from_point(cx, cy, w, h)

                if detected_zone == current_hover_zone and detected_zone is not None:
                    if dwell_start_time is not None:
                        elapsed = time.time() - dwell_start_time
                        ui.draw_dwell_progress(frame, centroid, elapsed / DWELL_TIME)

                        if elapsed >= DWELL_TIME:
                            _, status = game.check_answer(detected_zone)
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

        elif game_state in ("YOU_WIN", "GAME_OVER"):
            if game_state == "YOU_WIN":
                ui.draw_you_win(frame)
                cursor_color = (0, 255, 0)
            else:
                ui.draw_game_over(frame)
                cursor_color = (0, 0, 255)

            if centroid:
                ui.draw_cursor(frame, centroid, cursor_color)

                if dwell_start_time is not None:
                    elapsed = time.time() - dwell_start_time

                    if elapsed >= DELAY_TIME:
                        hover_time = elapsed - DELAY_TIME
                        ui.draw_dwell_progress(frame, centroid, hover_time / DWELL_TIME)

                        if hover_time >= DWELL_TIME:
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
            current_hover_zone = None
            dwell_start_time = None
        elif key == ord('d'):
            debug_mode = not debug_mode
            if not debug_mode and not tracker.calibrating:
                tracker.hide_debug()
        elif key == ord('c'):
            tracker.toggle_calibration()
            if not tracker.calibrating and not debug_mode:
                tracker.hide_debug()
        elif key == ord('s'):
            tracker.save_calibration()

    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()