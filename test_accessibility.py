#!/usr/bin/env python3
"""
Test de l'accessibilité des potions après modifications.
"""

import sys
sys.path.insert(0, '.')

from maze_new import Maze, generate_valid_maze
from config_new import Difficulty
import random

def test_accessible_tiles():
    print("=== Test get_accessible_tiles ===")
    maze = Maze(Difficulty.EASY)
    accessible = maze.get_accessible_tiles()
    print(f"Nombre de cases accessibles: {len(accessible)}")
    # Vérifier que le départ est dedans
    assert maze.start_pos in accessible, "Le départ doit être accessible"
    # Vérifier que toutes les cases accessibles sont walkable
    for (x, y) in accessible:
        assert maze.is_walkable(x, y), f"Case ({x},{y}) marquée accessible mais non walkable"
    print("OK: get_accessible_tiles fonctionne.")

def test_potions_placement():
    print("\n=== Test placement des potions ===")
    for diff in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
        print(f"Difficulté: {diff.name}")
        maze = Maze(diff)
        accessible = maze.get_accessible_tiles()
        # Vérifier que chaque potion est dans accessible
        for (x, y) in maze.potions:
            if (x, y) not in accessible:
                print(f"ERREUR: Potion à ({x},{y}) non accessible!")
                # Afficher le type de cellule
                cell = maze.grid[x][y]
                print(f"  Type cellule: {cell.type}, walkable: {cell.is_walkable()}")
                # Afficher un voisinage
                for dx in (-1,0,1):
                    for dy in (-1,0,1):
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < maze.width and 0 <= ny < maze.height:
                            c = maze.grid[nx][ny]
                            print(f"    ({nx},{ny}): {c.type.name} walkable:{c.is_walkable()}")
                raise AssertionError("Potion inaccessible")
        print(f"  {len(maze.potions)} potions toutes accessibles.")
    print("OK: Toutes les potions sont placées sur cases accessibles.")

def test_exit_accessible():
    print("\n=== Test accessibilité de la sortie ===")
    for diff in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD, Difficulty.EXTREME]:
        maze = Maze(diff)
        # Vérifier que la sortie est dans accessible
        accessible = maze.get_accessible_tiles()
        if maze.exit_pos not in accessible:
            print(f"ERREUR: Sortie {maze.exit_pos} non accessible en difficulté {diff.name}")
            # Vérifier le type de cellule
            cell = maze.grid[maze.exit_pos[0]][maze.exit_pos[1]]
            print(f"  Type: {cell.type}, walkable: {cell.is_walkable()}")
            raise AssertionError("Sortie inaccessible")
        print(f"  {diff.name}: Sortie accessible.")
    print("OK: La sortie est toujours accessible.")

def test_valid_maze_generation():
    print("\n=== Test generate_valid_maze ===")
    for diff in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
        maze = generate_valid_maze(diff, max_attempts=5)
        assert maze.is_valid(), f"Maze généré non valide pour {diff.name}"
        print(f"  {diff.name}: Labyrinthe valide généré.")
    print("OK: generate_valid_maze produit des labyrinthes valides.")

def test_performance():
    print("\n=== Test de performance (rapide) ===")
    import time
    start = time.time()
    for _ in range(10):
        maze = Maze(Difficulty.MEDIUM)
        accessible = maze.get_accessible_tiles()
        assert maze.is_valid()
    elapsed = time.time() - start
    print(f"10 générations + validation en {elapsed:.2f}s")
    assert elapsed < 5.0, "Trop lent"
    print("OK: Performance acceptable.")

def main():
    random.seed(42)  # Pour reproductibilité
    try:
        test_accessible_tiles()
        test_potions_placement()
        test_exit_accessible()
        test_valid_maze_generation()
        test_performance()
        print("\n=== TOUS LES TESTS PASSÉS ===")
        return 0
    except Exception as e:
        print(f"\nÉCHEC: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())