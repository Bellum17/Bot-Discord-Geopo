import csv
import re

def parse_value(value_str):
    """Parse une valeur comme '70k à 120k' ou '500k à 1m' en tuple de nombres"""
    if not value_str or value_str.strip() == "":
        return None
    
    # Nettoyer la chaîne
    value_str = value_str.strip().replace("(unité)", "").replace("(Dev)", "")
    
    # Extraire les nombres avec k/m
    pattern = r'(\d+(?:\.\d+)?)\s*([km]?)\s*à\s*(\d+(?:[\.,]\d+)?)\s*([km]?)'
    match = re.search(pattern, value_str)
    
    if match:
        min_val, min_unit, max_val, max_unit = match.groups()
        
        # Convertir les valeurs en millions
        min_val = float(min_val.replace(',', '.'))
        max_val = float(max_val.replace(',', '.'))
        
        if min_unit == 'k':
            min_val = min_val / 1000  # k = milliers, convertir en millions
        if max_unit == 'k':
            max_val = max_val / 1000
            
        return (min_val, max_val)
    
    # Si pas de fourchette, chercher une valeur unique
    single_pattern = r'(\d+(?:[\.,]\d+)?)\s*([km]?)'
    match = re.search(single_pattern, value_str)
    if match:
        val, unit = match.groups()
        val = float(val.replace(',', '.'))
        if unit == 'k':
            val = val / 1000
        return (val, val)
    
    return None

def parse_months(value_str):
    """Parse les mois comme '7 à 10 mois (Dev)'"""
    if not value_str:
        return None
    
    pattern = r'(\d+)\s*à\s*(\d+)\s*mois'
    match = re.search(pattern, value_str)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    
    # Valeur unique
    pattern = r'(\d+)\s*mois'
    match = re.search(pattern, value_str)
    if match:
        val = int(match.group(1))
        return (val, val)
    
    return None

# Analyser le CSV
with open('/Users/bejnamin/Desktop/Espace de Travail/technologies_data.csv', 'r', encoding='utf-8') as f:
    content = f.read()

# Parsing manuel des données importantes
lines = content.split('\n')

categories = {
    "vehicules_terrestres": {},
    "artillerie": {},
    "batiments_guerre": {},
    "appareils_aeriens": {},
    "missiles": {}
}

