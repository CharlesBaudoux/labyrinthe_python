"""
Classes des entités du jeu : Joueur, Ennemis, Items.
Version révisée avec mouvement grid-based.
"""

import random
from collections import deque
from config_new import (
    EnemyType, ItemType, PLAYER_MAX_HEALTH, PLAYER_INVINCIBILITY_DURATION,
    PLAYER_KNOCKBACK_DURATION, DIFFICULTY_SETTINGS, DIRECTIONS, FPS
)

print(">>> entities_new.py: Démarrage du module")

class Player:
    """Représente le joueur contrôlé par l'utilisateur (mouvement case par case)."""
    
    def __init__(self, x, y, total_potions):
        print(f">>> Player: Initialisation à ({x}, {y}) avec {total_potions} potions totales")
        self.grid_x = x  # Position en cases
        self.grid_y = y
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.potions_collected = 0
        self.total_potions = total_potions
        self.invincible = False
        self.invincible_timer = 0
        self.knockback_direction = (0, 0)
        self.knockback_timer = 0
        self.trail = []  # Liste des positions précédentes avec timestamp
        # Dash magique (mode Extrême uniquement)
        self.dash_cooldown = 0  # Temps restant avant prochain dash (ms)
        self.dash_active = False  # En cours de dash
        self.dash_direction = (0, 0)  # Direction du dash
        self.dash_progress = 0  # Progression du dash (0-1)
        self.dash_speed = 0.3  # Vitesse de déplacement par case (en fraction)
        self.last_direction = (0, -1)  # Dernière direction de déplacement (haut par défaut)
    
    def move(self, direction, maze):
        """
        Tente de se déplacer dans la direction donnée.
        direction: tuple (dx, dy) comme (0, -1) pour haut
        Retourne True si le déplacement a réussi.
        """
        if self.knockback_timer > 0:
            # Pendant le knockback, le joueur ne peut pas se déplacer volontairement
            return False
        
        dx, dy = direction
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        
        # Vérifier si la nouvelle position est valide
        if maze.is_walkable(new_x, new_y):
            # Ajouter l'ancienne position à la traînée (avec timestamp)
            import pygame
            self.trail.append((self.grid_x, self.grid_y, pygame.time.get_ticks()))
            # Déplacer
            self.grid_x = new_x
            self.grid_y = new_y
            # Mettre à jour la dernière direction
            self.last_direction = (dx, dy)
            print(f">>> Player: Déplacement vers ({self.grid_x}, {self.grid_y})")
            return True
        else:
            print(f">>> Player: Déplacement bloqué vers ({new_x}, {new_y})")
            return False
    
    def take_damage(self, amount=1):
        """Inflige des dégâts au joueur et active l'invincibilité temporaire."""
        if not self.invincible:
            self.health = max(0, self.health - amount)
            self.invincible = True
            self.invincible_timer = PLAYER_INVINCIBILITY_DURATION
            import traceback
            # Capturer la pile d'appel pour savoir d'où viennent les dégâts
            stack = traceback.extract_stack()
            caller = stack[-2] if len(stack) >= 2 else stack[-1]
            caller_info = f"{caller.filename}:{caller.lineno} ({caller.name})"
            print(f">>> Player: Prise de dégâts. Santé restante: {self.health} - Appelé depuis {caller_info}")
            return True
        print(f">>> Player: Déjà invincible, dégâts ignorés")
        return False
    
    def apply_knockback(self, source_x, source_y, maze):
        """Applique un knockback depuis la source donnée."""
        dx = self.grid_x - source_x
        dy = self.grid_y - source_y
        
        # Normaliser la direction (priorité aux diagonales)
        if dx != 0:
            dx = 1 if dx > 0 else -1
        if dy != 0:
            dy = 1 if dy > 0 else -1
        
        self.knockback_direction = (dx, dy)
        self.knockback_timer = PLAYER_KNOCKBACK_DURATION
        
        # Appliquer immédiatement un déplacement si possible
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        if maze.is_walkable(new_x, new_y):
            self.grid_x = new_x
            self.grid_y = new_y
            print(f">>> Player: Knockback vers ({self.grid_x}, {self.grid_y})")
    
    def dash(self, direction, maze):
        """Lance un dash magique dans la direction indiquée (si cooldown fini)."""
        import pygame
        if self.dash_cooldown > 0:
            return False
        if self.dash_active:
            return False
        dx, dy = direction
        # Vérifier si la direction est valide (au moins une composante non nulle)
        if dx == 0 and dy == 0:
            return False
        # Calculer la distance de dash (3 cases)
        target_x = self.grid_x + dx * 3
        target_y = self.grid_y + dy * 3
        # Vérifier les obstacles sur le chemin
        for step in range(1, 4):
            check_x = self.grid_x + dx * step
            check_y = self.grid_y + dy * step
            if not maze.is_walkable(check_x, check_y):
                # S'arrêter avant l'obstacle
                target_x = self.grid_x + dx * (step - 1)
                target_y = self.grid_y + dy * (step - 1)
                break
        # Activer le dash
        self.dash_active = True
        self.dash_direction = (dx, dy)
        self.dash_progress = 0.0
        self.dash_cooldown = 3000  # 3 secondes de cooldown (en ms)
        # Définir la position cible (garder en mémoire)
        self.dash_target = (target_x, target_y)
        print(f">>> Player: Dash lancé vers ({target_x}, {target_y})")
        return True
    
    def update(self, maze):
        """Met à jour les timers d'invincibilité, de knockback, dash et la traînée."""
        # Gérer l'invincibilité
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Gérer le knockback
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
        
        # Gérer le dash
        import pygame
        current_time = pygame.time.get_ticks()
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1000 // FPS  # Approximation
            if self.dash_cooldown < 0:
                self.dash_cooldown = 0
        
        if self.dash_active:
            self.dash_progress += self.dash_speed
            if self.dash_progress >= 1.0:
                # Fin du dash, téléportation à la position cible
                self.grid_x, self.grid_y = self.dash_target
                self.dash_active = False
                print(f">>> Player: Dash terminé à ({self.grid_x}, {self.grid_y})")
        
        # Nettoyer la traînée (supprimer les positions de plus de 1000 ms)
        self.trail = [(x, y, t) for (x, y, t) in self.trail if current_time - t <= 1000]
    
    def collect_potion(self):
        """Collecte une potion."""
        self.potions_collected += 1
        print(f">>> Player: Potion collectée ({self.potions_collected}/{self.total_potions})")
    
    def is_alive(self):
        """Retourne True si le joueur est en vie."""
        return self.health > 0
    
    def has_all_potions(self):
        """Retourne True si le joueur a collecté toutes les potions."""
        return self.potions_collected >= self.total_potions
    
    def get_grid_position(self):
        """Retourne la position du joueur en cases."""
        return (self.grid_x, self.grid_y)
    
    def __repr__(self):
        return f"Player({self.grid_x},{self.grid_y}) HP:{self.health} Potions:{self.potions_collected}/{self.total_potions}"


