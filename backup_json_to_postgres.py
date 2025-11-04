import os
import psycopg2
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")  # Mets l'URL Railway dans tes variables d'environnement
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def get_conn(max_retries=5, retry_delay=10):
    """
    Connexion à la base de données avec système de retry.
    """
    for attempt in range(max_retries):
        try:
            print(f"🔄 Tentative de connexion {attempt + 1}/{max_retries}...")
            conn = psycopg2.connect(DATABASE_URL)
            print("✅ Connexion réussie à PostgreSQL")
            return conn
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            
            if "not yet accepting connections" in error_msg:
                print(f"⏳ Base de données en cours de récupération...")
                if attempt < max_retries - 1:
                    print(f"   Attente de {retry_delay} secondes avant nouvelle tentative...")
                    time.sleep(retry_delay)
                    retry_delay *= 1.5  # Augmente progressivement le délai
                else:
                    print("❌ La base de données n'est toujours pas prête après toutes les tentatives")
                    raise
            elif "could not connect to server" in error_msg:
                print(f"🔌 Problème de connectivité réseau...")
                if attempt < max_retries - 1:
                    print(f"   Nouvelle tentative dans {retry_delay} secondes...")
                    time.sleep(retry_delay)
                else:
                    print("❌ Impossible de se connecter au serveur")
                    raise
            else:
                print(f"❌ Erreur de connexion inattendue: {error_msg}")
                raise
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            raise

def check_database_status():
    """
    Vérifie l'état de la base de données.
    """
    try:
        with get_conn(max_retries=1) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            print("✅ Base de données opérationnelle")
            return True
    except Exception as e:
        print(f"❌ Base de données non disponible: {e}")
        return False

def save_json_file_to_db(filename):
    """
    Sauvegarde un fichier JSON en base avec gestion d'erreurs.
    """
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"⚠️ Fichier {filename} non trouvé.")
        return False
    
    try:
        print(f"📁 Lecture du fichier {filename}...")
        with open(filepath, "r", encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier que c'est du JSON valide
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            print(f"❌ Fichier {filename} n'est pas un JSON valide: {e}")
            return False
        
        print(f"💾 Sauvegarde de {filename} en base...")
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO json_backups (filename, content, backup_date)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (filename) DO UPDATE SET 
                        content = EXCLUDED.content,
                        backup_date = EXCLUDED.backup_date
                """, (filename, content, datetime.now()))
                conn.commit()
        
        print(f"✅ Backup de {filename} effectué avec succès")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erreur de connexion lors du backup de {filename}: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du backup de {filename}: {e}")
        return False

def main():
    """
    Fonction principale avec gestion d'erreurs complète.
    """
    print("🚀 DÉBUT DU BACKUP JSON VERS POSTGRESQL")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier la disponibilité de DATABASE_URL
    if not DATABASE_URL:
        print("❌ ERREUR: Variable d'environnement DATABASE_URL non définie")
        print("💡 Définissez DATABASE_URL avec votre URL de connexion PostgreSQL")
        return
    
    # Vérifier l'existence du dossier data
    if not os.path.exists(DATA_DIR):
        print(f"❌ ERREUR: Dossier {DATA_DIR} non trouvé")
        return
    
    # Lister les fichiers JSON
    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    if not json_files:
        print("⚠️ Aucun fichier JSON trouvé dans le dossier data/")
        return
    
    print(f"📋 {len(json_files)} fichiers JSON trouvés:")
    for f in json_files:
        print(f"   • {f}")
    
    # Vérifier l'état de la base de données
    print("\n🔍 Vérification de l'état de la base de données...")
    if not check_database_status():
        print("\n⏳ Attente que la base de données soit prête...")
        print("💡 La base de données semble être en cours de récupération")
        print("   Cela peut prendre quelques minutes...")
        
        # Attendre un peu plus longtemps
        for i in range(6):
            print(f"   Vérification dans {30-i*5} secondes... ({i+1}/6)")
            time.sleep(5)
            if check_database_status():
                break
        else:
            print("❌ La base de données n'est toujours pas disponible")
            print("💡 Réessayez dans quelques minutes")
            return
    
    # Effectuer les backups
    print(f"\n💾 Début des backups...")
    success_count = 0
    failed_count = 0
    
    for filename in json_files:
        if save_json_file_to_db(filename):
            success_count += 1
        else:
            failed_count += 1
    
    # Résumé final
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU BACKUP:")
    print(f"✅ Réussis: {success_count}")
    print(f"❌ Échecs: {failed_count}")
    print(f"📁 Total: {len(json_files)}")
    
    if failed_count == 0:
        print("\n🎉 Tous les backups ont réussi !")
    else:
        print(f"\n⚠️ {failed_count} backup(s) ont échoué")
    
    print(f"🕐 Terminé: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()