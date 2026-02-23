#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from maze_new import Maze
from config_new import Difficulty
import random

random.seed(42)

for i in range(5):
    print(f"\n--- Génération {i+1} ---")
    maze = Maze(Difficulty.MEDIUM)
    accessible = maze.get_accessible_tiles()
    print(f"Accessibles: {len(accessible)}")
    print(f"Exit position: {maze.exit_pos}, exit in accessible? {maze.exit_pos in accessible}")
    print(f"Exit cell type: {maze.grid[maze.exit_pos[0]][maze.exit_pos[1]].type}")
    # Vérifier les voisins de la sortie
    for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
        nx, ny = maze.exit_pos[0] + dx, maze.exit_pos[1] + dy
        if 0 <= nx < maze.width and 0 <= ny < maze.height:
            cell = maze.grid[nx][ny]
            print(f"  ({nx},{ny}): {cell.type.name} walkable:{cell.is_walkable()}")
    # Vérifier chaque potion
    for idx, (x, y) in enumerate(maze.potions):
        print(f"Potion {idx}: ({x},{y}) in accessible? {(x,y) in accessible}")
    # Vérifier is_valid
    valid = maze.is_valid()
    print(f"is_valid: {valid}")
    if not valid:
        # Détailler
        targets = maze.potions + [maze.exit_pos]
        from collections import deque
        start = maze.start_pos
        visited = set()
        queue = deque([start])
        visited.add(start)
        remaining = set(targets)
        while queue and remaining:
            x, y = queue.popleft()
            if (x, y) in remaining:
                remaining.remove((x, y))
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < maze.width and 0 <= ny < maze.height and
                    (nx, ny) not in visited and
                    maze.grid[nx][ny].is_walkable()):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        print(f"Targets non atteints: {remaining}")
        break