class Enemy:
    """Représente un ennemi avec IA."""
    
    def __init__(self, x, y, enemy_type, difficulty):
        self.grid_x = x
        self.grid_y = y
        self.type = enemy_type
        self.difficulty = difficulty
        
        settings = DIFFICULTY_SETTINGS[difficulty]
        self.speed = settings["enemy_speed"]
        self.ai_type = settings["enemy_ai"]
        self.detection_range_base = settings.get("detection_range", 0)
        self.cooldown_moves = settings.get("cooldown_moves", 1)
        self.night_blindness = settings.get("night_blindness", False)
        
        self.move_timer = 0
        self.target = None
        self.cooldown_counter = 0  # Compteur de cooldown pour le mode stalker
        
        # Attributs spécifiques au type
        if enemy_type == EnemyType.WIZARD:
            self.color = "purple"
            self.attack_range = 2
        elif enemy_type == EnemyType.GHOST:
            self.color = "cyan"
            self.can_phase = False  # Peut traverser les murs ? (pour future extension)
        elif enemy_type == EnemyType.MONSTER:
            self.color = "red"
            self.attack_range = 1
    
    def update(self, player_pos, maze):
        """Met à jour la position de l'ennemi selon son IA."""
        self.move_timer -= 1
        if self.move_timer > 0:
            return
        
        # Réinitialiser le timer de mouvement
        self.move_timer = self.speed
        
        # Choix du comportement selon l'IA
        if self.ai_type == "stalker" and self.detection_range_base > 0:
            # Gestion du cooldown
            self.cooldown_counter += 1
            if self.cooldown_counter >= self.cooldown_moves:
                self.cooldown_counter = 0
                if self.can_see_player(player_pos, maze):
                    self.move_towards_player(player_pos, maze)
                else:
                    self.patrol(maze)
            else:
                # Cooldown : l'ennemi reste immobile
                pass
        elif self.ai_type == "hunter" and self.detection_range_base > 0:
            if self.can_see_player(player_pos, maze):
                self.move_towards_player(player_pos, maze)
            else:
                self.patrol(maze)
        else:
            self.patrol(maze)
    
    def can_see_player(self, player_pos, maze):
        """Vérifie si le joueur est dans le rayon de détection."""
        px, py = player_pos
        distance = abs(self.grid_x - px) + abs(self.grid_y - py)  # Distance de Manhattan
        
        # Ajustement de la portée si night_blindness est activé et que les murs sont invisibles
        detection_range = self.detection_range_base
        if self.night_blindness:
            # Vérifier si les murs sont visibles (phase ON du pulse)
            # On peut utiliser une fonction importée depuis renderer_new, mais pour simplifier,
            # on utilise un calcul basé sur le temps (même logique que should_draw_walls)
            import pygame
            ticks = pygame.time.get_ticks()
            # Cycle de 6 secondes, ON pendant les 2 premières secondes
            walls_visible = (ticks // 1000) % 6 < 2
            if not walls_visible:
                # Réduction à 2 cases
                detection_range = 2
        
        return distance <= detection_range
    
    def move_towards_player(self, player_pos, maze):
        """Déplace l'ennemi vers le joueur (chemin le plus court simplifié)."""
        px, py = player_pos
        
        # Chercher la direction qui rapproche le plus du joueur
        best_dir = None
        best_distance = float('inf')
        
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = self.grid_x + dx, self.grid_y + dy
            if maze.is_walkable(nx, ny):
                distance = abs(nx - px) + abs(ny - py)
                if distance < best_distance:
                    best_distance = distance
                    best_dir = (dx, dy)
        
        if best_dir:
            dx, dy = best_dir
            if maze.is_walkable(self.grid_x + dx, self.grid_y + dy):
                self.grid_x += dx
                self.grid_y += dy
                print(f">>> Enemy {self.type.name}: Déplacement chasseur vers ({self.grid_x}, {self.grid_y})")
    
    def patrol(self, maze):
        """Déplacement aléatoire."""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = self.grid_x + dx, self.grid_y + dy
            if maze.is_walkable(nx, ny):
                self.grid_x = nx
                self.grid_y = ny
                # print(f">>> Enemy {self.type.name}: Déplacement patrouille vers ({self.grid_x}, {self.grid_y})")
                return
    
    def get_grid_position(self):
        """Retourne la position de l'ennemi en cases."""
        return (self.grid_x, self.grid_y)
    
    def __repr__(self):
        return f"Enemy({self.grid_x},{self.grid_y}) {self.type.name}"


class Item:
    """Représente un objet interactif (potion, coffre)."""
    
    def __init__(self, x, y, item_type):
        self.grid_x = x
        self.grid_y = y
        self.type = item_type
        self.collected = False
        self.effect = None  # "vision", "freeze", None
        self.chest_opened = False  # Pour les coffres
        self.chest_result = None   # "bonus" ou "trap"
    
    def collect(self):
        """Marque l'objet comme collecté."""
        self.collected = True
    
    def open_chest(self):
        """Ouvre un coffre et détermine aléatoirement le résultat."""
        import random
        if self.type != ItemType.CHEST:
            return None
        # Verrou atomique : si déjà ouvert, retourner None pour éviter les effets multiples
        if self.chest_opened:
            print(f">>> Item.open_chest: Coffre déjà ouvert à ({self.grid_x}, {self.grid_y}) - sécurité")
            return None
        self.chest_opened = True
        # Nouvelles probabilités selon spécification
        # 30% dégât, 20% brouillard, 20% vie, 30% vide
        r = random.random()
        if r < 0.30:
            # Piège dégât (30%)
            self.chest_result = "trap"
            return {"type": "trap", "subtype": "damage"}
        elif r < 0.50:
            # Piège brouillard étendu (20%)
            self.chest_result = "trap"
            return {"type": "trap", "subtype": "fog"}
        elif r < 0.70:
            # Bonus vie (20%)
            self.chest_result = "bonus"
            return {"type": "bonus", "subtype": "health"}
        else:
            # Neutre/vide (30%)
            self.chest_result = "neutral"
            return {"type": "neutral", "subtype": "empty"}
    
    def get_grid_position(self):
        """Retourne la position de l'objet en cases."""
        return (self.grid_x, self.grid_y)
    
    def get_effect(self):
        """Retourne l'effet de la potion (si spéciale)."""
        if self.type == ItemType.POTION_VISION:
            return "vision"
        elif self.type == ItemType.POTION_FREEZE:
            return "freeze"
        return None
    
    def __repr__(self):
        effect = self.get_effect()
        if effect:
            return f"Item({self.grid_x},{self.grid_y}) {self.type.name} ({effect})"
        else:
            return f"Item({self.grid_x},{self.grid_y}) {self.type.name}"


def create_enemies_from_maze(maze, difficulty):
    """Crée une liste d'ennemis à partir des positions du labyrinthe."""
    enemies = []
    enemy_types = list(EnemyType)
    
    for i, (x, y) in enumerate(maze.enemy_positions):
        enemy_type = enemy_types[i % len(enemy_types)]
        enemy = Enemy(x, y, enemy_type, difficulty)
        enemies.append(enemy)
    
    print(f">>> create_enemies_from_maze: {len(enemies)} ennemis créés")
    return enemies


def create_items_from_maze(maze):
    """Crée une liste d'items à partir des positions du labyrinthe."""
    items = []
    
    # Distribution probabiliste des potions
    # 70% normale, 15% vision, 15% freeze
    import random
    
    for i, (x, y) in enumerate(maze.potions):
        r = random.random()
        if r < 0.70:
            potion_type = ItemType.POTION_NORMAL
        elif r < 0.85:
            potion_type = ItemType.POTION_VISION
        else:
            potion_type = ItemType.POTION_FREEZE
        item = Item(x, y, potion_type)
        items.append(item)
    
    # Coffres
    for x, y in maze.chests:
        chest_item = Item(x, y, ItemType.CHEST)
        items.append(chest_item)
    
    print(f">>> create_items_from_maze: {len(items)} items créés ({len(maze.potions)} potions)")
    return items