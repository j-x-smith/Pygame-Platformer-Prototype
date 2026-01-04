'''
Jamie X Smith
'''
from src.sprites import Player, GrassTile, DirtTile, SpikeTile, GoalTile, Zorg, CobbleTile
from config.config import *
def parse_level(level_file_path):
    data = []
    with open(level_file_path, "r") as f:
        for line in f:
            line = line.strip("\n")
            chars = list(line)
            curr_line = []
            for char in chars:
                match char:
                    case ".":
                        curr_line.append(" ")
                    case "P":
                        curr_line.append(Player)
                    case "G":
                        curr_line.append(GrassTile)
                    case "D":
                        curr_line.append(DirtTile)
                    case "S":
                        curr_line.append(SpikeTile)
                    case "F":
                        curr_line.append(GoalTile)
                    case "Z":
                        curr_line.append(Zorg)
                    case "C":
                        curr_line.append(CobbleTile)
            data.append(curr_line)
    
    return data

def load_level(level_data, game):
     for row_index, row in enumerate(level_data):
            for col_index, cell in enumerate(row):
                x = col_index * TILE_WIDTH
                y = row_index * TILE_HEIGHT
                
                if cell == Player:
                    game.player = Player(x, y)
                    game.player.tile_sprites = game.tile_sprites
                    game.player.game = game
                    game.all_sprites.add(game.player)
                elif cell == GrassTile:
                    new_tile = GrassTile(x, y)
                    game.tile_sprites.add(new_tile)
                    game.all_sprites.add(new_tile)
                elif cell == DirtTile:
                    new_tile = DirtTile(x, y)
                    game.tile_sprites.add(new_tile)
                    game.all_sprites.add(new_tile)
                elif cell == SpikeTile:
                    rotation = 0    
                    directions = [
                        (0, -1,   180),    # tile above → spike points up
                        (1,  0,  90),   # tile right → spike points left
                        (0,  1, 0),    # tile below → spike points down
                        (-1, 0,  -90),    # tile left → spike points right
                    ]
                    for dx, dy, rot in directions:
                        neighbor = get_tile(level_data, row_index + dy, col_index + dx)
                        if neighbor in (GrassTile, DirtTile):
                            rotation = rot
                            break

                    new_tile = SpikeTile(x, y, rotation)
                    game.tile_sprites.add(new_tile)
                    game.all_sprites.add(new_tile)
                elif cell == CobbleTile:
                    new_tile = CobbleTile(x, y)
                    game.tile_sprites.add(new_tile)
                    game.all_sprites.add(new_tile)
                elif cell == Zorg:
                    new_tile = Zorg(x, y)
                    new_tile.tile_sprites = game.tile_sprites
                    game.all_sprites.add(new_tile)
                elif cell == GoalTile:
                    new_tile = GoalTile(x, y)
                    game.tile_sprites.add(new_tile)
                    game.all_sprites.add(new_tile)

def get_tile(level_data, row, col):
    if 0 <= row < len(level_data) and 0 <= col < len(level_data[row]):
        return level_data[row][col]
    return None

if __name__ == "__main__":
    parse_level("./assets/levels/level1.txt")