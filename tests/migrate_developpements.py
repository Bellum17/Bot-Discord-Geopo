#!/usr/bin/env python3
"""
Script pour migrer l'ancienne structure de développements vers la nouvelle.
Ancienne: developpements[guild][role][categorie] = [liste]
Nouvelle: developpements[guild][role] = [liste avec dev.categorie]
"""

import json
import os
import shutil
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DEVELOPPEMENTS_FILE = os.path.join(DATA_DIR, "developpements.json")

def load_developpements():
    if os.path.exists(DEVELOPPEMENTS_FILE):
        with open(DEVELOPPEMENTS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_developpements(data):
    with open(DEVELOPPEMENTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def migrate_developpements():
    """
    Migre l'ancienne structure vers la nouvelle
    """
    print("🔄 Migration des développements technologiques...")
    
    # Charger les données actuelles
    developpements = load_developpements()
    
    if not developpements:
        print("❌ Aucun fichier de développements trouvé")
        return
    
    # Créer une sauvegarde
    backup_file = DEVELOPPEMENTS_FILE.replace(".json", f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    shutil.copy2(DEVELOPPEMENTS_FILE, backup_file)
    print(f"📄 Sauvegarde créée : {backup_file}")
    
    migrations_effectuees = 0
    
    for guild_id in developpements:
        for role_id in developpements[guild_id]:
            role_data = developpements[guild_id][role_id]
            
            # Vérifier si c'est l'ancienne structure (dict avec catégories)
            if isinstance(role_data, dict):
                print(f"🔧 Migration guild {guild_id}, role {role_id}")
                
                # Créer la nouvelle liste
                nouvelle_liste = []
                
                for categorie, dev_list in role_data.items():
                    if isinstance(dev_list, list):
                        for dev in dev_list:
                            if isinstance(dev, dict):
                                # S'assurer que la catégorie est incluse
                                if "categorie" not in dev:
                                    dev["categorie"] = categorie
                                nouvelle_liste.append(dev)
                
                # Remplacer l'ancienne structure
                developpements[guild_id][role_id] = nouvelle_liste
                migrations_effectuees += 1
                
            elif isinstance(role_data, list):
                # Déjà la nouvelle structure, vérifier que les catégories sont présentes
                for dev in role_data:
                    if isinstance(dev, dict) and "categorie" not in dev:
                        # Essayer de deviner la catégorie si elle manque
                        dev["categorie"] = "vehicules_terrestres"  # Par défaut
                        print(f"⚠️  Catégorie manquante ajoutée pour {dev.get('nom', 'Inconnu')}")
    
    # Sauvegarder les données migrées
    save_developpements(developpements)
    
    print(f"✅ Migration terminée ! {migrations_effectuees} rôles migrés")
    
    # Afficher un résumé
    total_devs = 0
    for guild_id in developpements:
        for role_id in developpements[guild_id]:
            if isinstance(developpements[guild_id][role_id], list):
                total_devs += len(developpements[guild_id][role_id])
    
    print(f"📊 Total de développements : {total_devs}")

if __name__ == "__main__":
    migrate_developpements()
