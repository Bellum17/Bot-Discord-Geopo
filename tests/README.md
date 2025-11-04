# 🧪 Dossier de Tests

Ce dossier contient tous les scripts de test et de debug créés pendant le développement du bot.

## 📂 Organisation des Fichiers

### 🔧 **Scripts de Correction**
- `fix_dev_calendar.py` - Corrige les développements existants avec métadonnées RP manquantes
- `fix_timezone.py` - Corrige les timestamps pour utiliser le fuseau horaire de Paris

### 🐛 **Scripts de Debug**
- `debug_dev_auto.py` - Debug des développements automatiques
- `debug_heure_complete.py` - Debug des heures de complétion
- `debug_timezone.py` - Debug du fuseau horaire

### 🧪 **Tests de Fonctionnalités**
- `test_corrections.py` - Test de toutes les corrections apportées
- `test_dev_completion.py` - Test de la complétion des développements
- `test_dev_display.py` - Test de l'affichage des développements
- `test_emplacement_pratique.py` - Test pratique de libération d'emplacements
- `test_slots_liberation.py` - Test de libération des emplacements de centres
- `test_gestion_centres_ephemeral.py` - Test que gestion_centres est ephemeral
- `test_simple_gestion.py` - Test simple des modifications de gestion_centres

### ⏰ **Tests de Calendrier**
- `test_calendar_advance.py` - Test d'avancement du calendrier
- `test_calendar_precision.py` - Test de précision du calendrier
- `test_cest_force.py` - Test du fuseau horaire CEST forcé
- `test_timezone.py` - Test du formatage des fuseaux horaires
- `test_final_timezone.py` - Test final du système de timezone

### 📝 **Tests de Timestamps**
- `test_simple_timestamp.py` - Test simple des timestamps
- `test_real_function.py` - Test de fonctions réelles
- `test_correction_heure.py` - Test de correction des heures

### 🏗️ **Scripts de Création**
- `create_new_dev.py` - Crée un nouveau développement de test
- `create_test_data.py` - Crée des données de test

### 🎮 **Scripts de Simulation**
- `simulate_calendrier_test.py` - Simule les tests de calendrier

## 🚀 **Utilisation**

Tous ces scripts peuvent être exécutés avec Python 3 :

```bash
cd tests
python3 nom_du_script.py
```

## ⚠️ **Avertissement**

Ces scripts sont à des fins de test et de debug uniquement. Ils ne font pas partie du bot principal et peuvent modifier les données de test.

## 🧹 **Nettoyage**

Ces fichiers peuvent être supprimés une fois que le bot est en production stable, mais ils sont utiles pour :
- Debug de problèmes futurs
- Tests de nouvelles fonctionnalités
- Validation après modifications

---

*Créé pendant le développement et debug du Bot-Discord-Geoppo*
