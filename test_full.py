#!/usr/bin/env python3
"""
Test d'intégration rapide du jeu.
"""
import sys
import pygame
import threading
import time

def run_game():
    """Lance le jeu et le quitte après 3 secondes."""
    try:
        from game_new import Game
        game = Game()
        # Démarrer une partie en facile
        game.reset_game(game.difficulty)
        start = time.time()
        while game.running and time.time() - start < 3:  # 3 secondes
            game.handle_events()
            game.update()
            game.render()
            pygame.display.flip()
            game.clock.tick(30)
        print("✅ Test d'intégration terminé sans crash.")
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du jeu: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        pygame.quit()

if __name__ == "__main__":
    run_game()