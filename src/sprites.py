'''
Jamie X Smith
'''
import pygame
from config.config import *
from src.soundhandler import load_sound

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, image_source, x, y, speed):
        super().__init__()
        if isinstance(image_source, str):
            self.image = pygame.image.load(image_source).convert_alpha()
        else:
            self.image = image_source
        
        self.rect = self.image.get_rect(topleft=(x,y))
        self.speed = speed

    def update(self, delta_time):
        pass

class Player(GameSprite):
    def __init__(self, x, y):
        super().__init__("assets/sprites/ivan.png", x, y, PLAYER_SPEED)
        self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        # Recreate rect with correct size after scaling
        self.rect = self.image.get_rect(topleft=(x, y))
        self.lives = PLAYER_LIVES
        self.direction_x = 0
        self.velocity_y = 0
        self.spawn_x = x
        self.spawn_y = y
        self.goal_reached = False
        self.game = None
        self.jump_power = JUMP_STRENGTH

        self.on_ground = False
        self.tile_sprites = None

        self.death_sound = load_sound("assets/sounds/sfx/death.wav", volume=300)
        self.jump_sound = load_sound("assets/sounds/sfx/jump.wav", volume=100)
        self.jump_held = False  # prevents consuming multiple jumps while key is held
        self.down_held = False
        self.is_dashing =False
        self.dash_timer = 0
        self.dash_duration = 0.15
        self.dash_speed = DASH_STRENGTH
        
        self.max_jump_count = PLAYER_JUMP_COUNT
        self.current_jumps = 0
    
    def handle_input(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction_x = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction_x = 1
        else:
            self.direction_x = 0
        
        jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
        down_pressed = keys[pygame.K_s] or keys[pygame.K_DOWN]
        dash_pressed = keys[pygame.K_q] or keys[pygame.K_e]

        if keys[pygame.K_HASH]:
            self.jump_power = DEV_JUMP_STRENGTH

        # Edge-detect jump so holding the key doesn't chain-fire jumps
        if jump_pressed and not self.jump_held and self.current_jumps < self.max_jump_count:
            self.velocity_y = self.jump_power
            self.on_ground = False
            self.current_jumps += 1
            self.jump_sound.play()
            self.jump_held = True
        elif not jump_pressed:
            self.jump_held = False

        if dash_pressed and not self.is_dashing and self.direction_x != 0:
            self.is_dashing = True
            self.dash_timer = self.dash_duration
        
        # Edge-detect jump so holding the key doesn't chain-fire jumps
        if down_pressed and not self.down_held:
            self.velocity_y = DOWN_STRENGTH
            self.on_ground = False
            self.jump_sound.play()
            self.down_held = True
        elif not down_pressed:
            self.down_held = False

    def update(self, delta_time):
        # Store previous position for collision detection
        prev_x = self.rect.x
        prev_y = self.rect.y
        if self.is_dashing:
            self.rect.x += self.direction_x * self.dash_speed * self.game.delta_time
            self.dash_timer -= self.game.delta_time
            if self.dash_timer <= 0:
                self.is_dashing = False
        
        self.rect.x += self.direction_x * self.speed * delta_time

        # Check horizontal collisions (exclude spike tiles)
        if self.tile_sprites:
            horizontal_collisions = pygame.sprite.spritecollide(self, self.tile_sprites, False)
            for tile in horizontal_collisions:
                # Skip spike tiles - they don't block movement, they kill
                if isinstance(tile, (SpikeTile, GoalTile)):
                    continue
                if self.direction_x > 0:
                    self.rect.right = tile.rect.left
                elif self.direction_x < 0:
                    self.rect.left = tile.rect.right
        
        # Apply gravity and vertical movement
        self.velocity_y += GRAVITY * delta_time
        self.rect.y += self.velocity_y * delta_time

        # Check vertical collisions (exclude spike tiles)
        self.on_ground = False
        if self.tile_sprites:
            # Get all tiles the player is currently colliding with
            vertical_collisions = pygame.sprite.spritecollide(self, self.tile_sprites, False)
            
            for tile in vertical_collisions:
                # Skip spike tiles - they don't block movement, they kill
                if isinstance(tile, (SpikeTile, GoalTile)):
                    continue
                    
                # Calculate previous bottom position
                prev_bottom = prev_y + self.rect.height
                
                # Determine which side the player is overlapping from
                overlap_from_top = self.rect.bottom - tile.rect.top
                overlap_from_bottom = tile.rect.bottom - self.rect.top
                
                # Ground collision: player is falling (or stationary) and overlapping tile from above
                if self.velocity_y >= 0:
                    # Check if player's bottom crossed into the tile
                    if self.rect.bottom > tile.rect.top:
                        # Make sure player was above tile before movement
                        if prev_bottom <= tile.rect.top:
                            self.rect.bottom = tile.rect.top
                            self.velocity_y = 0
                            self.on_ground = True
                            self.current_jumps = 0
                            break
                        # If already inside, push up if more overlap from top
                        elif overlap_from_top > overlap_from_bottom:
                            self.rect.bottom = tile.rect.top
                            self.velocity_y = 0
                            self.on_ground = True
                            break
                
                # Ceiling collision: player is moving up and overlapping tile from below
                elif self.velocity_y < 0:
                    # Check if player's top crossed into the tile
                    if self.rect.top < tile.rect.bottom:
                        # Make sure player was below tile before movement
                        if prev_y >= tile.rect.bottom:
                            self.rect.top = tile.rect.bottom
                            self.velocity_y = 0
                            break
                        # If already inside, push down if more overlap from bottom
                        elif overlap_from_bottom > overlap_from_top:
                            self.rect.top = tile.rect.bottom
                            self.velocity_y = 0
                            break
        
        if self.tile_sprites:
            # Get all tiles the player is now touching in its final, corrected position.
            special_collisions = pygame.sprite.spritecollide(self, self.tile_sprites, False)
            
            for tile in special_collisions:
                # 1. Check for Spike Collision (Hazard)
                if isinstance(tile, SpikeTile):
                    self.death_sound.play()
                    self.respawn()
                    return  # Exit early to prevent any further updates
                
                # 2. Check for Goal Collision (The working goal logic!)
                # The logic is identical to spikes: if the bounding boxes overlap, the event is triggered.
                if isinstance(tile, GoalTile) and self.goal_reached == False: 
                    if self.rect.bottom > tile.rect.top and self.rect.bottom <= tile.rect.bottom:
                
                        # --- Goal Reached ---
                        self.goal_reached = True
                        self.game.curr_level +=1
                        self.game.load_new_level(self.game.curr_level) # Load the new level
                        print("GOAL!")
                        return # Exit early after a goal is triggered
        # Screen boundary checks
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
    
    def respawn(self):
        """Respawn the player at their spawn position"""
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.velocity_y = 0
        self.current_jumps = 0

class Zorg(GameSprite):
    def __init__(self, x, y):
        super().__init__("assets/sprites/zorg.png", x, y, 150)
        self.image = pygame.transform.scale(self.image, (TILE_WIDTH, TILE_HEIGHT))
        self.rect = self.image.get_rect(topleft=(x,y))
        self.tile_sprites = None
        self.on_ground = False
        self.direction_x = 1
        self.velocity_y = 0

    def update(self, delta_time):
        prev_x = self.rect.x
        prev_y = self.rect.y

        self.rect.x += self.direction_x * self.speed * delta_time
    
         # Check horizontal collisions (exclude spike tiles)
        if self.tile_sprites:
            horizontal_collisions = pygame.sprite.spritecollide(self, self.tile_sprites, False)
            for tile in horizontal_collisions:
                # Skip spike tiles - they don't block movement, they kill
                if isinstance(tile, (SpikeTile, GoalTile)):
                    continue
                if self.direction_x > 0:
                    self.rect.right = tile.rect.left
                elif self.direction_x < 0:
                    self.rect.left = tile.rect.right

        self.velocity_y += GRAVITY * delta_time
        self.rect.y += self.velocity_y * delta_time

        self.on_ground = False
        if self.tile_sprites:
            # Get all tiles the player is currently colliding with
            vertical_collisions = pygame.sprite.spritecollide(self, self.tile_sprites, False)
            
            for tile in vertical_collisions:
                # Skip spike tiles - they don't block movement, they kill
                if isinstance(tile, (SpikeTile, GoalTile)):
                    continue
                    
                # Calculate previous bottom position
                prev_bottom = prev_y + self.rect.height
                
                # Determine which side the player is overlapping from
                overlap_from_top = self.rect.bottom - tile.rect.top
                overlap_from_bottom = tile.rect.bottom - self.rect.top
                
                # Ground collision: player is falling (or stationary) and overlapping tile from above
                if self.velocity_y >= 0:
                    # Check if player's bottom crossed into the tile
                    if self.rect.bottom > tile.rect.top:
                        # Make sure player was above tile before movement
                        if prev_bottom <= tile.rect.top:
                            self.rect.bottom = tile.rect.top
                            self.velocity_y = 0
                            self.on_ground = True
                            self.current_jumps = 0
                            break
                        # If already inside, push up if more overlap from top
                        elif overlap_from_top > overlap_from_bottom:
                            self.rect.bottom = tile.rect.top
                            self.velocity_y = 0
                            self.on_ground = True
                            break
                
                # Ceiling collision: player is moving up and overlapping tile from below
                elif self.velocity_y < 0:
                    # Check if player's top crossed into the tile
                    if self.rect.top < tile.rect.bottom:
                        # Make sure player was below tile before movement
                        if prev_y >= tile.rect.bottom:
                            self.rect.top = tile.rect.bottom
                            self.velocity_y = 0
                            break
                        # If already inside, push down if more overlap from bottom
                        elif overlap_from_bottom > overlap_from_top:
                            self.rect.top = tile.rect.bottom
                            self.velocity_y = 0
                            break


class GrassTile(GameSprite):
    def __init__(self, x, y):
        super().__init__("assets/sprites/grass_tile.png", x, y, 0)
        self.image = pygame.transform.scale(self.image, (TILE_WIDTH, TILE_HEIGHT))
        # Recreate rect with correct size after scaling
        self.rect = self.image.get_rect(topleft=(x, y))

class DirtTile(GameSprite):
    def __init__(self, x, y):
        super().__init__("assets/sprites/dirt_tile.png", x, y, 0)
        self.image = pygame.transform.scale(self.image, (TILE_WIDTH, TILE_HEIGHT))
        # Recreate rect with correct size after scaling
        self.rect = self.image.get_rect(topleft=(x, y))

class SpikeTile(GameSprite):
    def __init__(self, x, y, rotation=0):
        super().__init__("assets/sprites/spike.png", x, y, 0)
        self.image = pygame.transform.scale(self.image, (TILE_WIDTH, TILE_HEIGHT))
        if rotation != 0:
            self.image = pygame.transform.rotate(self.image, rotation)
        self.rect = self.image.get_rect(topleft=(x, y))

class GoalTile(GameSprite):
    def __init__(self, x, y):
        super().__init__("assets/sprites/goal.png", x, y, 0)
        self.image = pygame.transform.scale(self.image, (TILE_WIDTH, TILE_HEIGHT))
        self.rect = self.image.get_rect(topleft=(x,y))

class CobbleTile(GameSprite):
    def __init__(self, x, y):
        super().__init__("assets/sprites/cobble.png", x, y, 0)
        self.image = pygame.transform.scale(self.image, (TILE_WIDTH, TILE_HEIGHT))
        self.rect = self.image.get_rect(topleft=(x,y))
