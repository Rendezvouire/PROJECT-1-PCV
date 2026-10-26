import random
import time

class SimonSaysGame:
    def __init__(self, zone_keys, zones_config, time_limit=5.0, max_lives=3):
        self.zone_keys = zone_keys
        self.zones_config = zones_config
        self.time_limit = time_limit
        self.win_score = 10
        self.max_lives = max_lives

        self.palette = {cfg["ink_name"]: cfg["color"] for cfg in zones_config.values()}
        self.layout = dict(zones_config)
        
        self.score = 0
        self.lives = max_lives
        self.target_zone = None
        self.target_type = None
        self.round_start_time = None
    
    def start_new_game(self):
        self.score = 0
        self.lives = self.max_lives
        self.generate_new_target()

    def shuffle_layout(self):
        ink_names = list(self.palette.keys())
        random.shuffle(ink_names)

        text_names = ink_names[:]
        while any(t == i for t, i in zip(text_names, ink_names)):
            random.shuffle(text_names)

        self.layout = {
            zone: {"text": text, "color": self.palette[ink], "ink_name": ink}
            for zone, text, ink in zip(self.zone_keys, text_names, ink_names)
        }

    def generate_new_target(self):
        self.shuffle_layout()
        self.target_zone = random.choice(self.zone_keys)
        self.target_type = random.choice(["TEXT", "INK"])
        self.round_start_time = time.time()

    def get_remaining_time(self):
        if self.round_start_time is None:
            return self.time_limit
        elapsed_time = time.time() - self.round_start_time
        return max(0.0, self.time_limit - elapsed_time)

    def is_time_up(self):
        return self.get_remaining_time() <= 0

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            return True
        self.generate_new_target()
        return False

    def check_answer(self, selected_zone):
        if selected_zone == self.target_zone:
            self.score += 1
            if self.score >= self.win_score:
                return True, "You Win!"
            self.generate_new_target()
            return True, "Replay"
        
        if self.lose_life():
            return False, "You Lose!"
        return False, "Try Again"
        
    def handle_time_up(self):
        if self.lose_life():
            return True, "You Lose!"
        return False, "Try Again"

    def get_instruction_text(self):
        if self.target_type == "TEXT":
            return f"Touch the text: '{self.layout[self.target_zone]['text']}'"
        else:
            return f"Touch the color: '{self.layout[self.target_zone]['ink_name']}'"