# Mapping des technologies trouvées dans le CSV
tech_data = [
    # Format: (nom, categorie, dev_range_millions, cout_unite_range, mois_range)
    ("Char léger", "vehicules_terrestres", "8 à 11 millions", "70k à 120k", "7 à 10 mois"),
    ("Char Moyen", "vehicules_terrestres", "8 à 13 millions", "130k à 200k", "7 à 11 mois"),
    ("Char Lourd", "vehicules_terrestres", "13 à 15 millions", "350k à 500k", "10 à 15 mois"),
    ("Char d'assaut principal (MBT)", "vehicules_terrestres", "10 à 15 millions", "250k à 300k", "9 à 12 mois"),
    ("IFV", "vehicules_terrestres", "7 à 11 millions", "90k à 160k", "7 à 13 mois"),
    ("APC", "vehicules_terrestres", "6 à 10 millions", "80k à 145k", "7 à 12 mois"),
    ("Chasseur de chars", "vehicules_terrestres", "11 à 17 millions", "135k à 200k", "9 à 13 mois"),
    ("Char super lourd", "vehicules_terrestres", "20 à 25 millions", "400k à 500k", "9 à 12 mois"),
    ("Lance-roquettes multiple", "vehicules_terrestres", "9 à 15 millions", "120k à 200k", "8 à 13 mois"),
    
    # Artillerie  
    ("Artillerie de campagne (70mm à 160mm)", "artillerie", "5 à 10 millions", "10k à 20k", "4 à 6 mois"),
    ("Artillerie lourde (+ de 160mm)", "artillerie", "8 à 13 millions", "30k à 50k", "5 à 8 mois"),
    ("Artillerie légère (- de 70mm)", "artillerie", "3 à 5 millions", "5k à 10k", "3 à 5 mois"),
    ("Mortier d'infanterie (- de 70mm)", "artillerie", "4 à 6 millions", "700 à 900", "3 à 6 mois"),
    ("Mortier de campagne (70mm à 120mm)", "artillerie", "5 à 8 millions", "800 à 1k", "4 à 7 mois"),
    ("Mortier lourd (+ de 120mm)", "artillerie", "5 à 10 millions", "1k à 1,5k", "6 à 9 mois"),
    ("Canon anti-aérien", "artillerie", "3 à 5 millions", "5k à 15k", "3 à 6 mois"),
    ("Canon anti-char", "artillerie", "3 à 5 millions", "5k à 15k", "3 à 6 mois"),
    ("SPAG", "artillerie", "9 à 15 millions", "150k à 300k", "7 à 12 mois"),
    
    # Bâtiments de guerre
    ("Destroyer", "batiments_guerre", "20 à 25 millions", "500k à 1m", "6 à 12 mois"),
    ("Cuirassé", "batiments_guerre", "40 à 50 millions", "2m à 5m", "10 à 15 mois"),
    ("Croiseur léger", "batiments_guerre", "30 à 35 millions", "800k à 1,5m", "8 à 12 mois"),
    ("Croiseur Lourd", "batiments_guerre", "40 à 45 millions", "1m à 2m", "10 à 15 mois"),
    ("Frégate", "batiments_guerre", "15 à 20 millions", "300k à 700k", "6 à 10 mois"),
    ("Porte-Hélicoptère", "batiments_guerre", "35 à 45 millions", "2m à 5m", "10 à 15 mois"),
    ("Porte-Avion", "batiments_guerre", "50 à 80 millions", "5m à 10m", "10 à 18 mois"),
    ("Porte-Avion léger", "batiments_guerre", "25 à 40 millions", "2m à 4m", "10 à 15 mois"),
    ("Porte-Avion (Propulsion nucléaire)", "batiments_guerre", "100 à 150 millions", "50m à 80m", "24 mois"),
    ("Sous-marin (Diesel, ou Diesel-Electrique)", "batiments_guerre", "15 à 30 millions", "500k à 2m", "8 à 15 mois"),
    ("SNLE", "batiments_guerre", "30 à 70 millions", "10m à 30m", "10 à 18 mois"),
    ("SNA", "batiments_guerre", "30 à 70 millions", "10m à 30m", "10 à 18 mois"),
    ("Corvette", "batiments_guerre", "20 à 30 millions", "400k à 800k", "6 à 10 mois"),
    ("Patrouilleur", "batiments_guerre", "5 à 10 millions", "100k à 500k", "3 à 5 mois"),
    ("Barge de Débarquement", "batiments_guerre", "2 à 5 millions", "100k à 300k", "3 à 5 mois"),
    
    # Appareils aériens
    ("Avion multirôle", "appareils_aeriens", "10 à 15 millions", "350k à 700k", "8 à 12 mois"),
    ("Avion d'attaque au sol", "appareils_aeriens", "10 à 20 millions", "300k à 600k", "6 à 12 mois"),
    ("Avion de chasse (interception)", "appareils_aeriens", "10 à 20 millions", "300k à 600k", "6 à 12 mois"),
    ("Bombardier tactique", "appareils_aeriens", "20 à 25 millions", "500k à 700k", "8 à 12 mois"),
    ("Bombardier stratégique", "appareils_aeriens", "30 à 35 millions", "750k à 1 million", "10 à 12 mois"),
    ("Avion de reconnaissance", "appareils_aeriens", "5 à 10 millions", "200k à 300k", "6 à 9 mois"),
    ("Avion de transport (matériel/troupe)", "appareils_aeriens", "10 à 20 millions", "500k à 700k", "6 à 12 mois"),
    ("AWACS", "appareils_aeriens", "10 à 20 millions", "300k à 500k", "6 à 12 mois"),
    ("Hélicoptère d'attaque", "appareils_aeriens", "9 à 15 millions", "100k à 300k", "6 à 12 mois"),
    ("Hélicoptère de reconnaissance", "appareils_aeriens", "5 à 10 millions", "75k à 200k", "6 à 9 mois"),
    ("Hélicoptère de transport", "appareils_aeriens", "9 à 15 millions", "200k à 400k", "6 à 12 mois"),
    ("Drone de reconnaissance", "appareils_aeriens", "3 à 5 millions", "150k à 500k", "3 à 6 mois"),
    ("Drone suicide", "appareils_aeriens", "1 à 2 millions", "10k à 30k", "3 à 6 mois"),
    ("Drone d'Attaque", "appareils_aeriens", "5 à 15 millions", "300k à 1m", "6 à 12 mois"),
    
    # Missiles
    ("SRBM (300 à 1000km)", "missiles", "20 à 25 millions", "500k à 2m", "8 à 15 mois"),
    ("MRBM (1000 à 3000km)", "missiles", "35 à 50 millions", "5m à 20m", "12 à 18 mois"),
    ("ICBM (+ de 5500km)", "missiles", "150 à 300 millions", "50m", "24 mois"),
    ("IRBM (3500-5500 km)", "missiles", "50 à 75 millions", "25m", "12 à 24 mois"),
    ("BRBM (-300 km)", "missiles", "15 à 20 millions", "500k à 1,5m", "8 à 12 mois"),
    ("SAM", "missiles", "20 à 25 millions", "500k à 2m", "8 à 15 mois"),
    ("ATGM", "missiles", "5 à 7 millions", "1500 à 2000", "5 à 8 mois"),
    ("MANPADS", "missiles", "5 à 8 millions", "1700 à 2200", "5 à 8 mois"),
]

print("# DONNÉES CORRIGÉES POUR LE BOT :")
print()

for nom, categorie, dev_str, cout_str, mois_str in tech_data:
    dev_range = parse_value(dev_str)
    cout_range = parse_value(cout_str)
    mois_range = parse_months(mois_str)
    
    if dev_range and cout_range and mois_range:
        print(f'"{nom}": {{"name": "{nom}", "dev_range": {dev_range}, "cout_range": {cout_range}, "mois_range": {mois_range}}},')
