# Algorithmes de Génération et Vérification

## 1. Recursive Backtracking (Génération de labyrinthe)

### Principe
Crée un labyrinthe parfait (un seul chemin entre deux cellules) en utilisant une pile pour explorer récursivement.

### Pseudo-code
```python
def generate_recursive_backtracking(width, height):
    # Initialiser la grille avec toutes les cellules ayant 4 murs
    grid = [[Cell(x, y) for y in range(height)] for x in range(width)]
    
    # Choisir une cellule de départ
    stack = [(0, 0)]
    grid[0][0].visited = True
    
    while stack:
        x, y = stack[-1]
        current = grid[x][y]
        
        # Obtenir les voisins non visités
        neighbors = []
        for dx, dy, direction in [(-1, 0, 'W'), (1, 0, 'E'), (0, -1, 'N'), (0, 1, 'S')]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and not grid[nx][ny].visited:
                neighbors.append((nx, ny, direction))
        
        if neighbors:
            # Choisir un voisin aléatoire
            nx, ny, direction = random.choice(neighbors)
            next_cell = grid[nx][ny]
            
            # Abattre le mur entre current et next_cell
            if direction == 'N':
                current.walls['N'] = False
                next_cell.walls['S'] = False
            elif direction == 'S':
                current.walls['S'] = False
                next_cell.walls['N'] = False
            elif direction == 'E':
                current.walls['E'] = False
                next_cell.walls['W'] = False
            elif direction == 'W':
                current.walls['W'] = False
                next_cell.walls['E'] = False
            
            # Marquer comme visité et empiler
            next_cell.visited = True
            stack.append((nx, ny))
        else:
            # Backtrack
            stack.pop()
    
    return grid
```

### Caractéristiques
- Complexité : O(n) où n = width * height
- Garantit un chemin unique entre deux cellules
- Produit un labyrinthe avec beaucoup de cul-de-sac
- Adapté pour les jeux car offre des chemins sinueux

## 2. Breadth-First Search (BFS) pour vérification de victoire

### Objectif
Vérifier que depuis la position de départ, le joueur peut atteindre toutes les potions ET la sortie.

### Pseudo-code
```python
def bfs_path_exists(maze, start, targets):
    """
    maze : instance de Maze
    start : tuple (x, y)
    targets : liste de tuples (positions des potions + sortie)
    Retourne True si tous les targets sont accessibles depuis start
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
            if (0 <= nx < maze.width and 0 <= ny < maze.height and
                (nx, ny) not in visited and
                maze.grid[nx][ny].is_walkable()):
                visited.add((nx, ny))
                queue.append((nx, ny))
    
    return len(remaining) == 0
```

### Utilisation dans la génération
```python
def generate_valid_maze(width, height, num_potions, num_traps, num_enemies):
    """Génère un labyrinthe valide (garantie de victoire)"""
    max_attempts = 100
    for attempt in range(max_attempts):
        maze = Maze(width, height)
        maze.generate_recursive_backtracking()
        maze.place_items(num_potions, num_traps, num_enemies)
        
        # Vérifier l'accessibilité
        targets = maze.potions + [maze.exit_pos]
        if bfs_path_exists(maze, maze.start_pos, targets):
            return maze  # Valide
    
    # Fallback : régénérer avec moins d'objets
    return generate_valid_maze(width, height, num_potions-1, num_traps, num_enemies)
```

## 3. Placement des objets

### Potions
- Placées aléatoirement sur des cellules FLOOR
- Pas sur la même cellule qu'un autre objet
- Pas sur la position de départ
- Minimum distance de 3 cases entre deux potions (optionnel)

### Pièges (coffres)
- Placés sur des cellules FLOOR
- Bloquent le passage (non traversables)
- Positionnées de manière à ne pas bloquer l'accès aux potions (vérifié par BFS après placement)

### Ennemis
- Placés sur des cellules FLOOR
- Pas sur la même cellule qu'un objet
- Distance minimale de 5 cases du joueur (pour éviter un début trop dur)

## 4. Algorithme de déplacement des ennemis

### Mode aléatoire (Facile, Moyen, Difficile)
```python
def random_move(self, maze):
    # Choisir une direction aléatoire parmi les voisins accessibles
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    random.shuffle(directions)
    
    for dx, dy in directions:
        nx, ny = self.x + dx, self.y + dy
        if maze.is_valid_position(nx, ny) and maze.grid[nx][ny].is_walkable():
            self.x, self.y = nx, ny
            return
```

