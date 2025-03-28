import pygame
import math
from abc import ABC, abstractmethod

class Tower(ABC):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.level = 1
        self.range = 100
        self.damage = 10
        self.attack_speed = 1.0
        self.cost = 100
        self.target = None
        self.last_attack_time = 0
        
    @abstractmethod
    def special_ability(self):
        pass
    
    def find_target(self, enemies):
        closest_enemy = None
        min_distance = float('inf')
        
        for enemy in enemies:
            dx = enemy.x - (self.x + 32)  # add 32 to get center of tower
            dy = enemy.y - (self.y + 32)
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= self.range and distance < min_distance:
                closest_enemy = enemy
                min_distance = distance
                
        return closest_enemy
        
    def can_attack(self, current_time):
        return current_time - self.last_attack_time >= 1000 / self.attack_speed
    
    def attack(self, current_time, enemies):
        if not self.can_attack(current_time):
            return False
            
        target = self.find_target(enemies)
        if target:
            target.health -= self.damage
            self.last_attack_time = current_time
            return True
        return False

class MeerkatScout(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.damage = 5
        self.attack_speed = 2.5
        self.range = 150
        self.cost = 75
        
    def special_ability(self):
        # reveal hidden enemies
        pass

class ChameleonSniper(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.damage = 30
        self.attack_speed = 3
        self.range = 200
        self.cost = 100
        self.is_hidden = True
        
    def special_ability(self):
        # toggle visibility
        self.is_hidden = not self.is_hidden
