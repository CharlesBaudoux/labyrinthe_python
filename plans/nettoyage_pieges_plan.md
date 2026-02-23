# Plan de nettoyage des pièges et correction de l'affichage des coffres

## Objectifs
1. Supprimer toutes les références aux pièges (TRAP) du système
2. Corriger l'affichage des coffres pour qu'ils soient visibles sur la carte
3. Augmenter le nombre de coffres par difficulté

## Modifications détaillées

### 1. config_new.py
- [ ] Supprimer `CellType.TRAP` de l'énumération `CellType` (ligne 156)
- [ ] Mettre à jour `DIFFICULTY_SETTINGS` pour chaque difficulté :
  - Easy: 2 coffres (actuellement 1)
  - Medium: 4 coffres (actuellement 2)
  - Hard: 6 coffres (actuellement 3)
  - Extreme: 8 coffres (actuellement 5)
- [ ] Vérifier qu'il n'y a pas d'entrée "trap" dans `ASSET_MAPPING` ou `FALLBACK_COLORS` (déjà absent)
- [ ] Vérifier que `ItemType` n'a pas de valeur `TRAP` (déjà absent)

### 2. maze_new.py
- [ ] Supprimer tout commentaire faisant référence aux pièges (lignes 207-208)
- [ ] Vérifier que la méthode `place_items` ne génère pas de pièges (déjà le cas)
- [ ] Vérifier que `self.chests` est utilisé correctement et que les cases restent `CellType.FLOOR`
- [ ] Confirmer que `is_walkable` ne traite pas `CellType.TRAP` différemment (à vérifier)

### 3. entities_new.py
- [ ] Mettre à jour le docstring de la classe `Item` : "Représente un objet interactif (potion, coffre)."
- [ ] Vérifier que `create_items_from_maze` ne crée pas d'items de type `TRAP` (déjà le cas)
- [ ] Laisser les références à "trap" dans `open_chest` (ce sont des résultats de coffre, pas des types d'item)

### 4. game_new.py
- [ ] Vérifier que la logique de traitement des résultats "trap" des coffres reste intacte
- [ ] S'assurer qu'aucun code ne fait référence à `ItemType.TRAP` ou `CellType.TRAP`

### 5. renderer_new.py (à vérifier)
- [ ] Vérifier qu'il n'y a pas de rendu spécial pour `CellType.TRAP`
- [ ] S'assurer que les coffres sont bien rendus avec l'asset `tile_0089.png`

### 6. Fichiers de test
- [ ] Mettre à jour `test_interactions.py` pour supprimer les références commentées aux pièges
- [ ] Mettre à jour les tests pour refléter les nouveaux nombres de coffres

## Validation
- [ ] Exécuter les tests existants pour s'assurer qu'aucune régression n'est introduite
- [ ] Tester manuellement que les coffres sont visibles sur la carte
- [ ] Vérifier que le jeu se lance sans erreur