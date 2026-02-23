# Conception des Classes de Base

## 1. Classe `Cell` (Cellule)
Représente une cellule du labyrinthe.

### Attributs
- `x`, `y` : coordonnées dans la grille
- `walls` : dict des murs (nord, sud, est, ouest) booléens
- `visited` : booléen pour la génération
- `type` : enum (EMPTY, WALL, FLOOR, TRAP, EXIT)
- `item` : référence à un Item présent sur cette cellule (None si vide)

### Méthodes
- `has_wall(direction)` : retourne True si un mur existe
- `remove_wall(direction)` : supprime un mur (pour la génération)
- `is_walkable()` : vérifie si la cellule est traversable (pas un mur, pas un piège)

## 2. Classe `Maze` (Labyrinthe)
Gère la grille et la génération procédurale.

### Attributs
- `width`, `height` : dimensions
- `grid` : matrice 2D de Cell
- `start_pos` : position de départ du joueur
- `exit_pos` : position de la porte de sortie
- `potions` : liste des positions des potions
- `traps` : liste des positions des pièges (coffres)
- `enemy_positions` : liste des positions initiales des ennemis

### Méthodes
- `generate_recursive_backtracking()` : implémente l'algorithme
- `bfs_path_exists(start, targets)` : vérifie l'accessibilité via BFS
- `get_neighbors(cell)` : retourne les cellules voisines accessibles
- `place_items(num_potions, num_traps, num_enemies)` : place aléatoirement les objets
- `is_valid_position(x, y)` : vérifie les limites et la traversabilité

## 3. Classe `Player` (Joueur)
Représente le personnage contrôlé.

### Attributs
- `x`, `y` : position actuelle
- `health` : points de vie (1-3)
- `max_health` : constante = 3
- `potions_collected` : nombre de potions ramassées
- `total_potions` : nombre total de potions à collecter
- `invincible` : booléen d'invincibilité temporaire
- `invincible_timer` : compteur de frames d'invincibilité
- `knockback_direction` : vecteur de knockback en cas de dégât
- `knockback_timer` : durée du knockback

### Méthodes
- `move(dx, dy, maze)` : tente de se déplacer, vérifie les collisions
- `take_damage(amount)` : réduit la santé, active l'invincibilité
- `collect_potion()` : incrémente le compteur
- `update()` : gère les timers d'invincibilité et de knockback
- `is_alive()` : retourne True si health > 0

## 4. Classe `Enemy` (Ennemi)
Base pour tous les types d'ennemis.

### Attributs
- `x`, `y` : position
- `type` : enum (WIZARD, GHOST, MONSTER)
- `speed` : nombre de frames entre chaque mouvement
- `move_timer` : compteur pour le timing
- `patrol_path` : liste de positions pour le patrouillage (optionnel)
- `target` : position cible (pour l'IA chasseuse)
- `detection_range` : portée de détection du joueur

### Méthodes
- `update(player_pos, maze)` : décide du comportement selon le mode
- `move_towards_player(player_pos, maze)` : chemin vers le joueur (A* simple)
- `patrol()` : déplacement aléatoire ou patrouille
- `can_see_player(player_pos, maze)` : vérifie la ligne de vue

## 5. Classe `Item` (Objet)
Base pour les objets interactifs.

### Attributs
- `x`, `y` : position
- `type` : enum (POTION_RED, POTION_GREEN, POTION_BLUE, POTION_PURPLE, TRAP)
- `collected` : booléen

### Méthodes
- `collect()` : marque comme collecté
- `draw(surface, sprites)` : affichage

## 6. Classe `Renderer` (Moteur de rendu)
Gère l'affichage avec optimisation.

### Attributs
- `screen` : surface Pygame principale
- `sprites` : dictionnaire des images chargées (redimensionnées)
- `tile_size` : 48 pixels
- `camera_x`, `camera_y` : position de la caméra
- `fog_surface` : surface alpha pour le brouillard
- `fog_radius` : rayon de visibilité (dépend du mode)
- `light_texture` : texture du trou de lumière (gradient circulaire)

### Méthodes
- `load_sprites()` : charge et redimensionne les assets
- `draw_maze(maze, visible_cells)` : dessine les cellules visibles (culling)
- `draw_entity(entity)` : dessine une entité (joueur, ennemi, item)
- `draw_fog(player_pos)` : applique le masque de brouillard
- `update_camera(player_pos)` : centre la caméra sur le joueur
- `get_visible_rect()` : calcule la zone visible pour le culling

## 7. Classe `UI` (Interface utilisateur)
Gère les menus et HUD.

### Attributs
- `font` : police Pygame
- `current_screen` : enum (MENU, GAME, GAME_OVER, WIN)
- `selected_option` : option sélectionnée dans le menu
- `start_time` : temps de début de partie (pour le chrono)
- `highscores` : dict des meilleurs temps chargés depuis JSON

### Méthodes
- `draw_menu()` : affiche les 4 modes de difficulté
- `draw_hud(player, elapsed_time)` : affiche vies, potions, chrono
- `draw_game_over()` : écran de défaite
- `draw_win_screen(elapsed_time, highscore_beaten)` : écran de victoire
- `load_highscores()` : charge depuis highscore.json
- `save_highscore(mode, time)` : sauvegarde si record battu

## 8. Classe `Game` (Jeu principal)
Classe principale qui orchestre tout.

### Attributs
- `running` : booléen de boucle principale
- `clock` : horloge Pygame
- `fps` : 30
- `mode` : difficulté sélectionnée
- `maze` : instance de Maze
- `player` : instance de Player
- `enemies` : liste d'Enemy
- `items` : liste d'Item
- `renderer` : instance de Renderer
- `ui` : instance de UI
- `state` : état du jeu (PLAYING, PAUSED, etc.)

### Méthodes
- `run()` : boucle principale
- `handle_events()` : gestion des entrées clavier
- `update()` : mise à jour des entités, collisions, etc.
- `render()` : appel du rendu
- `reset_game()` : réinitialise pour une nouvelle partie
- `check_win_condition()` : vérifie si toutes potions collectées et sortie atteinte
- `check_collisions()` : détecte collisions joueur-ennemi, joueur-item

## 9. Classe `Config` (Configuration)
Constantes et paramètres.

### Attributs statiques
- `SCREEN_WIDTH`, `SCREEN_HEIGHT` : 800, 600
- `TILE_SIZE` : 48
- `FPS` : 30
- `DIFFICULTY_SETTINGS` : dict avec paramètres par mode
- `ASSET_MAPPING` : mapping nom de fichier -> type d'objet
- `COLORS` : couleurs de fallback

## 10. Enumérations
```python
from enum import Enum

class CellType(Enum):
    EMPTY = 0
    WALL = 1
    FLOOR = 2
    TRAP = 3
    EXIT = 4

class EnemyType(Enum):
    WIZARD = 0
    GHOST = 1
    MONSTER = 2

class ItemType(Enum):
    POTION_RED = 0
    POTION_GREEN = 1
    POTION_BLUE = 2
    POTION_PURPLE = 3
    TRAP = 4

class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    WIN = 3
    PAUSED = 4
```

## Relations entre classes
- `Game` contient une instance de `Maze`, `Player`, `Renderer`, `UI`
- `Maze` contient une grille de `Cell`
- `Cell` peut référencer un `Item`
- `Game` gère une liste d'`Enemy` et d'`Item`
- `Renderer` utilise les sprites pour dessiner `Maze`, `Player`, `Enemy`, `Item`
- `UI` affiche des informations basées sur l'état de `Game` et `Player`