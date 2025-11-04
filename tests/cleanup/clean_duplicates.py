#!/usr/bin/env python3
"""
Script pour nettoyer les développements en double
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DEVELOPPEMENTS_FILE = os.path.join(DATA_DIR, "developpements.json")

def clean_duplicates():
    print("🧹 Nettoyage des développements en double")
    print("=" * 50)
    
    if not os.path.exists(DEVELOPPEMENTS_FILE):
        print("❌ Aucun fichier de développements trouvé")
        return
    
    # Charger les données
    with open(DEVELOPPEMENTS_FILE, "r") as f:
        data = json.load(f)
    
    total_removed = 0
    
    for guild_id in data:
        for role_id in data[guild_id]:
            if isinstance(data[guild_id][role_id], list):
                original_count = len(data[guild_id][role_id])
                
                # Créer un dictionnaire pour détecter les doublons
                seen = {}
                unique_devs = []
                
                for dev in data[guild_id][role_id]:
                    if isinstance(dev, dict):
                        # Créer une clé unique basée sur nom + technologie
                        key = f"{dev.get('nom', '')}-{dev.get('technologie', '')}"
                        
                        if key not in seen:
                            seen[key] = True
                            unique_devs.append(dev)
                        else:
                            print(f"🗑️  Doublon trouvé: {dev.get('nom', 'Inconnu')} ({dev.get('technologie', 'Inconnue')})")
                            total_removed += 1
                
                # Remplacer par la liste nettoyée
                data[guild_id][role_id] = unique_devs
                
                if original_count != len(unique_devs):
                    print(f"📊 Guild {guild_id}, Role {role_id}: {original_count} → {len(unique_devs)} développements")
    
    # Sauvegarder si des changements ont été faits
    if total_removed > 0:
        # Créer une sauvegarde
        backup_file = DEVELOPPEMENTS_FILE.replace(".json", f"_backup_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(backup_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"📄 Sauvegarde créée: {backup_file}")
        
        # Sauvegarder les données nettoyées
        with open(DEVELOPPEMENTS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ {total_removed} doublons supprimés")
    else:
        print("✅ Aucun doublon trouvé")

if __name__ == "__main__":
    clean_duplicates()
