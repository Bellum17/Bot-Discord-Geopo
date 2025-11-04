#!/usr/bin/env python3
"""Script pour nettoyer les commandes temp du fichier client.py"""

import re

def clean_temp_commands():
    with open('client.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Supprimer toutes les commandes temp_status et temp_distribute avec leurs fonctions
    # Pattern pour capturer les commandes temp complètes
    patterns_to_remove = [
        # Commandes temp_status (toutes les variantes)
        r'@bot\.tree\.command\(name="temp_status".*?\n(?=@bot\.tree\.command|def load_temp_usage|def save_temp_usage|# |$)',
        # Fonctions load_temp_usage et save_temp_usage
        r'def load_temp_usage\(\):.*?\n(?=def |@|# |$)',
        r'def save_temp_usage\(data\):.*?\n(?=def |@|# |$)',
        # Variables TEMP
        r'TARGET_GUILD_ID_TEMP.*?\n',
        r'BUDGET_PER_COUNTRY.*?\n',
        r'PIB_PER_COUNTRY.*?\n',
        r'COUNTRY_ROLES_TEMP.*?\n',
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
    
    # Nettoyer les lignes vides multiples
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # Sauvegarder
    with open('client.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Nettoyage terminé !")

if __name__ == "__main__":
    clean_temp_commands()
