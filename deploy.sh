#!/bin/bash
# Script de déploiement automatique pour Railway/Heroku

echo "🚀 Déploiement automatique du bot Discord"
echo "=========================================="

# Vérifier si on est dans un repo git
if [ ! -d ".git" ]; then
    echo "❌ Ce n'est pas un dépôt Git. Initialisation..."
    git init
    git remote add origin https://github.com/Bellum17/Bot-Discord-Geoppo.git
fi

# Ajouter tous les changements
echo "📝 Ajout des modifications..."
git add .

# Demander le message de commit
read -p "💬 Message de commit (optionnel): " commit_message
if [ -z "$commit_message" ]; then
    commit_message="Mise à jour automatique - $(date)"
fi

# Commit
echo "💾 Commit des changements..."
git commit -m "$commit_message"

# Push vers main
echo "🔄 Push vers le repository principal..."
git push origin main

echo "✅ Déploiement terminé!"
echo "⏳ Le bot se redémarrera automatiquement sur Railway/Heroku en ~30 secondes"
