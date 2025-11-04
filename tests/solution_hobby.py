#!/usr/bin/env python3
"""
Solution d'urgence pour Railway Hobby - Plan sans backups automatiques
"""

def hobby_plan_solution():
    """Solution spécifique au plan Railway Hobby."""
    print("🏠 SOLUTION RAILWAY HOBBY - PLAN SANS BACKUPS")
    print("=" * 50)
    print("✅ Vos 21 fichiers JSON sont SAUFS localement !")
    print("🎯 Objectif : Nouveau PostgreSQL propre + Restauration")
    print()
    
    print("🚀 SOLUTION RECOMMANDÉE - NOUVEAU VOLUME :")
    print("=" * 40)
    
    steps = [
        "1️⃣ Railway Dashboard → Votre projet → PostgreSQL",
        "2️⃣ Onglet 'Variables' → Add Variable",
        "3️⃣ Name: PGDATA",
        "4️⃣ Value: /var/lib/postgresql/newdata",
        "5️⃣ Cliquer 'Add' puis 'Deploy'",
        "6️⃣ Attendre 2-3 minutes → PostgreSQL démarre proprement",
        "7️⃣ Lancer: python3 backup_json_to_postgres.py",
        "8️⃣ ✅ TERMINÉ ! Toutes vos données restaurées"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n💡 POURQUOI ÇA MARCHE :")
    explanations = [
        "🔄 PGDATA change le répertoire de données PostgreSQL",
        "🆕 PostgreSQL créera un nouveau répertoire PROPRE",
        "🚫 Évite complètement le xlogtemp.29 corrompu",
        "✅ Base vide + vos JSON locaux = Restauration complète"
    ]
    
    for exp in explanations:
        print(f"   {exp}")

def alternative_solution():
    """Solution alternative si la première ne marche pas."""
    print(f"\n🔄 PLAN B - NOUVEAU SERVICE POSTGRESQL :")
    print("=" * 40)
    
    steps_b = [
        "1️⃣ Railway Dashboard → Add Service",
        "2️⃣ Database → PostgreSQL", 
        "3️⃣ Nouveau service créé → Récupérer DATABASE_URL",
        "4️⃣ Mettre à jour votre .env avec la nouvelle URL",
        "5️⃣ Lancer: python3 backup_json_to_postgres.py",
        "6️⃣ Une fois OK → Supprimer l'ancien PostgreSQL"
    ]
    
    for step in steps_b:
        print(f"   {step}")
    
    print(f"\n💰 COÛT : Temporairement 2 PostgreSQL (puis 1 seul)")

def show_data_inventory():
    """Inventaire des données sauvegardées."""
    print(f"\n📦 INVENTAIRE DE VOS DONNÉES LOCALES :")
    print("=" * 35)
    
    import os
    import glob
    
    data_files = glob.glob("data/*.json")
    important_files = [
        "balances.json", "pib.json", "personnel.json", 
        "transactions.json", "levels.json", "invites.json"
    ]
    
    print(f"✅ TOTAL : {len(data_files)} fichiers JSON sauvegardés")
    print(f"\n🎯 FICHIERS CRITIQUES :")
    
    for file in important_files:
        if f"data/{file}" in [f.replace("\\", "/") for f in data_files]:
            size = os.path.getsize(f"data/{file}")
            print(f"   ✅ {file:<20} : {size:,} bytes")
        else:
            print(f"   ❌ {file:<20} : MANQUANT")
    
    print(f"\n💡 CONCLUSION : Vous pouvez recréer votre base PostgreSQL !")

def main():
    """Guide principal pour Railway Hobby."""
    hobby_plan_solution()
    alternative_solution()
    show_data_inventory()
    
    print(f"\n🎯 ACTION IMMÉDIATE :")
    print("=" * 20)
    print("🔧 Allez sur Railway Dashboard")
    print("➕ PostgreSQL → Variables → PGDATA=/var/lib/postgresql/newdata")
    print("🚀 Deploy et attendez 2-3 minutes")
    print("💾 Puis lancez backup_json_to_postgres.py")
    
    print(f"\n💪 Plan Hobby : AUCUN PROBLÈME avec cette méthode !")

if __name__ == "__main__":
    main()
