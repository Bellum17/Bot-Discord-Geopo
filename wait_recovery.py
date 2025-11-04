#!/usr/bin/env python3
"""
Script de surveillance simple pour PostgreSQL Railway en récupération
"""

import psycopg2
import time
from datetime import datetime

DATABASE_URL = "postgresql://postgres:xDzILQmEyYVdjIYZDdZgjZCNkWokewLB@centerbeam.proxy.rlwy.net:28022/railway"

def wait_for_recovery():
    """Attend la fin de la récupération PostgreSQL."""
    print("⏳ ATTENTE DE LA RÉCUPÉRATION POSTGRESQL")
    print("=" * 45)
    print(f"🕐 Démarrage: {datetime.now().strftime('%H:%M:%S')}")
    print("📝 D'après les logs: récupération automatique en cours")
    print("⏱️  Estimation: 5-15 minutes")
    print()
    
    start_time = time.time()
    attempt = 0
    
    while True:
        attempt += 1
        current_time = datetime.now().strftime('%H:%M:%S')
        elapsed = int(time.time() - start_time)
        elapsed_min = elapsed // 60
        elapsed_sec = elapsed % 60
        
        print(f"🔄 [{current_time}] Test #{attempt} (⏱️ {elapsed_min}m{elapsed_sec:02d}s)... ", end="", flush=True)
        
        try:
            # Test de connexion rapide
            conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
            
            # Test de requête simple
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                
                # Vérifier l'état de récupération
                cur.execute("SELECT pg_is_in_recovery()")
                in_recovery = cur.fetchone()[0]
                
                if in_recovery:
                    print("🔄 Encore en récupération...")
                else:
                    print("✅ RÉCUPÉRATION TERMINÉE !")
                    print(f"\n🎉 PostgreSQL est maintenant opérationnel !")
                    print(f"⏱️  Temps total: {elapsed_min}m{elapsed_sec:02d}s")
                    print(f"🚀 Vous pouvez maintenant lancer vos backups")
                    conn.close()
                    return True
            
            conn.close()
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            
            if "not yet accepting connections" in error_msg:
                print("⏳ Récupération en cours...")
            elif "database system is starting up" in error_msg:
                print("🔄 Démarrage en cours...")
            elif "timeout expired" in error_msg:
                print("⏱️ Timeout (récupération lente)...")
            else:
                print(f"❌ Erreur: {error_msg[:50]}...")
                
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
        
        # Attendre avant le prochain test
        if elapsed < 300:  # 5 premières minutes: test toutes les 30s
            time.sleep(30)
        else:  # Après 5 minutes: test toutes les 60s
            time.sleep(60)
        
        # Arrêt automatique après 30 minutes
        if elapsed > 1800:
            print(f"\n⏰ Timeout après 30 minutes")
            print("💡 La récupération prend plus de temps que prévu")
            print("📞 Contactez le support Railway si nécessaire")
            return False

def main():
    """Fonction principale."""
    print("🔍 MONITORING RÉCUPÉRATION POSTGRESQL RAILWAY")
    print("📋 Basé sur les logs: automatic recovery in progress")
    print("⏹️  Ctrl+C pour arrêter\n")
    
    try:
        success = wait_for_recovery()
        
        if success:
            print(f"\n💾 PROCHAINES ÉTAPES:")
            print("1. Tester: python3 check_postgres.py")
            print("2. Backup: python3 backup_json_to_postgres.py")
            print("3. Vérifier les données restaurées")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Surveillance interrompue par l'utilisateur")
        print("💡 Vous pouvez relancer le script plus tard")

if __name__ == "__main__":
    main()
