# Plan de modifications pour compatibilité Pygbag (WebAssembly)

## Problème identifié
Le jeu se fige sur l'écran "Veuillez cliquer/toucher la page" du navigateur parce que la boucle principale n'est pas asynchrone, ce qui bloque le thread du navigateur.

## Solution
Intégrer `asyncio` dans les fichiers suivants pour rendre la boucle principale asynchrone.

## 1. Modifications dans `game_new.py`

### 1.1. Ajouter l'import asyncio
```python
import pygame
import time
import json
import os
import asyncio  # <-- Ajouter cette ligne
from config_new import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLORS, get_controls, DIFFICULTY_SETTINGS,
    GameState, Difficulty, CellType, ItemType, DIRECTIONS, HIGHSCORE_FILE
)
```

### 1.2. Modifier la méthode `run()` pour la rendre asynchrone
```python
    async def run(self):  # <-- Ajouter 'async'
        """Boucle principale du jeu."""
        print(">>> Game: Démarrage de la boucle principale")
        
        while self.running:
            events = self.handle_events()
            
            if not self.running:
                break
            
            self.update()
            self.render()
            
            self.clock.tick(FPS)
            await asyncio.sleep(0)  # <-- Ajouter cette ligne cruciale
```

## 2. Modifications dans `main_new.py`

### 2.1. Ajouter l'import asyncio
```python
#!/usr/bin/env python3
"""
Point d'entrée principal du jeu de labyrinthe - Version révisée.
"""

import sys
import os
import asyncio  # <-- Ajouter cette ligne
```

### 2.2. Modifier la fonction `main()` pour la rendre asynchrone
```python
async def main():  # <-- Ajouter 'async'
    """Fonction principale asynchrone."""
    print("=" * 60)
    print("LABYRINTHE PYTHON - Redéveloppement complet")
    print("=" * 60)
    print()
    
    # ... [le reste du code inchangé] ...
    
    try:
        # Importer et lancer le jeu
        from game_new import Game
        game = Game()
        await game.run()  # <-- Ajouter 'await'
        print("\nJeu terminé. Merci d'avoir joué !")
    except Exception as e:
        print(f"\n✗ Erreur lors de l'exécution du jeu: {e}")
        import traceback
        traceback.print_exc()
        input("Appuyez sur Entrée pour quitter...")
```

### 2.3. Modifier le point d'entrée
```python
if __name__ == "__main__":
    asyncio.run(main())  # <-- Remplacer main() par asyncio.run(main())
```

## 3. Vérifications supplémentaires

### 3.1. Vérifier que `FPS` est défini dans `config_new.py`
Le fichier `config_new.py` doit contenir :
```python
FPS = 60
```

### 3.2. S'assurer qu'aucune autre boucle bloquante n'existe
- Vérifier les fichiers `entities_new.py`, `maze_new.py`, `renderer_new.py` pour des boucles `while` sans `await`.

## 4. Étapes de test

1. Appliquer les modifications ci-dessus
2. Lancer un test local avec Python pour vérifier que le jeu fonctionne toujours
3. Tester avec Pygbag en exécutant :
   ```bash
   pygbag --build mon_projet_labyrinthe
   ```
4. Ouvrir le navigateur et vérifier que le jeu ne se fige plus

## 5. Risques potentiels

- **Rétrocompatibilité** : Les modifications sont compatibles avec Python 3.7+ et ne cassent pas l'exécution locale.
- **Performances** : `await asyncio.sleep(0)` libère le contrôle au navigateur sans impact significatif sur les performances.
- **Gestion des événements** : Vérifier que `pygame.event.get()` fonctionne correctement dans un contexte asynchrone.

## 6. Fichiers à modifier

- [x] `game_new.py` - Ajout import asyncio et modification de `run()`
- [x] `main_new.py` - Ajout import asyncio et modification de `main()` et point d'entrée
- [ ] `config_new.py` - Vérifier la présence de `FPS` (déjà présent)

## 7. Notes d'implémentation

- L'ajout de `await asyncio.sleep(0)` après `self.clock.tick(FPS)` est **crucial** : il permet au navigateur de reprendre le contrôle et d'exécuter d'autres tâches.
- La méthode `run()` doit être appelée avec `await` depuis `main()`.
- Le point d'entrée `asyncio.run(main())` est nécessaire pour démarrer la boucle d'événements asyncio.

## 8. Validation

Après modifications, le jeu devrait :
- Démarrer normalement en local
- Fonctionner dans le navigateur via Pygbag sans figer
- Conserver toutes les fonctionnalités existantes (menu, gameplay, collisions, etc.)

---

**Prochaines étapes** : Basculer en mode Code pour appliquer ces modifications.