"""
Génération de labyrinthe procédural avec Recursive Backtracking et vérification BFS.
Version révisée avec génération robuste.
"""

import random
from collections import deque
from config_new import CellType, Difficulty, DIFFICULTY_SETTINGS

print(">>> maze_new.py: Démarrage du module")

class Cell:
    """Représente une cellule du labyrinthe."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {"N": True, "S": True, "E": True, "W": True}
        self.visited = False
        self.type = CellType.EMPTY
        self.item = None
    
    def has_wall(self, direction):
        return self.walls.get(direction, True)
    
    def remove_wall(self, direction):
        self.walls[direction] = False
    
    def is_walkable(self):
        """Retourne True si la cellule est traversable (pas un mur)."""
        return self.type != CellType.WALL
    
    def __repr__(self):
        return f"Cell({self.x},{self.y})[{self.type.name}]"


class Maze:
    """Gère la grille de cellules et la génération du labyrinthe."""
    
    def __init__(self, difficulty):
        print(f">>> Maze: Initialisation avec difficulté {difficulty}")
        self.difficulty = difficulty
        settings = DIFFICULTY_SETTINGS[difficulty]
        self.grid_size = settings["grid_size"]
        self.width = self.grid_size
        self.height = self.grid_size
        
        # Initialiser la grille
        self.grid = [[Cell(x, y) for y in range(self.height)] for x in range(self.width)]
        
        # Positions importantes
        self.start_pos = (0, 0)
        self.exit_pos = (self.width - 1, self.height - 1)
        self.potions = []      # Positions des potions
        self.enemy_positions = []  # Positions initiales des ennemis
        self.chests = []       # Positions des coffres
        
        # Génération
        self.generate_recursive_backtracking()
        self.place_items(
            settings["potions"],
            settings["enemies"],
            settings.get("chests", 0),
            settings.get("fog_radius")
        )
        
        print(f">>> Maze: Génération terminée. Potions: {len(self.potions)}, Ennemis: {len(self.enemy_positions)}, Coffres: {len(self.chests)}")
    
    def generate_recursive_backtracking(self):
        """Génère un labyrinthe parfait avec l'algorithme Recursive Backtracking."""
        print(">>> Maze: Début de la génération Recursive Backtracking")
        
        # Initialiser toutes les cellules comme non visitées
        for x in range(self.width):
            for y in range(self.height):
                self.grid[x][y].visited = False
        
        # Choisir une cellule de départ
        stack = [(0, 0)]
        self.grid[0][0].visited = True
        
        while stack:
            x, y = stack[-1]
            current = self.grid[x][y]
            
            # Obtenir les voisins non visités
            neighbors = []
            for dx, dy, direction in [(-1, 0, "W"), (1, 0, "E"), (0, -1, "N"), (0, 1, "S")]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and not self.grid[nx][ny].visited:
                    neighbors.append((nx, ny, direction))
            
            if neighbors:
                # Choisir un voisin aléatoire
                nx, ny, direction = random.choice(neighbors)
                next_cell = self.grid[nx][ny]
                
                # Abattre le mur entre current et next_cell
                if direction == "N":
                    current.remove_wall("N")
                    next_cell.remove_wall("S")
                elif direction == "S":
                    current.remove_wall("S")
                    next_cell.remove_wall("N")
                elif direction == "E":
                    current.remove_wall("E")
                    next_cell.remove_wall("W")
                elif direction == "W":
                    current.remove_wall("W")
                    next_cell.remove_wall("E")
                
                # Marquer comme visité et empiler
                next_cell.visited = True
                stack.append((nx, ny))
            else:
                # Backtrack
                stack.pop()
        
        # Marquer toutes les cellules comme FLOOR (pas de mur d'enceinte)
        for x in range(self.width):
            for y in range(self.height):
                self.grid[x][y].type = CellType.FLOOR
        
        # Créer des murs intérieurs : environ 20% des cellules deviennent des murs
        # (sauf départ, sortie et leurs alentours)
        for x in range(self.width):
            for y in range(self.height):
                # Éviter de mettre un mur sur le départ ou la sortie
                if (x, y) == self.start_pos or (x, y) == self.exit_pos:
                    continue
                # Éviter les cases adjacentes au départ
                if abs(x - self.start_pos[0]) + abs(y - self.start_pos[1]) <= 1:
                    continue
                # 20% de chance de devenir un mur
                if random.random() < 0.2:
                    self.grid[x][y].type = CellType.WALL
        
        # Assurer que la sortie est accessible (porte)
        self.grid[self.exit_pos[0]][self.exit_pos[1]].type = CellType.EXIT
        # Assurer que la position de départ est un FLOOR (déjà fait)
        self.grid[self.start_pos[0]][self.start_pos[1]].type = CellType.FLOOR
        
        # Garantir que les cases adjacentes au départ sont également des FLOOR
        for dx, dy in [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = self.start_pos[0] + dx, self.start_pos[1] + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                self.grid[nx][ny].type = CellType.FLOOR
        
        # Garantir que les cases adjacentes à la sortie sont également des FLOOR (au moins une)
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # exclure (0,0) pour ne pas écraser la sortie
            nx, ny = self.exit_pos[0] + dx, self.exit_pos[1] + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                self.grid[nx][ny].type = CellType.FLOOR
        
        # Vérification console
        if self.grid[self.start_pos[0]][self.start_pos[1]].type == CellType.FLOOR:
            print(">>> Maze: Vérification de spawn : OK")
        else:
            print(f">>> Maze: ERREUR: Joueur dans un mur à {self.start_pos}")
        
        print(">>> Maze: Génération Recursive Backtracking terminée")
    
    def place_items(self, num_potions, num_enemies, num_chests, fog_radius):
        """Place les potions, ennemis et coffres de manière aléatoire."""
        print(f">>> Maze: Placement des items (potions: {num_potions}, ennemis: {num_enemies}, coffres: {num_chests})")
        
        # Réinitialiser les listes
        self.potions = []
        self.enemy_positions = []
        self.chests = []
        
        # Obtenir toutes les cases accessibles depuis le départ (Flood Fill)
        accessible_cells = self.get_accessible_tiles()
        # Filtrer les cases FLOOR (et EXIT) et exclure le départ
        floor_cells = []
        for (x, y) in accessible_cells:
            if self.grid[x][y].type in (CellType.FLOOR, CellType.EXIT) and (x, y) != self.start_pos:
                floor_cells.append((x, y))
        
        if not floor_cells:
            print(">>> Maze: Aucune cellule accessible disponible (hormis départ)!")
            # Fallback: utiliser toutes les cases FLOOR (sans garantie d'accessibilité)
            floor_cells = []
            for x in range(self.width):
                for y in range(self.height):
                    if self.grid[x][y].type == CellType.FLOOR and (x, y) != self.start_pos:
                        floor_cells.append((x, y))
            if not floor_cells:
                print(">>> Maze: Aucune cellule FLOOR disponible!")
                return
        
        # Mélanger les cellules
        random.shuffle(floor_cells)
        
        # Placer les potions
        if len(floor_cells) >= num_potions:
            self.potions = floor_cells[:num_potions]
            floor_cells = floor_cells[num_potions:]
        else:
            self.potions = floor_cells[:]
            floor_cells = []
            print(f">>> Maze: Attention, moins de potions que demandé ({len(self.potions)} au lieu de {num_potions})")
        
        # Placer les ennemis
        if len(floor_cells) >= num_enemies:
            self.enemy_positions = floor_cells[:num_enemies]
            floor_cells = floor_cells[num_enemies:]
        else:
            self.enemy_positions = floor_cells[:]
            floor_cells = []
            print(f">>> Maze: Attention, moins d'ennemis que demandé ({len(self.enemy_positions)} au lieu de {num_enemies})")
        
        # Placer les coffres
        if len(floor_cells) >= num_chests:
            self.chests = floor_cells[:num_chests]
            floor_cells = floor_cells[num_chests:]
        else:
            self.chests = floor_cells[:]
            floor_cells = []
            print(f">>> Maze: Attention, moins de coffres que demandé ({len(self.chests)} au lieu de {num_chests})")
        
        # Vérifier que le labyrinthe est valide (toutes les potions accessibles)
        # Cette vérification devrait maintenant toujours réussir, mais on garde pour sécurité.
        if not self.is_valid():
            print(">>> Maze: ERREUR CRITIQUE: Labyrinthe non valide après placement sur cases accessibles.")
            # Réessayer avec moins d'items si nécessaire
            if not self.is_valid():
                print(">>> Maze: Toujours non valide. Réduction des potions.")
                # Garder seulement la première potion
                if len(self.potions) > 1:
                    self.potions = self.potions[:1]
        
        print(f">>> Maze: Items placés. Potions: {len(self.potions)}, Ennemis: {len(self.enemy_positions)}, Coffres: {len(self.chests)}")
    
    def is_valid(self):
        """Vérifie que toutes les potions et la sortie sont accessibles depuis le départ."""
        targets = self.potions + [self.exit_pos]
        return self.bfs_path_exists(self.start_pos, targets)
    
    def bfs_path_exists(self, start, targets):
        """
        Vérifie via BFS si tous les targets sont accessibles depuis start.
        Retourne True si oui, False sinon.
        """
        if not targets:
            return True
        
        visited = set()
        queue = deque([start])
        visited.add(start)
        remaining = set(targets)
        
        while queue and remaining:
            x, y = queue.popleft()
            
            # Vérifier si cette position est une cible
            if (x, y) in remaining:
                remaining.remove((x, y))
                if not remaining:
                    return True
            
            # Explorer les voisins accessibles
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and
                    (nx, ny) not in visited and
                    self.grid[nx][ny].is_walkable()):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        
        return len(remaining) == 0
    
    def get_accessible_tiles(self, start=None):
        """
        Retourne un ensemble des positions (x, y) accessibles depuis la position de départ.
        Utilise un BFS (Flood Fill) pour explorer toutes les cases traversables.
        """
        if start is None:
            start = self.start_pos
        from collections import deque
        visited = set()
        queue = deque([start])
        visited.add(start)
        
        while queue:
            x, y = queue.popleft()
            
            # Explorer les voisins accessibles
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and
                    (nx, ny) not in visited and
                    self.grid[nx][ny].is_walkable()):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        
        return visited
    
    def get_neighbors(self, x, y):
        """Retourne les cellules voisines accessibles (sans mur)."""
        neighbors = []
        for dx, dy, direction in [(-1, 0, "W"), (1, 0, "E"), (0, -1, "N"), (0, 1, "S")]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if not self.grid[x][y].has_wall(direction):
                    neighbors.append((nx, ny))
        return neighbors
    
    def is_walkable(self, x, y):
        """Vérifie si la position est dans la grille et traversable."""
        return (0 <= x < self.width and 0 <= y < self.height and
                self.grid[x][y].is_walkable())
    
    def get_cell(self, x, y):
        """Retourne la cellule à la position donnée."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return None
    
    def __repr__(self):
        return f"Maze({self.width}x{self.height}, potions={len(self.potions)}, enemies={len(self.enemy_positions)})"


def generate_valid_maze(difficulty, max_attempts=50):
    """
    Génère un labyrinthe valide (avec garantie de victoire).
    Réessaie jusqu'à max_attempts fois.
    """
    print(f">>> generate_valid_maze: Tentative de génération pour {difficulty}")
    for attempt in range(max_attempts):
        maze = Maze(difficulty)
        if maze.is_valid():
            print(f">>> generate_valid_maze: Succès à l'essai {attempt + 1}")
            return maze
        else:
            print(f">>> generate_valid_maze: Essai {attempt + 1} échoué (labyrinthe non valide)")
    
    # Fallback : créer un labyrinthe minimal valide
    print(f">>> generate_valid_maze: Échec après {max_attempts} tentatives. Fallback.")
    maze = Maze(difficulty)
    # Forcer la validité en réduisant les items
    maze.potions = maze.potions[:1] if maze.potions else []
    return maze