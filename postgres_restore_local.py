#!/usr/bin/env python3
"""
Script de restauration des données depuis une sauvegarde locale vers PostgreSQL
Restaure les fichiers JSON depuis un dossier de sauvegarde vers PostgreSQL
"""

import os
import psycopg2
import json
import glob
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_postgres_connection():
    """Établit une connexion à PostgreSQL."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion PostgreSQL: {e}")
        return None

def list_backup_folders():
    """Liste tous les dossiers de sauvegarde disponibles."""
    backup_folders = glob.glob("backup_postgres_*")
    backup_folders.sort(reverse=True)  # Plus récent en premier
    
    if not backup_folders:
        print("❌ Aucun dossier de sauvegarde trouvé")
        return None
    
    print("📁 Dossiers de sauvegarde disponibles:")
    for i, folder in enumerate(backup_folders, 1):
        # Lire les infos si disponibles
        info_file = os.path.join(folder, "_backup_info.json")
        if os.path.exists(info_file):
            try:
                with open(info_file, 'r') as f:
                    info = json.load(f)
                date_str = info.get('backup_date', 'Date inconnue')
                files_count = info.get('files_saved', 'Inconnu')
                print(f"  {i}. {folder} - {date_str} - {files_count} fichiers")
            except:
                print(f"  {i}. {folder}")
        else:
            print(f"  {i}. {folder}")
    
    return backup_folders

def restore_from_backup(conn, backup_folder):
    """Restaure les données depuis un dossier de sauvegarde vers PostgreSQL."""
    cursor = conn.cursor()
    
    # Vérifier que la table json_backups existe
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS json_backups (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) UNIQUE NOT NULL,
                content TEXT NOT NULL,
                backup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ Table json_backups prête")
    except Exception as e:
        print(f"❌ Erreur création table: {e}")
        return 0
    
    # Lister tous les fichiers JSON dans le dossier
    json_files = glob.glob(os.path.join(backup_folder, "*.json"))
    json_files = [f for f in json_files if not os.path.basename(f).startswith('_')]  # Exclure _backup_info.json
    
    if not json_files:
        print(f"❌ Aucun fichier JSON trouvé dans {backup_folder}")
        return 0
    
    restored_count = 0
    
    for file_path in json_files:
        filename = os.path.basename(file_path)
        
        try:
            # Lire le fichier JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Valider le JSON
            json.loads(content)
            
            # Insérer ou mettre à jour dans PostgreSQL
            cursor.execute("""
                INSERT INTO json_backups (filename, content, backup_date)
                VALUES (%s, %s, %s)
                ON CONFLICT (filename) 
                DO UPDATE SET 
                    content = EXCLUDED.content,
                    backup_date = EXCLUDED.backup_date
            """, (filename, content, datetime.now()))
            
            print(f"✅ {filename} restauré")
            restored_count += 1
            
        except json.JSONDecodeError as e:
            print(f"❌ Fichier JSON invalide {filename}: {e}")
        except Exception as e:
            print(f"❌ Erreur restauration {filename}: {e}")
    
    # Valider les changements
    conn.commit()
    cursor.close()
    
    return restored_count

def main():
    """Fonction principale de restauration."""
    print("🔄 RESTAURATION DEPUIS SAUVEGARDE LOCALE")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier la variable DATABASE_URL
    if not DATABASE_URL:
        print("❌ ERREUR: Variable DATABASE_URL non définie")
        return
    
    # Lister les sauvegardes disponibles
    backup_folders = list_backup_folders()
    if not backup_folders:
        return
    
    # Demander à l'utilisateur de choisir
    try:
        choice = input("\n👆 Entrez le numéro du dossier à restaurer (ou 'q' pour quitter): ").strip()
        
        if choice.lower() == 'q':
            print("❌ Restauration annulée")
            return
        
        folder_index = int(choice) - 1
        if folder_index < 0 or folder_index >= len(backup_folders):
            print("❌ Numéro invalide")
            return
        
        selected_folder = backup_folders[folder_index]
        
    except (ValueError, KeyboardInterrupt):
        print("❌ Sélection annulée")
        return
    
    # Confirmation
    print(f"\n⚠️  Vous allez restaurer depuis: {selected_folder}")
    confirm = input("🤔 Continuer ? Cette action va écraser les données actuelles (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Restauration annulée")
        return
    
    # Connexion à PostgreSQL
    print("🔗 Connexion à PostgreSQL...")
    conn = get_postgres_connection()
    if not conn:
        return
    
    print("✅ Connexion PostgreSQL établie")
    
    # Restauration
    print(f"📤 Restauration depuis {selected_folder}...")
    restored_count = restore_from_backup(conn, selected_folder)
    
    # Fermer la connexion
    conn.close()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DE LA RESTAURATION:")
    print(f"✅ Fichiers restaurés: {restored_count}")
    print(f"📁 Depuis: {selected_folder}")
    print("🔄 Vos données ont été restaurées dans PostgreSQL !")
    print("=" * 50)

if __name__ == "__main__":
    main()
