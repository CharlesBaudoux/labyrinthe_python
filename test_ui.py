#!/usr/bin/env python3
"""
Test minimal pour vérifier les fonctions d'UI sans ouvrir de fenêtre.
"""
import sys
import pygame
pygame.init()
pygame.display.set_mode((1, 1))  # Petite fenêtre invisible

from config_new import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from renderer_new import Renderer
from entities_new import Player

# Créer un renderer avec une surface écran mock
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
renderer = Renderer(screen)

# Créer un joueur mock
player = Player(5, 5, 3)
player.dash_cooldown = 1500  # 1.5 secondes restantes

# Test draw_dash_gauge
try:
    renderer.draw_dash_gauge(player)
    print("✅ draw_dash_gauge exécuté sans erreur")
except Exception as e:
    print(f"❌ draw_dash_gauge a échoué: {e}")
    sys.exit(1)

# Test draw_compass avec une cible
try:
    renderer.draw_compass((5, 5), (10, 10))
    print("✅ draw_compass exécuté sans erreur")
except Exception as e:
    print(f"❌ draw_compass a échoué: {e}")
    sys.exit(1)

# Test draw_compass avec cible None
try:
    renderer.draw_compass((5, 5), None)
    print("✅ draw_compass avec None exécuté sans erreur")
except Exception as e:
    print(f"❌ draw_compass avec None a échoué: {e}")
    sys.exit(1)

# Vérifier que l'asset compass est chargé
if "compass" in renderer.sprites:
    print("✅ Sprite compass chargé")
else:
    print("⚠️ Sprite compass non chargé (fallback attendu)")

print("Tous les tests UI passés.")
pygame.quit()