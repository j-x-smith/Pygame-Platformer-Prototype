'''
Jamie X Smith
'''
import pygame
from config.config import *
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

        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.all_sprites = pygame.sprite.Group()
        self.tile_sprites = pygame.sprite.Group()
        
        self.curr_level = 1
        self.load_new_level(self.curr_level)
        
        if self.player is None:
            self.player = Player(60, 450)
            self.player.tile_sprites = self.tile_sprites
            self.all_sprites.add(self.player)

    def load_new_level(self, level_number):
        try:
            level_data = parse_level(f"./assets/levels/level{level_number}.txt")
            self.all_sprites.empty()
            self.tile_sprites.empty()
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

            self.all_sprites.update(self.delta_time)

            self.screen.fill(self.bg_color)
            self.all_sprites.draw(self.screen)
            
            
            # Render and blit debug text
            debug_text = DEBUG_FONT.render(f"FPS: {self.clock.get_fps():.0f}, Jumps Used: {self.player.current_jumps}, Max Jumps: {self.player.max_jump_count}", antialias=True, color=WHITE)
            self.screen.blit(debug_text, (10, 10))

            pygame.display.flip()

        pygame.quit()