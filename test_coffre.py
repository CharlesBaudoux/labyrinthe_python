#!/usr/bin/env python3
"""
Test de collision avec les coffres.
"""
import sys
sys.path.insert(0, '.')

from config_new import Difficulty, ItemType
from maze_new import generate_valid_maze
from entities_new import Player

print("=== TEST COFFRE ===")
maze = generate_valid_maze(Difficulty.EASY)
print(f"Maze généré. Coffres positions: {maze.chests}")

if not maze.chests:
    print("Aucun coffre généré, test impossible.")
    sys.exit(0)

chest_pos = maze.chests[0]
print(f"Coffre à {chest_pos}")
cell = maze.grid[chest_pos[0]][chest_pos[1]]
print(f"Type de cellule: {cell.type}")
print(f"is_walkable? {cell.is_walkable()}")

# Créer un joueur à côté du coffre (à gauche)
player_x = chest_pos[0] - 1
player_y = chest_pos[1]
if player_x < 0:
    player_x = chest_pos[0] + 1
player = Player(player_x, player_y, maze.potions)

print(f"Joueur à ({player_x}, {player_y})")
# Tenter de se déplacer vers le coffre
dx = chest_pos[0] - player_x
dy = chest_pos[1] - player_y
direction = (dx, dy)
print(f"Direction {direction}")
success = player.move(direction, maze)
print(f"Déplacement réussi ? {success}")
