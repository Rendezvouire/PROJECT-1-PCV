import random
import time

class SimonSaysGame:
    def __init__(self, zone_keys, zones_config, time_limit=5.0):
        self.zone_keys = zone_keys
        self.zones_config = zones_config
        self.time_limit = time_limit
        self.win_score = 10
        
        self.score = 0
        self.target_zone = None
        self.target_type = None
        self.round_start_time = None
    
    def start_new_game(self):
        self.score = 0
        self.generate_new_target()

    def generate_new_target(self):
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

    def check_answer(self, selected_zone):
        if selected_zone == self.target_zone:
            self.score += 1
            if self.score >= self.win_score:
                return True, "You Win!"
            
            self.generate_new_target()
            return True, "Replay"
        else:
            self.score -= 3
            if self.score <= 0:
                self.score = 0
                return False, "You Lose!"
            else: 
                self.generate_new_target()
                return False, "Try Again"
        
    def handle_time_up(self):
        self.score -= 5
        if self.score <= 0:
            self.score = 0
            return True, "You Lose!"
        else:
            self.generate_new_target()
            return False, "Try Again"

    def get_instruction_text(self):
        if self.target_type == "TEXT":
            return f"Touch the text: '{self.zones_config[self.target_zone]['text']}'"
        else:
            return f"Touch the color: '{self.zones_config[self.target_zone]['bg_name']}'"