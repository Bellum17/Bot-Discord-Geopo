#!/usr/bin/env python3
"""
Test pour vérifier le nouveau système de nom des centres technologiques.
"""

import sys
import os
import json
from pathlib import Path

# Ajouter le répertoire parent au path pour importer le module
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

def load_centres_tech():
    """Charge les données des centres technologiques."""
    try:
        with open(parent_dir / "data" / "centres_tech.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_centres_tech(data):
    """Sauvegarde les données des centres technologiques."""
    with open(parent_dir / "data" / "centres_tech.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_centre_identifier(centre):
    """Retourne l'identifiant d'un centre (nom si existe, sinon localisation)."""
    return centre.get("nom", centre.get("localisation", ""))

def test_centre_avec_nom():
    """Test la création d'un centre avec nom et localisation séparés."""
    print("=== Test Centre avec Nom ===")
    
    centres_data = load_centres_tech()
    guild_id = "123456_test"
    pays_id = "789012_test"
    
    if guild_id not in centres_data:
        centres_data[guild_id] = {}
    if pays_id not in centres_data[guild_id]:
        centres_data[guild_id][pays_id] = []
    
    # Créer un nouveau centre avec nom et localisation
    nouveau_centre = {
        "nom": "Centre Atlantique",
        "localisation": "Brest",
        "specialisation": "Marine",
        "niveau": 1,
        "emplacements_max": 2,
        "developpements": [],
        "date_creation": 1234567890
    }
    
    centres_data[guild_id][pays_id].append(nouveau_centre)
    save_centres_tech(centres_data)
    
    print(f"✅ Centre créé: {nouveau_centre['nom']} à {nouveau_centre['localisation']}")
    print(f"   Identifiant: {get_centre_identifier(nouveau_centre)}")

def test_compatibilite_ancien():
    """Test la compatibilité avec un ancien centre (sans nom)."""
    print("\n=== Test Compatibilité Ancien Centre ===")
    
    centres_data = load_centres_tech()
    guild_id = "123456_test"
    pays_id = "789012_test"
    
    # Créer un ancien centre (sans nom)
    ancien_centre = {
        "localisation": "Base Alpha",
        "specialisation": "Terrestre",
        "niveau": 2,
        "emplacements_max": 3,
        "developpements": [],
        "date_creation": 1234567800
    }
    
    centres_data[guild_id][pays_id].append(ancien_centre)
    save_centres_tech(centres_data)
    
    print(f"✅ Ancien centre créé: {ancien_centre['localisation']}")
    print(f"   Identifiant: {get_centre_identifier(ancien_centre)}")

def test_recherche_centres():
    """Test la recherche de centres par identifiant."""
    print("\n=== Test Recherche Centres ===")
    
    centres_data = load_centres_tech()
    guild_id = "123456_test"
    pays_id = "789012_test"
    
    if guild_id not in centres_data or pays_id not in centres_data[guild_id]:
        print("❌ Aucun centre trouvé pour les tests")
        return
    
    centres = centres_data[guild_id][pays_id]
    
    # Test recherche par nom
    for centre in centres:
        identifiant = get_centre_identifier(centre)
        print(f"Centre trouvé: {identifiant}")
        
        # Simuler la recherche (comme dans amelioration)
        for c in centres:
            if get_centre_identifier(c).lower() == identifiant.lower():
                print(f"✅ Recherche réussie pour: {identifiant}")
                break

def afficher_tous_centres():
    """Affiche tous les centres pour vérification."""
    print("\n=== Tous les Centres ===")
    
    centres_data = load_centres_tech()
    
    for guild_id, guilds in centres_data.items():
        if "test" not in guild_id:
            continue
            
        for pays_id, centres in guilds.items():
            print(f"\nPays {pays_id}:")
            for i, centre in enumerate(centres, 1):
                nom = centre.get("nom", "Pas de nom")
                localisation = centre.get("localisation", "Pas de localisation")
                identifiant = get_centre_identifier(centre)
                
                print(f"  {i}. {identifiant}")
                if centre.get("nom") and centre.get("localisation"):
                    print(f"     📍 Localisation: {localisation}")
                print(f"     🔬 Spécialisation: {centre['specialisation']}")
                print(f"     📊 Niveau: {centre['niveau']}")

def cleanup_test():
    """Nettoie les données de test."""
    print("\n=== Nettoyage ===")
    
    centres_data = load_centres_tech()
    
    # Supprimer les données de test
    keys_to_remove = [k for k in centres_data.keys() if "test" in k]
    for key in keys_to_remove:
        del centres_data[key]
    
    save_centres_tech(centres_data)
    print("✅ Données de test supprimées")

if __name__ == "__main__":
    print("Test du système de noms des centres technologiques")
    print("=" * 50)
    
    try:
        test_centre_avec_nom()
        test_compatibilite_ancien()
        test_recherche_centres()
        afficher_tous_centres()
        
        print("\n" + "=" * 50)
        print("✅ Tous les tests terminés avec succès!")
        
        # Demander si on veut nettoyer
        response = input("\nSupprimer les données de test? (o/N): ").strip().lower()
        if response == 'o':
            cleanup_test()
        
    except Exception as e:
        print(f"❌ Erreur durante les tests: {e}")
        import traceback
        traceback.print_exc()
