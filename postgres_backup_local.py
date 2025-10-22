#!/usr/bin/env python3
"""
Script de sauvegarde locale des données PostgreSQL
Récupère toutes les données depuis PostgreSQL et les sauvegarde dans un dossier local
"""

import os
import psycopg2
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def create_backup_folder():
    """Crée un dossier de sauvegarde avec timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = f"backup_postgres_{timestamp}"
    
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    
    return backup_folder

def get_postgres_connection():
    """Établit une connexion à PostgreSQL."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion PostgreSQL: {e}")
        return None

def backup_json_data(conn, backup_folder):
    """Récupère et sauvegarde toutes les données JSON depuis PostgreSQL."""
    cursor = conn.cursor()
    
    try:
        # Récupérer tous les fichiers JSON sauvegardés
        cursor.execute("SELECT filename, content, backup_date FROM json_backups ORDER BY filename")
        results = cursor.fetchall()
        
        if not results:
            print("❌ Aucune donnée JSON trouvée dans PostgreSQL")
            return 0
        
        saved_count = 0
        
        for filename, content, backup_date in results:
            try:
                # Sauvegarder le fichier JSON
                file_path = os.path.join(backup_folder, filename)
                
                # Valider le JSON avant sauvegarde
                json_data = json.loads(content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ {filename} sauvegardé ({len(content)} caractères)")
                saved_count += 1
                
            except json.JSONDecodeError as e:
                print(f"❌ Erreur JSON pour {filename}: {e}")
            except Exception as e:
                print(f"❌ Erreur sauvegarde {filename}: {e}")
        
        return saved_count
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données: {e}")
        return 0
    finally:
        cursor.close()

def create_backup_info(backup_folder, saved_count):
    """Crée un fichier d'information sur la sauvegarde."""
    info = {
        "backup_date": datetime.now().isoformat(),
        "database_url": DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else "masqué",
        "files_saved": saved_count,
        "backup_folder": backup_folder,
        "description": "Sauvegarde locale des données PostgreSQL"
    }
    
    info_path = os.path.join(backup_folder, "_backup_info.json")
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Informations de sauvegarde créées: {info_path}")

def main():
    """Fonction principale de sauvegarde."""
    print("🚀 DÉBUT DE LA SAUVEGARDE POSTGRESQL LOCALE")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier la variable DATABASE_URL
    if not DATABASE_URL:
        print("❌ ERREUR: Variable DATABASE_URL non définie")
        print("💡 Vérifiez votre fichier .env")
        return
    
    # Créer le dossier de sauvegarde
    backup_folder = create_backup_folder()
    print(f"📁 Dossier de sauvegarde: {backup_folder}")
    
    # Connexion à PostgreSQL
    print("🔗 Connexion à PostgreSQL...")
    conn = get_postgres_connection()
    if not conn:
        return
    
    print("✅ Connexion PostgreSQL établie")
    
    # Sauvegarde des données
    print("💾 Récupération des données JSON...")
    saved_count = backup_json_data(conn, backup_folder)
    
    # Fermer la connexion
    conn.close()
    
    # Créer les informations de sauvegarde
    create_backup_info(backup_folder, saved_count)
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DE LA SAUVEGARDE:")
    print(f"✅ Fichiers sauvegardés: {saved_count}")
    print(f"📁 Dossier: {backup_folder}")
    print(f"📏 Taille du dossier: {get_folder_size(backup_folder)}")
    print("🔒 Vos données PostgreSQL sont maintenant sauvegardées localement !")
    print("=" * 50)

def get_folder_size(folder_path):
    """Calcule la taille d'un dossier."""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        
        # Conversion en unités lisibles
        if total_size < 1024:
            return f"{total_size} B"
        elif total_size < 1024 * 1024:
            return f"{total_size / 1024:.1f} KB"
        else:
            return f"{total_size / (1024 * 1024):.1f} MB"
    except:
        return "Inconnu"

if __name__ == "__main__":
    main()
