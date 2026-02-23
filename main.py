#!/usr/bin/env python3
"""
Point d'entrée principal du jeu de labyrinthe - Version révisée.
"""

import sys
import os
import asyncio

# Ajouter le répertoire courant au chemin Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("LABYRINTHE PYTHON - Redéveloppement complet")
print("=" * 60)
print()

def check_dependencies():
    """Vérifie que Pygame est installé."""
    try:
        import pygame
        print(f"✓ Pygame version {pygame.version.ver} installée")
        return True
    except ImportError:
        print("✗ Pygame n'est pas installé")
        print("Installez-le avec: pip install pygame==2.5.2")
        return False

def check_assets():
    """Vérifie la présence des assets."""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    if not os.path.exists(assets_dir):
        print(f"✗ Dossier assets non trouvé: {assets_dir}")
        print("  Le jeu utilisera des formes géométriques à la place.")
        return False
    
    # Vérifier quelques fichiers essentiels
    essential_files = [
        "tile_0001.png",  # Mur
        "tile_0096.png",  # Joueur
        "tile_0045.png",  # Sortie
    ]
    
    missing = []
    for filename in essential_files:
        path = os.path.join(assets_dir, filename)
        if not os.path.exists(path):
            missing.append(filename)
    
    if missing:
        print(f"✗ {len(missing)} assets essentiels manquants:")
        for filename in missing:
            print(f"  - {filename}")
        print("  Le jeu utilisera des formes géométriques à la place.")
        return False
    
    print("✓ Assets trouvés")
    return True

async def main():
    """Fonction principale asynchrone."""
    # Vérifications
    if not check_dependencies():
        print("\nInstallation des dépendances requises...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame==2.5.2"])
            print("✓ Pygame installé avec succès")
        except Exception as e:
            print(f"✗ Échec de l'installation: {e}")
            print("Veuillez installer Pygame manuellement.")
            input("Appuyez sur Entrée pour quitter...")
            return
    
    check_assets()
    
    print()
    print("Configuration du jeu:")
    print("  - Résolution: 800x600")
    print("  - FPS: 30")
    print("  - Taille des tiles: 48x48")
    print("  - Contrôles: Flèches ou ZQSD")
    print("  - Échap: Menu/Pause")
    print("  - P: Pause")
    print()
    print("Lancement du jeu...")
    print("-" * 60)
    
    try:
        # Importer et lancer le jeu
        from game_new import Game
        game = Game()
        await game.run()
        print("\nJeu terminé. Merci d'avoir joué !")
    except Exception as e:
        print(f"\n✗ Erreur lors de l'exécution du jeu: {e}")
        import traceback
        traceback.print_exc()
        input("Appuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    asyncio.run(main())
