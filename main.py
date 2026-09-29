import cv2
import time
from config import zones_config, zone_keys, dwell_time
from tracker import hand_recognition, get_zone_from_point
from game_logic import SimonSaysGame

def main():
    cap = cv2.VideoCapture(0)
    game = SimonSaysGame(zone_keys, zones_config)
    
    dwell_start_time = None
    current_hover_zone = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        mid_x, mid_y = w // 2, h // 2

        centroid, mask = hand_recognition(frame)

        # Gambar garis & teks zona
        cv2.line(frame, (mid_x, 0), (mid_x, h), (255, 255, 255), 2)
        cv2.line(frame, (0, mid_y), (w, mid_y), (255, 255, 255), 2)

        zone_positions = {
            "TL": (mid_x // 4, mid_y // 2),
            "TR": (mid_x + mid_x // 4, mid_y // 2),
            "BL": (mid_x // 4, mid_y + mid_y // 2),
            "BR": (mid_x + mid_x // 4, mid_y + mid_y // 2)
        }

        for zone_key, pos in zone_positions.items():
            cfg = zones_config[zone_key]
            cv2.putText(frame, cfg["text"], pos, cv2.FONT_HERSHEY_SIMPLEX, 1.2, cfg["color"], 3)

        cv2.rectangle(frame, (0, 0), (w, 50), (0, 0, 0), -1)
        cv2.putText(frame, game.get_instruction_text(), (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"Skor: {game.score}", (w - 150, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        if centroid:
            cx, cy = centroid
            cv2.circle(frame, (cx, cy), 15, (0, 255, 0), -1)

            detected_zone = get_zone_from_point(cx, cy, w, h)

            if detected_zone == current_hover_zone:
                if dwell_start_time is not None:
                    elapsed = time.time() - dwell_start_time
                    angle = int((elapsed / dwell_time) * 360)
                    cv2.ellipse(frame, (cx, cy), (30, 30), 0, 0, min(angle, 360), (0, 255, 255), 4)

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
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()