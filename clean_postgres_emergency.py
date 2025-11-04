#!/usr/bin/env python3
"""
Script de nettoyage d'urgence pour PostgreSQL
Pour résoudre les problèmes de connexion et d'espace
"""

import os
import psycopg2
import time
from datetime import datetime, timedelta

DATABASE_URL = os.getenv("DATABASE_URL")

def emergency_cleanup():
    """Nettoyage d'urgence de la base de données."""
    print("🚨 NETTOYAGE D'URGENCE POSTGRESQL")
    print("=" * 50)
    
    max_retries = 10
    for attempt in range(max_retries):
        try:
            print(f"🔄 Tentative de connexion {attempt + 1}/{max_retries}...")
            
            conn = psycopg2.connect(DATABASE_URL)
            print("✅ Connexion établie !")
            
            with conn.cursor() as cur:
                # Vérifier l'espace disque
                print("\n💾 Vérification de l'espace...")
                cur.execute("""
                    SELECT 
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size('"'||schemaname||'"."'||tablename||'"')) as size
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY pg_total_relation_size('"'||schemaname||'"."'||tablename||'"') DESC
                """)
                
                tables = cur.fetchall()
                print("📊 Taille des tables:")
                for schema, table, size in tables:
                    print(f"   • {table}: {size}")
                
                # Nettoyer les anciens logs si ils existent
                print("\n🧹 Nettoyage des anciens logs...")
                try:
                    # Supprimer les logs de plus de 7 jours
                    cutoff_date = datetime.now() - timedelta(days=7)
                    cur.execute("""
                        DELETE FROM json_backups 
                        WHERE backup_date < %s 
                        AND filename LIKE '%log%'
                    """, (cutoff_date,))
                    deleted_logs = cur.rowcount
                    print(f"   🗑️ {deleted_logs} anciens logs supprimés")
                except Exception as e:
                    print(f"   ⚠️ Pas de logs à nettoyer: {e}")
                
                # Vacuum pour récupérer l'espace
                print("\n🔧 Optimisation de la base...")
                cur.execute("VACUUM;")
                print("   ✅ VACUUM effectué")
                
                # Analyser les statistiques
                cur.execute("ANALYZE;")
                print("   ✅ ANALYZE effectué")
                
                # Vérifier l'état après nettoyage
                cur.execute("SELECT COUNT(*) FROM json_backups;")
                backup_count = cur.fetchone()[0]
                print(f"\n📋 Backups restants: {backup_count}")
                
                conn.commit()
                print("✅ Nettoyage terminé avec succès !")
                
            conn.close()
            return True
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            print(f"❌ Erreur: {error_msg}")
            
            if "not yet accepting connections" in error_msg:
                print("⏳ Base en récupération, attente...")
                time.sleep(30)
            else:
                print("❌ Autre erreur de connexion")
                time.sleep(10)
                
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            time.sleep(10)
    
    print("❌ Impossible de se connecter après toutes les tentatives")
    return False

def wait_for_database():
    """Attend que la base de données soit disponible."""
    print("⏳ ATTENTE DE LA DISPONIBILITÉ DE LA BASE")
    print("=" * 50)
    
    max_wait = 30  # minutes
    check_interval = 60  # secondes
    
    for minute in range(max_wait):
        try:
            print(f"🔍 Vérification {minute + 1}/{max_wait} (minute {minute + 1})...")
            
            conn = psycopg2.connect(DATABASE_URL)
            print("✅ Base de données disponible !")
            conn.close()
            return True
            
        except psycopg2.OperationalError as e:
            if "not yet accepting connections" in str(e):
                print(f"⏳ Encore en récupération... (minute {minute + 1})")
                if minute < max_wait - 1:
                    print(f"   Prochaine vérification dans {check_interval} secondes")
                    time.sleep(check_interval)
            else:
                print(f"❌ Autre erreur: {e}")
                break
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            break
    
    print(f"❌ Base de données toujours non disponible après {max_wait} minutes")
    return False

def main():
    """Menu principal pour le nettoyage d'urgence."""
    print("🚨 SCRIPT DE RÉCUPÉRATION POSTGRESQL")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL non définie")
        return
    
    print("\n🎯 STRATÉGIE DE RÉCUPÉRATION:")
    print("1. Attendre que la base soit disponible")
    print("2. Effectuer un nettoyage d'urgence")
    print("3. Optimiser la base de données")
    
    # Étape 1: Attendre la disponibilité
    print(f"\n{'='*20} ÉTAPE 1: ATTENTE {'='*20}")
    if not wait_for_database():
        print("\n💡 SOLUTIONS ALTERNATIVES:")
        print("• La base peut être en maintenance prolongée")
        print("• Vérifiez le statut Railway")
        print("• Contactez le support si nécessaire")
        return
    
    # Étape 2: Nettoyage
    print(f"\n{'='*20} ÉTAPE 2: NETTOYAGE {'='*20}")
    if emergency_cleanup():
        print("\n🎉 RÉCUPÉRATION RÉUSSIE !")
        print("💾 Vous pouvez maintenant relancer vos backups")
    else:
        print("\n❌ Récupération échouée")
        print("💡 Réessayez dans quelques minutes")

if __name__ == "__main__":
    main()
