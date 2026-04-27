#!/usr/bin/env python3
"""
DaRkb0x Payload -- Digimon V-Pet
---------------------------------------
A Python-based Digimon Virtual Pet simulator for the DaRkb0x LCD.
Inspired by Berational91's DigimonVPet and SydMontague's dm-vpet-python.

Controls:
  UP/DOWN  : Navigate Icons
  OK       : Select / Action
  KEY1     : Back / Cancel
  KEY3     : Exit to DaRkb0x Menu

Logic:
  - Hunger/Strength decay over time.
  - Care mistakes (hunger/strength at 0) influence evolution.
  - Training increases strength and weight.
"""

import os
import sys
import time
import json
import random
import signal
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Path setup for imports
# ---------------------------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

import RPi.GPIO as GPIO
import LCD_1in44, LCD_Config
from payloads._input_helper import get_button, flush_input

# ---------------------------------------------------------------------------
# Hardware Config
# ---------------------------------------------------------------------------
PINS = {
    "UP": 6, "DOWN": 19, "LEFT": 5, "RIGHT": 26,
    "OK": 13, "KEY1": 21, "KEY2": 20, "KEY3": 16,
}

LCD = LCD_1in44.LCD()
LCD.LCD_Init(LCD_1in44.SCAN_DIR_DFT)
WIDTH, HEIGHT = LCD.width, LCD.height

# ---------------------------------------------------------------------------
# Game Constants
# ---------------------------------------------------------------------------
STATE_FILE = "/root/DaRkb0x/loot/vpet_save.json"
SPRITE_SIZE = 48  # Upscaled 16x16
GRID_SIZE = 16

# Icons for the top/bottom menu
ICONS = ["FEED", "LIGHT", "TRAIN", "MEDIC", "CLEAN", "STATS", "BATTLE", "ALERT"]

# Evolution Paths (Simplified)
# Level: 0=Baby, 1=In-Training, 2=Rookie, 3=Champion
EVOLUTIONS = {
    "Botamon": {"next": "Koromon", "time": 60},  # 1 min for testing
    "Koromon": {"next": "Agumon", "time": 300},  # 5 min for testing
    "Agumon": {"next": "Greymon", "time": 3600}, # 1 hour
}

# ---------------------------------------------------------------------------
# Sprites (16x16 Bitmaps)
# ---------------------------------------------------------------------------
# Placeholder bitmaps for common sprites
SPRITE_DATA = {
    "Botamon": [
        0,0,0,1,1,1,1,0,0,0,
        0,0,1,1,1,1,1,1,0,0,
        0,1,1,1,1,1,1,1,1,0,
        1,1,0,1,1,1,1,0,1,1,
        1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,
        0,1,1,1,1,1,1,1,1,0,
        0,0,1,1,1,1,1,1,0,0,
    ],
    "Koromon": [
        0,0,1,1,1,1,1,1,0,0,
        0,1,1,1,1,1,1,1,1,0,
        1,1,0,1,1,1,1,0,1,1,
        1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,
        1,1,1,0,0,0,0,1,1,1,
        0,1,1,1,1,1,1,1,1,0,
        0,0,1,1,1,1,1,1,0,0,
    ],
    "Agumon": [
        0,0,1,1,1,1,0,0,
        0,1,1,1,1,1,1,0,
        1,0,1,1,1,1,0,1,
        1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,
        0,1,1,0,0,1,1,0,
        0,1,1,1,1,1,1,0,
        0,1,0,1,1,0,1,0,
    ],
    "Poop": [
        0,0,1,1,1,0,0,
        0,1,1,1,1,1,0,
        1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,
    ]
}

