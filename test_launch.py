#!/usr/bin/env python3
"""
Script de test pour vérifier le lancement du jeu et la génération du labyrinthe.
"""

import sys
import os
import pygame
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_new import Game
from config_new import Difficulty

print("=== TEST DE LANCEMENT DU JEU ===")

# Initialiser Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Test Labyrinthe")

# Créer une instance de Game
game = Game()
print("Game créé.")

# Forcer la difficulté EASY et démarrer une partie
game.reset_game(Difficulty.EASY)
print("Partie initialisée.")

# Simuler quelques boucles
for i in range(10):
    # Gérer les événements (juste QUIT)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Mettre à jour la logique
    game.update()
    
    # Dessiner
    game.render()
    pygame.display.flip()
    time.sleep(0.1)

print("Test terminé sans crash.")
pygame.quit()