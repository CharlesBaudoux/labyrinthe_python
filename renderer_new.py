"""
Système de rendu Pygame avec culling et brouillard de guerre dynamique.
Version révisée avec brouillard correct.
"""

import pygame
import os
from config_new import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, COLORS, ASSET_MAPPING,
    get_asset_path, get_fallback_color, CellType, EnemyType, ItemType
)

print(">>> renderer_new.py: Démarrage du module")

class Renderer:
    """Gère l'affichage du jeu avec optimisations."""
    
    def __init__(self, screen):
        print(">>> Renderer: Initialisation")
        self.screen = screen
        self.sprites = {}
        self.tile_size = TILE_SIZE
        self.camera_offset_x = 0  # Décalage de la caméra en pixels
        self.camera_offset_y = 0
        
        # Brouillard de guerre
        self.fog_surface = None
        self.fog_radius = None  # Rayon en cases
        
        # Chargement des sprites
        self.load_sprites()
        
        print(f">>> Renderer: {len(self.sprites)} sprites chargés")
    
    def load_sprites(self):
        """Charge et redimensionne les sprites depuis le dossier assets."""
        print(">>> Renderer: Chargement des sprites...")
        
        for key, filename in ASSET_MAPPING.items():
            path = get_asset_path(key)
            if path and os.path.exists(path):
                try:
                    # Charger l'image
                    sprite = pygame.image.load(path).convert_alpha()
                    # Redimensionner de 16x16 à 48x48 avec NEAREST neighbor
                    sprite = pygame.transform.scale(sprite, (self.tile_size, self.tile_size))
                    self.sprites[key] = sprite
                    print(f"  ✓ {filename}")
                except Exception as e:
                    print(f"  ✗ {filename} (erreur: {e})")
                    self.create_fallback_sprite(key)
            else:
                print(f"  ✗ {filename} (fichier non trouvé)")
                self.create_fallback_sprite(key)
    
    def create_fallback_sprite(self, key):
        """Crée un sprite de fallback (carré coloré)."""
        color = get_fallback_color(key)
        surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        surface.fill(color)
        # Ajouter un contour
        pygame.draw.rect(surface, COLORS["black"], (0, 0, self.tile_size, self.tile_size), 2)
        self.sprites[key] = surface
    
    def init_fog(self, fog_radius):
        """Initialise le brouillard de guerre."""
        self.fog_radius = fog_radius
        if fog_radius is None:
            self.fog_surface = None
            print(">>> Renderer: Brouillard désactivé")
        else:
            # Créer une surface de la taille de l'écran
            self.fog_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            print(f">>> Renderer: Brouillard activé (rayon: {fog_radius} cases)")
    
    def update_camera(self, player_grid_x, player_grid_y, maze_width, maze_height):
        """Met à jour le décalage de la caméra pour centrer le joueur."""
        # Position du joueur en pixels (centre de la case)
        player_pixel_x = player_grid_x * self.tile_size + self.tile_size // 2
        player_pixel_y = player_grid_y * self.tile_size + self.tile_size // 2
        
        # Calculer l'offset pour centrer le joueur
        target_offset_x = player_pixel_x - SCREEN_WIDTH // 2
        target_offset_y = player_pixel_y - SCREEN_HEIGHT // 2
        
        # Limiter l'offset aux bords du labyrinthe
        max_offset_x = max(0, maze_width * self.tile_size - SCREEN_WIDTH)
        max_offset_y = max(0, maze_height * self.tile_size - SCREEN_HEIGHT)
        
        self.camera_offset_x = max(0, min(target_offset_x, max_offset_x))
        self.camera_offset_y = max(0, min(target_offset_y, max_offset_y))
        
        # print(f">>> Renderer: Camera offset ({self.camera_offset_x}, {self.camera_offset_y})")
    
    def grid_to_screen(self, grid_x, grid_y):
        """Convertit des coordonnées grille en coordonnées écran."""
        screen_x = grid_x * self.tile_size - self.camera_offset_x
        screen_y = grid_y * self.tile_size - self.camera_offset_y
        return (screen_x, screen_y)
    
    def get_visible_grid_range(self, maze_width, maze_height):
        """Retourne la plage de cellules visibles à l'écran (culling)."""
        start_x = max(0, int(self.camera_offset_x // self.tile_size) - 1)
        start_y = max(0, int(self.camera_offset_y // self.tile_size) - 1)
        end_x = min(maze_width, int((self.camera_offset_x + SCREEN_WIDTH) // self.tile_size) + 2)
        end_y = min(maze_height, int((self.camera_offset_y + SCREEN_HEIGHT) // self.tile_size) + 2)
        
        return (start_x, start_y, end_x, end_y)
    
    def draw_maze(self, maze):
        """Dessine le labyrinthe (seulement les cellules visibles)."""
        start_x, start_y, end_x, end_y = self.get_visible_grid_range(maze.width, maze.height)
        
        # Effet sonar : n'afficher les murs que pendant la phase ON
        draw_walls = self.should_draw_walls()
        
        # DEBUG
        if not hasattr(self, '_debug_printed'):
            self._debug_printed = {"visible": False, "hidden": False}
        
        if draw_walls and not self._debug_printed["visible"]:
            print(">>> ÉTAT : MURS VISIBLES")
            self._debug_printed["visible"] = True
            self._debug_printed["hidden"] = False
        elif not draw_walls and not self._debug_printed["hidden"]:
            print(">>> ÉTAT : MURS CACHÉS")
            self._debug_printed["hidden"] = True
            self._debug_printed["visible"] = False
        
        wall_count = 0
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                cell = maze.get_cell(x, y)
                if not cell:
                    continue
                
                screen_x, screen_y = self.grid_to_screen(x, y)
                
                # Dessiner selon le type de cellule
                if cell.type == CellType.WALL:
                    wall_count += 1
                    if draw_walls:
                        # Mur : afficher un caractère "x" blanc (sonar)
                        self.draw_wall_char(screen_x, screen_y)
                        # TEST : rectangle blanc 4x4 au centre pour vérification
                        center_x = screen_x + self.tile_size // 2 - 2
                        center_y = screen_y + self.tile_size // 2 - 2
                        pygame.draw.rect(
                            self.screen,
                            (255, 255, 255),
                            (center_x, center_y, 4, 4)
                        )
                elif cell.type == CellType.EXIT:
                    self.draw_tile("exit", screen_x, screen_y)
                # Pour le FLOOR, on ne dessine rien (fond noir)
                
                # NOTE: On ne dessine plus les murs graphiques (supprimé)
        
        # DEBUG : afficher le nombre de murs détectés dans la grille visible
        if draw_walls:
            print(f">>> DEBUG : Nombre de murs détectés dans la grille : {wall_count}")
    
    def draw_wall_char(self, screen_x, screen_y):
        """Dessine un caractère 'x' blanc centré pour représenter un mur."""
        # Utiliser "x" simple (caractère ASCII)
        char = "x"
        
        # Créer une police
        font_size = self.tile_size - 10
        font = pygame.font.Font(None, font_size)
        text = font.render(char, True, COLORS["white"])
        text_rect = text.get_rect(center=(screen_x + self.tile_size // 2,
                                          screen_y + self.tile_size // 2))
        self.screen.blit(text, text_rect)
    
    def should_draw_walls(self):
        """
        Détermine si les murs doivent être affichés selon le cycle sonar.
        Cycle : 2 secondes ON, 4 secondes OFF (total 6 secondes).
        """
        ticks = pygame.time.get_ticks()
        # Convertir en secondes (1000 ms = 1 s)
        seconds = ticks // 1000
        # Position dans le cycle de 6 secondes
        pos_in_cycle = seconds % 6
        # Afficher seulement pendant les 2 premières secondes du cycle
        return pos_in_cycle < 2
    
    def draw_damage_flash(self, alpha=100):
        """Dessine un calque rouge semi-transparent sur tout l'écran."""
        flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        flash_surface.fill((255, 0, 0, alpha))
        self.screen.blit(flash_surface, (0, 0))
    
    def draw_tile(self, tile_key, screen_x, screen_y):
        """Dessine une tile à la position écran donnée."""
        if tile_key in self.sprites:
            self.screen.blit(self.sprites[tile_key], (screen_x, screen_y))
        else:
            # Fallback ultime
            pygame.draw.rect(
                self.screen,
                COLORS["red"],
                (screen_x, screen_y, self.tile_size, self.tile_size)
            )
    
    def draw_cell_walls(self, cell, screen_x, screen_y):
        """Dessine les murs individuels pour un effet visuel."""
        wall_color = COLORS["dark_gray"]
        wall_thickness = 2
        
        if cell.has_wall("N"):
            pygame.draw.line(
                self.screen,
                wall_color,
                (screen_x, screen_y),
                (screen_x + self.tile_size, screen_y),
                wall_thickness
            )
        if cell.has_wall("S"):
            pygame.draw.line(
                self.screen,
                wall_color,
                (screen_x, screen_y + self.tile_size),
                (screen_x + self.tile_size, screen_y + self.tile_size),
                wall_thickness
            )
        if cell.has_wall("W"):
            pygame.draw.line(
                self.screen,
                wall_color,
                (screen_x, screen_y),
                (screen_x, screen_y + self.tile_size),
                wall_thickness
            )
        if cell.has_wall("E"):
            pygame.draw.line(
                self.screen,
                wall_color,
                (screen_x + self.tile_size, screen_y),
                (screen_x + self.tile_size, screen_y + self.tile_size),
                wall_thickness
            )
    
    def draw_player(self, player):
        """Dessine le joueur."""
        screen_x, screen_y = self.grid_to_screen(player.grid_x, player.grid_y)
        
        # Si invincible, clignotement (affichage une frame sur deux)
        if player.invincible and (pygame.time.get_ticks() // 200) % 2 == 0:
            return  # Skip le rendu pendant le clignotement
        
        self.draw_tile("player", screen_x, screen_y)
    
    def draw_player_trail(self, player):
        """Dessine la traînée magique du joueur (positions récentes)."""
        current_time = pygame.time.get_ticks()
        for (x, y, timestamp) in player.trail:
            # Vérifier si la position est récente (moins de 1000 ms)
            if current_time - timestamp > 1000:
                continue
            screen_x, screen_y = self.grid_to_screen(x, y)
            # Dessiner un petit cercle blanc au centre de la case
            center_x = screen_x + self.tile_size // 2
            center_y = screen_y + self.tile_size // 2
            pygame.draw.circle(
                self.screen,
                COLORS["white"],
                (center_x, center_y),
                3  # rayon 3 pixels
            )
    
    def draw_enemies(self, enemies):
        """Dessine tous les ennemis."""
        for enemy in enemies:
            screen_x, screen_y = self.grid_to_screen(enemy.grid_x, enemy.grid_y)
            
            # Déterminer la clé du sprite selon le type
            if enemy.type == EnemyType.WIZARD:
                key = "enemy_wizard"
            elif enemy.type == EnemyType.GHOST:
                key = "enemy_ghost"
            else:  # MONSTER
                key = "enemy_monster"
            
            self.draw_tile(key, screen_x, screen_y)
    
    def draw_items(self, items):
        """Dessine tous les items (potions et coffres)."""
        for item in items:
            if item.collected:
                continue
                
            screen_x, screen_y = self.grid_to_screen(item.grid_x, item.grid_y)
            
            # Déterminer la clé du sprite selon le type
            if item.type == ItemType.POTION_NORMAL:
                key = "potion_normal"
            elif item.type == ItemType.POTION_VISION:
                key = "potion_vision"
            elif item.type == ItemType.POTION_FREEZE:
                key = "potion_freeze"
            elif item.type == ItemType.CHEST:
                key = "chest"
            else:
                continue
            
            self.draw_tile(key, screen_x, screen_y)
    
    def draw_fog(self, player_grid_x, player_grid_y):
        """Dessine le brouillard de guerre si activé."""
        if self.fog_surface is None or self.fog_radius is None:
            return
        
        # Réinitialiser la surface de brouillard (noir opaque)
        self.fog_surface.fill((0, 0, 0, 255))
        
        # Position du joueur en pixels écran
        player_screen_x, player_screen_y = self.grid_to_screen(player_grid_x, player_grid_y)
        # Centre du joueur en pixels écran
        player_center_x = player_screen_x + self.tile_size // 2
        player_center_y = player_screen_y + self.tile_size // 2
        
        # Rayon en pixels
        radius_pixels = self.fog_radius * self.tile_size
        
        # Dessiner un cercle transparent au centre (trou de lumière)
        pygame.draw.circle(
            self.fog_surface,
            (0, 0, 0, 0),  # Transparent
            (player_center_x, player_center_y),
            radius_pixels
        )
        
        # Appliquer le brouillard sur l'écran
        self.screen.blit(self.fog_surface, (0, 0))
    
    def draw_hud(self, player, elapsed_time, potion_effects=None):
        """Dessine le HUD (vies, potions, temps) avec indicateurs d'effets."""
        if potion_effects is None:
            potion_effects = {}
        current_time = pygame.time.get_ticks()
        # Fond semi-transparent
        hud_bg = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 150))
        self.screen.blit(hud_bg, (0, 0))
        
        # Police
        font = pygame.font.Font(None, 32)
        small_font = pygame.font.Font(None, 24)
        
        # Vies
        life_text = f"Vies: {player.health}/{player.max_health}"
        life_surface = font.render(life_text, True, COLORS["white"])
        self.screen.blit(life_surface, (20, 15))
        
        # Potions
        potion_text = f"Potions: {player.potions_collected}/{player.total_potions}"
        potion_surface = font.render(potion_text, True, COLORS["white"])
        self.screen.blit(potion_surface, (200, 15))
        
        # Temps
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_text = f"Temps: {minutes:02d}:{seconds:02d}"
        time_surface = font.render(time_text, True, COLORS["white"])
        self.screen.blit(time_surface, (SCREEN_WIDTH - 200, 15))
        
        # Barre de progression des potions
        bar_width = 150
        bar_height = 15
        bar_x = 400
        bar_y = 22
        
        # Fond de la barre
        pygame.draw.rect(
            self.screen,
            COLORS["dark_gray"],
            (bar_x, bar_y, bar_width, bar_height)
        )
        
        # Remplissage
        if player.total_potions > 0:
            progress = player.potions_collected / player.total_potions
            fill_width = int(bar_width * progress)
            color = COLORS["green"] if player.potions_collected == player.total_potions else COLORS["blue"]
            pygame.draw.rect(
                self.screen,
                color,
                (bar_x, bar_y, fill_width, bar_height)
            )
        
        # Indicateurs d'effets de potion
        effect_font = pygame.font.Font(None, 24)
        indicator_x = 600
        indicator_y = 20
        
        # Vision active
        if current_time < potion_effects.get("vision", 0):
            vision_text = "💡 Vision +"
            vision_surface = effect_font.render(vision_text, True, COLORS["yellow"])
            self.screen.blit(vision_surface, (indicator_x, indicator_y))
            indicator_x += 120
        
        # Gel actif
        if current_time < potion_effects.get("freeze", 0):
            freeze_text = "🧊 Gelé"
            freeze_surface = effect_font.render(freeze_text, True, COLORS["cyan"])
            self.screen.blit(freeze_surface, (indicator_x, indicator_y))
    
    def draw_dash_gauge(self, player):
        """Dessine la jauge de recharge du dash."""
        if not hasattr(player, 'dash_cooldown'):
            return
        # Cooldown max = 3000 ms (3 secondes)
        max_cooldown = 3000.0
        current_cooldown = player.dash_cooldown
        if current_cooldown < 0:
            current_cooldown = 0
        ratio = 1.0 - (current_cooldown / max_cooldown)
        
        # Position et dimensions de la jauge
        gauge_x = SCREEN_WIDTH - 220
        gauge_y = 60
        gauge_width = 200
        gauge_height = 12
        
        # Fond
        pygame.draw.rect(
            self.screen,
            COLORS["dark_gray"],
            (gauge_x, gauge_y, gauge_width, gauge_height)
        )
        # Remplissage
        fill_width = int(gauge_width * ratio)
        if fill_width > 0:
            color = COLORS["cyan"] if ratio >= 1.0 else COLORS["blue"]
            pygame.draw.rect(
                self.screen,
                color,
                (gauge_x, gauge_y, fill_width, gauge_height)
            )
        # Texte
        font = pygame.font.Font(None, 20)
        text = "Dash prêt" if ratio >= 1.0 else f"Dash ({int(current_cooldown/1000)}s)"
        text_surface = font.render(text, True, COLORS["white"])
        self.screen.blit(text_surface, (gauge_x, gauge_y + gauge_height + 2))
    
    def draw_compass(self, player_pos, target_pos):
        """Dessine une boussole pointant vers la potion la plus proche."""
        if target_pos is None:
            return
        # Calculer le vecteur direction
        dx = target_pos[0] - player_pos[0]
        dy = target_pos[1] - player_pos[1]
        # Normaliser pour obtenir une direction cardinale
        if abs(dx) > abs(dy):
            # Horizontal
            if dx > 0:
                direction = "E"
            else:
                direction = "W"
        else:
            # Vertical
            if dy > 0:
                direction = "S"
            else:
                direction = "N"
        
        # Charger le sprite de la boussole ou dessiner une flèche
        if "compass" in self.sprites:
            sprite = self.sprites["compass"]
            sprite_rect = sprite.get_rect()
        else:
            # Fallback : dessiner un cercle avec une flèche
            sprite = None
        
        # Position de la boussole en haut à droite
        compass_x = SCREEN_WIDTH - 80
        compass_y = 80
        radius = 20
        
        # Cercle de fond
        pygame.draw.circle(
            self.screen,
            COLORS["dark_gray"],
            (compass_x, compass_y),
            radius
        )
        # Flèche directionnelle
        arrow_color = COLORS["yellow"]
        if direction == "N":
            points = [
                (compass_x, compass_y - radius + 5),
                (compass_x - 8, compass_y + 5),
                (compass_x + 8, compass_y + 5)
            ]
        elif direction == "S":
            points = [
                (compass_x, compass_y + radius - 5),
                (compass_x - 8, compass_y - 5),
                (compass_x + 8, compass_y - 5)
            ]
        elif direction == "E":
            points = [
                (compass_x + radius - 5, compass_y),
                (compass_x - 5, compass_y - 8),
                (compass_x - 5, compass_y + 8)
            ]
        else:  # W
            points = [
                (compass_x - radius + 5, compass_y),
                (compass_x + 5, compass_y - 8),
                (compass_x + 5, compass_y + 8)
            ]
        pygame.draw.polygon(self.screen, arrow_color, points)
        
        # Texte de distance
        distance = abs(dx) + abs(dy)
        font = pygame.font.Font(None, 18)
        text = f"{distance}"
        text_surface = font.render(text, True, COLORS["white"])
        text_rect = text_surface.get_rect(center=(compass_x, compass_y + radius + 10))
        self.screen.blit(text_surface, text_rect)
    
    def draw_all(self, maze, player, enemies, items, elapsed_time, potion_effects=None, compass_target=None):
        """Dessine tous les éléments du jeu (ordre de rendu correct)."""
        if potion_effects is None:
            potion_effects = {}
        
        # Fond noir
        self.screen.fill(COLORS["black"])
        
        # 1. Labyrinthe
        self.draw_maze(maze)
        
        # 2. Items (potions, pièges)
        self.draw_items(items)
        
        # 3. Ennemis
        self.draw_enemies(enemies)
        
        # 4. Traînée magique du joueur
        self.draw_player_trail(player)
        
        # 5. Joueur
        self.draw_player(player)
        
        # 6. Brouillard de guerre (par-dessus tout mais sous le HUD)
        # Ajuster le rayon du brouillard si effet vision actif
        current_time = pygame.time.get_ticks()
        vision_active = current_time < potion_effects.get("vision", 0)
        original_fog_radius = self.fog_radius
        if vision_active and original_fog_radius is not None:
            self.fog_radius = original_fog_radius + 3  # +3 cases de visibilité
            # Recalculer la surface de brouillard
            self.init_fog(self.fog_radius)
        
        self.draw_fog(player.grid_x, player.grid_y)
        
        # Restaurer le rayon original après le dessin
        if vision_active and original_fog_radius is not None:
            self.fog_radius = original_fog_radius
            self.init_fog(self.fog_radius)
        
        # 7. HUD (toujours visible) avec indicateurs d'effets
        self.draw_hud(player, elapsed_time, potion_effects)
        # 8. Jauge de dash
        self.draw_dash_gauge(player)
        # 9. Boussole (si cible fournie)
        if compass_target is not None:
            self.draw_compass(player.get_grid_position(), compass_target)