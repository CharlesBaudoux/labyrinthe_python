"""
Classe principale du jeu - Version révisée avec boucle d'événements correcte.
"""

import pygame
import time
import json
import os
import asyncio
from config_new import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLORS, get_controls, DIFFICULTY_SETTINGS,
    GameState, Difficulty, CellType, ItemType, DIRECTIONS, HIGHSCORE_FILE
)
from maze_new import generate_valid_maze
from entities_new import Player, create_enemies_from_maze, create_items_from_maze
from renderer_new import Renderer

print(">>> game_new.py: Démarrage du module")

class Game:
    """Classe principale du jeu."""
    
    def __init__(self):
        print(">>> Game: Initialisation (pièges supprimés, unification visuelle coffres)")
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Labyrinthe Pygame - Redéveloppement")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # État du jeu
        self.state = GameState.MENU
        self.difficulty = Difficulty.EASY
        
        # Composants
        self.maze = None
        self.player = None
        self.enemies = []
        self.items = []
        self.renderer = Renderer(self.screen)
        
        # Variables de jeu
        self.start_time = None
        self.elapsed_time = 0
        self.new_highscore = False
        self.highscores = self.load_highscores()
        self.damage_flash_end = 0  # Timestamp de fin du flash rouge (ms)
        self.potion_effects = {
            "vision": 0,  # Timestamp de fin de l'effet vision (ms)
            "freeze": 0,  # Timestamp de fin de l'effet freeze (ms)
        }
        self.player_trail = []  # Déplacé depuis Player? (géré dans Player)
        # Boussole de potion
        self.compass_target = None  # (x, y) de la potion cible
        self.compass_cooldown = 0   # Temps restant avant réactivation (ms)
        self.compass_active = True  # La boussole est-elle active ?
        
        # Sélection du menu
        self.selected_option = 0  # 0-3 pour les 4 difficultés
        
        print(">>> Game: Initialisation terminée")
    
    def load_highscores(self):
        """Charge les meilleurs scores depuis le fichier JSON."""
        default_scores = {
            "easy": 0.0,
            "medium": 0.0,
            "hard": 0.0,
            "extreme": 0.0
        }
        
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, "r") as f:
                    scores = json.load(f)
                    # Fusionner avec les valeurs par défaut
                    for key in default_scores:
                        if key in scores:
                            default_scores[key] = float(scores[key])
                print(">>> Game: High scores chargés")
            except Exception as e:
                print(f">>> Game: Erreur lors du chargement des high scores: {e}")
        else:
            print(">>> Game: Fichier highscore.json non trouvé, utilisation des valeurs par défaut")
        
        return default_scores
    
    def save_highscore(self):
        """Sauvegarde un nouveau high score si battu."""
        diff_key = self.difficulty.name.lower()
        current_best = self.highscores.get(diff_key, 0.0)
        
        # 0.0 signifie qu'aucun score n'a été enregistré
        if current_best == 0.0 or self.elapsed_time < current_best:
            self.highscores[diff_key] = self.elapsed_time
            self.new_highscore = True
            try:
                with open(HIGHSCORE_FILE, "w") as f:
                    json.dump(self.highscores, f, indent=2)
                print(f">>> Game: NOUVEAU RECORD pour {diff_key}: {self.elapsed_time:.2f}s")
                return True
            except Exception as e:
                print(f">>> Game: Erreur lors de la sauvegarde du high score: {e}")
        
        return False
    
    def reset_game(self, difficulty):
        """Réinitialise le jeu pour une nouvelle partie."""
        print(f">>> Game: Réinitialisation du jeu pour la difficulté {difficulty}")
        self.difficulty = difficulty
        self.state = GameState.PLAYING
        self.new_highscore = False
        
        # Générer un labyrinthe valide
        self.maze = generate_valid_maze(difficulty)
        
        # Créer le joueur
        start_x, start_y = self.maze.start_pos
        settings = DIFFICULTY_SETTINGS[difficulty]
        self.player = Player(start_x, start_y, settings["potions"])
        
        # Créer les ennemis
        self.enemies = create_enemies_from_maze(self.maze, difficulty)
        
        # Créer les items
        self.items = create_items_from_maze(self.maze)
        
        # Configurer le rendu
        fog_radius = settings.get("fog_radius")
        self.renderer.init_fog(fog_radius)
        
        # Réinitialiser la boussole
        self.compass_target = None
        self.compass_cooldown = 0
        self.compass_active = True
        
        # Démarrer le chronomètre
        self.start_time = time.time()
        self.elapsed_time = 0
        
        print(f">>> Game: Partie prête. Joueur à ({start_x}, {start_y})")
    
    def handle_events(self):
        """Gère les événements Pygame."""
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                print(">>> Game: QUIT event")
            
            elif event.type == pygame.KEYDOWN:
                # Touche Échap pour quitter
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.MENU
                        print(">>> Game: Retour au menu (ESC)")
                    else:
                        self.running = False
                
                # Touche P pour pause
                elif event.key == pygame.K_p:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                        print(">>> Game: Pause activée")
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                        print(">>> Game: Pause désactivée")
                
                # Gestion du menu
                elif self.state == GameState.MENU:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        # Sélection directe par chiffre
                        index = event.key - pygame.K_1 + 1
                        self.selected_option = index - 1
                        self.reset_game(Difficulty(index))
                        print(f">>> Game: Difficulté sélectionnée par touche: {index}")
                    
                    elif event.key == pygame.K_UP or event.key == pygame.K_z:
                        self.selected_option = (self.selected_option - 1) % 4
                        print(f">>> Game: Option menu: {self.selected_option}")
                    
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.selected_option = (self.selected_option + 1) % 4
                        print(f">>> Game: Option menu: {self.selected_option}")
                    
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Convertir l'option sélectionnée en difficulté
                        difficulty = Difficulty(self.selected_option + 1)
                        self.reset_game(difficulty)
                        print(f">>> Game: Difficulté sélectionnée: {difficulty}")
                
                # Gestion des mouvements pendant le jeu (un appui = une case)
                elif self.state == GameState.PLAYING:
                    moved = False
                    if event.key == pygame.K_UP or event.key == pygame.K_z:
                        moved = self.player.move(DIRECTIONS["UP"], self.maze)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        moved = self.player.move(DIRECTIONS["DOWN"], self.maze)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_q:
                        moved = self.player.move(DIRECTIONS["LEFT"], self.maze)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        moved = self.player.move(DIRECTIONS["RIGHT"], self.maze)
                    elif event.key == pygame.K_SPACE:
                        # Dash dans la dernière direction
                        if self.player.dash(self.player.last_direction, self.maze):
                            # Après un dash, vérifier les collisions et victoire
                            self.check_collisions()
                            self.check_win_condition()
                    
                    if moved:
                        # Vérifier les collisions après un déplacement
                        self.check_collisions()
                        # Vérifier les conditions de victoire
                        self.check_win_condition()
                
                # Gestion des écrans de fin
                elif self.state in (GameState.GAME_OVER, GameState.WIN):
                    # Appuyer sur n'importe quelle touche pour retourner au menu
                    self.state = GameState.MENU
                    print(">>> Game: Retour au menu depuis écran de fin")
        
        return events
    
    def check_collisions(self):
        """Vérifie les collisions entre les entités."""
        player_pos = self.player.get_grid_position()
        
        # Collision joueur-ennemi
        for enemy in self.enemies:
            if player_pos == enemy.get_grid_position():
                if self.player.take_damage(1):
                    self.player.apply_knockback(enemy.grid_x, enemy.grid_y, self.maze)
                    # Déclencher le flash rouge (200 ms)
                    self.damage_flash_end = pygame.time.get_ticks() + 200
        
        # Collision joueur-objets
        # Log des items à la position du joueur
        items_at_pos = [item for item in self.items if player_pos == item.get_grid_position() and not item.collected]
        if items_at_pos:
            print(f"DEBUG: {len(items_at_pos)} item(s) non collecté(s) à la position {player_pos}: {[item.type.name for item in items_at_pos]}")
        
        for item in self.items[:]:  # Copie pour suppression
            if player_pos == item.get_grid_position() and not item.collected:
                print(f"DEBUG: Tentative de collision avec l'objet {id(item)} à la position {item.get_grid_position()}")
                if item.type == ItemType.CHEST:
                    print(f">>> CHEST détecté à {item.get_grid_position()}")
                    # Coffre : ouvrir et appliquer résultat
                    result = item.open_chest()
                    if result is None:
                        print(f">>> ERREUR: open_chest a retourné None (coffre déjà ouvert?) - suppression de l'item")
                        self.items.remove(item)
                        continue
                    item.collected = True
                    # Appliquer le résultat selon le type
                    result_type = result["type"]
                    subtype = result["subtype"]
                    print(f"DEBUG: Coffre ouvert - Type: {result_type}, Subtype: {subtype}")
                    
                    if result_type == "bonus":
                        if subtype == "health":
                            # Ajouter 1 point de vie sans dépasser le maximum
                            self.player.health = min(self.player.max_health, self.player.health + 1)
                            print(f">>> Coffre bonus : +1 HP (vie: {self.player.health}/{self.player.max_health})")
                        # Note: le subtype "shield" et "vision_boost" ne sont plus générés par open_chest
                    
                    elif result_type == "trap":
                        if subtype == "damage":
                            self.player.take_damage(1)
                            print(">>> Coffre piégé (damage) : -1 HP")
                        elif subtype == "fog":
                            # Étendre le brouillard (réduire le rayon de visibilité)
                            if self.renderer.fog_radius is not None:
                                # Réduire le rayon (minimum 1 pour éviter les crashs)
                                new_radius = max(1, self.renderer.fog_radius - 1)
                                self.renderer.fog_radius = new_radius
                                print(f">>> Coffre piégé : Brouillard étendu (rayon: {new_radius})")
                            else:
                                print(">>> Coffre piégé : Brouillard étendu (ignoré, brouillard désactivé)")
                        else:
                            print(f"ERREUR: subtype de piège inconnu: {subtype} - aucun effet appliqué")
                    
                    elif result_type == "neutral":
                        # Coffre vide
                        print(">>> Coffre vide : rien ne se passe")
                    else:
                        print(f"ERREUR: result_type inconnu: {result_type} - aucun effet appliqué")
                    
                    self.items.remove(item)
                else:  # Potion (normale, vision, freeze)
                    item.collect()
                    self.player.collect_potion()
                    # Appliquer effet spécial si potion spéciale
                    effect = item.get_effect()
                    if effect == "vision":
                        self.potion_effects["vision"] = pygame.time.get_ticks() + 10000  # 10 secondes
                        print(">>> Effet VISION activé (+3 cases de visibilité)")
                    elif effect == "freeze":
                        self.potion_effects["freeze"] = pygame.time.get_ticks() + 5000   # 5 secondes
                        print(">>> Effet FREEZE activé (ennemis gelés)")
                    self.items.remove(item)
    
    def check_win_condition(self):
        """Vérifie si le joueur a gagné."""
        if not self.player.has_all_potions():
            return
        
        # Le joueur a toutes les potions, vérifier s'il est sur la sortie
        if self.player.get_grid_position() == self.maze.exit_pos:
            self.state = GameState.WIN
            self.elapsed_time = time.time() - self.start_time
            self.save_highscore()
            print(f">>> Game: VICTOIRE ! Temps: {self.elapsed_time:.2f}s")
    
    def check_game_over(self):
        """Vérifie si le joueur a perdu."""
        if not self.player.is_alive():
            self.state = GameState.GAME_OVER
            print(">>> Game: GAME OVER")
    
    def update(self):
        """Met à jour la logique du jeu."""
        if self.state != GameState.PLAYING:
            return
        
        # Mettre à jour le temps écoulé
        self.elapsed_time = time.time() - self.start_time
        
        # Mettre à jour le joueur
        self.player.update(self.maze)
        
        # Mettre à jour les ennemis (sauf si gelés)
        current_time = pygame.time.get_ticks()
        frozen = current_time < self.potion_effects["freeze"]
        player_pos = self.player.get_grid_position()
        for enemy in self.enemies:
            if not frozen:
                enemy.update(player_pos, self.maze)
        
        # Vérifier les collisions (après déplacement des ennemis)
        self.check_collisions()
        
        # Vérifier les conditions de défaite
        self.check_game_over()
        
        # Vérifier les conditions de victoire
        self.check_win_condition()
        
        # Mettre à jour la caméra
        self.renderer.update_camera(
            self.player.grid_x, self.player.grid_y,
            self.maze.width, self.maze.height
        )
        
        # Mettre à jour la boussole
        self.update_compass()
    
    def update_compass(self):
        """Met à jour la boussole qui indique la potion la plus proche."""
        current_time = pygame.time.get_ticks()
        # Désactiver temporairement après collecte ?
        if self.compass_cooldown > 0:
            self.compass_cooldown -= self.clock.get_time()
            if self.compass_cooldown <= 0:
                self.compass_cooldown = 0
                self.compass_active = True
        
        if not self.compass_active:
            self.compass_target = None
            return
        
        # Trouver les potions non collectées
        uncollected = []
        for item in self.items:
            if item.type in (ItemType.POTION_NORMAL, ItemType.POTION_VISION, ItemType.POTION_FREEZE) and not item.collected:
                uncollected.append(item)
        
        if not uncollected:
            self.compass_target = None
            return
        
        # Choisir la potion la plus proche en distance de Manhattan
        player_pos = self.player.get_grid_position()
        closest = min(uncollected, key=lambda item: abs(item.grid_x - player_pos[0]) + abs(item.grid_y - player_pos[1]))
        self.compass_target = (closest.grid_x, closest.grid_y)
    
    def draw_menu(self):
        """Dessine le menu principal."""
        self.screen.fill(COLORS["black"])
        
        # Titre
        font_big = pygame.font.Font(None, 72)
        title = font_big.render("LABYRINTHE PYTHON", True, COLORS["cyan"])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Options
        font = pygame.font.Font(None, 36)
        options = [
            "1. FACILE (10x10, 3 potions, pas de brouillard)",
            "2. MOYEN (20x20, 6 potions, brouillard rayon 5)",
            "3. DIFFICILE (30x30, 10 potions, brouillard rayon 3)",
            "4. EXTRÊME (40x40, 15 potions, brouillard total + IA chasseuse)",
        ]
        
        for i, option_text in enumerate(options):
            color = COLORS["yellow"] if i == self.selected_option else COLORS["white"]
            option = font.render(option_text, True, color)
            option_rect = option.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 50))
            self.screen.blit(option, option_rect)
        
        # Instructions
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "Utilisez les flèches ↑↓ ou Z/S pour naviguer, ENTREE pour sélectionner",
            "Appuyez sur 1-4 pour sélectionner directement",
            "Échap pour quitter"
        ]
        
        for i, text in enumerate(instructions):
            instr = font_small.render(text, True, COLORS["gray"])
            instr_rect = instr.get_rect(center=(SCREEN_WIDTH // 2, 450 + i * 30))
            self.screen.blit(instr, instr_rect)
        
        # High scores
        highscores_text = font_small.render("MEILLEURS TEMPS:", True, COLORS["green"])
        highscores_rect = highscores_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(highscores_text, highscores_rect)
        
        y_offset = 580
        for diff_key, score in self.highscores.items():
            if score > 0:
                time_str = f"{int(score // 60):02d}:{int(score % 60):02d}"
                text = f"{diff_key.upper()}: {time_str}"
            else:
                text = f"{diff_key.upper()}: --:--"
            
            score_text = font_small.render(text, True, COLORS["light_gray"])
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(score_text, score_rect)
            y_offset += 25
    
    def draw_game_over(self):
        """Dessine l'écran Game Over."""
        # Rendu du jeu en arrière-plan
        self.renderer.draw_all(self.maze, self.player, self.enemies, self.items, self.elapsed_time, None, None)
        
        # Overlay sombre
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Texte
        font_big = pygame.font.Font(None, 72)
        font = pygame.font.Font(None, 36)
        
        game_over = font_big.render("GAME OVER", True, COLORS["red"])
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over, game_over_rect)
        
        instruction = font.render("Appuyez sur une touche pour continuer...", True, COLORS["white"])
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_win_screen(self):
        """Dessine l'écran de victoire."""
        # Rendu du jeu en arrière-plan
        self.renderer.draw_all(self.maze, self.player, self.enemies, self.items, self.elapsed_time, None, None)
        
        # Overlay sombre
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Texte
        font_big = pygame.font.Font(None, 72)
        font = pygame.font.Font(None, 36)
        
        win = font_big.render("VICTOIRE !", True, COLORS["yellow"])
        win_rect = win.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(win, win_rect)
        
        # Temps
        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        time_text = f"Temps: {minutes:02d}:{seconds:02d}"
        time_surface = font.render(time_text, True, COLORS["cyan"])
        time_rect = time_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(time_surface, time_rect)
        
        # Nouveau record
        if self.new_highscore:
            record = font.render("NOUVEAU RECORD !", True, COLORS["green"])
            record_rect = record.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(record, record_rect)
        
        instruction = font.render("Appuyez sur une touche pour continuer...", True, COLORS["white"])
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_pause_screen(self):
        """Dessine l'écran de pause."""
        # Rendu du jeu en arrière-plan
        self.renderer.draw_all(self.maze, self.player, self.enemies, self.items, self.elapsed_time, None, None)
        
        # Overlay sombre
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Texte
        font_big = pygame.font.Font(None, 72)
        font = pygame.font.Font(None, 36)
        
        pause = font_big.render("PAUSE", True, COLORS["yellow"])
        pause_rect = pause.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(pause, pause_rect)
        
        instruction = font.render("Appuyez sur P pour reprendre", True, COLORS["white"])
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(instruction, instruction_rect)
    
    def render(self):
        """Dessine tout à l'écran selon l'état du jeu."""
        if self.state == GameState.MENU:
            self.draw_menu()
        
        elif self.state == GameState.PLAYING:
            self.renderer.draw_all(self.maze, self.player, self.enemies, self.items, self.elapsed_time, self.potion_effects, self.compass_target)
            # Flash rouge si dégâts récents
            current_ticks = pygame.time.get_ticks()
            if current_ticks < self.damage_flash_end:
                self.renderer.draw_damage_flash(alpha=100)
        
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        elif self.state == GameState.WIN:
            self.draw_win_screen()
        
        elif self.state == GameState.PAUSED:
            self.draw_pause_screen()
        
        pygame.display.flip()
    
    async def run(self):
        """Boucle principale du jeu."""
        print(">>> Game: Démarrage de la boucle principale")
        
        while self.running:
            events = self.handle_events()
            
            if not self.running:
                break
            
            self.update()
            self.render()
            
            self.clock.tick(FPS)
            await asyncio.sleep(0)
        
        pygame.quit()
        print(">>> Game: Fermeture du jeu")