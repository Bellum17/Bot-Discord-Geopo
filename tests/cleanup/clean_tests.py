#!/usr/bin/env python3
"""
Script pour nettoyer les fichiers de test (à utiliser avec précaution)
"""

import os
import shutil

def clean_tests():
    """Nettoie le dossier tests (ATTENTION: supprime tous les fichiers)"""
    tests_dir = "tests"
    
    if not os.path.exists(tests_dir):
        print("❌ Le dossier tests n'existe pas")
        return
    
    print("⚠️  ATTENTION: Ce script va SUPPRIMER tous les fichiers de test!")
    print(f"📁 Dossier: {os.path.abspath(tests_dir)}")
    
    # Lister les fichiers
    files = [f for f in os.listdir(tests_dir) if f.endswith('.py')]
    
    if not files:
        print("✅ Aucun fichier .py à supprimer")
        return
    
    print(f"\n📋 Fichiers qui seront supprimés ({len(files)}):")
    for file in sorted(files):
        print(f"   • {file}")
    
    print(f"\n🗑️  Voulez-vous vraiment supprimer ces {len(files)} fichiers de test?")
    confirmation = input("Tapez 'SUPPRIMER' pour confirmer: ")
    
    if confirmation == "SUPPRIMER":
        deleted_count = 0
        for file in files:
            try:
                os.remove(os.path.join(tests_dir, file))
                deleted_count += 1
                print(f"   ✅ {file} supprimé")
            except Exception as e:
                print(f"   ❌ Erreur avec {file}: {e}")
        
        print(f"\n🎉 {deleted_count}/{len(files)} fichiers supprimés")
        
        # Optionnel: supprimer le dossier entier s'il est vide
        remaining_files = os.listdir(tests_dir)
        if len(remaining_files) <= 1:  # Juste le README.md
            print(f"\n🗂️  Supprimer aussi le dossier tests/ ?")
            confirm_folder = input("Tapez 'OUI' pour supprimer le dossier: ")
            if confirm_folder == "OUI":
                shutil.rmtree(tests_dir)
                print("✅ Dossier tests/ supprimé")
    else:
        print("❌ Suppression annulée")

if __name__ == "__main__":
    clean_tests()
