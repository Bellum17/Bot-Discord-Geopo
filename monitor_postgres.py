#!/usr/bin/env python3
"""
Surveillance automatique de l'état PostgreSQL Railway
"""

import psycopg2
import time
from datetime import datetime

DATABASE_URL = "postgresql://postgres:xDzILQmEyYVdjIYZDdZgjZCNkWokewLB@centerbeam.proxy.rlwy.net:28022/railway"

def monitor_postgres():
    """Surveille l'état de PostgreSQL en continu."""
    print("📡 SURVEILLANCE POSTGRESQL RAILWAY")
    print("=" * 45)
    print(f"🕐 Début: {datetime.now().strftime('%H:%M:%S')}")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter")
    print()
    
    attempt = 0
    
    while True:
        attempt += 1
        current_time = datetime.now().strftime('%H:%M:%S')
        
        try:
            print(f"🔄 [{current_time}] Test #{attempt}... ", end="", flush=True)
            
            conn = psycopg2.connect(DATABASE_URL)
            
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            
            conn.close()
            
            print("✅ CONNEXION RÉUSSIE !")
            print(f"🎉 PostgreSQL est maintenant disponible !")
            print(f"⏱️  Récupération terminée après {attempt} tentatives")
            break
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            
            if "not yet accepting connections" in error_msg:
                print("🔄 Toujours en récupération...")
            elif "could not connect" in error_msg:
                print("🔌 Problème de connexion...")
            else:
                print("❌ Autre erreur...")
            
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Surveillance arrêtée par l'utilisateur")
            print(f"📊 {attempt} tentatives effectuées")
            break
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # Attendre 30 secondes avant le prochain test
        time.sleep(30)

if __name__ == "__main__":
    try:
        monitor_postgres()
    except KeyboardInterrupt:
        print("\n👋 Surveillance terminée")
