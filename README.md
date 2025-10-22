# 🤖 Bot Discord Pax Ruinae

Bot Discord avancé pour le serveur de rôleplay géopolitique Pax Ruinae.

## 🚀 Fonctionnalités

- **Système économique** avec budgets et PIB
- **Système XP/Niveaux** 
- **Gestion des pays** et rôles
- **Centres technologiques** et développements
- **Calendrier RP** automatisé
- **Intelligence artificielle** avec Ollama
- **Système de backup** PostgreSQL
- **Modération avancée**

## 📦 Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# Modifier .env avec vos tokens

# Démarrer le bot
./start_bot.sh
```

## 🤖 IA Ollama

Le bot intègre Ollama pour l'intelligence artificielle :
- Modèle : `deepseek-r1:8b`
- Commande : `/ai`

## 📁 Structure

- `client.py` - Bot principal
- `ollama_integration.py` - Module IA
- `data/` - Données JSON
- `tests/` - Scripts de test et debug