def draw_sprite(draw, name, x, y, scale=3, color=(0,0,0)):
    data = SPRITE_DATA.get(name, SPRITE_DATA["Botamon"])
    # Determine width based on list size (assume square if possible, else custom)
    sw = 8 if len(data) <= 64 else 10
    sh = len(data) // sw
    
    for i, bit in enumerate(data):
        if bit:
            px = x + (i % sw) * scale
            py = y + (i // sw) * scale
            draw.rectangle([px, py, px + scale - 1, py + scale - 1], fill=color)

# ---------------------------------------------------------------------------
# Game Logic
# ---------------------------------------------------------------------------
class VPet:
    def __init__(self):
        self.load()
        self.last_tick = time.time()
        self.menu_idx = 0
        self.show_menu = False
        self.action_msg = ""
        self.action_msg_time = 0

    def load(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    self.data = json.load(f)
            except:
                self.reset()
        else:
            self.reset()

    def reset(self):
        self.data = {
            "name": "Botamon",
            "age": 0,
            "weight": 5,
            "hunger": 4,
            "strength": 4,
            "effort": 0,
            "care_mistakes": 0,
            "born_at": time.time(),
            "last_care": time.time(),
            "poop": 0,
            "sick": False,
            "sleep": False,
            "alive": True
        }
        self.save()

    def save(self):
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(self.data, f)

    def tick(self):
        if not self.data["alive"]: return
        
        now = time.time()
        elapsed = now - self.last_tick
        
        # Hunger/Strength decay (every 10 mins approx)
        if now - self.data["last_care"] > 600:
            if self.data["hunger"] > 0: self.data["hunger"] -= 1
            else: self.data["care_mistakes"] += 1
            
            if self.data["strength"] > 0: self.data["strength"] -= 1
            
            # Poop chance
            if random.random() < 0.2:
                self.data["poop"] = min(4, self.data["poop"] + 1)
                
            self.data["last_care"] = now
            self.save()

        # Evolution Check
        current_name = self.data["name"]
        if current_name in EVOLUTIONS:
            evo_info = EVOLUTIONS[current_name]
            if now - self.data["born_at"] > evo_info["time"]:
                self.data["name"] = evo_info["next"]
                self.data["born_at"] = now
                self.action_msg = f"EVOLVED TO {self.data['name']}!"
                self.action_msg_time = now + 5
                self.save()

        self.last_tick = now

    def perform_action(self, action):
        now = time.time()
        if action == "FEED":
            if self.data["hunger"] < 4:
                self.data["hunger"] += 1
                self.data["weight"] += 1
                self.action_msg = "MUNCH MUNCH..."
            else:
                self.action_msg = "REFUSED!"
        elif action == "CLEAN":
            if self.data["poop"] > 0:
                self.data["poop"] = 0
                self.action_msg = "CLEANED!"
            else:
                self.action_msg = "ALREADY CLEAN"
        elif action == "TRAIN":
            if self.data["strength"] < 4:
                self.data["strength"] += 1
                self.data["effort"] += 1
                self.data["weight"] += 2
                self.action_msg = "TRAINING..."
            else:
                self.action_msg = "MAX STRENGTH"
        elif action == "MEDIC":
            if self.data["sick"]:
                self.data["sick"] = False
                self.action_msg = "HEALED"
            else:
                self.action_msg = "NOT SICK"
        elif action == "STATS":
            self.show_stats()
            return
            
        self.action_msg_time = now + 2
        self.save()

    def show_stats(self):
        # Temporary full screen stats
        img = Image.new("RGB", (WIDTH, HEIGHT), "white")
        d = ImageDraw.Draw(img)
        d.text((10, 10), f"NAME: {self.data['name']}", fill="black")
        d.text((10, 25), f"AGE: {int((time.time()-self.data['born_at'])/3600)}d", fill="black")
        d.text((10, 40), f"WEIGHT: {self.data['weight']}g", fill="black")
        d.text((10, 55), f"HUNGER: {'♥'*self.data['hunger']}", fill="black")
        d.text((10, 70), f"STR:    {'★'*self.data['strength']}", fill="black")
        d.text((10, 110), "BACK (KEY1)", fill="grey")
        LCD.LCD_ShowImage(img, 0, 0)
        while True:
            btn = get_button(PINS, GPIO)
            if btn == "KEY1": break
            time.sleep(0.1)

    def draw(self):
        img = Image.new("RGB", (WIDTH, HEIGHT), "white")
        d = ImageDraw.Draw(img)
        
        # Border
        d.rectangle([0, 0, 127, 127], outline="black", width=2)
        
        # Menu Icons (Top)
        for i in range(4):
            color = "black" if self.menu_idx == i and self.show_menu else "grey"
            d.text((10 + i*30, 5), ICONS[i][:1], fill=color)
            if self.menu_idx == i and self.show_menu:
                d.rectangle([8 + i*30, 3, 22 + i*30, 15], outline="black")

        # Menu Icons (Bottom)
        for i in range(4):
            color = "black" if self.menu_idx == i+4 and self.show_menu else "grey"
            d.text((10 + i*30, 110), ICONS[i+4][:1], fill=color)
            if self.menu_idx == i+4 and self.show_menu:
                d.rectangle([8 + i*30, 108, 22 + i*30, 120], outline="black")

        # Main Area
        if time.time() < self.action_msg_time:
            d.text((20, 50), self.action_msg, fill="black")
        else:
            # Pet Sprite
            bounce = int(abs(time.time() % 1 - 0.5) * 10)
            draw_sprite(d, self.data["name"], 40, 40 + bounce, scale=5)
            
            # Poops
            for i in range(self.data["poop"]):
                draw_sprite(d, "Poop", 90, 80 - i*10, scale=2)

        LCD.LCD_ShowImage(img, 0, 0)

# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------
def main():
    pet = VPet()
    running = True
    
    GPIO.setmode(GPIO.BCM)
    for p in PINS.values():
        GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    try:
        while running:
            pet.tick()
            pet.draw()
            
            btn = get_button(PINS, GPIO)
            if btn == "KEY3":
                running = False
            elif btn == "UP":
                pet.show_menu = True
                pet.menu_idx = (pet.menu_idx - 1) % 8
            elif btn == "DOWN":
                pet.show_menu = True
                pet.menu_idx = (pet.menu_idx + 1) % 8
            elif btn == "OK":
                if pet.show_menu:
                    pet.perform_action(ICONS[pet.menu_idx])
                    pet.show_menu = False
            elif btn == "KEY1":
                pet.show_menu = False

            time.sleep(0.1)

    finally:
        pet.save()
        LCD.LCD_Clear()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
