#!/usr/bin/env python3
"""
Gestionnaire de sauvegardes PostgreSQL - Interface unifiée
Permet de sauvegarder et restaurer facilement les données PostgreSQL
"""

import os
import sys
import subprocess
from datetime import datetime

def print_header():
    """Affiche l'en-tête du gestionnaire."""
    print("🗄️  GESTIONNAIRE DE SAUVEGARDES POSTGRESQL")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def print_menu():
    """Affiche le menu principal."""
    print("🔧 OPTIONS DISPONIBLES:")
    print("  1. 💾 Créer une sauvegarde")
    print("  2. 🔄 Restaurer depuis une sauvegarde")
    print("  3. 📋 Lister les sauvegardes")
    print("  4. 🗑️  Nettoyer les anciennes sauvegardes")
    print("  5. ❌ Quitter")
    print()

def create_backup():
    """Lance le script de sauvegarde."""
    print("💾 Création d'une sauvegarde...")
    try:
        result = subprocess.run(['python3', 'postgres_backup_local.py'], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False

def restore_backup():
    """Lance le script de restauration."""
    print("🔄 Restauration depuis une sauvegarde...")
    try:
        result = subprocess.run(['python3', 'postgres_restore_local.py'], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur lors de la restauration: {e}")
        return False

def list_backups():
    """Liste toutes les sauvegardes disponibles."""
    import glob
    import json
    
    backup_folders = glob.glob("backup_postgres_*")
    backup_folders.sort(reverse=True)
    
    if not backup_folders:
        print("📁 Aucune sauvegarde trouvée")
        return
    
    print(f"📁 {len(backup_folders)} sauvegarde(s) trouvée(s):")
    print()
    
    total_size = 0
    
    for i, folder in enumerate(backup_folders, 1):
        # Lire les infos si disponibles
        info_file = os.path.join(folder, "_backup_info.json")
        if os.path.exists(info_file):
            try:
                with open(info_file, 'r') as f:
                    info = json.load(f)
                date_str = info.get('backup_date', 'Date inconnue')
                files_count = info.get('files_saved', 'Inconnu')
                folder_size = info.get('total_size_mb', 0)
                total_size += folder_size
                
                print(f"  {i:2d}. 📁 {folder}")
                print(f"      📅 {date_str}")
                print(f"      📊 {files_count} fichiers - {folder_size:.2f} MB")
                print()
            except:
                print(f"  {i:2d}. 📁 {folder} (infos indisponibles)")
        else:
            print(f"  {i:2d}. 📁 {folder} (infos indisponibles)")
    
    print(f"📊 Taille totale des sauvegardes: {total_size:.2f} MB")

def cleanup_backups():
    """Nettoie les anciennes sauvegardes."""
    import glob
    import shutil
    
    backup_folders = glob.glob("backup_postgres_*")
    backup_folders.sort(reverse=True)
    
    if len(backup_folders) <= 5:
        print("🧹 Pas de nettoyage nécessaire (≤ 5 sauvegardes)")
        return
    
    print(f"🧹 {len(backup_folders)} sauvegardes trouvées")
    print("📝 Politique: Garder les 5 plus récentes")
    
    to_delete = backup_folders[5:]
    
    if not to_delete:
        print("✅ Aucune sauvegarde à supprimer")
        return
    
    print(f"🗑️  {len(to_delete)} sauvegarde(s) à supprimer:")
    for folder in to_delete:
        print(f"   - {folder}")
    
    confirm = input("\n🤔 Confirmer la suppression ? (y/N): ").strip().lower()
    
    if confirm == 'y':
        deleted_count = 0
        for folder in to_delete:
            try:
                shutil.rmtree(folder)
                print(f"✅ {folder} supprimé")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Erreur suppression {folder}: {e}")
        
        print(f"\n🎯 {deleted_count}/{len(to_delete)} sauvegardes supprimées")
    else:
        print("❌ Nettoyage annulé")

def main():
    """Fonction principale du gestionnaire."""
    print_header()
    
    # Vérifier que les scripts existent
    if not os.path.exists('postgres_backup_local.py'):
        print("❌ Script postgres_backup_local.py introuvable")
        return
    
    if not os.path.exists('postgres_restore_local.py'):
        print("❌ Script postgres_restore_local.py introuvable")
        return
    
    while True:
        print_menu()
        
        try:
            choice = input("👆 Votre choix (1-5): ").strip()
            
            if choice == '1':
                print()
                success = create_backup()
                if success:
                    print("\n✅ Sauvegarde terminée avec succès !")
                else:
                    print("\n❌ Erreur lors de la sauvegarde")
                
            elif choice == '2':
                print()
                success = restore_backup()
                if success:
                    print("\n✅ Restauration terminée avec succès !")
                else:
                    print("\n❌ Erreur lors de la restauration")
                
            elif choice == '3':
                print()
                list_backups()
                
            elif choice == '4':
                print()
                cleanup_backups()
                
            elif choice == '5':
                print("👋 Au revoir !")
                break
                
            else:
                print("❌ Choix invalide, veuillez choisir entre 1 et 5")
            
            if choice != '5':
                input("\n📝 Appuyez sur Entrée pour continuer...")
                print("\n" + "=" * 50 + "\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    main()
