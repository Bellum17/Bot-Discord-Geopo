#!/usr/bin/env python3
"""
Script de diagnostic PostgreSQL pour identifier les problèmes de connexion.
"""

import os
import psycopg2
import time
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

def test_connection():
    """Test la connexion à PostgreSQL avec diagnostic détaillé."""
    print("🔍 DIAGNOSTIC POSTGRESQL")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier DATABASE_URL
    if not DATABASE_URL:
        print("❌ ERREUR: Variable DATABASE_URL non définie")
        return False
    
    print(f"🔗 URL de connexion configurée: {'Oui' if DATABASE_URL else 'Non'}")
    
    # Extraire les informations de l'URL (sans révéler le mot de passe)
    try:
        from urllib.parse import urlparse
        parsed = urlparse(DATABASE_URL)
        print(f"🖥️ Serveur: {parsed.hostname}")
        print(f"🔌 Port: {parsed.port}")
        print(f"🗄️ Base de données: {parsed.path[1:] if parsed.path else 'N/A'}")
        print(f"👤 Utilisateur: {parsed.username}")
    except Exception as e:
        print(f"⚠️ Impossible de parser l'URL: {e}")
    
    print("\n🔄 Test de connexion...")
    
    # Essayer plusieurs fois avec diagnostic
    for attempt in range(5):
        try:
            print(f"\n📡 Tentative {attempt + 1}/5...")
            start_time = time.time()
            
            conn = psycopg2.connect(DATABASE_URL)
            connection_time = time.time() - start_time
            
            print(f"✅ Connexion réussie en {connection_time:.2f}s")
            
            # Test de requête
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]
                print(f"🗄️ Version PostgreSQL: {version[:50]}...")
                
                cur.execute("SELECT current_database()")
                db_name = cur.fetchone()[0]
                print(f"📊 Base de données actuelle: {db_name}")
                
                cur.execute("SELECT NOW()")
                server_time = cur.fetchone()[0]
                print(f"🕐 Heure serveur: {server_time}")
                
                # Test de tables
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = cur.fetchall()
                print(f"📋 Tables disponibles: {len(tables)}")
                for table in tables[:5]:
                    print(f"   • {table[0]}")
                if len(tables) > 5:
                    print(f"   ... et {len(tables) - 5} autres")
            
            conn.close()
            print("\n🎉 Diagnostic réussi - PostgreSQL est opérationnel !")
            return True
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            print(f"❌ Erreur de connexion: {error_msg}")
            
            if "not yet accepting connections" in error_msg:
                print("🔄 La base de données est en cours de récupération")
                print("💡 Cela indique généralement un redémarrage ou une maintenance")
                
            elif "could not connect to server" in error_msg:
                print("🔌 Problème de connectivité réseau")
                print("💡 Vérifiez votre connexion internet ou l'état du serveur")
                
            elif "password authentication failed" in error_msg:
                print("🔐 Problème d'authentification")
                print("💡 Vérifiez vos identifiants de connexion")
                
            elif "database" in error_msg and "does not exist" in error_msg:
                print("🗄️ Base de données inexistante")
                print("💡 Vérifiez le nom de la base de données")
                
            else:
                print("❓ Erreur inconnue")
            
            if attempt < 4:
                wait_time = (attempt + 1) * 10
                print(f"⏳ Attente de {wait_time} secondes...")
                time.sleep(wait_time)
            
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return False
    
    print("\n❌ Échec du diagnostic après 5 tentatives")
    return False

def check_recovery_status():
    """Vérifie spécifiquement l'état de récupération."""
    print("\n🔍 VÉRIFICATION DE L'ÉTAT DE RÉCUPÉRATION")
    print("-" * 40)
    
    for i in range(10):
        try:
            print(f"🔄 Vérification {i+1}/10...")
            conn = psycopg2.connect(DATABASE_URL)
            
            with conn.cursor() as cur:
                # Vérifier l'état de récupération
                cur.execute("SELECT pg_is_in_recovery()")
                in_recovery = cur.fetchone()[0]
                
                if in_recovery:
                    print("🔄 Base de données en mode de récupération")
                else:
                    print("✅ Base de données prête pour les connexions")
                    conn.close()
                    return True
            
            conn.close()
            
        except psycopg2.OperationalError as e:
            if "not yet accepting connections" in str(e):
                print(f"⏳ Toujours en récupération... (tentative {i+1})")
                time.sleep(30)  # Attendre 30 secondes
            else:
                print(f"❌ Autre erreur: {e}")
                break
        except Exception as e:
            print(f"❌ Erreur: {e}")
            break
    
    return False

def main():
    """Fonction principale de diagnostic."""
    success = test_connection()
    
    if not success:
        print("\n🔄 Vérification spécifique de l'état de récupération...")
        recovery_done = check_recovery_status()
        
        if recovery_done:
            print("✅ Base de données maintenant disponible !")
        else:
            print("❌ Base de données toujours non disponible")
            print("\n💡 SOLUTIONS POSSIBLES:")
            print("• Attendre quelques minutes (récupération en cours)")
            print("• Vérifier l'état du serveur Railway")
            print("• Contacter le support si le problème persiste")
            print("• Vérifier les variables d'environnement")

if __name__ == "__main__":
    main()
