#!/usr/bin/env python3
"""
Diagnostic rapide PostgreSQL pour vérifier l'état de la base de données
"""

import os
import psycopg2
import time
from datetime import datetime

def check_postgres_status():
    """Vérifie l'état de PostgreSQL."""
    print("🔍 DIAGNOSTIC POSTGRESQL")
    print("=" * 40)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("\n❌ DATABASE_URL non définie")
        print("💡 Vérifiez votre fichier .env")
        print("📝 Format attendu: postgresql://user:password@host:port/database")
        return False
    
    print(f"\n🔗 URL configurée: {'Oui' if database_url else 'Non'}")
    
    # Extraire les informations (sans révéler le mot de passe)
    try:
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        print(f"🖥️ Serveur: {parsed.hostname}")
        print(f"🔌 Port: {parsed.port}")
        print(f"🗄️ Base: {parsed.path[1:] if parsed.path else 'N/A'}")
    except Exception as e:
        print(f"⚠️ Erreur parsing URL: {e}")
    
    # Test de connexion
    print(f"\n🔄 Test de connexion...")
    
    for attempt in range(3):
        try:
            print(f"📡 Tentative {attempt + 1}/3...")
            start_time = time.time()
            
            conn = psycopg2.connect(database_url)
            connection_time = time.time() - start_time
            
            print(f"✅ Connexion réussie en {connection_time:.2f}s")
            
            # Test de requête
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]
                print(f"🗄️ PostgreSQL: {version[:60]}...")
                
                cur.execute("SELECT current_database()")
                db_name = cur.fetchone()[0]
                print(f"📊 Base actuelle: {db_name}")
                
                # Vérifier l'état de récupération
                cur.execute("SELECT pg_is_in_recovery()")
                in_recovery = cur.fetchone()[0]
                
                if in_recovery:
                    print("🔄 État: En mode récupération")
                else:
                    print("✅ État: Opérationnel")
            
            conn.close()
            print("\n🎉 PostgreSQL est disponible !")
            return True
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            print(f"❌ Erreur: {error_msg[:100]}...")
            
            if "not yet accepting connections" in error_msg:
                print("🔄 Base de données en cours de récupération/maintenance")
                print("💡 Cela peut prendre quelques minutes")
                
            elif "could not connect to server" in error_msg:
                print("🔌 Problème de connectivité réseau")
                
            elif "password authentication failed" in error_msg:
                print("🔐 Problème d'authentification")
                
            else:
                print("❓ Autre erreur de connexion")
            
            if attempt < 2:
                wait_time = (attempt + 1) * 15
                print(f"⏳ Attente de {wait_time}s avant nouvelle tentative...")
                time.sleep(wait_time)
            
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            break
    
    print("\n❌ Connexion impossible après 3 tentatives")
    return False

def main():
    """Fonction principale."""
    available = check_postgres_status()
    
    if not available:
        print(f"\n{'='*40}")
        print("💡 SOLUTIONS POSSIBLES:")
        print("🔧 Si c'est une maintenance:")
        print("   • Attendre 10-30 minutes")
        print("   • Réessayer périodiquement")
        
        print("\n🔧 Si c'est un problème de config:")
        print("   • Vérifier le fichier .env")
        print("   • Vérifier DATABASE_URL")
        print("   • Contacter l'hébergeur (Railway/Heroku/etc.)")
        
        print(f"\n⏰ Prochain test recommandé dans 15 minutes")
    else:
        print(f"\n💾 Vous pouvez maintenant lancer vos backups !")

if __name__ == "__main__":
    main()
