import pygame
import sys
import os
import time
from game.towers import MeerkatScout, ChameleonSniper
from game.enemies import Poacher, Deforester, InvasiveSpecies
from game.waves import WAVES, ENEMY_STATS

pygame.init()

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 768
FPS = 60
GRID_SIZE = 64  # size of each cell
GRID_COLS = (WINDOW_WIDTH - 250 - 64) // GRID_SIZE
GRID_ROWS = WINDOW_HEIGHT // GRID_SIZE
SIDEBAR_WIDTH = 250

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 19)
BROWN = (139, 69, 19)
LIGHT_GREEN = (144, 238, 144)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 191, 255)
PURPLE = (147, 112, 219)
LIGHT_GRAY = (200, 200, 200)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Wild Defense")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"  # menu, game, pause, game_over
        
        # Game state
        self.towers = []
        self.enemies = []
        self.selected_tower_type = None
        self.money = 200
        self.wave = 0
        self.wave_started = False
        self.current_wave = []  # list of (enemy_type, spawn_time) tuples
        self.next_spawn_index = 0  # index of next enemy to spawn in current wave
        self.wave_start_time = 0
        self.wave_complete = False
        self.path = self.create_path()
        
        # Tower info
        self.tower_types = {
            "meerkat": {
                "class": MeerkatScout,
                "name": "Meerkat Scout",
                "cost": 75,
                "description": "Fast attack speed, low damage",
                "stats": ["Damage: 5", "Speed: 2.5/s", "Range: 150"]
            },
            "chameleon": {
                "class": ChameleonSniper,
                "name": "Chameleon Sniper",
                "cost": 100,
                "description": "High damage, long range",
                "stats": ["Damage: 30", "Speed: 3.0/s", "Range: 200"]
            }
        }
        
        # load assets
        self.load_assets()
        self.diamond_img = pygame.image.load('assets/dia.png').convert_alpha()
        self.diamond_img = pygame.transform.scale(self.diamond_img, (50, 50))
        
        # base stats
        self.base_health = 100
        self.max_base_health = 100
        
        # visual effects
        self.attack_lines = []  # list of (start_pos, end_pos, time) tuples
        self.attack_line_duration = 100  # milliseconds

    def load_assets(self):
        # create fonts
        self.title_font = pygame.font.Font(None, 74)
        self.menu_font = pygame.font.Font(None, 36)
        self.game_font = pygame.font.Font(None, 24)
        
    def create_path(self):
        path = [
            (0, 4 * GRID_SIZE),  # start
            (8 * GRID_SIZE, 4 * GRID_SIZE),
            (8 * GRID_SIZE, 8 * GRID_SIZE),
            (12 * GRID_SIZE, 8 * GRID_SIZE),  # end
        ]
        return path
        
    def spawn_enemy(self):
        if not self.wave_started or self.wave_complete:
            return

        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.wave_start_time

        # check if we have more enemies to spawn in this wave
        if self.next_spawn_index < len(self.current_wave):
            enemy_type, delay = self.current_wave[self.next_spawn_index]
            
            # if enough time has passed, spawn the next enemy
            if elapsed_time >= delay:
                stats = ENEMY_STATS[enemy_type]
                if enemy_type == "poacher":
                    enemy = Poacher(self.path, stats["health"], stats["speed"], stats["damage"], stats["reward"])
                elif enemy_type == "deforester":
                    enemy = Deforester(self.path, stats["health"], stats["speed"], stats["damage"], stats["reward"])
                else:  # invasive
                    enemy = InvasiveSpecies(self.path, stats["health"], stats["speed"], stats["damage"], stats["reward"])
                
                self.enemies.append(enemy)
                self.next_spawn_index += 1
        
        # check if wave is complete
        if self.next_spawn_index >= len(self.current_wave):
            all_dead = True
            for enemy in self.enemies:
                if not enemy.dead:
                    all_dead = False
                    break
            if all_dead:
                self.wave_complete = True
                self.wave_started = False

    def start_wave(self):
        if self.wave < len(WAVES):
            self.current_wave = WAVES[self.wave]
            self.wave_started = True
            self.wave_complete = False
            self.next_spawn_index = 0
            self.wave_start_time = pygame.time.get_ticks()
        else:
            print("No more waves! You win!")
            self.state = "game_over"

    def update_enemies(self):
        # update enemies
        for enemy in self.enemies[:]:
            enemy.move()
            # check if enemy died
            if enemy.check_death():
                self.money += enemy.reward
                self.enemies.remove(enemy)
                continue
            # remove enemy if it reaches the end
            if enemy.path_index >= len(self.path) - 1:
                self.base_health -= 10  # lose health when enemy reaches base
                self.enemies.remove(enemy)
                if self.base_health <= 0:
                    self.state = "game_over"
                
    def update_towers(self):
        current_time = pygame.time.get_ticks()
        
        # update towers
        for tower in self.towers:
            if tower.attack(current_time, self.enemies):
                # add visual attack line
                target = tower.find_target(self.enemies)
                if target:
                    start_pos = (tower.x + GRID_SIZE//2, tower.y + GRID_SIZE//2)
                    end_pos = (int(target.x), int(target.y))
                    self.attack_lines.append((start_pos, end_pos, current_time))
        
        # remove old attack lines
        self.attack_lines = [(start, end, time) for start, end, time in self.attack_lines
                           if current_time - time < self.attack_line_duration]
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.state == "menu":
                    button_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2, 200, 50)
                    if button_rect.collidepoint(mouse_pos):
                        self.state = "game"
                
                elif self.state == "game":
                    # handle tower selection from sidebar
                    if mouse_pos[0] > WINDOW_WIDTH - SIDEBAR_WIDTH:
                        # meerkat button area
                        if 60 <= mouse_pos[1] <= 160:
                            self.selected_tower_type = "meerkat"
                        # chameleon button area
                        elif 200 <= mouse_pos[1] <= 300:
                            self.selected_tower_type = "chameleon"
                    # handle start wave button
                    elif not self.wave_started and mouse_pos[1] > WINDOW_HEIGHT - 60 and WINDOW_WIDTH - SIDEBAR_WIDTH - 150 <= mouse_pos[0] <= WINDOW_WIDTH - SIDEBAR_WIDTH:
                        self.wave += 1
                        self.start_wave()
                    # handle tower placement
                    elif self.selected_tower_type and mouse_pos[0] < WINDOW_WIDTH - SIDEBAR_WIDTH:
                        grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
                        grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
                        
                        # check if we can place tower here
                        can_place = True
                        # don't place on UI area
                        if mouse_pos[1] > WINDOW_HEIGHT - 100:
                            can_place = False
                        else:
                            for tower in self.towers:
                                if tower.x == grid_x and tower.y == grid_y:
                                    can_place = False
                                    break
                        
                        # check if we have enough money
                        tower_info = self.tower_types[self.selected_tower_type]
                        if can_place and self.money >= tower_info["cost"]:
                            self.towers.append(tower_info["class"](grid_x, grid_y))
                            self.money -= tower_info["cost"]
            
            elif event.type == pygame.KEYDOWN and self.state == "game_over":
                # reset game
                self.__init__()
                
    def draw_menu(self):
        self.screen.fill(GREEN)
        
        # title
        title_text = self.title_font.render("Wild Defense", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
        self.screen.blit(title_text, title_rect)
        
        # start button
        button_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2, 200, 50)
        pygame.draw.rect(self.screen, WHITE, button_rect)
        start_text = self.menu_font.render("Start Game", True, BLACK)
        text_rect = start_text.get_rect(center=button_rect.center)
        self.screen.blit(start_text, text_rect)
        
    def draw_game(self):
        self.screen.fill(LIGHT_GREEN)  # background clr
        
        # grid
        for x in range(0, WINDOW_WIDTH - SIDEBAR_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH - SIDEBAR_WIDTH, y))
            
        # path
        for i in range(len(self.path) - 1):
            pygame.draw.line(self.screen, BROWN, self.path[i], self.path[i + 1], 5)
            pygame.draw.circle(self.screen, BROWN, self.path[i], 10)
        
        # draw diamond at the end of path
        base_x, base_y = self.path[-1]
        # center the diamond image on the base position
        diamond_rect = self.diamond_img.get_rect(center=(base_x, base_y))
        self.screen.blit(self.diamond_img, diamond_rect)
        
        # draw base health bar
        health_width = 60 * (self.base_health / self.max_base_health)
        pygame.draw.rect(self.screen, RED, (base_x - 30, base_y - 35, 60, 8))
        pygame.draw.rect(self.screen, GREEN, (base_x - 30, base_y - 35, health_width, 8))
        
        # draw towers
        for tower in self.towers:
            color = RED if isinstance(tower, MeerkatScout) else BLACK
            pygame.draw.rect(self.screen, color, 
                           (tower.x + 5, tower.y + 5, GRID_SIZE - 10, GRID_SIZE - 10))
            # only draw range circle if tower is selected (wow such awesome game dev skills!!)
            if (tower.x + GRID_SIZE > pygame.mouse.get_pos()[0] > tower.x and 
                tower.y + GRID_SIZE > pygame.mouse.get_pos()[1] > tower.y):
                pygame.draw.circle(self.screen, GRAY, (tower.x + GRID_SIZE//2, tower.y + GRID_SIZE//2), 
                                 tower.range, 1)
        
        # draw attack lines
        current_time = pygame.time.get_ticks()
        for start_pos, end_pos, time in self.attack_lines:
            # make lines fade out
            age = current_time - time
            alpha = 255 * (1 - age / self.attack_line_duration)
            line_color = (*RED, int(alpha))
            line_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(line_surface, line_color, start_pos, end_pos, 2)
            self.screen.blit(line_surface, (0, 0))
        
        # draw enemies
        for enemy in self.enemies:
            if not enemy.dead:
                pygame.draw.circle(self.screen, YELLOW, (int(enemy.x), int(enemy.y)), 15)
                # draw health bar
                health_width = 30 * (enemy.health / enemy.max_health)
                pygame.draw.rect(self.screen, RED, (enemy.x - 15, enemy.y - 20, 30, 5))
                pygame.draw.rect(self.screen, GREEN, (enemy.x - 15, enemy.y - 20, health_width, 5))
        
        # draw right sidebar
        pygame.draw.rect(self.screen, WHITE, (WINDOW_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
        
        # draw sidebar title
        title_text = self.menu_font.render("Towers", True, BLACK)
        self.screen.blit(title_text, (WINDOW_WIDTH - SIDEBAR_WIDTH + 20, 20))
        
        # draw tower options in sidebar
        y_offset = 60
        for tower_type, info in self.tower_types.items():
            # tower box
            box_rect = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH + 10, y_offset, SIDEBAR_WIDTH - 20, 120)
            pygame.draw.rect(self.screen, LIGHT_GRAY, box_rect)
            if self.selected_tower_type == tower_type:
                pygame.draw.rect(self.screen, BLUE, box_rect, 3)
            
            # tower icon
            icon_color = RED if tower_type == "meerkat" else BLACK
            pygame.draw.rect(self.screen, icon_color,
                           (WINDOW_WIDTH - SIDEBAR_WIDTH + 20, y_offset + 10, 40, 40))
            
            # tower name and cost
            name_text = self.game_font.render(info["name"], True, BLACK)
            cost_text = self.game_font.render(f"Cost: ${info['cost']}", True, BLACK)
            self.screen.blit(name_text, (WINDOW_WIDTH - SIDEBAR_WIDTH + 70, y_offset + 10))
            self.screen.blit(cost_text, (WINDOW_WIDTH - SIDEBAR_WIDTH + 70, y_offset + 30))
            
            # tower stats
            for i, stat in enumerate(info["stats"]):
                stat_text = self.game_font.render(stat, True, BLACK)
                self.screen.blit(stat_text, (WINDOW_WIDTH - SIDEBAR_WIDTH + 20, y_offset + 60 + i * 20))
            
            y_offset += 160
        
        # draw bottom UI (money, wave, health)
        pygame.draw.rect(self.screen, WHITE, (0, WINDOW_HEIGHT - 100, WINDOW_WIDTH - SIDEBAR_WIDTH, 100))
        
        # draw money and wave info
        money_text = self.game_font.render(f"Money: ${self.money}", True, BLACK)
        wave_text = self.game_font.render(f"Wave: {self.wave}", True, BLACK)
        health_text = self.game_font.render(f"Base Health: {self.base_health}", True, BLACK)
        self.screen.blit(money_text, (20, WINDOW_HEIGHT - 50))
        self.screen.blit(wave_text, (20, WINDOW_HEIGHT - 80))
        self.screen.blit(health_text, (200, WINDOW_HEIGHT - 50))
        
        # draw wave status
        if self.wave < len(WAVES):
            if not self.wave_started:
                wave_text = f"Wave {self.wave + 1} - Click Start Wave to begin!"
            else:
                enemies_left = len(self.current_wave) - self.next_spawn_index
                for enemy in self.enemies:
                    if not enemy.dead:
                        enemies_left += 1
                wave_text = f"Wave {self.wave + 1} - {enemies_left} enemies remaining"
        else:
            wave_text = "All waves complete!"
        
        wave_text_surface = self.game_font.render(wave_text, True, BLACK)
        self.screen.blit(wave_text_surface, (400, WINDOW_HEIGHT - 50))
        
        # draw start wave button
        if not self.wave_started:
            start_wave_rect = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH - 150, WINDOW_HEIGHT - 60, 140, 50)
            pygame.draw.rect(self.screen, GREEN, start_wave_rect)
            start_text = self.game_font.render("Start Wave", True, WHITE)
            text_rect = start_text.get_rect(center=start_wave_rect.center)
            self.screen.blit(start_text, text_rect)
        
    def draw_game_over(self):
        self.screen.fill(BLACK)
        game_over_text = self.title_font.render("Game Over!", True, RED)
        wave_text = self.menu_font.render(f"You survived {self.wave} waves", True, WHITE)
        restart_text = self.menu_font.render("Press any key to restart", True, WHITE)
        
        self.screen.blit(game_over_text, 
                        game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3)))
        self.screen.blit(wave_text, 
                        wave_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)))
        self.screen.blit(restart_text, 
                        restart_text.get_rect(center=(WINDOW_WIDTH//2, 2*WINDOW_HEIGHT//3)))
        
    def run(self):
        while self.running:
            self.handle_events()
            
            # update game state
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "game":
                self.spawn_enemy()
                self.update_enemies()
                self.update_towers()
                self.draw_game()
            elif self.state == "game_over":
                self.draw_game_over()
                
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
