import random

class SimonSaysGame:
    def __init__(self, zone_keys, zones_config):
        self.zone_keys = zone_keys
        self.zones_config = zones_config
        self.score = 0
        self.target_zone = random.choice(self.zone_keys)
        self.target_type = random.choice(["TEXT", "INK"])

    def generate_new_target(self):
        self.target_zone = random.choice(self.zone_keys)
        self.target_type = random.choice(["TEXT", "INK"])

    def check_answer(self, selected_zone):
        if selected_zone == self.target_zone:
            self.score += 1
            is_correct = True
        else:
            self.score = max(0, self.score - 1)
            is_correct = False
        
        self.generate_new_target()
        return is_correct

    def get_instruction_text(self):
        if self.target_type == "TEXT":
            return f"Sentuh Kata Teks: '{self.zones_config[self.target_zone]['text']}'"
        else:
            return f"Sentuh Tinta Warna: '{self.zones_config[self.target_zone]['bg_name']}'"