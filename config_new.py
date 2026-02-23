"""
Configuration du jeu de labyrinthe - Version révisée
"""

import os
from enum import Enum

# ============================================================================
# CHEMINS
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.json")

# ============================================================================
# PARAMÈTRES D'AFFICHAGE
# ============================================================================

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 48  # Taille d'une case en pixels
FPS = 30

# Couleurs (format RGB)
COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "gray": (128, 128, 128),
    "dark_gray": (64, 64, 64),
    "light_gray": (200, 200, 200),
    "brown": (139, 69, 19),
    "orange": (255, 165, 0),
    "cyan": (0, 255, 255),
    "pink": (255, 192, 203),
    "dark_blue": (0, 0, 128),
    "dark_green": (0, 128, 0),
    "gold": (255, 215, 0),
}

# ============================================================================
# DIFFICULTÉS
# ============================================================================

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXTREME = 4

DIFFICULTY_SETTINGS = {
    Difficulty.EASY: {
        "name": "Facile",
        "grid_size": 10,
        "potions": 3,
        "enemies": 1,
        "chests": 2,
        "fog_radius": None,  # Pas de brouillard
        "enemy_speed": 10,   # Frames entre mouvements
        "enemy_ai": "random",
        "detection_range": 0,
    },
    Difficulty.MEDIUM: {
        "name": "Moyen",
        "grid_size": 20,
        "potions": 6,
        "enemies": 3,
        "chests": 4,
        "fog_radius": 5,     # Rayon de visibilité en cases
        "enemy_speed": 8,
        "enemy_ai": "random",
        "detection_range": 0,
    },
    Difficulty.HARD: {
        "name": "Difficile",
        "grid_size": 30,
        "potions": 10,
        "enemies": 5,
        "chests": 6,
        "fog_radius": 3,
        "enemy_speed": 6,
        "enemy_ai": "random",
        "detection_range": 0,
    },
    Difficulty.EXTREME: {
        "name": "Extrême",
        "grid_size": 40,
        "potions": 15,
        "enemies": 8,
        "chests": 8,
        "fog_radius": 2,
        "enemy_speed": 4,
        "enemy_ai": "stalker",
        "detection_range": 7,      # Portée de détection du joueur (cases)
        "cooldown_moves": 2,       # Mouvement tous les 2 mouvements du joueur
        "night_blindness": True,   # Réduction de détection quand murs invisibles
    },
}

# ============================================================================
# MAPPING DES ASSETS
# ============================================================================

ASSET_MAPPING = {
    "player": "tile_0096.png",
    "enemy_wizard": "tile_0084.png",
    "enemy_ghost": "tile_0108.png",
    "enemy_monster": "tile_0109.png",
    "potion_normal": "tile_0113.png",
    "potion_vision": "tile_0114.png",
    "potion_freeze": "tile_0115.png",
    "potion_purple": "tile_0116.png",  # gardé pour compatibilité (non utilisé)
    "exit": "tile_0045.png",
    "floor1": "tile_0043.png",
    "floor2": "tile_0048.png",
    "floor3": "tile_0049.png",
    "wall": "tile_0001.png",
    "heart": "tile_0044.png",
    "chest": "tile_0089.png",
    "compass": "tile_0112.png",
}

# Couleurs de fallback si un asset est manquant
FALLBACK_COLORS = {
    "player": COLORS["blue"],
    "enemy_wizard": COLORS["purple"],
    "enemy_ghost": COLORS["cyan"],
    "enemy_monster": COLORS["red"],
    "potion_normal": COLORS["red"],
    "potion_vision": COLORS["yellow"],
    "potion_freeze": COLORS["cyan"],
    "potion_purple": COLORS["purple"],
    "exit": COLORS["yellow"],
    "floor1": COLORS["light_gray"],
    "floor2": COLORS["gray"],
    "floor3": COLORS["dark_gray"],
    "wall": COLORS["brown"],
    "heart": COLORS["pink"],
    "chest": COLORS["gold"],
    "compass": COLORS["yellow"],
}

# ============================================================================
# ÉNUMÉRATIONS
# ============================================================================

class CellType(Enum):
    EMPTY = 0
    WALL = 1
    FLOOR = 2
    EXIT = 4

class EnemyType(Enum):
    WIZARD = 0
    GHOST = 1
    MONSTER = 2

class ItemType(Enum):
    POTION_NORMAL = 0
    POTION_VISION = 1
    POTION_FREEZE = 2
    CHEST = 4

class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    WIN = 3
    PAUSED = 4

# ============================================================================
# PARAMÈTRES DE JEU
# ============================================================================

PLAYER_MAX_HEALTH = 3
PLAYER_INVINCIBILITY_DURATION = 60  # frames (2 secondes à 30 FPS)
PLAYER_KNOCKBACK_DURATION = 20      # frames

ENEMY_TYPES = [EnemyType.WIZARD, EnemyType.GHOST, EnemyType.MONSTER]
ITEM_TYPES = [
    ItemType.POTION_NORMAL,
    ItemType.POTION_VISION,
    ItemType.POTION_FREEZE,
    ItemType.CHEST,
]

# Directions (dx, dy) pour le mouvement grid-based
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

# Contrôles (flèches + ZQSD) - défini dynamiquement après import pygame
def get_controls():
    if pygame:
        return {
            pygame.K_UP: "UP",
            pygame.K_z: "UP",
            pygame.K_DOWN: "DOWN",
            pygame.K_s: "DOWN",
            pygame.K_LEFT: "LEFT",
            pygame.K_q: "LEFT",
            pygame.K_RIGHT: "RIGHT",
            pygame.K_d: "RIGHT",
        }
    else:
        # Fallback pour les tests sans pygame
        return {}

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_asset_path(asset_key):
    """Retourne le chemin complet d'un asset."""
    filename = ASSET_MAPPING.get(asset_key)
    if filename:
        return os.path.join(ASSETS_DIR, filename)
    return None

def get_fallback_color(asset_key):
    """Retourne la couleur de fallback pour un asset."""
    return FALLBACK_COLORS.get(asset_key, COLORS["white"])

def get_difficulty_by_index(index):
    """Convertit un index 1-4 en enum Difficulty."""
    if index == 1:
        return Difficulty.EASY
    elif index == 2:
        return Difficulty.MEDIUM
    elif index == 3:
        return Difficulty.HARD
    elif index == 4:
        return Difficulty.EXTREME
    else:
        return Difficulty.EASY  # fallback

# Import de pygame pour les constantes de touches
try:
    import pygame
    pygame.init()
except ImportError:
    pygame = None