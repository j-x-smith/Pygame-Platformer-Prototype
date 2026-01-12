'''
Jamie X Smith
'''
import pygame
from config.config import *
from src.ui import *
from src.sprites import Player
from src.levelhandler import parse_level, load_level
from src.soundhandler import load_music

class Game:
    def __init__(self):
        pygame.init()

        # Timing and Runtime
        self.running = True
        self.clock = pygame.time.Clock()
        self.delta_time = 0.1
        self.framerate = FPS
        self.bg_color = BG_COLOR
        self.bg_music = load_music("assets/sounds/music/bg_music2.wav", volume=20, loop=True)
        self.bg_music.play()
        self.state = "PLAYING"

        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.render_layer = pygame.sprite.Group()
        self.update_layer = pygame.sprite.Group()
        self.tile_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.laser_sprites = pygame.sprite.Group()
        
        self.curr_level = 1
        self.load_new_level(self.curr_level)
        
        if self.player is None:
            self.player = Player(60, 450)
            self.player.tile_sprites = self.tile_sprites
            self.player.enemy_sprites = self.enemy_sprites
            self.all_sprites.add(self.player)

    def load_new_level(self, level_number):
        try:
            level_data = parse_level(f"./assets/levels/level{level_number}.txt")
            self.render_layer.empty()
            self.update_layer.empty()
            self.tile_sprites.empty()
            self.enemy_sprites.empty()
            self.laser_sprites.empty()
            self.player = None
            load_level(level_data, self)
        except Exception as e:
            print(e)

    def tick(self):
        self.delta_time = self.clock.tick(self.framerate) / 1000
        self.delta_time = max(0.001, min(0.1, self.delta_time))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

    def main(self):
        while self.running:
            self.tick()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.handle_input()

            self.update_layer.update(self.delta_time)

            self.screen.fill(self.bg_color)
            self.render_layer.draw(self.screen)
            
            # Render and blit debug text
            if self.state == "PLAYING":
                DEBUG_FONT.draw_text(self.screen, f"FPS: {self.clock.get_fps():.0f}, LIVES: {self.player.lives}", pos=(10,10))
            elif self.state == "GAME_OVER":
                DEBUG_FONT.draw_text(self.screen, "Game Over!", (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
            pygame.display.flip()

        pygame.quit()