### Mode chasseur (Extrême)
```python
def hunt_player(self, player_pos, maze):
    # Utilise un BFS simple pour trouver le chemin le plus court
    start = (self.x, self.y)
    target = player_pos
    
    # Si le joueur est dans le rayon de détection
    if distance(start, target) <= self.detection_range:
        # Chemin vers le joueur (algorithme greedy)
        path = self.find_path_to_player(start, target, maze)
        if path and len(path) > 1:
            next_pos = path[1]  # Premier pas du chemin
            self.x, self.y = next_pos
```

### Algorithme de chemin (simplifié)
```python
def find_path_to_player(self, start, target, maze):
    """Retourne le chemin le plus court avec BFS"""
    queue = deque([(start, [])])  # (position, chemin)
    visited = set([start])
    
    while queue:
        (x, y), path = queue.popleft()
        
        if (x, y) == target:
            return path + [(x, y)]
        
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < maze.width and 0 <= ny < maze.height and
                (nx, ny) not in visited and
                maze.grid[nx][ny].is_walkable()):
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(x, y)]))
    
    return None  # Pas de chemin trouvé
```

## 5. Culling (Optimisation du rendu)

### Principe
Ne dessiner que les cellules visibles à l'écran.

### Calcul de la zone visible
```python
def get_visible_cells(self, camera_x, camera_y):
    """Retourne les coordonnées des cellules dans le viewport"""
    tile_size = self.tile_size
    screen_width, screen_height = self.screen.get_size()
    
    # Convertir les coordonnées écran en coordonnées grille
    start_x = max(0, camera_x // tile_size - 1)
    start_y = max(0, camera_y // tile_size - 1)
    end_x = min(self.maze.width, (camera_x + screen_width) // tile_size + 2)
    end_y = min(self.maze.height, (camera_y + screen_height) // tile_size + 2)
    
    visible_cells = []
    for x in range(start_x, end_x):
        for y in range(start_y, end_y):
            visible_cells.append((x, y))
    
    return visible_cells
```

## 6. Brouillard de guerre (Fog of War)

### Technique du masque alpha
1. Créer une surface de la taille de l'écran avec alpha=200 (noir semi-transparent)
2. Dessiner un cercle avec alpha=0 centré sur le joueur (trou de lumière)
3. Appliquer cette surface sur l'écran avec blending SRCALPHA

### Implémentation
```python
def create_fog_surface(self):
    """Crée une surface de brouillard pré-calculée"""
    fog = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
    fog.fill((0, 0, 0, 200))  # Noir semi-transparent
    
    # Créer un cercle de transparence (trou de lumière)
    center_x, center_y = self.screen_width // 2, self.screen_height // 2
    radius = self.fog_radius * self.tile_size
    
    # Dessiner un gradient circulaire
    for r in range(radius, 0, -1):
        alpha = int(200 * (r / radius) ** 2)  # Alpha décroissant vers le centre
        pygame.draw.circle(fog, (0, 0, 0, alpha), (center_x, center_y), r)
    
    # Centre complètement transparent
    pygame.draw.circle(fog, (0, 0, 0, 0), (center_x, center_y), radius // 3)
    
    return fog
```

### Mise à jour dynamique
- Le brouillard est statique (pré-calculé)
- On le dessine à chaque frame à la position du joueur
- Pour le mode "brouillard total" (Extrême), réduire le rayon

## 7. Gestion des collisions

### Détection simple
```python
def check_collisions(self):
    # Collision joueur-ennemi
    for enemy in self.enemies:
        if (self.player.x, self.player.y) == (enemy.x, enemy.y):
            self.player.take_damage(1)
            # Knockback
            self.apply_knockback(enemy)
    
    # Collision joueur-potion
    for item in self.items[:]:  # Copie pour suppression
        if item.type.startswith('POTION') and not item.collected:
            if (self.player.x, self.player.y) == (item.x, item.y):
                item.collect()
                self.player.collect_potion()
                self.items.remove(item)
```

### Knockback
```python
def apply_knockback(self, enemy):
    """Repousse le joueur dans la direction opposée à l'ennemi"""
    dx = self.player.x - enemy.x
    dy = self.player.y - enemy.y
    
    # Normaliser la direction
    if dx != 0 or dy != 0:
        length = max(1, abs(dx) + abs(dy))
        knock_x = dx // length if dx != 0 else 0
        knock_y = dy // length if dy != 0 else 0
        
        # Tenter de déplacer le joueur
        new_x = self.player.x + knock_x
        new_y = self.player.y + knock_y
        
        if self.maze.is_valid_position(new_x, new_y):
            self.player.x, self.player.y = new_x, new_y