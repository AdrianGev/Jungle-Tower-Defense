import pygame
from abc import ABC, abstractmethod

class Enemy(ABC):
    def __init__(self, path, health=100, speed=1, damage=10, reward=10):
        self.path = path
        self.path_index = 0
        self.x = path[0][0]
        self.y = path[0][1]
        self.health = health
        self.max_health = health
        self.speed = speed
        self.damage = damage
        self.reward = reward
        self.dead = False
        
    def move(self):
        if self.dead:
            return
            
        if self.path_index < len(self.path) - 1:
            target_x, target_y = self.path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance < self.speed:
                self.path_index += 1
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
                
    def check_death(self):
        if self.health <= 0 and not self.dead:
            self.dead = True
            return True
        return False

class Poacher(Enemy):
    def __init__(self, path, health=50, speed=2, damage=5, reward=10):
        super().__init__(path, health, speed, damage, reward)

class Deforester(Enemy):
    def __init__(self, path, health=100, speed=1, damage=10, reward=15):
        super().__init__(path, health, speed, damage, reward)

class InvasiveSpecies(Enemy):
    def __init__(self, path, health=75, speed=3, damage=15, reward=20):
        super().__init__(path, health, speed, damage, reward)
        self.reproduction_rate = 0.1  # Chance to spawn new enemy

class Bulldozer(Enemy):
    def __init__(self, path, health=2000, speed=0.75, damage=50, reward=80):
        super().__init__(path, health, speed, damage, reward)
