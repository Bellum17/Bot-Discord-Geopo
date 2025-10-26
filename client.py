def save_all_json_to_postgres():
    """Sauvegarde tous les fichiers JSON dans PostgreSQL via backup_json_to_postgres.py."""
    try:
        os.system(f"python3 backup_json_to_postgres.py")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde PostgreSQL : {e}")

def restore_all_json_from_postgres():
    """Restaure tous les fichiers JSON depuis PostgreSQL via restore_json_from_postgres.py."""
    try:
        os.system(f"python3 restore_json_from_postgres.py")
    except Exception as e:
        print(f"Erreur lors de la restauration PostgreSQL : {e}")
import os
import sys
import json
import time

import discord
from discord.ext import commands

# Import du module Ollama supprimé
from discord import app_commands
import json
xp_system_status_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "xp_system_status.json")
def load_xp_system_status():
    if os.path.exists(xp_system_status_path):
        with open(xp_system_status_path, 'r') as f:
            return json.load(f)
    return {"servers": {}}

def save_xp_system_status(status):
    with open(xp_system_status_path, 'w') as f:
        json.dump(status, f, indent=4)

xp_system_status = load_xp_system_status()
import time
import datetime
from zoneinfo import ZoneInfo
import asyncio
import typing
import random
import sys
import atexit
import signal
import aiohttp
import io
import textwrap
import re
import geopandas as gpd
import numpy as np
from shapely.ops import unary_union
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from PIL import Image, ImageDraw, ImageFont # type: ignore
from dotenv import load_dotenv
from discord.ext.tasks import loop

# Chargement des variables d'environnement
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("ERREUR: DISCORD_TOKEN n'est pas défini dans le fichier .env")
    print("Créez un fichier .env avec DISCORD_TOKEN=votre_token_discord")
    sys.exit(1)

# Configuration du répertoire de base et des constantes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBED_COLOR = 0xefe7c5
SANCTION_COLOR = 0x162e50  # Couleur pour les sanctions (mute, ban, warn)
IMAGE_URL = "https://zupimages.net/up/21/03/vl8j.png"
ADMIN_IDS = [300740726257139712]  # IDs des administrateurs du bot
COUNTRY_MANAGER_ROLE_ID = 1418245630639476868  # Rôle autorisé à créer/supprimer des pays
EXCLUDED_ROLE_IDS = [1424143590246056127]  # Rôles exclus du système économique

def is_valid_country_role(role_id):
    """Vérifie si un rôle peut être utilisé dans le système économique."""
    return int(role_id) not in EXCLUDED_ROLE_IDS

def has_country_management_permissions(interaction: discord.Interaction):
    """Vérifie si l'utilisateur a les permissions pour gérer les pays."""
    # Vérifier permissions admin
    if interaction.user.guild_permissions.administrator:
        return True
    
    # Vérifier ADMIN_IDS
    if interaction.user.id in ADMIN_IDS:
        return True
    
    # Vérifier le rôle spécifique
    for role in interaction.user.roles:
        if role.id == COUNTRY_MANAGER_ROLE_ID:
            return True
    
    return False

def get_paris_time():
    """Retourne l'heure actuelle de Paris (CEST/CET) en format ISO."""
    return datetime.datetime.now(ZoneInfo("Europe/Paris")).isoformat()

def format_paris_time(iso_string):
    """Formate une chaîne ISO en heure de Paris lisible."""
    try:
        # Si la chaîne a déjà un fuseau horaire
        if '+' in iso_string or iso_string.endswith('Z'):
            dt = datetime.datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            paris_dt = dt.astimezone(ZoneInfo("Europe/Paris"))
        else:
            # Si pas de fuseau horaire, considérer comme heure de Paris
            dt = datetime.datetime.fromisoformat(iso_string)
            paris_dt = dt.replace(tzinfo=ZoneInfo("Europe/Paris"))
        
        return paris_dt.strftime("%d/%m/%Y à %H:%M")
    except:
        return iso_string
MONNAIE_EMOJI = "<:Monnaie:1412039375063355473>"
INVISIBLE_CHAR = "⠀"
HELP_THUMBNAIL_URL = "https://cdn.discordapp.com/attachments/1411865291041931327/1422937730177826827/c4959984-ba58-486b-a7c3-a17b231b80a9.png?ex=68de7d87&is=68dd2c07&hm=78336c03ba0fbcfd847d2e7a4e14307b2ecc964b97be95648fbc2a1a9884da9c&"
HELP_HEADER_IMAGE_URL = "https://cdn.discordapp.com/attachments/1412872314525192233/1422963949682561096/Capture_decran_2025-10-01_a_17.10.31.png?ex=68de95f2&is=68dd4472&hm=75f6f6e77beb2dc7d09e85cf105a6dbd10570f08794388287ebdcf21e3645f2e&"
HELP_HEADER_SEPARATOR = "-# ─────────────────────────────"
WELCOME_ROLE_ID = 1393340583665209514
WELCOME_CHANNEL_ID = 1416882330576097310
WELCOME_PUBLIC_MESSAGE = (
    "### <:PX_Festif:1423426894019297381> Bienvenue à toi ! {mention}\n"
    "> ▪︎ Ce serveur est actuellement en cours de refonte et rouvrira très prochainement, dans les semaines à venir, voire dans les prochains jours. Si tu as besoin de renseignements, le salon <#1393318935692312787> a été mis à jour depuis et le staff reste à ta disposition pour répondre à tes questions. En attendant, nous t’invitons à faire connaissance avec les autres membres et à patienter sereinement jusqu’à la réouverture du rôleplay !"
)
WELCOME_DM_MESSAGE = (
    "### <:PX_Festif:1423426894019297381> Bienvenue à toi !\n"
    "> ▪︎ Ce serveur est actuellement en cours de refonte et rouvrira très prochainement, dans les semaines à venir, voire dans les prochains jours. Si tu as besoin de renseignements, le salon <#1393318935692312787> a été mis à jour depuis et le staff reste à ta disposition pour répondre à tes questions. En attendant, nous t’invitons à faire connaissance avec les autres membres et à patienter sereinement jusqu’à la réouverture du rôleplay !\n\n"
    "-# Envoyé depuis le serveur 𝐏𝐀𝐗 𝐑𝐔𝐈𝐍𝐀𝐄."
)
HELP_VIEW_TOP_URL = "https://cdn.discordapp.com/attachments/1411865291041931327/1423095868201898055/72de43e34dc04d4fab20473c798afb67.png?ex=68df10ce&is=68ddbf4e&hm=c5e6e9bd6f73f6945f05404d28df207d47156a1ac42acaf66293422bb30bd33d&"
HELP_VIEW_BOTTOM_URL = "https://cdn.discordapp.com/attachments/1411865291041931327/1423095868470460496/0e19006685eb40119c16b69826b91c56.png?ex=68df10ce&is=68ddbf4e&hm=9fb6ed54561624910b84ea69eabad8695230219daaa72ad44dbe097f11278023&"

# === Configuration générale du bot ===
PRIMARY_GUILD_ID = 1393301496283795640
PERMANENT_STATUS_TEXT = "Gestionne les Nations"

# Chemins des fichiers de données
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

BALANCE_FILE = os.path.join(DATA_DIR, "balances.json")
LOG_FILE = os.path.join(DATA_DIR, "log_channel.json")
MESSAGE_LOG_FILE = os.path.join(DATA_DIR, "message_log_channel.json")
LOANS_FILE = os.path.join(DATA_DIR, "loans.json")
PIB_FILE = os.path.join(DATA_DIR, "pib.json")
BALANCE_BACKUP_FILE = os.path.join(DATA_DIR, "balances_backup.json")
TRANSACTION_LOG_FILE = os.path.join(DATA_DIR, "transactions.json")
PAYS_LOG_FILE = os.path.join(DATA_DIR, "pays_log_channel.json")
PAYS_IMAGES_FILE = os.path.join(DATA_DIR, "pays_images.json")
MUTE_LOG_FILE = os.path.join(DATA_DIR, "mute_log_channel.json")
WARNINGS_FILE = os.path.join(DATA_DIR, "warnings.json")

# === XP/LEVEL SYSTEM ===
LVL_FILE = os.path.join(DATA_DIR, "levels.json")
LVL_LOG_CHANNEL_FILE = os.path.join(DATA_DIR, "lvl_log_channel.json")

def load_levels():
    if not os.path.exists(LVL_FILE):
        with open(LVL_FILE, "w") as f:
            json.dump({}, f)
    try:
        with open(LVL_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des niveaux: {e}")
        return {}

def save_levels(data):
    try:
        with open(LVL_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des niveaux: {e}")

def load_lvl_log_channel():
    if not os.path.exists(LVL_LOG_CHANNEL_FILE):
        with open(LVL_LOG_CHANNEL_FILE, "w") as f:
            json.dump({}, f)
    try:
        with open(LVL_LOG_CHANNEL_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement du salon de log lvl: {e}")
        return {}

def save_lvl_log_channel(data):
    try:
        with open(LVL_LOG_CHANNEL_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du salon de log lvl: {e}")

levels = load_levels()
lvl_log_channel_data = load_lvl_log_channel()

def xp_for_level(level):
    if level > 100:
        return None
    if level <= 1:
        return 10
    elif level == 2:
        return 20
    else:
        return 2 * xp_for_level(level - 1)

def migrate_levels_data():
    """Migration désactivée - retour au système XP simple"""
    print("✅ Données déjà à jour")
    return 0

def get_progress_bar(xp, level):
    total = xp_for_level(level)
    percent = int((xp / total) * 100) if total > 0 else 0
    filled = percent // 10
    if percent == 0:
        bar = "<:Barre2_Vide:1417667900596027522>"
    else:
        bar = "<:Barre2_Rempli:1417667907508244581>"
    for i in range(1, 10):
        if i <= filled:
            bar += "<:Barre1_Rempli:1417667903905595583>"
        else:
            bar += "<:Barre1_Vide:1417667899153186928>"
    if percent == 100:
        bar += "<:Barre3_Rempli:1417667906027913226>"
    else:
        bar += "<:Barre3_Vide:1417667902471147520>"
    return f"{bar} — {percent}%"

# === WARNING SYSTEM ===
def load_warnings():
    if not os.path.exists(WARNINGS_FILE):
        with open(WARNINGS_FILE, "w") as f:
            json.dump({}, f)
    try:
        with open(WARNINGS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des avertissements: {e}")
        return {}

def save_warnings(warnings_data):
    try:
        with open(WARNINGS_FILE, "w") as f:
            json.dump(warnings_data, f, indent=2)
        # Backup PostgreSQL
        try:
            import psycopg2, os
            DATABASE_URL = os.getenv("DATABASE_URL")
            if DATABASE_URL:
                with psycopg2.connect(DATABASE_URL) as conn:
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM json_backups WHERE filename = %s", ("warnings.json",))
                        with open(WARNINGS_FILE, "r") as f:
                            content = f.read()
                        cur.execute("""
                            INSERT INTO json_backups (filename, content, updated_at)
                            VALUES (%s, %s, NOW())
                            ON CONFLICT (filename) DO UPDATE SET content = EXCLUDED.content, updated_at = NOW()
                        """, ("warnings.json", content))
                    conn.commit()
        except Exception as e:
            print(f"[DEBUG] Erreur sauvegarde PostgreSQL warnings: {e}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des avertissements: {e}")

# Configuration PIB
PIB_DEFAULT = 0

# Configuration des centres technologiques
CENTRES_TECH_FILE = os.path.join(DATA_DIR, "centres_tech.json")
CENTRE_COUT_BASE = 10000000  # 10 millions
CENTRE_AMELIORATION_1 = 10000000  # 10 millions
CENTRE_AMELIORATION_2 = 20000000  # 20 millions
CENTRE_EMPLACEMENTS_BASE = 1
SPECIALISATIONS = ["Terrestre", "Aérien", "Marine", "Armes de Destruction Massive", "Spatial"]

# Variables globales pour le suivi de l'état du bot
BOT_START_TIME = time.time()
BOT_DISCONNECT_HANDLED = False

# Configuration des intents Discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Définition d'une classe pour la pagination
class PaginationView(discord.ui.View):
    """Une vue pour la pagination des embeds avec boutons."""
    
    def __init__(self, pages, author_id, timeout=None):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.author_id = author_id
        self.current_page = 0
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page précédente."""
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Vous n'êtes pas autorisé à utiliser ces boutons.", ephemeral=True)
            return

        self.current_page = max(0, self.current_page - 1)
        await interaction.response.edit_message(embed=self.pages[self.current_page])
    
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page suivante."""
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Vous n'êtes pas autorisé à utiliser ces boutons.", ephemeral=True)
            return

        self.current_page = min(len(self.pages) - 1, self.current_page + 1)
        await interaction.response.edit_message(embed=self.pages[self.current_page])

# Définition de la classe du bot
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Suppression de toutes les commandes distantes puis resynchronisation globale
        print("Synchronisation globale des commandes slash...")
        try:
            cmds = await self.tree.sync()
            print(f"Commandes globales synchronisées ({len(cmds)}) : {[c.name for c in cmds]}")
        except Exception as e:
            print(f"Erreur lors de la synchronisation globale : {e}")
        
        # Démarrer les tâches planifiées
        auto_save_economy.start()
        verify_and_fix_balances.start()
        
        print("Bot prêt et tâches planifiées démarrées.")

# Création de l'instance du bot

bot = MyBot()

async def apply_permanent_presence(client: commands.Bot) -> None:
    """Applique le statut permanent configuré pour le bot."""
    try:
        activity = discord.CustomActivity(name=PERMANENT_STATUS_TEXT)
        await client.change_presence(status=discord.Status.online, activity=activity)
    except Exception as exc:
        # Discord refuse parfois les statuts personnalisés pour les bots ; on journalise pour diagnostic.
        print(f"[DEBUG] Impossible de définir l'activité personnalisée : {exc}")
        await client.change_presence(status=discord.Status.online)

# === COMMANDE POUR ENREGISTRER LES IDS DES MEMBRES ===

# === COMMANDE DE SUPPRESSION DE MESSAGES ===
@bot.tree.command(name="purge", description="Supprime un nombre de messages dans ce salon (max 1000)")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, nombre: int):
    await interaction.response.defer(ephemeral=True)
    if nombre < 1 or nombre > 1000:
        await interaction.followup.send("Le nombre doit être entre 1 et 1000.", ephemeral=True)
        return
    channel = interaction.channel
    try:
        deleted = await channel.purge(limit=nombre)
        await interaction.followup.send(f"{len(deleted)} messages supprimés.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Erreur lors de la suppression : {e}", ephemeral=True)

@bot.event
async def on_guild_join(guild: discord.Guild):
    await apply_permanent_presence(bot)
    try:
        await bot.tree.sync(guild=discord.Object(id=guild.id))
        print(f"[INFO] Commandes synchronisées pour la guild {guild.name} ({guild.id})")
    except Exception as exc:
        print(f"[WARN] Échec de synchronisation sur la guild {guild.id} : {exc}")

# Variables globales pour les données
balances = {}
log_channel_data = {}
message_log_channel_data = {}
loans = []
pib_data = {}
pays_log_channel_data = {}
pays_images = {}
mute_log_channel_data = {}
warnings = {}
developpements_data = {}
generaux_data = {}
bonus_xp_active = {}  # {guild_id: end_time}

# Chargement des balances et autres données après la définition de la fonction
# (L'appel à load_all_data() est déplacé après la définition de la fonction)
def format_number(number):
    """Formate un nombre pour l'affichage avec séparateurs de milliers."""
    if isinstance(number, int):
        return f"{number:,}".replace(",", " ")
    return str(number)

def format_unit_cost(cost, unit_multiplier):
    """Formate le coût unitaire avec la bonne unité (milliers/millions)."""
    if unit_multiplier == 1000000:
        # Coût en millions
        millions = cost / 1000000
        if millions == int(millions):
            return f"{int(millions)} millions"
        else:
            return f"{millions:.1f} millions"
    elif unit_multiplier == 1000:
        # Coût en milliers
        milliers = cost / 1000
        if milliers == int(milliers):
            return f"{int(milliers)}k"
        else:
            return f"{milliers:.1f}k"
    else:
        # Coût en unités de base
        return f"{format_number(cost)}"

def format_unit_range(min_val, max_val, unit_multiplier):
    """Formate une fourchette de coûts avec la bonne unité."""
    if unit_multiplier == 1000000:
        return f"{min_val} / {max_val} millions"
    elif unit_multiplier == 1000:
        return f"{min_val} / {max_val} milliers"
    else:
        return f"{min_val} / {max_val}"

# ===== FONCTIONS DE GESTION DES DONNÉES =====

# Fonction pour charger toutes les données
def load_all_data():
    """Charge toutes les données nécessaires au démarrage."""
    global balances, log_channel_data, message_log_channel_data, loans, pib_data, pays_log_channel_data, pays_images, mute_log_channel_data, warnings, developpements_data, generaux_data
    
    # Chargement de toutes les données
    balances.update(load_balances())
    log_channel_data.update(load_log_channel())
    message_log_channel_data.update(load_message_log_channel())
    loans.extend(load_loans())
    pib_data.update(load_pib())
    pays_log_channel_data.update(load_pays_log_channel())
    pays_images.update(load_pays_images())
    warnings.update(load_warnings())
    developpements_data.update(load_developpements())
    generaux_data.update(load_generaux())
## Fonction de chargement du canal de statut supprimée (obsolète)

def load_pays_images():
    """Charge les images des pays depuis le fichier."""
    if not os.path.exists(PAYS_IMAGES_FILE):
        with open(PAYS_IMAGES_FILE, "w") as f:
            json.dump({}, f)
    try:
        with open(PAYS_IMAGES_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des images de pays: {e}")
        return {}

def save_pays_images(data):
    """Sauvegarde les images des pays dans le fichier."""
    try:
        with open(PAYS_IMAGES_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des images de pays: {e}")

def load_balances():
    """Charge les données des balances depuis le fichier principal."""
    balances_data = {}
    
    # Charger le fichier principal
    try:
        if os.path.exists(BALANCE_FILE):
            with open(BALANCE_FILE, "r") as f:
                balances_data = json.load(f)
                print(f"Balances chargées depuis {BALANCE_FILE}: {len(balances_data)} entrées")
    except Exception as e:
        print(f"Erreur lors du chargement des balances: {e}")
    
    # Si aucun fichier n'existe, créer un fichier vide
    if not balances_data:
        balances_data = {}
        print("Création d'un nouveau fichier de balances")
    
    # Créer le fichier s'il n'existe pas
    if not os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "w") as f:
            json.dump(balances_data, f)
    
    return balances_data

def save_balances(balances_data):
    """Sauvegarde les balances dans le fichier principal."""
    # Filtrer les rôles exclus avant la sauvegarde
    filtered_balances = {role_id: balance for role_id, balance in balances_data.items() 
                        if is_valid_country_role(role_id)}
    
    try:
        with open(BALANCE_FILE, "w") as f:
            json.dump(filtered_balances, f)
        print(f"[DEBUG] Balances sauvegardées dans {BALANCE_FILE} ({len(filtered_balances)} entrées)")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des balances: {e}")

def load_log_channel():
    """Charge les données du canal de log."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump({}, f)
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des logs: {e}")
        return {}

def save_log_channel(data):
    """Sauvegarde les données du canal de log."""
    try:
        with open(LOG_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des logs: {e}")

def load_message_log_channel():
    """Charge les données du canal de log des messages."""
    if not os.path.exists(MESSAGE_LOG_FILE):
        with open(MESSAGE_LOG_FILE, "w") as f:
            json.dump({}, f)
    try:
        with open(MESSAGE_LOG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des logs de messages: {e}")
        return {}

def save_message_log_channel(data):
    """Sauvegarde les données du canal de log des messages."""
    try:
        with open(MESSAGE_LOG_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des logs de messages: {e}")

def load_loans():
    """Charge les données des prêts."""
    if not os.path.exists(LOANS_FILE):
        with open(LOANS_FILE, "w") as f:
            json.dump([], f)
    try:
        with open(LOANS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des prêts: {e}")
        return []

def save_loans(loans_data):
    """Sauvegarde les données des prêts."""
    try:
        with open(LOANS_FILE, "w") as f:
            json.dump(loans_data, f)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des prêts: {e}")

def load_pib():
    """Charge les données du PIB."""
    if not os.path.exists(PIB_FILE):
        return {}  # Ne crée pas le fichier, retourne juste un dict vide
    try:
        with open(PIB_FILE, "r") as f:
            data = json.load(f)
        
        # Nettoyer les données corrompues
        cleaned_data = {}
        for role_id, pib_value in data.items():
            if isinstance(pib_value, (int, float)):
                cleaned_data[role_id] = pib_value
            else:
                print(f"[DEBUG] PIB corrompu pour role {role_id}: {pib_value}, converti en 0")
                cleaned_data[role_id] = 0
        
        # Si des données ont été nettoyées, sauvegarder
        if len(cleaned_data) != len(data) or any(cleaned_data[k] != data[k] for k in cleaned_data):
            print("[DEBUG] Données PIB corrompues détectées, nettoyage automatique...")
            save_pib(cleaned_data)
        
        return cleaned_data
    except Exception as e:
        print(f"Erreur lors du chargement du PIB: {e}")
        return {}

def save_pib(pib_data):
    """Sauvegarde les données du PIB et synchronise avec PostgreSQL."""
    try:
        # Filtrer les rôles exclus avant la sauvegarde
        filtered_pib = {role_id: pib for role_id, pib in pib_data.items() 
                       if is_valid_country_role(role_id)}
        
        # Si le dictionnaire est vide, supprimer le fichier
        if not filtered_pib:
            if os.path.exists(PIB_FILE):
                os.remove(PIB_FILE)
                print("Fichier pib.json supprimé car aucun pays n'a de PIB.")
        else:
            # Créer le fichier seulement s'il y a des données
            with open(PIB_FILE, "w") as f:
                json.dump(filtered_pib, f, indent=2)
        save_all_json_to_postgres()
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du PIB: {e}")

def load_pays_log_channel():
    """Charge les données du canal de log des pays."""
    if not os.path.exists(PAYS_LOG_FILE):
        with open(PAYS_LOG_FILE, "w") as f:
            json.dump({}, f)
    try:
        with open(PAYS_LOG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement du canal de log des pays: {e}")
        return {}

def save_pays_log_channel(data):
    """Sauvegarde les données du canal de log des pays."""
    try:
        with open(PAYS_LOG_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du canal de log des pays: {e}")

def load_centres_tech():
    """Charge les données des centres technologiques."""
    if not os.path.exists(CENTRES_TECH_FILE):
        return {}
    try:
        with open(CENTRES_TECH_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement des centres tech: {e}")
        return {}

def save_centres_tech(data):
    """Sauvegarde les données des centres technologiques."""
    try:
        with open(CENTRES_TECH_FILE, "w") as f:
            json.dump(data, f, indent=2)
        save_all_json_to_postgres()
    except Exception as e:
        print(f"[ERROR] Erreur lors de la sauvegarde des centres tech: {e}")

def get_centre_emplacements(niveau):
    """Retourne le nombre d'emplacements selon le niveau du centre."""
    if niveau == 1:
        return CENTRE_EMPLACEMENTS_BASE
    elif niveau == 2:
        return CENTRE_EMPLACEMENTS_BASE + 1
    elif niveau == 3:
        return CENTRE_EMPLACEMENTS_BASE + 2
    return CENTRE_EMPLACEMENTS_BASE

def get_centre_cout_amelioration(niveau_actuel):
    """Retourne le coût d'amélioration selon le niveau actuel."""
    if niveau_actuel == 1:
        return CENTRE_AMELIORATION_1
    elif niveau_actuel == 2:
        return CENTRE_AMELIORATION_2
    return 0  # Niveau max atteint

def get_domaine_from_tech(tech_name):
    """Détermine le domaine d'une technologie à partir de son nom."""
    tech_lower = tech_name.lower()
    
    # Mots-clés pour chaque domaine
    if any(keyword in tech_lower for keyword in ["char", "tank", "artillerie", "infanterie", "terrestre"]):
        return "Terrestre"
    elif any(keyword in tech_lower for keyword in ["avion", "chasseur", "bombardier", "hélicoptère", "aérien"]):
        return "Aérien"
    elif any(keyword in tech_lower for keyword in ["naval", "destroyer", "frégate", "sous-marin", "marine"]):
        return "Marine"
    elif any(keyword in tech_lower for keyword in ["nucléaire", "bombe", "missile", "destruction", "amd"]):
        return "Armes de Destruction Massive"
    elif any(keyword in tech_lower for keyword in ["satellite", "fusée", "spatial", "orbite"]):
        return "Spatial"
    else:
        return "Terrestre"  # Par défaut

## Fonction de sauvegarde du canal de statut supprimée (obsolète)

def log_transaction(from_id, to_id, amount, transaction_type, guild_id):
    """
    Journalise une transaction dans l'historique, sans modifier les balances.
    Les balances sont déjà modifiées par les commandes correspondantes.
    """
    transaction = {
        "from_id": from_id,
        "to_id": to_id,
        "amount": amount,
        "timestamp": int(time.time()),
        "type": transaction_type,
        "guild_id": guild_id
    }
    
    # Charger les transactions existantes
    transactions = []
    if os.path.exists(TRANSACTION_LOG_FILE):
        try:
            with open(TRANSACTION_LOG_FILE, "r") as f:
                transactions = json.load(f)
        except json.JSONDecodeError:
            transactions = []
    
    # Ajouter la nouvelle transaction
    transactions.append(transaction)
    
    # Limiter l'historique à 1000 transactions
    if len(transactions) > 1000:
        transactions = transactions[-1000:]
    
    # Sauvegarder les transactions
    try:
        with open(TRANSACTION_LOG_FILE, "w") as f:
            json.dump(transactions, f)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la transaction: {e}")
    
    # Ne PAS modifier les balances ici, car elles sont déjà modifiées par les commandes

# ===== FONCTION DE LOG =====

# Fonction pour envoyer un log au format embed
async def send_log(guild, message=None, embed=None):
    """
    Envoie un message dans le salon de log économique du serveur.
    Prend soit un message texte simple, soit un embed déjà formaté.
    """
    log_channel_id = log_channel_data.get(str(guild.id))
    if log_channel_id:
        channel = guild.get_channel(int(log_channel_id))
        if channel:
            try:
                # Si un embed est déjà fourni, l'utiliser directement
                if embed:
                    await channel.send(embed=embed)
                # Sinon créer un embed à partir du message texte
                elif message:
                    log_embed = discord.Embed(
                        description=f"{message}{INVISIBLE_CHAR}",
                        color=EMBED_COLOR,
                        timestamp=datetime.datetime.now()
                    )
                    await channel.send(embed=log_embed)
            except Exception as e:
                print(f"Erreur lors de l'envoi du log: {e}")

# Fonction pour envoyer un log de pays
async def send_pays_log(guild, embed):
    """Envoie un embed dans le salon de log des pays du serveur."""
    pays_log_channel_id = pays_log_channel_data.get(str(guild.id))
    if pays_log_channel_id:
        channel = guild.get_channel(int(pays_log_channel_id))
        if channel:
            try:
                await channel.send(embed=embed)
            except Exception as e:
                print(f"Erreur lors de l'envoi du log de pays: {e}")

# Fonction pour envoyer un log de mute
async def send_mute_log(guild, embed):
    """Envoie un embed dans le salon de log des sanctions mute/unmute du serveur."""
    mute_log_channel_id = mute_log_channel_data.get(str(guild.id))
    if mute_log_channel_id:
        channel = guild.get_channel(int(mute_log_channel_id))
        if channel:
            try:
                await channel.send(embed=embed)
            except Exception as e:
                print(f"Erreur lors de l'envoi du log mute: {e}")

# ===== TÂCHES PLANIFIÉES =====

@loop(minutes=10)
async def auto_save_economy():
    """Sauvegarde automatique de l'économie."""
    try:
        print("Sauvegarde automatique de l'économie...")
        save_balances(balances)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde automatique: {e}")

@loop(hours=12)
async def verify_and_fix_balances():
    """Vérifie et corrige les balances périodiquement."""
    try:
        print("Vérification périodique des balances...")
        
        # Recherche des montants anormalement élevés
        abnormal_balances = {}
        for role_id, amount in balances.items():
            if len(role_id) >= 18 and amount > 3000000000:  # Plus de 3 milliards est suspect
                corrected_amount = amount // 3
                abnormal_balances[role_id] = (amount, corrected_amount)
                balances[role_id] = corrected_amount
        
        if abnormal_balances:
            print(f"CORRECTION PÉRIODIQUE: {len(abnormal_balances)} soldes anormalement élevés ont été corrigés")
            for role_id, (old_amount, new_amount) in abnormal_balances.items():
                print(f"  - ID {role_id}: {old_amount} -> {new_amount}")
            save_balances(balances)
            
    except Exception as e:
        print(f"Erreur lors de la vérification périodique des balances: {e}")

# ===== GESTIONNAIRES DE SIGNAUX =====

def signal_handler(sig, frame):
    """Gestionnaire de signal pour la fermeture propre."""
    print(f"Signal {sig} reçu, fermeture en cours...")
    
    # Sauvegarde des données importantes
    try:
        save_balances(balances)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde finale: {e}")
    
    # Attendre un peu pour permettre la sauvegarde des données
    time.sleep(1)
    
    # Forcer la sortie sans attendre d'opérations asynchrones
    sys.exit(0)

def exit_handler():
    """Gestionnaire pour atexit."""
    global BOT_DISCONNECT_HANDLED
    if not BOT_DISCONNECT_HANDLED:
        print("Fermeture du bot en cours...")
        BOT_DISCONNECT_HANDLED = True
        
        # Sauvegarde des données importantes
        try:
            save_balances(balances)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde finale: {e}")

def verify_economy_data(bot):
    """Vérifie l'intégrité des données économiques au démarrage."""
    print("Vérification des données économiques...")
    
    # Vérifier les balances négatives
    negative_balances = {}
    for entity_id, amount in balances.items():
        if amount < 0:
            negative_balances[entity_id] = amount
            # Correction automatique
            balances[entity_id] = 0
    
    if negative_balances:
        print(f"AVERTISSEMENT: {len(negative_balances)} soldes négatifs ont été corrigés")
        save_balances(balances)
    
    # Correction des montants anormalement élevés
    abnormal_balances = {}
    for role_id, amount in balances.items():
        # Vérifier si c'est un rôle et non un utilisateur (les IDs de rôle ont généralement 18-19 chiffres)
        if len(role_id) >= 18 and amount > 3000000000:  # Plus de 3 milliards est suspect
            # Calcul de la valeur normale (divisé par 3 car semble être triplé)
            corrected_amount = amount // 3
            abnormal_balances[role_id] = (amount, corrected_amount)
            balances[role_id] = corrected_amount
            print(f"Correction de balance pour ID {role_id}: {amount} -> {corrected_amount}")
    
    if abnormal_balances:
        print(f"AVERTISSEMENT: {len(abnormal_balances)} soldes anormalement élevés ont été corrigés")
        save_balances(balances)
    
    print("Vérification des données économiques terminée")

def verify_and_fix_budgets():
    """Vérifie et corrige les budgets au démarrage du bot."""
    print("Vérification des budgets...")
    
    # Identifier les budgets problématiques (trop élevés)
    problematic_budgets = []
    for user_id, amount in balances.items():
        # Si le budget est supérieur à 2 milliards, c'est probablement une erreur
        if amount > 2000000000:
            problematic_budgets.append((user_id, amount))
    
    # Corriger les budgets problématiques
    for user_id, amount in problematic_budgets:
        print(f"Budget anormal détecté - ID: {user_id}, Montant: {amount}")
        
    print(f"Vérification terminée: {len(problematic_budgets)} budgets anormaux détectés")

# ===== ÉVÉNEMENTS DU BOT =====

@bot.event
async def on_message_delete(message):
    """Journalise les messages supprimés."""
    if message.guild is None:  # Ignore DM messages
        return
    # Ignore si le message vient d'un salon de logs
    log_channels = []
    log_channel_id = log_channel_data.get(str(message.guild.id))
    msg_log_channel_id = message_log_channel_data.get(str(message.guild.id))
    if log_channel_id:
        log_channels.append(int(log_channel_id))
    if msg_log_channel_id:
        log_channels.append(int(msg_log_channel_id))
    if message.channel.id in log_channels:
        return
    channel = None
    msg_log_channel_id = message_log_channel_data.get(str(message.guild.id))
    if msg_log_channel_id:
        channel = message.guild.get_channel(int(msg_log_channel_id))
    if channel:
        try:
            embed = discord.Embed(
                title="Message supprimé",
                description=f"**Auteur :** {message.author.mention}\n**Salon :** {message.channel.mention}\n**Contenu :**\n{message.content}",
                color=discord.Color.red()
            )
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Erreur lors de la journalisation d'un message supprimé: {e}")

@bot.event
async def on_message_edit(before, after):
    """Journalise les messages modifiés."""
    if before.guild is None:  # Ignore DM messages
        return
    if before.author.bot:
        return
    log_channels = []
    log_channel_id = log_channel_data.get(str(before.guild.id))
    msg_log_channel_id = message_log_channel_data.get(str(before.guild.id))
    if log_channel_id:
        log_channels.append(int(log_channel_id))
    if msg_log_channel_id:
        log_channels.append(int(msg_log_channel_id))
    if before.channel.id in log_channels:
        return
    # Fonction utilitaire pour obtenir le salon de log des messages
    def get_message_log_channel(guild):
        msg_log_channel_id = message_log_channel_data.get(str(guild.id))
        if msg_log_channel_id:
            return guild.get_channel(int(msg_log_channel_id))
        return None

    channel = get_message_log_channel(before.guild)
    if channel:
        try:
            embed = discord.Embed(
                title="Message modifié",
                description=f"**Auteur :** {before.author.mention}\n**Salon :** {before.channel.mention}\n**Avant :**\n{before.content}\n**Après :**\n{after.content}",
                color=discord.Color.orange()
            )
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Erreur lors de la journalisation d'un message modifié: {e}")

@bot.event
async def on_command_error(ctx, error):
    """Gère les erreurs de commandes."""
    print(f"Erreur de commande: {error}")

@bot.event
async def on_error(event, *args, **kwargs):
    """Gère les erreurs d'événements."""
    print(f"Erreur dans l'événement {event}: {sys.exc_info()[0]}")

# Ajout de l'événement on_message pour l'XP
xp_system_active = False  # Obsolète, remplacé par xp_system_status

@bot.event
async def on_message(message):
    global levels, xp_system_status, bonus_xp_active
    if message.author.bot or not message.guild:
        return
    
    # === SYSTÈME DE DÉBAT - Retrait automatique du rôle ===
    if message.channel.id == DEBAT_CHANNEL_ID:
        debat_role = message.guild.get_role(DEBAT_ROLE_ID)
        if debat_role and debat_role in message.author.roles:
            try:
                await message.author.remove_roles(debat_role, reason="A parlé dans le salon débat")
                print(f"[DEBAT] Rôle débat retiré à {message.author} (ID: {message.author.id}) pour avoir parlé dans le salon débat")
            except discord.Forbidden:
                print(f"[DEBAT] Impossible de retirer le rôle débat à {message.author} - permissions insuffisantes")
            except Exception as e:
                print(f"[DEBAT] Erreur lors du retrait du rôle débat à {message.author}: {e}")
    
    guild_id = str(message.guild.id)
    if not xp_system_status["servers"].get(guild_id, False):
        await bot.process_commands(message)
        return
    user_id = str(message.author.id)
    if user_id not in levels:
        levels[user_id] = {"xp": 0, "level": 1}
    
    # Vérifier si le bonus XP est actif et encore valide
    bonus_active = False
    if guild_id in bonus_xp_active:
        import time
        if time.time() < bonus_xp_active[guild_id]:
            bonus_active = True
        else:
            # Bonus expiré, le supprimer
            del bonus_xp_active[guild_id]
    
    # Calcul XP : 1 XP de base + 1 XP tous les 10 caractères
    char_count = len(message.content)
    
    # Bonus XP par grade acquis
    palier_roles = {
        10: 1427993128811626606,
        20: 1417893555376230570,
        30: 1417893729066291391,
        40: 1417893878136176680,
        50: 1417894464122261555,
        60: 1417894846844244139,
        70: 1417895041862733986,
        80: 1417895157553958922,
        90: 1417895282443812884,
        100: 1417895415273099404
    }
    member = message.guild.get_member(message.author.id)
    bonus_grade = 0
    if member:
        for i, role_id in enumerate(palier_roles.values(), start=1):
            if discord.utils.get(member.roles, id=role_id):
                bonus_grade += i
    
    # Rôle spécial
    special_role_id = 1393303261519417385
    has_special = member and discord.utils.get(member.roles, id=special_role_id)
    
    # XP de base
    xp_chair = char_count // 10  # XP chair (1 XP tous les 10 caractères)
    if has_special:
        xp_gain = 5 + (char_count // 15) * 2 + xp_chair
    else:
        xp_gain = 2 + xp_chair + bonus_grade
    
    # Ajouter le bonus temporaire si actif
    if bonus_active:
        xp_gain += 3  # +3 XP par message
        xp_gain += (char_count // 10) * 2  # +2 XP tous les 10 caractères (en plus du bonus existant)
    
    levels[user_id]["xp"] += xp_gain
    
    # Vérifier si l'utilisateur a assez d'XP pour passer au niveau suivant
    current_level = levels[user_id]["level"]
    current_xp = levels[user_id]["xp"]
    xp_needed = xp_for_level(current_level)
    
    # Gérer les montées de niveau
    while current_xp >= xp_needed and xp_needed is not None:
        current_xp -= xp_needed
        current_level += 1
        xp_needed = xp_for_level(current_level)
    
    # Mettre à jour les données
    old_level = levels[user_id]["level"]
    levels[user_id]["level"] = current_level
    levels[user_id]["xp"] = current_xp
    
    save_levels(levels)
    try:
        save_all_json_to_postgres()
    except Exception as e:
        print(f"[ERROR] Sauvegarde PostgreSQL après message : {e}")
    
    # Vérifier si niveau a augmenté
    if current_level > old_level:
        # Gestion des rôles de palier pour chaque niveau gagné
        for level_gained in range(old_level + 1, current_level + 1):
            palier_roles = {
                10: 1427993128811626606,
                20: 1417893555376230570,
                30: 1417893729066291391,
                40: 1417893878136176680,
                50: 1417894464122261555,
                60: 1417894846844244139,
                70: 1417895041862733986,
                80: 1417895157553958922,
                90: 1417895282443812884,
                100: 1417895415273099404
            }
            palier = (level_gained // 10) * 10
            member = message.guild.get_member(message.author.id)
            # Ajout du nouveau rôle de palier si atteint
            if palier in palier_roles and member and level_gained % 10 == 0:
                new_role = message.guild.get_role(palier_roles[palier])
                if new_role:
                    await member.add_roles(new_role)
                    # Retrait de l'ancien rôle de palier
                    old_palier = palier - 10
                    if old_palier in palier_roles:
                        old_role = message.guild.get_role(palier_roles[old_palier])
                        if old_role:
                            await member.remove_roles(old_role)
                    # Log d'attribution du rôle (embed stylisé)
                    lvl_channel_id = lvl_log_channel_data.get(guild_id)
                    if lvl_channel_id:
                        channel = message.guild.get_channel(int(lvl_channel_id))
                        if channel:
                            embed = discord.Embed(
                                description=(
                                    "⠀\n"
                                    f"> ## {message.author.mention} a obtenu le grade de {new_role.mention} au **niveau {level_gained} !** 🎉\n"
                                    "⠀"
                                ),
                                color=0x162e50
                            )
                            embed.set_image(url="https://cdn.discordapp.com/attachments/1412872314525192233/1417983114390536363/PAX_RUINAE_5.gif?ex=68cc772f&is=68cb25af&hm=f095b505d44febce0e7a8cbf52fea9ac14c79aacaa17762ec66cb4d22ccc6b4d&")
                            await channel.send(embed=embed)
        # Log passage de niveau (embed stylisé)
        lvl_channel_id = lvl_log_channel_data.get(guild_id)
        if lvl_channel_id:
            channel = message.guild.get_channel(int(lvl_channel_id))
            if channel:
                embed = discord.Embed(
                    description=(
                        "⠀\n"
                        f"> ## {message.author.mention} est passé au **niveau {levels[user_id]['level']} !** 🎉\n"
                        "⠀"
                    ),
                    color=0x162e50
                )
                embed.set_image(url="https://cdn.discordapp.com/attachments/1412872314525192233/1417983114390536363/PAX_RUINAE_5.gif?ex=68cc772f&is=68cb25af&hm=f095b505d44febce0e7a8cbf52fea9ac14c79aacaa17762ec66cb4d22ccc6b4d&")
                await channel.send(embed=embed)
# Commande pour ajouter de l'XP à un membre

# ===== COMMANDES DE BASE =====

@bot.tree.command(name="setlogeconomy", description="Définit le salon de logs pour l'économie")
@app_commands.checks.has_permissions(administrator=True)
async def setlogeconomy(interaction: discord.Interaction, channel: discord.TextChannel):
    log_channel_data[str(interaction.guild.id)] = channel.id
    save_log_channel(log_channel_data)
    embed = discord.Embed(
        description=f"> Salon de logs défini sur {channel.mention}.{INVISIBLE_CHAR}",
        color=EMBED_COLOR
    )
    embed.set_image(url=IMAGE_URL)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Fonction utilitaire pour convertir les majuscules en caractères spéciaux
def is_valid_image_url(url):
    """Vérifie si l'URL pointe vers une image valide."""
    if not url:
        return False
    # ...existing code...
    # Traitement XP, économie, etc. (déjà présent)
    # Synchronisation automatique PostgreSQL à chaque message
    try:
        save_all_json_to_postgres()
    except Exception as e:
        print(f"[ERROR] Sauvegarde PostgreSQL après message : {e}")
    # ...existing code...
    # Vérification simple des extensions d'image communes
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    url_lower = url.lower()
    
    # Vérifier si l'URL se termine par une extension d'image
    for ext in image_extensions:
        if url_lower.endswith(ext):
            return True
    
    # Vérifier si c'est une URL d'hébergement d'images connue
    image_hosts = ['imgur.com', 'i.imgur.com', 'zupimages.net', 'tenor.com', 
                   'media.discordapp.net', 'cdn.discordapp.com']
    
    for host in image_hosts:
        if host in url_lower:
            return True
    
    # URLs qui contiennent des paramètres mais sont des images
    if re.search(r'\.(jpg|jpeg|png|gif|webp|bmp)(\?|#)', url_lower):
        return True
    
    return False

def convert_to_bold_letters(text):
    """Convertit les lettres majuscules en caractères gras spéciaux."""
    bold_letters = {
        'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘', 'F': '𝗙', 'G': '𝗚', 'H': '𝗛', 'I': '𝗜',
        'J': '𝗝', 'K': '𝗞', 'L': '𝗟', 'M': '𝗠', 'N': '𝗡', 'O': '𝗢', 'P': '𝗣', 'Q': '𝗤', 'R': '𝗥',
        'S': '𝗦', 'T': '𝗧', 'U': '𝗨', 'V': '𝗩', 'W': '𝗪', 'X': '𝗫', 'Y': '𝗬', 'Z': '𝗭'
    }
    
    result = ""
    for char in text:
        if char.isupper() and char in bold_letters:
            result += bold_letters[char]
        else:
            result += char
    
    return result

# Pour la commande creer_pays, ajouter ces rôles à la gestion
@bot.tree.command(name="creer_pays", description="Crée un nouveau pays avec son rôle et son salon")
@app_commands.describe(
    nom="Nom du pays",
    budget="Budget initial du pays",
    pib="PIB du pays (valeur informative)",
    continent="Continent auquel appartient le pays",
    categorie="Catégorie où créer le salon du pays",
    dirigeant="Utilisateur qui sera le dirigeant du pays",
    drapeau_salon="Emoji à ajouter au début du nom du pays (facultatif)",
    drapeau_perso="Emoji personnalisé du pays pour les messages et l'icône du rôle (facultatif)",
    couleur="Code couleur hexadécimal pour le rôle (ex: #FF0000 pour rouge, facultatif)",
    image="URL d'une image représentant le pays (facultatif)",
    nom_salon_secret="Nom du salon secret à créer (facultatif)",
    categorie_secret="Catégorie où créer le salon secret (facultatif)",
    economie="Type d'économie du pays (facultatif)",
    regime_politique="Régime politique du pays (facultatif)",
    gouvernement="Forme de gouvernement du pays (facultatif)"
)
@app_commands.choices(continent=[
    discord.app_commands.Choice(name="Europe", value="1413995502785138799"),
    discord.app_commands.Choice(name="Afrique", value="1413995608922128394"),
    discord.app_commands.Choice(name="Amérique", value="1413995735732457473"),
    discord.app_commands.Choice(name="Asie", value="1413995874304004157"),
    discord.app_commands.Choice(name="Océanie", value="1413996176956461086")
])
@app_commands.choices(economie=[
    discord.app_commands.Choice(name="Économie ultra-libérale", value="1417234199353622569"),
    discord.app_commands.Choice(name="Économie libérale", value="1417234220115431434"),
    discord.app_commands.Choice(name="Économie mixte", value="1417234887508754584"),
    discord.app_commands.Choice(name="Socialisme de marché", value="1417234944832442621"),
    discord.app_commands.Choice(name="Économie planifiée", value="1417234931146555433"),
    discord.app_commands.Choice(name="Économie dirigiste", value="1417235038168289290"),
    discord.app_commands.Choice(name="Économie corporatiste", value="1417235052814794853")
])
@app_commands.choices(regime_politique=[
    discord.app_commands.Choice(name="Démocratie", value="1417251476782448843"),
    discord.app_commands.Choice(name="Autoritarisme", value="1417251480573968525"),
    discord.app_commands.Choice(name="Totalitarisme", value="1417251556776218654"),
    discord.app_commands.Choice(name="Monarchie", value="1417251565068226691"),
    discord.app_commands.Choice(name="Oligarchie", value="1417251568327200828"),
    discord.app_commands.Choice(name="Théocratie", value="1417251571661537320"),
    discord.app_commands.Choice(name="Technocratie", value="1417251574568456232"),
    discord.app_commands.Choice(name="Régime populaire", value="1417251577714053170"),
    discord.app_commands.Choice(name="Régime militaire", value="1417252579766829076")
])
@app_commands.choices(gouvernement=[
    discord.app_commands.Choice(name="Régime parlementaire", value="1417254283694313652"),
    discord.app_commands.Choice(name="Régime présidentielle", value="1417254315684528330"),
    discord.app_commands.Choice(name="République parlementaire", value="1417254344180371636"),
    discord.app_commands.Choice(name="République présidentielle", value="1417254681243025428"),
    discord.app_commands.Choice(name="Monarchie parlementaire", value="1417254399004246161"),
    discord.app_commands.Choice(name="Monarchie absolue", value="1417254501110251540"),
    discord.app_commands.Choice(name="Gouvernement directorial", value="1417254550951428147"),
    discord.app_commands.Choice(name="Gouvernement de Transition", value="1417254582156791908"),
    discord.app_commands.Choice(name="Gouvernement populaire", value="1417254615224680508"),
    discord.app_commands.Choice(name="Stratocratie", value="1417254639069560904"),
    discord.app_commands.Choice(name="Aucun gouvernement", value="1417254809253314590")
])
@app_commands.choices(religion=[
    discord.app_commands.Choice(name="Catholicisme", value="1417622211329659010"),
    discord.app_commands.Choice(name="Protestantisme", value="1417622670702280845"),
    discord.app_commands.Choice(name="Orthodoxie", value="1417622925745586206"),
    discord.app_commands.Choice(name="Sunnisme", value="1417623400695988245"),
    discord.app_commands.Choice(name="Chiisme", value="1417624032131682304"),
    discord.app_commands.Choice(name="Judaïsme", value="1417624442905038859"),
    discord.app_commands.Choice(name="Hindouisme", value="1417625845425766562"),
    discord.app_commands.Choice(name="Bouddhisme", value="1417626007770366123"),
    discord.app_commands.Choice(name="Shintoïsme", value="1424945271858528326"),
    discord.app_commands.Choice(name="Laïcisme", value="1417626204885745805"),
    discord.app_commands.Choice(name="Athéisme", value="1417626362738512022"),
    discord.app_commands.Choice(name="Tengrisme", value="1424789872329101498"),
    discord.app_commands.Choice(name="Foi des Sept", value="1419446723310256138"),
    discord.app_commands.Choice(name="Dieu Noyé", value="1424783855331577856"),
    discord.app_commands.Choice(name="Culte de Solaria", value="1425197116858437653"),
])
@app_commands.choices(religion=[
    discord.app_commands.Choice(name="Catholicisme", value="1417622211329659010"),
    discord.app_commands.Choice(name="Protestantisme", value="1417622670702280845"),
    discord.app_commands.Choice(name="Orthodoxie", value="1417622925745586206"),
    discord.app_commands.Choice(name="Sunnisme", value="1417623400695988245"),
    discord.app_commands.Choice(name="Chiisme", value="1417624032131682304"),
    discord.app_commands.Choice(name="Judaïsme", value="1417624442905038859"),
    discord.app_commands.Choice(name="Hindouisme", value="1417625845425766562"),
    discord.app_commands.Choice(name="Bouddhisme", value="1417626007770366123"),
    discord.app_commands.Choice(name="Shintoïsme", value="1424945271858528326"),
    discord.app_commands.Choice(name="Laïcisme", value="1417626204885745805"),
    discord.app_commands.Choice(name="Athéisme", value="1417626362738512022"),
    discord.app_commands.Choice(name="Tengrisme", value="1424789872329101498"),
    discord.app_commands.Choice(name="Foi des Sept", value="1419446723310256138"),
    discord.app_commands.Choice(name="Dieu Noyé", value="1424783855331577856"),
    discord.app_commands.Choice(name="Culte de Solaria", value="1425197116858437653"),
])
async def creer_pays(
    interaction: discord.Interaction, 
    nom: str,
    budget: int,
    pib: int,
    continent: str,
    categorie: discord.CategoryChannel,
    dirigeant: discord.Member,
    drapeau_salon: str = None,
    drapeau_perso: str = None,
    couleur: str = None,
    image: str = None,
    nom_salon_secret: str = None,
    categorie_secret: discord.CategoryChannel = None,
    economie: str = None,
    regime_politique: str = None,
    gouvernement: str = None,
    religion: str = None
):
    """Crée un nouveau pays avec son rôle et son salon."""
    await interaction.response.defer()
    
    # Vérifier les permissions pour créer des pays
    if not has_country_management_permissions(interaction):
        embed = discord.Embed(
            title="❌ Permission refusée",
            description="Vous n'avez pas les permissions nécessaires pour créer des pays.",
            color=0xff4444
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    # Vérifier que le budget est positif
    ROLE_PAYS_PAR_DEFAUT = 1417253039491776733
    if budget <= 0:
        await interaction.followup.send("> Le budget initial doit être positif.", ephemeral=True)
        return
    
    # Image par défaut ou personnalisée
    pays_image = IMAGE_URL
    if image and is_valid_image_url(image):
        pays_image = image
    
    # Emoji par défaut ou personnalisé
    emoji_pays = drapeau_salon if drapeau_salon else ""
    emoji_message = drapeau_perso if drapeau_perso else "🏛️"
    
    # IDs des rôles à gérer
    # Ajout des rôles économie, régime politique, gouvernement et rôle par défaut
    roles_a_ajouter = [ROLE_PAYS_PAR_DEFAUT]
    if economie:
        roles_a_ajouter.append(int(economie))
    if regime_politique:
        roles_a_ajouter.append(int(regime_politique))
    if gouvernement:
        roles_a_ajouter.append(int(gouvernement))
    # Ajout du rôle de continent
    if continent:
        roles_a_ajouter.append(int(continent))
    # Attribution des rôles au dirigeant
    for role_id in roles_a_ajouter:
        role_obj = interaction.guild.get_role(role_id)
        if role_obj and role_obj not in dirigeant.roles:
            await dirigeant.add_roles(role_obj, reason="Création du pays")
    ROLE_JOUEUR_ID = 1410289640170328244
    ROLE_NON_JOUEUR_ID = 1393344053608710315
    
    # Liste des rôles à ajouter automatiquement
    auto_roles_ids = [
        1413995329656852662,
        1413997188089909398,
        1413993747515052112,
        1413995073632207048,
        1413993786001985567,
        1413994327473918142,
        1413994277029023854,
        1413993819292045315,
        1413994233622302750,
        1413995459827077190,
        ROLE_JOUEUR_ID  # Ajouter le rôle de joueur
    ]
    
    try:
        # Obtenir le rôle de continent pour positionner le nouveau rôle
        continent_role = interaction.guild.get_role(int(continent))
        if not continent_role:
            await interaction.followup.send(f"> Erreur: Rôle de continent introuvable (ID: {continent}).", ephemeral=True)
            return
        print(f"[DEBUG] Rôle continent trouvé : {continent_role.name}")

        # Créer le rôle
        role_name = f"{emoji_pays}・❝ ｢ {nom} ｣ ❞" if emoji_pays else f"❝ ｢ {nom} ｣ ❞"
        role_kwargs = {"name": role_name, "mentionable": True}
        if couleur:
            try:
                if couleur.startswith('#'):
                    couleur = couleur[1:]
                color_value = int(couleur, 16)
                role_kwargs["color"] = discord.Color(color_value)
            except ValueError:
                pass  # Utiliser la couleur par défaut
        print(f"[DEBUG] Création du rôle pays : {role_name}")
        role = await interaction.guild.create_role(**role_kwargs)
        
        # Définir l'emoji drapeau_perso comme icône du rôle si fourni
        if drapeau_perso:
            try:
                # Vérifier si c'est un emoji unicode ou personnalisé
                if drapeau_perso.startswith('<:') or drapeau_perso.startswith('<a:'):
                    # Emoji personnalisé Discord
                    await role.edit(display_icon=drapeau_perso)
                    print(f"[DEBUG] Icône du rôle définie sur l'emoji personnalisé : {drapeau_perso}")
                else:
                    # Emoji unicode
                    await role.edit(unicode_emoji=drapeau_perso)
                    print(f"[DEBUG] Icône du rôle définie sur l'emoji unicode : {drapeau_perso}")
            except Exception as e:
                print(f"[ERROR] Impossible de définir l'emoji comme icône de rôle : {e}")
                # Fallback : essayer avec display_icon si unicode_emoji échoue
                try:
                    await role.edit(display_icon=drapeau_perso)
                    print(f"[DEBUG] Icône du rôle définie via display_icon : {drapeau_perso}")
                except Exception as e2:
                    print(f"[ERROR] Échec total pour l'icône de rôle : {e2}")
        # Enregistrement du budget dans balances
        print(f"[DEBUG] Enregistrement du budget pour le pays {role.id} : {budget}")
        balances[str(role.id)] = budget
        save_balances(balances)
        
        # Initialisation du PIB
        pib_data = load_pib()
        pib_data[str(role.id)] = {"pib": pib}

        # Positionner le rôle pays juste en dessous du rôle de continent
        try:
            server_roles = await interaction.guild.fetch_roles()
            continent_position = continent_role.position
            positions = {role: continent_position - 1}
            await interaction.guild.edit_role_positions(positions)
        except Exception as e:
            print(f"[ERROR] Positionnement du rôle pays : {e}")

        # Création du salon principal
        formatted_name = convert_to_bold_letters(nom)
        channel_name = f"【{emoji_pays}】・{formatted_name.lower().replace(' ', '-')}" if emoji_pays else f"【】・{formatted_name.lower().replace(' ', '-') }"
        
        print(f"[DEBUG] Création du salon principal : {channel_name}")
        print(f"[DEBUG] Catégorie utilisée : {categorie.name} (ID: {categorie.id})")
        
        # Créer le salon avec synchronisation de la catégorie
        channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=categorie
            # Pas d'overwrites = synchronisation automatique avec la catégorie
        )
        
        print(f"[DEBUG] Salon créé, permissions héritées de la catégorie")
        # Petit délai pour assurer la synchronisation
        await asyncio.sleep(0.5)
        
        # Ajouter les permissions spécifiques du rôle de pays SANS écraser les autres
        print(f"[DEBUG] Ajout des permissions pour le rôle {role.name}")
        await channel.set_permissions(
            role,
            read_messages=True,
            send_messages=True,
            read_message_history=True,
            embed_links=True,
            attach_files=True,
            add_reactions=True,
            send_messages_in_threads=True,
            create_public_threads=True,
            create_private_threads=True,
            manage_webhooks=True,
            manage_messages=True
        )
        print(f"[DEBUG] Permissions du rôle de pays appliquées")
        pays_log_channel_data[str(role.id)] = channel.id
        save_pays_log_channel(pays_log_channel_data)
        print(f"[DEBUG] Salon principal créé : {channel.name}")

        # Ajout des rôles au dirigeant
        try:
            print("[DEBUG] Ajout des rôles au dirigeant...")
            await dirigeant.add_roles(role)
            await dirigeant.add_roles(continent_role)
            # Ajout des rôles de base
            for base_role_id in [1417619445060206682, 1417619843611627530]:
                base_role = interaction.guild.get_role(base_role_id)
                if base_role and base_role not in dirigeant.roles:
                    await dirigeant.add_roles(base_role)
            # Ajout du rôle de religion si précisé
            if religion:
                role_religion = interaction.guild.get_role(int(religion))
                if role_religion and role_religion not in dirigeant.roles:
                    await dirigeant.add_roles(role_religion)
        except Exception as e:
            print(f"[ERROR] Ajout des rôles au dirigeant : {e}")

        # Ajout du rôle joueur et retrait du rôle non-joueur
        await asyncio.sleep(0)
        # Ajout du rôle joueur et retrait du rôle non-joueur
        role_joueur_id = 1410289640170328244
        role_non_joueur_id = 1393344053608710315
        role_joueur = interaction.guild.get_role(role_joueur_id)
        role_non_joueur = interaction.guild.get_role(role_non_joueur_id)
        if role_joueur:
            await dirigeant.add_roles(role_joueur)
        if role_non_joueur and role_non_joueur in dirigeant.roles:
            await dirigeant.remove_roles(role_non_joueur)

        # Ajout des rôles automatiques
        try:
            print("[DEBUG] Ajout des rôles automatiques...")
            for auto_role_id in auto_roles_ids:
                auto_role = interaction.guild.get_role(auto_role_id)
                if auto_role:
                    await dirigeant.add_roles(auto_role)
        except Exception as e:
            print(f"[ERROR] Ajout des rôles automatiques : {e}")

        # Enregistrement de l'image si fournie
        try:
            print("[DEBUG] Enregistrement de l'image du pays...")
            if image and is_valid_image_url(image):
                pays_images[str(role.id)] = image
        except Exception as e:
            print(f"[ERROR] Enregistrement image pays : {e}")

        # Initialisation du PIB (déjà fait)
        try:
            print("[DEBUG] Initialisation du PIB...")
        except Exception as e:
            print(f"[ERROR] Initialisation personnel : {e}")

        # Sauvegarde des données
        try:
            print("[DEBUG] Sauvegarde des données...")
            save_balances(balances)
            save_pib(pib_data)
            save_pays_images(pays_images)
            save_all_json_to_postgres()
        except Exception as e:
            print(f"[ERROR] Sauvegarde des données : {e}")

        # Envoi du message embed de confirmation
        try:
            print("[DEBUG] Envoi du message embed de confirmation...")
            regime_role = interaction.guild.get_role(int(regime_politique)) if regime_politique else None
            gouvernement_role = interaction.guild.get_role(int(gouvernement)) if gouvernement else None
            religion_role = interaction.guild.get_role(int(religion)) if religion else None
            continent_role_obj = interaction.guild.get_role(int(continent)) if continent else None
            drapeau_emoji = drapeau_perso if drapeau_perso else ""
            embed = discord.Embed(
                title="🏛️ | Nouveau pays enregistré",
                description=(
                    "⠀\n"
                    f"> − **Nom du pays :** {nom}\n"
                    f"> − **Budget :** {format_number(budget)}\n"
                    f"> − **PIB :** {format_number(pib)}\n"
                    "> \n"
                    f"> − **Continent :** {continent_role_obj.mention if continent_role_obj else 'Non défini'}\n"
                    f"> − **Régime politique :** {regime_role.mention if regime_role else 'Non défini'}\n"
                    f"> − **Forme de Gouvernement :** {gouvernement_role.mention if gouvernement_role else 'Non défini'}\n"
                    f"> − **Religion d'État :** {religion_role.mention if religion_role else 'Non défini'}\n"
                    "> \n"
                    f"> − **Drapeau personnalisé :** {drapeau_emoji}\n⠀"
                ),
                color=0xebe3bd
            )
            embed.set_image(url=image if image and is_valid_image_url(image) else IMAGE_URL)
            await interaction.followup.send(embed=embed)
            # Envoi du message de bienvenue dans le salon spécifique
            bienvenue_channel_id = 1393945519327281153
            bienvenue_channel = interaction.guild.get_channel(bienvenue_channel_id)
            if bienvenue_channel:
                # Récupération des rôles pour l'affichage
                regime_role = interaction.guild.get_role(int(regime_politique)) if regime_politique else None
                gouvernement_role = interaction.guild.get_role(int(gouvernement)) if gouvernement else None
                religion_role = interaction.guild.get_role(int(religion)) if religion else None
                continent_role = interaction.guild.get_role(int(continent)) if continent else None
                drapeau_emoji = drapeau_perso if drapeau_perso else ""
                bienvenue_embed = discord.Embed(
                    title="🏛️ | Un nouveau Pays fait son apparition",
                    description=(
                        "⠀\n"
                        f"> − **Nom du pays** : {role.mention}\n"
                        f"> − **Gouvernement** : {gouvernement_role.mention if gouvernement_role else 'Non défini'}\n"
                        f"> − **Régime Politique** : {regime_role.mention if regime_role else 'Non défini'}\n"
                        f"> − **Religion** : {religion_role.mention if religion_role else 'Non défini'}\n"
                        f"> − **Continent** : {continent_role.mention if continent_role else 'Non défini'}\n"
                        f"> − **Drapeau personnalisé** : {drapeau_emoji}\n"
                        "> \n"
                        f"> En te souhaitant une belle expérience {dirigeant.mention} sur **PAX RUINAE** !\n⠀"
                    ),
                    color=0x162e50
                )
                bienvenue_embed.set_image(url=image if image and is_valid_image_url(image) else IMAGE_URL)
                await bienvenue_channel.send(embed=bienvenue_embed)
        except Exception as e:
            print(f"[ERROR] Envoi embed confirmation : {e}")
            await interaction.followup.send(f"> Pays créé, mais erreur lors de l'envoi du message : {e}", ephemeral=True)

        # Créer le salon secret si demandé
        if nom_salon_secret and categorie_secret:
            try:
                formatted_secret_name = convert_to_bold_letters(nom_salon_secret)
                secret_channel_name = f"【{emoji_pays}】・{formatted_secret_name.lower().replace(' ', '-')}" if emoji_pays else f"【】・{formatted_secret_name.lower().replace(' ', '-') }"
                
                print(f"[DEBUG] Création du salon secret : {secret_channel_name}")
                print(f"[DEBUG] Catégorie secrète utilisée : {categorie_secret.name} (ID: {categorie_secret.id})")
                
                # Créer le salon avec synchronisation de la catégorie
                secret_channel = await interaction.guild.create_text_channel(
                    name=secret_channel_name,
                    category=categorie_secret
                    # Pas d'overwrites = synchronisation automatique avec la catégorie
                )
                
                print(f"[DEBUG] Salon secret créé, permissions héritées de la catégorie")
                # Petit délai pour assurer la synchronisation
                await asyncio.sleep(0.5)
                
                # Ajouter les permissions spécifiques du rôle de pays SANS écraser les autres
                print(f"[DEBUG] Ajout des permissions pour le rôle {role.name} sur le salon secret")
                await secret_channel.set_permissions(
                    role,
                    read_messages=True,
                    send_messages=True,
                    read_message_history=True,
                    embed_links=True,
                    attach_files=True,
                    add_reactions=True,
                    send_messages_in_threads=True,
                    create_public_threads=True,
                    create_private_threads=True,
                    manage_webhooks=True,
                    manage_messages=True
                )
                print(f"[DEBUG] Permissions du rôle de pays appliquées sur le salon secret")
            except Exception as e:
                print(f"[ERROR] Création salon secret : {e}")
                await interaction.followup.send(f"> Pays créé, mais erreur lors de la création du salon secret : {e}", ephemeral=True)

        # Log de l'action
        modifications = []
        modifications.append("Pays créé")
        modifications.append("Rôle attribué")
        modifications.append("Salon créé")
        modifications.append("Budget initialisé")
        log_embed = discord.Embed(
            title=f"🏛️ | Création de pays",
            description=f"> **Administrateur :** {interaction.user.mention}\n> **Pays créé : ** {role.mention}\n> **Modifications : ** {', '.join(modifications)}{INVISIBLE_CHAR}",
            color=EMBED_COLOR,
            timestamp=datetime.datetime.now()
        )
        await send_log(interaction.guild, embed=log_embed)

        # Log détaillé dans le canal de log des pays
        pays_log_embed = discord.Embed(
            title=f"🏛️ | Nouveau Pays : {nom}",
            description=f"Un nouveau pays a rejoint la scène internationale!",
            color=EMBED_COLOR
        )
        pays_log_embed.add_field(
            name="Informations",
            value=f"> **Nom :** {nom}\n"
                f"> **Continent :** {continent_role.name}\n"
                f"> **Rôle :** {role.mention}\n"
                f"> **Salon :** {channel.mention}\n"
                f"> **PIB :** {format_number(pib)} {MONNAIE_EMOJI}\n"
                f"> **Créé par :** {interaction.user.mention}",
            inline=False
        )
        pays_log_embed.add_field(
            name="Gouvernement",
            value=f"> **Dirigeant :** {dirigeant.mention}\n"
                f"> **Budget alloué :** {format_number(budget)} {MONNAIE_EMOJI}",
            inline=False
        )
        pays_log_embed.add_field(
            name="Message officiel",
            value=f"Nous souhaitons la bienvenue à {dirigeant.mention}, nouveau dirigeant de {role.mention} sur la scène internationale. Nous lui souhaitons succès et prospérité dans la conduite de cette nation!",
            inline=False
        )
        pays_log_embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        pays_log_embed.set_image(url=image if image and is_valid_image_url(image) else IMAGE_URL)
        pays_log_embed.set_footer(text=f"Date de création : {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        await send_pays_log(interaction.guild, pays_log_embed)

    except Exception as e:
        await interaction.followup.send(f"> Erreur lors de la création du pays : {e}", ephemeral=True)
        print(f"[ERROR] Exception dans creer_pays : {e}")
        return

        # Si un emoji personnalisé est fourni, essayer de l'appliquer comme icône du rôle
        if drapeau_perso:
            try:
                emoji_id = None
                if drapeau_perso.startswith('<') and drapeau_perso.endswith('>'):
                    emoji_parts = drapeau_perso.strip('<>').split(':')
                    if len(emoji_parts) >= 3:
                        emoji_id = int(emoji_parts[2])
                if emoji_id:
                    emoji = await interaction.guild.fetch_emoji(emoji_id)
                    if emoji:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(str(emoji.url)) as resp:
                                if resp.status == 200:
                                    emoji_bytes = await resp.read()
                                    try:
                                        await role.edit(display_icon=emoji_bytes)
                                    except discord.Forbidden:
                                        await interaction.followup.send("> Note: Impossible d'appliquer l'emoji comme icône de rôle. Cette fonctionnalité nécessite des boosts de serveur.", ephemeral=True)
                                    except Exception as e:
                                        print(f"Erreur lors de l'application de l'icône de rôle: {e}")
            except Exception as e:
                print(f"Erreur lors du traitement de l'emoji personnalisé: {e}")

        # Trouver la position correcte pour le nouveau rôle de pays
        try:
            server_roles = await interaction.guild.fetch_roles()
            continent_position = continent_role.position
            positions = {role: continent_position - 1}
            await interaction.guild.edit_role_positions(positions)
            print(f"[DEBUG] Rôle de pays positionné juste en dessous du continent {continent_role.name}")
        except Exception as e:
            print(f"Erreur lors du positionnement du rôle: {e}")

        # Créer le salon principal
        formatted_name = convert_to_bold_letters(nom)
        channel_name = f"【{emoji_pays}】・{formatted_name.lower().replace(' ', '-')}" if emoji_pays else f"【】・{formatted_name.lower().replace(' ', '-') }"
        
        print(f"[DEBUG] Création du salon principal : {channel_name}")
        print(f"[DEBUG] Catégorie utilisée : {categorie.name} (ID: {categorie.id})")
        
        # Créer le salon avec synchronisation de la catégorie
        channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=categorie
            # Pas d'overwrites = synchronisation automatique avec la catégorie
        )
        
        print(f"[DEBUG] Salon créé, permissions héritées de la catégorie")
        # Petit délai pour assurer la synchronisation
        await asyncio.sleep(0.5)
        
        # Ajouter les permissions spécifiques du rôle de pays SANS écraser les autres
        print(f"[DEBUG] Ajout des permissions pour le rôle {role.name}")
        await channel.set_permissions(
            role,
            read_messages=True,
            send_messages=True,
            read_message_history=True,
            embed_links=True,
            attach_files=True,
            add_reactions=True,
            send_messages_in_threads=True,
            create_public_threads=True,
            create_private_threads=True,
            manage_webhooks=True,
            manage_messages=True
        )
        print(f"[DEBUG] Permissions du rôle de pays appliquées")
        pays_log_channel_data[str(role.id)] = channel.id
        save_pays_log_channel(pays_log_channel_data)
        print(f"[DEBUG] Salon principal créé : {channel.name}")

        # Ajout des rôles au dirigeant
        try:
            print("[DEBUG] Ajout des rôles au dirigeant...")
            await dirigeant.add_roles(role)
            await dirigeant.add_roles(continent_role)
        except Exception as e:
            print(f"[ERROR] Ajout des rôles au dirigeant : {e}")

        # Ajout du rôle joueur et retrait du rôle non-joueur
        try:
            print("[DEBUG] Ajout du rôle joueur et retrait du rôle non-joueur...")
            role_joueur_id = 1410289640170328244
            role_non_joueur_id = 1393344053608710315
            role_joueur = interaction.guild.get_role(role_joueur_id)
            role_non_joueur = interaction.guild.get_role(role_non_joueur_id)
            if role_joueur:
                await dirigeant.add_roles(role_joueur)
            if role_non_joueur and role_non_joueur in dirigeant.roles:
                await dirigeant.remove_roles(role_non_joueur)
        except Exception as e:
            print(f"[ERROR] Ajout/retrait rôle joueur/non-joueur : {e}")

        # Ajout des rôles automatiques
        try:
            print("[DEBUG] Ajout des rôles automatiques...")
            for auto_role_id in auto_roles_ids:
                auto_role = interaction.guild.get_role(auto_role_id)
                if auto_role:
                    await dirigeant.add_roles(auto_role)
        except Exception as e:
            print(f"[ERROR] Ajout des rôles automatiques : {e}")

        # Enregistrement de l'image si fournie
        try:
            print("[DEBUG] Enregistrement de l'image du pays...")
            if image and is_valid_image_url(image):
                pays_images[str(role.id)] = image
        except Exception as e:
            print(f"[ERROR] Enregistrement image pays : {e}")

        # Initialisation du PIB (déjà fait)
        try:
            print("[DEBUG] Initialisation du PIB...")
        except Exception as e:
            print(f"[ERROR] Initialisation personnel : {e}")

        # Sauvegarde des données
        try:
            print("[DEBUG] Sauvegarde des données...")
            save_balances(balances)
            save_pib(pib_data)
            save_pays_images(pays_images)
            save_all_json_to_postgres()
        except Exception as e:
            print(f"[ERROR] Sauvegarde des données : {e}")

        # Envoi du message embed de confirmation
        try:
            print("[DEBUG] Envoi du message embed de confirmation...")
            embed = discord.Embed(
                title="🏛️ Nouveau pays créé",
                description=f"> **Pays:** {role.mention}\n"
                    f"> **Continent:** {continent_role.mention}\n"
                    f"> **Salon:** {channel.mention}\n"
                    f"> **PIB:** {format_number(pib)} {MONNAIE_EMOJI}\n"
                    f"> **Budget alloué:** {format_number(budget)} {MONNAIE_EMOJI}\n"
                    f"> **Dirigeant:** {dirigeant.mention}{INVISIBLE_CHAR}",
                color=EMBED_COLOR
            )
            embed.set_image(url=image if image and is_valid_image_url(image) else IMAGE_URL)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"[ERROR] Envoi embed confirmation : {e}")
            await interaction.followup.send(f"> Pays créé, mais erreur lors de l'envoi du message : {e}", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"> Erreur lors de la création du pays : {e}", ephemeral=True)
        print(f"[ERROR] Exception dans creer_pays : {e}")
        return

        # Créer le salon secret si un nom est fourni et une catégorie spécifiée
        secret_channel = None
        if nom_salon_secret and categorie_secret:
            formatted_secret_name = convert_to_bold_letters(nom_salon_secret)
            secret_channel_name = f"【{emoji_pays}】・{formatted_secret_name.lower().replace(' ', '-')}" if emoji_pays else f"【】・{formatted_secret_name.lower().replace(' ', '-')}"
            
            print(f"[DEBUG] Création du salon secret : {secret_channel_name}")
            print(f"[DEBUG] Catégorie secrète utilisée : {categorie_secret.name} (ID: {categorie_secret.id})")
            
            # Créer le salon avec synchronisation de la catégorie
            secret_channel = await interaction.guild.create_text_channel(
                name=secret_channel_name,
                category=categorie_secret
                # Pas d'overwrites = synchronisation automatique avec la catégorie
            )
            
            print(f"[DEBUG] Salon secret créé, permissions héritées de la catégorie")
            # Petit délai pour assurer la synchronisation
            await asyncio.sleep(0.5)
            
            # Ajouter les permissions spécifiques du rôle de pays SANS écraser les autres
            print(f"[DEBUG] Ajout des permissions pour le rôle {role.name} sur le salon secret")
            await secret_channel.set_permissions(
                role,
                read_messages=True,
                send_messages=True,
                read_message_history=True,
                embed_links=True,
                attach_files=True,
                add_reactions=True,
                send_messages_in_threads=True,
                create_public_threads=True,
                create_private_threads=True,
                manage_webhooks=True,
                manage_messages=True
            )
            print(f"[DEBUG] Permissions du rôle de pays appliquées sur le salon secret")
        
        # Gérer les données du pays
        role_id = str(role.id)
        
        # Attribuer le budget au pays
        balances[role_id] = budget
        
        # ID des rôles spéciaux de joueur et non-joueur
        role_joueur_id = 1410289640170328244
        role_non_joueur_id = 1393344053608710315
        
        # Attribuer les rôles au dirigeant
        await dirigeant.add_roles(role)
        await dirigeant.add_roles(continent_role)
        
        # Ajouter le rôle joueur et retirer le rôle non-joueur
        role_joueur = interaction.guild.get_role(role_joueur_id)
        role_non_joueur = interaction.guild.get_role(role_non_joueur_id)
        
        if role_joueur:
            await dirigeant.add_roles(role_joueur)
        
        if role_non_joueur and role_non_joueur in dirigeant.roles:
            await dirigeant.remove_roles(role_non_joueur)
        
        # Ajouter tous les rôles automatiques
        for auto_role_id in auto_roles_ids:
            auto_role = interaction.guild.get_role(auto_role_id)
            if auto_role:
                await dirigeant.add_roles(auto_role)
        
        # Enregistrer l'image si fournie
        if image and is_valid_image_url(image):
            pays_images[role_id] = image
        
        # Initialiser le PIB
        pib_data[role_id] = {
            "pib": pib
        }
        
        # Sauvegarder toutes les données
        save_balances(balances)
        save_pib(pib_data)
        save_pays_images(pays_images)
        save_all_json_to_postgres()
        
        # Embed de confirmation
        embed = discord.Embed(
            title="🏛️ Nouveau pays créé",
            description=f"> **Pays:** {role.mention}\n"
                f"> **Continent:** {continent_role.mention}\n"
                f"> **Salon:** {channel.mention}\n"
                f"> **PIB:** {format_number(pib)} {MONNAIE_EMOJI}\n"
                f"> **Budget alloué:** {format_number(budget)} {MONNAIE_EMOJI}\n"
                f"> **Dirigeant:** {dirigeant.mention}{INVISIBLE_CHAR}",
            color=EMBED_COLOR
        )
        embed.set_image(url=pays_image)
        await interaction.followup.send(embed=embed)
    
        # Message de bienvenue
        welcome_embed = discord.Embed(
            title=f"{emoji_message} | Bienvenue dans votre pays !",
            description=f"> *Ce salon est réservé aux membres du pays {role.mention}*\n"
                       f"> \n" 
                       f"> PIB : {format_number(pib)} {MONNAIE_EMOJI}\n"
                       f"> Budget alloué : {format_number(budget)} {MONNAIE_EMOJI}\n"
                       f"> Dirigeant : {dirigeant.mention}\n"
                       f"> \n"
                       f"> :black_small_square: Nous vous souhaitons une agréable expérience au sein du Rôleplay !{INVISIBLE_CHAR}",
            color=EMBED_COLOR
        )
        welcome_embed.set_image(url=pays_image)
        await channel.send(embed=welcome_embed)
    
        # Log de l'action
        log_embed = discord.Embed(
            title=f"🏛️ | Création de pays",
            description=f"> **Administrateur :** {interaction.user.mention}\n"
                       f"> **Pays créé : ** {role.mention}\n"
                       f"> **Continent : ** {continent_role.mention}\n"
                       f"> **PIB : ** {format_number(pib)} {MONNAIE_EMOJI}\n"
                       f"> **Dirigeant désigné : ** {dirigeant.mention}\n"
                       f"> **Budget alloué : ** {format_number(budget)} {MONNAIE_EMOJI}"
                       f"{INVISIBLE_CHAR}",
            color=EMBED_COLOR,
            timestamp=datetime.datetime.now()
        )
        await send_log(interaction.guild, embed=log_embed)
    
        # Envoyer un log détaillé dans le canal de log des pays
        pays_log_embed = discord.Embed(
            title=f"🏛️ | Nouveau Pays : {nom}",
            description=f"Un nouveau pays a rejoint la scène internationale!",
            color=EMBED_COLOR
        )
        pays_log_embed.add_field(
            name="Informations",
            value=f"> **Nom :** {nom}\n"
                f"> **Continent :** {continent_role.name}\n"
                f"> **Rôle :** {role.mention}\n"
                f"> **Salon :** {channel.mention}\n"
                f"> **PIB :** {format_number(pib)} {MONNAIE_EMOJI}\n"
                f"> **Créé par :** {interaction.user.mention}",
            inline=False
        )
    
        pays_log_embed.add_field(
            name="Gouvernement",
            value=f"> **Dirigeant :** {dirigeant.mention}\n"
                f"> **Budget alloué :** {format_number(budget)} {MONNAIE_EMOJI}",
            inline=False
        )
    
        pays_log_embed.add_field(
            name="Message officiel",
            value=f"Nous souhaitons la bienvenue à {dirigeant.mention}, nouveau dirigeant de {role.mention} sur la scène internationale. Nous lui souhaitons succès et prospérité dans la conduite de cette nation!",
            inline=False
        )
    
        pays_log_embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        pays_log_embed.set_image(url=pays_image)
        pays_log_embed.set_footer(text=f"Date de création : {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        
        await send_pays_log(interaction.guild, pays_log_embed)
        
    except Exception as e:
        await interaction.followup.send(f"> Erreur inattendue ou blocage lors de la création du pays : {e}", ephemeral=True)

# Ajouter une commande pour modifier l'image d'un pays
@bot.tree.command(name="modifier_image_pays", description="Modifie l'image d'un pays")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    role="Rôle du pays dont vous voulez modifier l'image",
    image="URL de la nouvelle image du pays"
)
async def modifier_image_pays(
    interaction: discord.Interaction,
    role: discord.Role,
    image: str
):
    """Modifie l'image d'un pays."""
    await interaction.response.defer(ephemeral=True)
    
    # Vérifier que le rôle est bien un pays
    role_id = str(role.id)
    if role_id not in balances:
        await interaction.followup.send("> Ce rôle ne semble pas être un pays.", ephemeral=True)
        return
    
    # Vérifier l'URL de l'image
    if not is_valid_image_url(image):
        await interaction.followup.send("> URL d'image invalide. Veuillez fournir une URL directe vers une image (JPG, PNG, etc.)", ephemeral=True)
        return
    
    # Enregistrer la nouvelle image
    pays_images[role_id] = image
    save_pays_images(pays_images)
    save_all_json_to_postgres()
    
    # Confirmation
    embed = discord.Embed(
        description=f"> L'image du pays {role.mention} a été mise à jour.{INVISIBLE_CHAR}",
        color=EMBED_COLOR
    )
    embed.set_image(url=image)
    await interaction.followup.send(embed=embed)
    
    # Log de l'action
    log_embed = discord.Embed(
        title="🏛️ | Modification d'image de pays",
        description=f"> **Administrateur :** {interaction.user.mention}\n"
                   f"> **Pays modifié :** {role.mention}{INVISIBLE_CHAR}",
        color=EMBED_COLOR,
        timestamp=datetime.datetime.now()
    )
    log_embed.set_image(url=image)
    await send_log(interaction.guild, embed=log_embed)

# Ajouter la commande pour définir le canal de log des pays
@bot.tree.command(name="setlogpays", description="Définit le salon de logs pour les pays")
@app_commands.checks.has_permissions(administrator=True)
async def setlogpays(interaction: discord.Interaction, channel: discord.TextChannel):
    pays_log_channel_data[str(interaction.guild.id)] = channel.id
    save_pays_log_channel(pays_log_channel_data)
    embed = discord.Embed(
        description=f"> Salon de logs pour les pays défini sur {channel.mention}.{INVISIBLE_CHAR}",
        color=EMBED_COLOR
    )
    embed.set_image(url=IMAGE_URL)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Commande ranking simplifiée : affiche seulement l'argent total en circulation

# Commande classement : affiche le classement des membres par argent
@bot.tree.command(name="classement_eco", description="Affiche le classement des membres par argent")
async def classement_eco(interaction: discord.Interaction):

    classement = sorted(balances.items(), key=lambda x: x[1], reverse=True)
    per_page = 15
    pages = [classement[i:i+per_page] for i in range(0, len(classement), per_page)]
    def make_embed(page_idx):
        page = pages[page_idx]
        desc = "⠀\n"
        for idx, (role_id, amount) in enumerate(page):
            rank = idx + 1 + page_idx * per_page
            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"
            else:
                medal = f"{rank}."
            role = interaction.guild.get_role(int(role_id))
            if role:
                desc += f"{medal} {role.mention} — {format_number(amount)} <:PX_MDollars:1417605571019804733>\n"
        embed = discord.Embed(
            title="Classement des budgets par pays",
            description=desc,
            color=EMBED_COLOR
        )
        embed.set_image(url=IMAGE_URL)
        embed.set_footer(text=f"Page {page_idx+1}/{len(pages)}")
        return embed

    if not classement:
        await interaction.response.send_message("Aucun membre n'a d'argent enregistré.", ephemeral=True)
        return

    class ClassementView(discord.ui.View):
        def __init__(self, pages):
            super().__init__(timeout=None)
            self.pages = pages
            self.page_idx = 0
            self.message = None

        @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
        async def prev(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
            if self.page_idx > 0:
                self.page_idx -= 1
                await interaction_btn.response.edit_message(embed=make_embed(self.page_idx), view=self)

        @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
        async def next(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
            if self.page_idx < len(self.pages) - 1:
                self.page_idx += 1
                await interaction_btn.response.edit_message(embed=make_embed(self.page_idx), view=self)

    view = ClassementView(pages)
    await interaction.response.send_message(embed=make_embed(0), view=view)

# Commande /payer : la cible est un rôle (pays) obligatoire, si rien n'est précisé l'argent est détruit (bot), et on ne save pas dans ce cas
@bot.tree.command(name="payer", description="Payer un autre pays ou détruire de l'argent de son pays")
@app_commands.describe(
    cible="Le rôle (pays) à payer. Si rien n'est sélectionné, l'argent est payé au bot.",
    montant="Montant à payer"
)
@app_commands.choices()
async def payer(interaction: discord.Interaction, montant: int, cible: typing.Optional[discord.Role] = None):
    # Cherche le premier rôle pays du membre qui a de l'argent
    user_roles = [r for r in interaction.user.roles if str(r.id) in balances and balances[str(r.id)] > 0]
    if not user_roles:
        await interaction.response.send_message(
            "> Vous n'avez aucun rôle pays avec de l'argent pour payer.", ephemeral=True)
        return
    pays_role = user_roles[0]
    pays_id = str(pays_role.id)
    solde = balances.get(pays_id, 0)
    if montant <= 0:
        await interaction.response.send_message(
            "> Le montant doit être positif.", ephemeral=True)
        return
    if montant > solde:
        await interaction.response.send_message(
            "> Votre pays n'a pas assez d'argent pour payer.", ephemeral=True)
        return
    if cible:
        cible_id = str(cible.id)
        balances[pays_id] -= montant
        balances[cible_id] = balances.get(cible_id, 0) + montant
        print("[DEBUG] Sauvegarde balances.json après paiement...")
        save_balances(balances)
        print("[DEBUG] Sauvegarde PostgreSQL après paiement...")
        save_all_json_to_postgres()
        embed = discord.Embed(
            description=f"> {format_number(montant)} {MONNAIE_EMOJI} payés de {pays_role.mention} à {cible.mention}.{INVISIBLE_CHAR}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    else:
        # Paiement au bot : l'argent est détruit, on ne save pas balances
        balances[pays_id] -= montant
        print("[DEBUG] Sauvegarde balances.json après destruction d'argent...")
        save_balances(balances)
        print("[DEBUG] Sauvegarde PostgreSQL après destruction d'argent...")
        save_all_json_to_postgres()
        embed = discord.Embed(
            description=f"> {format_number(montant)} {MONNAIE_EMOJI} ont été retirés de la circulation depuis {pays_role.mention}.{INVISIBLE_CHAR}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# Commande pour reset l'économie
@bot.tree.command(name="reset_economie", description="Réinitialise toute l'économie et supprime l'argent en circulation (admin seulement)")
@app_commands.checks.has_permissions(administrator=True)
async def reset_economie(interaction: discord.Interaction):
    """Réinitialise l'économie : vide tous les fichiers de données économiques."""
    await interaction.response.defer(ephemeral=True)
    confirm_view = discord.ui.View()
    confirm_button = discord.ui.Button(label="Confirmer la réinitialisation", style=discord.ButtonStyle.danger)
    cancel_button = discord.ui.Button(label="Annuler", style=discord.ButtonStyle.secondary)
    confirm_view.add_item(confirm_button)
    confirm_view.add_item(cancel_button)

    async def confirm_callback(interaction2: discord.Interaction):
        if interaction2.user.id != interaction.user.id:
            await interaction2.response.send_message("Vous n'êtes pas autorisé à confirmer cette action.", ephemeral=True)
            return
        # Vider les variables en mémoire
        global balances, loans
        balances.clear()
        loans.clear()
        # personnel supprimé
        # Sauvegarder les fichiers vides
        for file_path, empty_value in [
            (BALANCE_FILE, {}),
            (LOANS_FILE, []),
            (PIB_FILE, {}),
            (TRANSACTION_LOG_FILE, []),
        ]:
            try:
                with open(file_path, "w") as f:
                    json.dump(empty_value, f)
            except Exception as e:
                await interaction2.response.send_message(f"Erreur lors de la suppression de {os.path.basename(file_path)} : {e}", ephemeral=True)
                return
        # Supprimer les données économiques dans PostgreSQL
        import psycopg2, os
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL:
            try:
                with psycopg2.connect(DATABASE_URL) as conn:
                    with conn.cursor() as cur:
                        for filename in ["balances.json", "balances_backup.json", "loans.json", "transactions.json", "personnel.json"]:
                            cur.execute("DELETE FROM json_backups WHERE filename = %s", (filename,))
                    conn.commit()
                print("[DEBUG] Données économiques supprimées de PostgreSQL.")
            except Exception as e:
                print(f"[DEBUG] Erreur lors de la suppression des données économiques dans PostgreSQL : {e}")
        await interaction2.response.edit_message(content="✅ Économie réinitialisée avec succès !", view=None)

    async def cancel_callback(interaction2: discord.Interaction):
        if interaction2.user.id != interaction.user.id:
            await interaction2.response.send_message("Vous n'êtes pas autorisé à annuler cette action.", ephemeral=True)
            return
        await interaction2.response.edit_message(content="❌ Réinitialisation annulée.", view=None)

    confirm_button.callback = confirm_callback
    cancel_button.callback = cancel_callback

    await interaction.followup.send(
        "⚠️ Cette action va supprimer toutes les données économiques (balances, prêts, transactions). Confirmez-vous ?",
        view=confirm_view,
        ephemeral=True
    )

# Commande /balance : voir l'argent de son pays ou d'un autre (optionnel)
@bot.tree.command(name="balance", description="Affiche l'argent de votre pays ou d'un autre rôle (optionnel)")
@app_commands.describe(role="Le rôle (pays) dont vous voulez voir l'argent (optionnel)")
async def balance(interaction: discord.Interaction, role: discord.Role = None):
    await interaction.response.defer(ephemeral=True)
    
    # Restaurer les données depuis PostgreSQL pour avoir les valeurs les plus récentes
    print("[DEBUG] Restauration des données depuis PostgreSQL...")
    restore_all_json_from_postgres()
    
    # Recharger les données après restauration
    current_balances = load_balances()
    current_pib_data = load_pib()
    
    # Si aucun rôle n'est précisé, on cherche le premier rôle du membre qui est dans le système balances
    if role is None:
        # D'abord, essayer de trouver un rôle déjà dans le système balances
        user_roles = [r for r in interaction.user.roles if str(r.id) in current_balances and is_valid_country_role(str(r.id))]
        
        # Si aucun rôle n'est trouvé, chercher dans pays_images (rôles pays créés)
        if not user_roles:
            pays_images_data = load_pays_images()
            user_roles = [r for r in interaction.user.roles if str(r.id) in pays_images_data and is_valid_country_role(str(r.id))]
        
        if not user_roles:
            await interaction.followup.send(
                "> Vous n'avez aucun rôle pays. Précisez un rôle pour voir sa balance.", ephemeral=True)
            return
        
        role = user_roles[0]
        print(f"[DEBUG] Rôle automatiquement détecté: {role.name} (ID: {role.id})")
    
    # Vérifie que l'utilisateur a bien ce rôle ou est admin
    if role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
        await interaction.followup.send(
            "> Vous n'avez pas ce rôle, vous ne pouvez pas voir la balance de ce pays.", ephemeral=True)
        return
    
    role_id = str(role.id)
    
    print(f"[DEBUG] User: {interaction.user.name}")
    print(f"[DEBUG] Tous les rôles de l'utilisateur: {[f'{r.name}({r.id})' for r in interaction.user.roles]}")
    print(f"[DEBUG] Role recherché: {role.name} (ID: {role_id})")
    print(f"[DEBUG] Balances disponibles: {len(current_balances)} entrées")
    print(f"[DEBUG] PIB disponibles: {len(current_pib_data)} entrées")
    
    # Utiliser les données fraîchement chargées depuis PostgreSQL
    montant = current_balances.get(role_id, 0)
    print(f"[DEBUG] Balance pour role_id {role_id}: {montant}")
    
    # Récupérer le PIB depuis les données fraîchement chargées
    pib = current_pib_data.get(role_id, 0)  # PIB stocké comme entier simple
    print(f"[DEBUG] PIB pour role_id {role_id}: {pib}")
    
    # Vérifier si le role_id existe dans les données
    if role_id not in current_balances:
        print(f"[DEBUG] ⚠️ Role ID {role_id} NON TROUVÉ dans balances.json")
        # Afficher les 5 premiers role_ids pour comparaison
        sample_ids = list(current_balances.keys())[:5]
        print(f"[DEBUG] Exemples de role_ids disponibles: {sample_ids}")
    
    if role_id not in current_pib_data:
        print(f"[DEBUG] ⚠️ Role ID {role_id} NON TROUVÉ dans pib.json")
    
    # Vérification de type pour éviter les erreurs
    if isinstance(pib, dict):
        print(f"[DEBUG] PIB est un dictionnaire, conversion en 0: {pib}")
        pib = 0
    elif not isinstance(pib, (int, float)):
        print(f"[DEBUG] PIB n'est pas un nombre, conversion en 0: {pib}")
        pib = 0
    
    print(f"[DEBUG] PIB pour role_id {role_id}: {pib}")
    print(f"[DEBUG] PIB data complet: {current_pib_data}")
    # Calcul de la dette totale (somme des emprunts avec taux)
    dette_totale = 0
    emprunts_trouves = []
    
    print(f"[DEBUG] Recherche d'emprunts pour role_id: {role_id}")
    print(f"[DEBUG] Total emprunts dans la base: {len(loans)}")
    print(f"[DEBUG] Tous les emprunts: {loans}")
    
    # Récupérer tous les membres ayant ce rôle pour identifier les citoyens
    citoyens_ids = []
    for member in interaction.guild.members:
        if any(str(member_role.id) == role_id for member_role in member.roles):
            citoyens_ids.append(str(member.id))
    
    print(f"[DEBUG] Citoyens du pays {role.name} (role_id: {role_id}): {citoyens_ids}")
    
    for i, emprunt in enumerate(loans):
        # Vérifier si l'emprunt concerne ce rôle/pays
        emprunt_role_id = emprunt.get("role_id")
        emprunt_demandeur_id = emprunt.get("demandeur_id")
        
        print(f"[DEBUG] Emprunt {i}: role_id={emprunt_role_id}, demandeur_id={emprunt_demandeur_id}")
        
        # Cas 1: Emprunt fait par le pays lui-même
        if emprunt_role_id == role_id:
            principal = emprunt.get("somme", 0)
            taux = emprunt.get("taux", 0)
            dette_emprunt = int(principal * (1 + taux / 100))
            dette_totale += dette_emprunt
            emprunts_trouves.append({
                "type": "pays",
                "principal": principal,
                "taux": taux,
                "dette": dette_emprunt
            })
            print(f"[DEBUG] ✅ Emprunt du pays trouvé: principal={principal}, taux={taux}, dette={dette_emprunt}")
        
        # Cas 2: Emprunt fait par un citoyen auprès de la Banque centrale
        elif emprunt_role_id is None and emprunt_demandeur_id in citoyens_ids:
            principal = emprunt.get("somme", 0)
            taux = emprunt.get("taux", 0)
            dette_emprunt = int(principal * (1 + taux / 100))
            dette_totale += dette_emprunt
            emprunts_trouves.append({
                "type": "citoyen_banque_centrale",
                "demandeur": emprunt_demandeur_id,
                "principal": principal,
                "taux": taux,
                "dette": dette_emprunt
            })
            print(f"[DEBUG] ✅ Emprunt citoyen Banque centrale trouvé: demandeur={emprunt_demandeur_id}, principal={principal}, taux={taux}, dette={dette_emprunt}")
    
    print(f"[DEBUG] Dette totale calculée pour {role_id}: {dette_totale}")
    print(f"[DEBUG] PIB pour {role_id}: {pib}")
    print(f"[DEBUG] Nombre d'emprunts trouvés: {len(emprunts_trouves)}")
    
    # Vérification de type pour dette_totale
    if not isinstance(dette_totale, (int, float)):
        print(f"[DEBUG] Dette totale n'est pas un nombre, conversion en 0: {dette_totale}")
        dette_totale = 0
    
    # Pourcentage dette/PIB
    pourcentage_pib = 0
    if isinstance(pib, (int, float)) and pib > 0 and isinstance(dette_totale, (int, float)) and dette_totale > 0:
        pourcentage_pib = round((dette_totale / pib) * 100, 2)
        print(f"[DEBUG] Calcul pourcentage: {dette_totale} / {pib} * 100 = {pourcentage_pib}%")
    else:
        print(f"[DEBUG] Pas de calcul de pourcentage: pib={pib}, dette_totale={dette_totale}")
    # Texte formaté
    texte = (
        "⠀\n"
        "> <:PX_MDollars:1417605571019804733> | **Budget :** {}\n"
        "> <:PX_MDollars:1417605571019804733> | **PIB :** {}\n"
        "> <:PX_MDollars:1417605571019804733> | **Dette total :** {} - ({}% au PIB)\n⠀"
    ).format(
        format_number(montant),
        format_number(pib) if pib is not None else "Non défini",
        format_number(dette_totale),
        pourcentage_pib
    )
    embed = discord.Embed(
        description=texte,
        color=0xebe3bd
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1393317478133661746/1430388154057232455/balance.png?ex=68f99847&is=68f846c7&hm=caf730cf84810b8340517e384f07ee782ae2e619c82fd831c321dff36eeea061&")
    await interaction.followup.send(embed=embed, ephemeral=True)

# Commande pour ajouter de l'argent à un rôle
@bot.tree.command(name="add_money", description="Ajoute de l'argent au budget ou PIB d'un rôle (admin seulement)")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    role="Le rôle (pays) à créditer", 
    montant="Montant à ajouter",
    type_argent="Type d'argent à modifier"
)
@app_commands.choices(type_argent=[
    discord.app_commands.Choice(name="Budget", value="budget"),
    discord.app_commands.Choice(name="PIB", value="pib")
])
async def add_money(interaction: discord.Interaction, role: discord.Role, montant: int, type_argent: str):
    if montant <= 0:
        await interaction.response.send_message("> Le montant doit être positif.", ephemeral=True)
        return
    
    role_id = str(role.id)
    
    if type_argent == "budget":
        # Ajouter au budget
        current_balance = balances.get(role_id, 0)
        
        # Vérification de type pour le budget
        if not isinstance(current_balance, (int, float)):
            print(f"[DEBUG] Balance n'est pas un nombre, initialisation à 0: {current_balance}")
            current_balance = 0
        
        balances[role_id] = current_balance + montant
        print("[DEBUG] Sauvegarde balances.json après ajout d'argent...")
        save_balances(balances)
        print("[DEBUG] Sauvegarde PostgreSQL après ajout d'argent...")
        save_all_json_to_postgres()
        
        embed = discord.Embed(
            description=f"> {format_number(montant)} {MONNAIE_EMOJI} ajoutés au **budget** de {role.mention}. Nouveau solde : {format_number(balances[role_id])} {MONNAIE_EMOJI}.{INVISIBLE_CHAR}",
            color=discord.Color.green()
        )
    else:  # PIB
        # Ajouter au PIB
        if role_id not in pib_data:
            pib_data[role_id] = PIB_DEFAULT
        
        # Vérification de type pour éviter les erreurs
        current_pib = pib_data[role_id]
        if isinstance(current_pib, dict):
            print(f"[DEBUG] PIB est un dictionnaire, initialisation à PIB_DEFAULT: {current_pib}")
            current_pib = PIB_DEFAULT
        elif not isinstance(current_pib, (int, float)):
            print(f"[DEBUG] PIB n'est pas un nombre, initialisation à PIB_DEFAULT: {current_pib}")
            current_pib = PIB_DEFAULT
        
        pib_data[role_id] = current_pib + montant
        print("[DEBUG] Sauvegarde pib.json après ajout de PIB...")
        save_pib(pib_data)
        print("[DEBUG] Sauvegarde PostgreSQL après ajout de PIB...")
        save_all_json_to_postgres()
        
        embed = discord.Embed(
            description=f"> {format_number(montant)} {MONNAIE_EMOJI} ajoutés au **PIB** de {role.mention}. Nouveau PIB : {format_number(pib_data[role_id])} {MONNAIE_EMOJI}.{INVISIBLE_CHAR}",
            color=discord.Color.green()
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Commande pour retirer de l'argent à un rôle
@bot.tree.command(name="remove_money", description="Retire de l'argent du budget ou PIB d'un rôle (admin seulement)")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    role="Le rôle (pays) à débiter", 
    montant="Montant à retirer",
    type_argent="Type d'argent à modifier"
)
@app_commands.choices(type_argent=[
    discord.app_commands.Choice(name="Budget", value="budget"),
    discord.app_commands.Choice(name="PIB", value="pib")
])
async def remove_money(interaction: discord.Interaction, role: discord.Role, montant: int, type_argent: str):
    if montant <= 0:
        await interaction.response.send_message("> Le montant doit être positif.", ephemeral=True)
        return
    
    role_id = str(role.id)
    
    if type_argent == "budget":
        # Retirer du budget
        solde = balances.get(role_id, 0)
        if montant > solde:
            await interaction.response.send_message("> Le rôle n'a pas assez d'argent dans son budget.", ephemeral=True)
            return
        
        nouveau_solde = solde - montant
        balances[role_id] = nouveau_solde
        print("[DEBUG] Sauvegarde balances.json après retrait d'argent...")
        save_balances(balances)
        print("[DEBUG] Sauvegarde PostgreSQL après retrait d'argent...")
        save_all_json_to_postgres()
        
        embed = discord.Embed(
            description=f"> {format_number(montant)} {MONNAIE_EMOJI} retirés du **budget** de {role.mention}. Nouveau solde : {format_number(nouveau_solde)} {MONNAIE_EMOJI}.{INVISIBLE_CHAR}",
            color=discord.Color.red()
        )
    else:  # PIB
        # Retirer du PIB
        pib_actuel = pib_data.get(role_id, PIB_DEFAULT)
        if montant > pib_actuel:
            await interaction.response.send_message("> Le rôle n'a pas assez d'argent dans son PIB.", ephemeral=True)
            return
        
        nouveau_pib = pib_actuel - montant
        pib_data[role_id] = nouveau_pib
        print("[DEBUG] Sauvegarde pib.json après retrait de PIB...")
        save_pib(pib_data)
        print("[DEBUG] Sauvegarde PostgreSQL après retrait de PIB...")
        save_all_json_to_postgres()
        
        embed = discord.Embed(
            description=f"> {format_number(montant)} {MONNAIE_EMOJI} retirés du **PIB** de {role.mention}. Nouveau PIB : {format_number(nouveau_pib)} {MONNAIE_EMOJI}.{INVISIBLE_CHAR}",
            color=discord.Color.red()
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="supprimer_pays", description="Supprime un pays, son rôle et son salon")
async def supprimer_pays(interaction: discord.Interaction, pays: discord.Role, raison: str = None):
    """Supprime un pays, son rôle et son salon."""
    
    # Vérifier les permissions pour supprimer des pays
    if not has_country_management_permissions(interaction):
        embed = discord.Embed(
            title="❌ Permission refusée",
            description="Vous n'avez pas les permissions nécessaires pour supprimer des pays.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Suppression des transactions liées au pays
    try:
        import os, json
        DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        transactions_path = os.path.join(DATA_DIR, "transactions.json")
        with open(transactions_path, "r") as f:
            transactions = json.load(f)
        # Filtrer toutes les transactions où le pays supprimé n'est ni source ni destination
        transactions = [t for t in transactions if str(pays.id) not in (str(t.get("source")), str(t.get("destination")))]
        with open(transactions_path, "w") as f:
            json.dump(transactions, f)
        # Mettre à jour le backup PostgreSQL
        try:
            import psycopg2, os
            DATABASE_URL = os.getenv("DATABASE_URL")
            if DATABASE_URL:
                with psycopg2.connect(DATABASE_URL) as conn:
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM json_backups WHERE filename = %s", ("transactions.json",))
                        with open(transactions_path, "r") as f:
                            content = f.read()
                        cur.execute("""
                            INSERT INTO json_backups (filename, content, updated_at)
                            VALUES (%s, %s, NOW())
                            ON CONFLICT (filename) DO UPDATE SET content = EXCLUDED.content, updated_at = NOW()
                        """, ("transactions.json", content))
                    conn.commit()
                print("[DEBUG] Données économiques supprimées de PostgreSQL.")
        except Exception as e:
            print(f"[DEBUG] Erreur lors de la suppression des données économiques dans PostgreSQL : {e}")
    except Exception as e:
        print(f"[ERROR] Suppression des transactions liées au pays : {e}")
    await interaction.response.defer(ephemeral=True)
    try:
        # Liste des rôles à retirer aux membres du pays
        roles_a_retirer = [
            1413995329656852662, 1413995459827077190, 1413993747515052112, 1413995073632207048,
            1417253039491776733, 1413993786001985567, 1413994327473918142, 1413994277029023854,
            1413993819292045315, 1413994233622302750, 1410289640170328244, 1413997188089909398
        ]
        # Rôles de continent
        roles_continents = [1413995502785138799, 1413995608922128394, 1413995735732457473, 1413995874304004157, 1413996176956461086]
        # Retirer tous les rôles listés + rôles de continent + rôle du pays
        # Tous les IDs possibles pour economie, regime, gouvernement
        roles_economie = [1417234199353622569, 1417234220115431434, 1417234887508754584, 1417234944832442621, 1417234931146555433, 1417235038168289290, 1417235052814794853]
        roles_regime = [1417251476782448843, 1417251480573968525, 1417251556776218654, 1417251565068226691, 1417251568327200828, 1417251571661537320, 1417251574568456232, 1417251577714053170, 1417252579766829076]
        roles_gouv = [1417254283694313652, 1417254315684528330, 1417254344180371636, 1417254681243025428, 1417254399004246161, 1417254501110251540, 1417254550951428147, 1417254582156791908, 1417254615224680508, 1417254639069560904, 1417254809253314590]
        for membre in pays.members:
            # Retirer tous les rôles à retirer
            for role_id in roles_a_retirer + roles_continents + [pays.id]:
                role_obj = interaction.guild.get_role(role_id)
                if role_obj and role_obj in membre.roles:
                    await membre.remove_roles(role_obj)
            # Retirer tous les rôles economie, regime, gouvernement
            for role_id in roles_economie + roles_regime + roles_gouv:
                role_selected = interaction.guild.get_role(role_id)
                if role_selected and role_selected in membre.roles:
                    await membre.remove_roles(role_selected)
            # Retirer le rôle de religion
                roles_religion = [
                    1417622211329659010, 1417622670702280845, 1417622925745586206,
                    1417623400695988245, 1417624032131682304, 1417624442905038859,
                    1417625845425766562, 1417626007770366123, 1424945271858528326,
                    1417626204885745805, 1417626362738512022, 1424789872329101498,
                    1419446723310256138, 1424783855331577856, 1425197116858437653
                ]
            for role_id in roles_religion:
                role_religion = interaction.guild.get_role(role_id)
                if role_religion and role_religion in membre.roles:
                    await membre.remove_roles(role_religion)
            # Retirer les rôles de base
            for base_role_id in [1417619445060206682, 1417619843611627530]:
                base_role = interaction.guild.get_role(base_role_id)
                if base_role and base_role in membre.roles:
                    await membre.remove_roles(base_role)
            # Ajouter le rôle 1393344053608710315
            role_ajouter = interaction.guild.get_role(1393344053608710315)
            if role_ajouter and role_ajouter not in membre.roles:
                await membre.add_roles(role_ajouter)
        # Supprimer le salon du pays via l'ID associé au rôle (stocké dans pays_log_channel_data)
        salons_supprimes = []
        # Suppression par ID (stocké lors de creer_pays)
        salon_id = pays_log_channel_data.get(str(pays.id))
        salon_trouve = None
        if salon_id:
            salon = interaction.guild.get_channel(int(salon_id))
            if salon:
                salon_trouve = salon
        # Si pas trouvé par ID, recherche par nom EXACT généré comme dans creer_pays
        if not salon_trouve:
            # Récupérer l'emoji utilisé dans le nom du salon (si possible)
            emoji_pays = ""
            # On tente de récupérer l'emoji du nom du rôle (si présent)
            if pays.name.startswith("【") and "】" in pays.name:
                emoji_pays = pays.name.split("【")[1].split("】")[0]
            # Récupérer le nom du pays sans emoji ni décorations
            nom_pays_brut = pays.name
            if "】・" in nom_pays_brut:
                nom_pays_brut = nom_pays_brut.split("】・", 1)[1]
            # Reconstruire le nom du salon
            formatted_name = nom_pays_brut
            channel_name = f"【{emoji_pays}】・{formatted_name}".lower().replace(" ", "-")
            for channel in interaction.guild.text_channels:
                if channel.name == channel_name:
                    salon_trouve = channel
                    break
        # Suppression du salon trouvé (uniquement si trouvé par ID ou nom exact)
        if salon_trouve:
            try:
                await salon_trouve.delete(reason=f"Suppression du pays {pays.name}")
                salons_supprimes.append(salon_trouve.name)
            except Exception:
                pass
        # Nettoyage de l'association
        pays_log_channel_data.pop(str(pays.id), None)
        save_pays_log_channel(pays_log_channel_data)
        # Suppression de l'argent associé au rôle du pays
        if str(pays.id) in balances:
            balances.pop(str(pays.id))
            save_balances(balances)
            
        # Suppression du PIB associé au rôle du pays
        pib_data = load_pib()
        if str(pays.id) in pib_data:
            pib_data.pop(str(pays.id))
            save_pib(pib_data)
            
        # Suppression des développements technologiques associés au pays
        developpements = load_developpements()
        guild_id = str(interaction.guild.id)
        if guild_id in developpements and str(pays.id) in developpements[guild_id]:
            developpements[guild_id].pop(str(pays.id))
            save_developpements(developpements)
            
            # Suppression dans PostgreSQL
            try:
                import psycopg2, os
                DATABASE_URL = os.getenv("DATABASE_URL")
                if DATABASE_URL:
                    with psycopg2.connect(DATABASE_URL) as conn:
                        with conn.cursor() as cur:
                            cur.execute("DELETE FROM json_backups WHERE filename = %s", ("balances.json",))
                            # Réenregistrer balances.json sans le pays supprimé
                            import json
                            DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
                            balances_path = os.path.join(DATA_DIR, "balances.json")
                            with open(balances_path, "w") as f:
                                json.dump(balances, f)
                            with open(balances_path, "r") as f:
                                content = f.read()
                            cur.execute("""
                                INSERT INTO json_backups (filename, content, updated_at)
                                VALUES (%s, %s, NOW())
                                ON CONFLICT (filename) DO UPDATE SET content = EXCLUDED.content, updated_at = NOW()
                            """, ("balances.json", content))
                        conn.commit()
            except Exception as err:
                print(f"[ERROR] Suppression balance pays dans PostgreSQL : {err}")
        # Supprimer le rôle du pays
        await pays.delete(reason=raison or "Suppression du pays")
        # Réponse à l'utilisateur
        embed = discord.Embed(
            title="Pays supprimé",
            description=f"> Le pays {pays.name} et son salon associé ont été supprimés.\n> Salon supprimé : {', '.join(salons_supprimes) if salons_supprimes else 'Aucun'}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"> Erreur lors de la suppression du pays : {e}", ephemeral=True)

@bot.tree.command(name="modifier_pays", description="Modifie les informations d'un pays existant")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    role="Rôle du pays à modifier",
    nom="Nouveau nom pour le pays (facultatif)",
    nouveau_dirigeant="Nouveau dirigeant du pays (facultatif)",
    economie="Type d'économie du pays (facultatif)",
    regime_politique="Régime politique du pays (facultatif)",
    gouvernement="Forme de gouvernement du pays (facultatif)"
)
@app_commands.choices(economie=[
    discord.app_commands.Choice(name="Économie ultra-libérale", value="1417234199353622569"),
    discord.app_commands.Choice(name="Économie libérale", value="1417234220115431434"),
    discord.app_commands.Choice(name="Économie mixte", value="1417234887508754584"),
    discord.app_commands.Choice(name="Socialisme de marché", value="1417234944832442621"),
    discord.app_commands.Choice(name="Économie planifiée", value="1417234931146555433"),
    discord.app_commands.Choice(name="Économie dirigiste", value="1417235038168289290"),
    discord.app_commands.Choice(name="Économie corporatiste", value="1417235052814794853")
])
@app_commands.choices(regime_politique=[
    discord.app_commands.Choice(name="Démocratie", value="1417251476782448843"),
    discord.app_commands.Choice(name="Autoritarisme", value="1417251480573968525"),
    discord.app_commands.Choice(name="Totalitarisme", value="1417251556776218654"),
    discord.app_commands.Choice(name="Monarchie", value="1417251565068226691"),
    discord.app_commands.Choice(name="Oligarchie", value="1417251568327200828"),
    discord.app_commands.Choice(name="Théocratie", value="1417251571661537320"),
    discord.app_commands.Choice(name="Technocratie", value="1417251574568456232"),
    discord.app_commands.Choice(name="Régime populaire", value="1417251577714053170"),
    discord.app_commands.Choice(name="Régime militaire", value="1417252579766829076")
])
@app_commands.choices(gouvernement=[
    discord.app_commands.Choice(name="Régime parlementaire", value="1417254283694313652"),
    discord.app_commands.Choice(name="Régime présidentielle", value="1417254315684528330"),
    discord.app_commands.Choice(name="République parlementaire", value="1417254344180371636"),
    discord.app_commands.Choice(name="République présidentielle", value="1417254681243025428"),
    discord.app_commands.Choice(name="Monarchie parlementaire", value="1417254399004246161"),
    discord.app_commands.Choice(name="Monarchie absolue", value="1417254501110251540"),
    discord.app_commands.Choice(name="Gouvernement directorial", value="1417254550951428147"),
    discord.app_commands.Choice(name="Gouvernement de Transition", value="1417254582156791908"),
    discord.app_commands.Choice(name="Gouvernement populaire", value="1417254615224680508"),
    discord.app_commands.Choice(name="Stratocratie", value="1417254639069560904"),
    discord.app_commands.Choice(name="Aucun gouvernement", value="1417254809253314590")
])
async def modifier_pays(
    interaction: discord.Interaction,
    role: discord.Role,
    nom: str = None,
    nouveau_dirigeant: discord.Member = None,
    economie: str = None,
    regime_politique: str = None,
    gouvernement: str = None,
    religion: str = None
):
    """Modifie le nom et/ou le dirigeant d'un pays existant."""
    await interaction.response.defer()
    modifications = []
    try:
        # Changement de nom du pays
        if nom:
            old_role_name = role.name
            role_name = f"❝ ｢ {nom} ｣ ❞"
            await role.edit(name=role_name)
            modifications.append("nom du rôle")
            # Renommer le salon principal si trouvé
            for channel in interaction.guild.text_channels:
                if channel.permissions_for(role).read_messages and not channel.permissions_for(interaction.guild.default_role).read_messages:
                    formatted_name = convert_to_bold_letters(nom)
                    channel_name = f"【】・{formatted_name.lower().replace(' ', '-')}"
                    await channel.edit(name=channel_name)
                    modifications.append("nom du salon")
                    break
        # Changement de dirigeant
        if nouveau_dirigeant:
            ancien_dirigeant = None
            for membre in role.members:
                # Ajout des rôles de base
                for base_role_id in [1417619445060206682, 1417619843611627530]:
                    base_role = interaction.guild.get_role(base_role_id)
                    if base_role and base_role not in membre.roles:
                        await membre.add_roles(base_role)
                if religion:
                    role_religion = interaction.guild.get_role(int(religion))
                    if role_religion:
                        await membre.add_roles(role_religion)
                    if membre != nouveau_dirigeant:
                        ancien_dirigeant = membre
                        # break  # Removed invalid break statement
            auto_roles_ids = [
                1413995329656852662, 1413997188089909398, 1413993747515052112, 1413995073632207048,
                1413993786001985567, 1413994327473918142, 1413994277029023854, 1413993819292045315,
                1413994233622302750, 1413995459827077190, 1410289640170328244
            ]
            if ancien_dirigeant:
                await ancien_dirigeant.remove_roles(role)
                for auto_role_id in auto_roles_ids:
                    auto_role = interaction.guild.get_role(auto_role_id)
                    if auto_role and auto_role in ancien_dirigeant.roles:
                        await ancien_dirigeant.remove_roles(auto_role)
            await nouveau_dirigeant.add_roles(role)
            for auto_role_id in auto_roles_ids:
                auto_role = interaction.guild.get_role(auto_role_id)
                if auto_role and auto_role not in nouveau_dirigeant.roles:
                    await nouveau_dirigeant.add_roles(auto_role)
            modifications.append("dirigeant remplacé")
        # Modification des rôles économie, régime politique, gouvernement
        ROLE_PAYS_PAR_DEFAUT = 1417253039491776733
        roles_economie = [1417234199353622569, 1417234220115431434, 1417234887508754584, 1417234944832442621, 1417234931146555433, 1417235038168289290, 1417235052814794853]
        roles_regime = [1417251476782448843, 1417251480573968525, 1417251556776218654, 1417251565068226691, 1417251568327200828, 1417251571661537320, 1417251574568456232, 1417251577714053170, 1417252579766829076]
        roles_gouv = [1417254283694313652, 1417254315684528330, 1417254344180371636, 1417254681243025428, 1417254399004246161, 1417254501110251540, 1417254550951428147, 1417254582156791908, 1417254615224680508, 1417254639069560904, 1417254809253314590]
        # Retirer tous les anciens rôles
        for role_id in [ROLE_PAYS_PAR_DEFAUT] + roles_economie + roles_regime + roles_gouv:
            role_obj = interaction.guild.get_role(role_id)
            if role_obj:
                for membre in role.members:
                    if role_obj in membre.roles:
                        await membre.remove_roles(role_obj)
        # Ajouter les nouveaux rôles si précisés
        for membre in role.members:
            if economie:
                role_economie = interaction.guild.get_role(int(economie))
                if role_economie:
                    await membre.add_roles(role_economie)
            if regime_politique:
                role_regime = interaction.guild.get_role(int(regime_politique))
                if role_regime:
                    await membre.add_roles(role_regime)
            if gouvernement:
                role_gouv = interaction.guild.get_role(int(gouvernement))
                if role_gouv:
                    await membre.add_roles(role_gouv)
            # Toujours ajouter le rôle par défaut
            role_defaut = interaction.guild.get_role(ROLE_PAYS_PAR_DEFAUT)
            if role_defaut:
                await membre.add_roles(role_defaut)
        modifications.append("rôles modifiés")
        if modifications:
            embed = discord.Embed(
                title="🏛️ Pays modifié",
                description=f"> **Pays:** {role.mention}\n> **Modifications:** {', '.join(modifications)}{INVISIBLE_CHAR}",
                color=EMBED_COLOR
            )
            embed.set_image(url=IMAGE_URL)
            await interaction.followup.send(embed=embed)
            log_embed = discord.Embed(
                title=f"🏛️ | Modification de pays",
                description=f"> **Administrateur :** {interaction.user.mention}\n> **Pays modifié : ** {role.mention}\n> **Modifications : ** {', '.join(modifications)}{INVISIBLE_CHAR}",
                color=EMBED_COLOR,
                timestamp=datetime.datetime.now()
            )
            await send_log(interaction.guild, embed=log_embed)
        else:
            await interaction.followup.send("> Aucune modification n'a été apportée.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"> Erreur lors de la modification du pays: {e}", ephemeral=True)

@bot.tree.command(name="creer_drapeau", description="Convertit une image en drapeau style emoji Twitter")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    image_url="URL de l'image à convertir en drapeau",
    nom_emoji="Nom à donner à l'emoji (sans espaces ni caractères spéciaux)"
)
async def creer_drapeau(interaction: discord.Interaction, image_url: str, nom_emoji: str):
    """Convertit une image en drapeau style emoji Twitter."""
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Vérifier le nom d'emoji
        if not nom_emoji.replace("_", "").isalnum():
            await interaction.followup.send("> Le nom de l'emoji doit contenir uniquement des lettres, chiffres et underscores.", ephemeral=True)
            return
        
        # Télécharger l'image
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    await interaction.followup.send(f"> Erreur lors du téléchargement de l'image (code {resp.status}).", ephemeral=True)
                    return
                img_bytes = await resp.read()
        
        # Ouvrir l'image
        original = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        
        # Créer une image carrée avec ratio 4:3 (style Twitter flag)
        width, height = 128, 96
        
        # Redimensionner l'image en préservant son ratio et en la recadrant si nécessaire
        img_ratio = original.width / original.height
        target_ratio = width / height
        
        if img_ratio > target_ratio:  # Image plus large
            new_height = height
            new_width = int(new_height * img_ratio)
            resized = original.resize((new_width, new_height), Image.LANCZOS)
            # Recadrer le centre
            left = (new_width - width) // 2
            resized = resized.crop((left, 0, left + width, height))
        else:  # Image plus haute
            new_width = width
            new_height = int(new_width / img_ratio)
            resized = original.resize((new_width, new_height), Image.LANCZOS)
            # Recadrer le centre
            top = (new_height - height) // 2
            resized = resized.crop((0, top, width, top + height))
        
        # Créer un masque avec coins arrondis (style Twitter)
        # Les drapeaux Twitter ont des coins légèrement arrondis
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        
        # Rayon d'arrondi style Twitter (environ 10% de la largeur)
        radius = int(width * 0.1)
        
        # Dessiner un rectangle avec coins arrondis
        draw.rectangle((radius, 0, width - radius, height), fill=255)  # Partie horizontale centrale
        draw.rectangle((0, radius, width, height - radius), fill=255)  # Partie verticale centrale
        
        # Coins arrondis
        draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=255)  # Coin supérieur gauche
        draw.pieslice((width - radius * 2, 0, width, radius * 2), 270, 0, fill=255)  # Coin supérieur droit
        draw.pieslice((0, height - radius * 2, radius * 2, height), 90, 180, fill=255)  # Coin inférieur gauche
        draw.pieslice((width - radius * 2, height - radius * 2, width, height), 0, 90, fill=255)  # Coin inférieur droit
        
        # Appliquer le masque
        result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        result.paste(resized, (0, 0), mask)
        
        # Enregistrer en mémoire
        buffer = io.BytesIO()
        result.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Créer l'emoji
        try:
            emoji = await interaction.guild.create_custom_emoji(
                name=nom_emoji,
                image=buffer.read()
            )
            
            # Message de confirmation
            embed = discord.Embed(
                title="🏁 Drapeau créé",
                description=f"> L'emoji a été créé avec succès : {str(emoji)}\n"
                           f"> **Nom :** {emoji.name}\n"
                           f"> **ID :** {emoji.id}{INVISIBLE_CHAR}",
                color=EMBED_COLOR
            )
            embed.set_image(url=emoji.url)
            await interaction.followup.send(embed=embed)
            
        except discord.Forbidden:
            await interaction.followup.send("> Je n'ai pas les permissions nécessaires pour créer des emojis sur ce serveur.", ephemeral=True)
        except discord.HTTPException as e:
                       await interaction.followup.send(f"> Erreur lors de la création de l'emoji : {e}", ephemeral=True)
        
    except Exception as e:
        await interaction.followup.send(f"> Erreur lors de la création du drapeau : {str(e)}", ephemeral=True)

def check_duplicate_json_files():
    """Vérifie s'il existe des fichiers JSON en double dans le projet."""
    json_files = [
        "balances.json", "log_channel.json", "message_log_channel.json", 
        "loans.json", "balances_backup.json",
        "transactions.json", "pays_log_channel.json", "pays_images.json",
        "generaux.json"
    ]
    
    duplicates = []
    for file in json_files:
        root_path = os.path.join(BASE_DIR, file)
        data_path = os.path.join(DATA_DIR, file)
        
        if os.path.exists(root_path) and os.path.exists(data_path):
            duplicates.append(file)
    

    
    if duplicates:
        print(f"AVERTISSEMENT: Les fichiers suivants existent à la fois à la racine et dans le dossier data: {', '.join(duplicates)}")
        print("Pour éviter les conflits, supprimez les fichiers à la racine et gardez uniquement ceux dans le dossier data.")

from discord import Permissions

# Durées de mute disponibles (en secondes)
MUTE_DURATIONS = [
    ("1 minute", 60),
    ("5 minutes", 5 * 60),
    ("10 minutes", 10 * 60),
    ("15 minutes", 15 * 60),
    ("30 minutes", 30 * 60),
    ("1 heure", 60 * 60),
    ("2 heures", 2 * 60 * 60),
    ("4 heures", 4 * 60 * 60),
    ("6 heures", 6 * 60 * 60),
    ("10 heures", 10 * 60 * 60),
    ("24 heures", 24 * 60 * 60),
]

MUTE_ROLE_ID = 1414694151622234212  # ID du rôle mute à utiliser en priorité

def get_mute_role(guild):
    """Retourne le rôle mute par ID si possible, sinon par nom."""
    role = guild.get_role(MUTE_ROLE_ID)
    if role:
        return role
    for role in guild.roles:
        if role.name.lower() == "mute":
            return role
    return None

@bot.tree.command(name="creer_role_mute", description="Crée le rôle mute et configure les permissions sur tous les salons")
@app_commands.checks.has_permissions(administrator=True)
async def creer_role_mute(interaction: discord.Interaction):
    await interaction.response.send_message("Création du rôle mute en cours...", ephemeral=True)
    guild = interaction.guild

    # Vérifier si le rôle mute existe déjà
    mute_role = get_mute_role(guild)
    if mute_role:
        await interaction.followup.send(f"> Le rôle mute existe déjà : {mute_role.mention}", ephemeral=True)
        return

    # Créer le rôle mute
    try:
        mute_role = await guild.create_role(name="Mute", color=discord.Color.grey(), reason="Rôle pour mute")
    except Exception as e:
        await interaction.followup.send(f"> Erreur lors de la création du rôle mute : {e}", ephemeral=True)
        return

    # Configurer les permissions sur toutes les catégories et salons
    for category in guild.categories:
        try:
            await category.set_permissions(
                mute_role, 
                send_messages=False, 
                speak=False, 
                add_reactions=False, 
                use_external_emojis=False,
                create_public_threads=False,
                create_private_threads=False,
                connect=False
            )
        except Exception:
            pass
    for channel in guild.channels:
        try:
            await channel.set_permissions(
                mute_role, 
                send_messages=False, 
                speak=False, 
                add_reactions=False, 
                use_external_emojis=False,
                create_public_threads=False,
                create_private_threads=False,
                connect=False
            )
        except Exception:
            pass

    embed = discord.Embed(
        description=f"> Le rôle {mute_role.mention} a été créé et configuré avec toutes les restrictions sur tous les salons.{INVISIBLE_CHAR}",
        color=EMBED_COLOR
    )
    await interaction.followup.send(embed=embed, ephemeral=True)

# Générer les choix pour la durée
duration_choices = [
    app_commands.Choice(name=label, value=str(seconds))
    for label, seconds in MUTE_DURATIONS
]

@bot.tree.command(name="mute", description="Mute un membre pour une durée définie")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    membre="Membre à mute",
    duree="Durée du mute",
    raison="Raison du mute (optionnel)"
)
@app_commands.choices(duree=duration_choices)
async def mute(
    interaction: discord.Interaction,
    membre: discord.Member,
    duree: str,
    raison: str = None
):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    mute_role = get_mute_role(guild)
    if not mute_role:
        await interaction.followup.send("> Le rôle mute n'existe pas. Utilisez /creer_role_mute d'abord.", ephemeral=True)
        return
    await membre.add_roles(mute_role, reason=raison or "Mute via commande")
    seconds = int(duree)
    label = next((lbl for lbl, sec in MUTE_DURATIONS if sec == seconds), f"{seconds} secondes")
    try:
        await membre.send(
            f"Vous avez été mute sur **{guild.name}** pour {label}." + (f"\nRaison : {raison}" if raison else "")
        )
    except Exception:
        pass
    embed = discord.Embed(
        description=f"> {membre.mention} a été mute pour **{label}**.{INVISIBLE_CHAR}",
        color=discord.Color.orange()
    )
    await interaction.followup.send(embed=embed, ephemeral=True)
    # Log dans le salon de mute
    log_embed = discord.Embed(
        title="🔇 Mute appliqué",
        description=f"> **Utilisateur :** {membre.mention}\n> **Durée :** {label}\n> **Par :** {interaction.user.mention}\n> **Raison :** {raison or 'Non spécifiée'}",
        color=discord.Color.orange(),
        timestamp=datetime.datetime.now()
    )
    await send_mute_log(guild, log_embed)
    # Enregistre le mute actif
    unmute_time = time.time() + seconds
    active_mutes[f"{guild.id}:{membre.id}"] = {
        "guild_id": str(guild.id),
        "user_id": str(membre.id),
        "unmute_time": unmute_time
    }
    save_active_mutes(active_mutes)
    
    print(f"[MUTES] ✅ Mute enregistré: {membre.name} dans {guild.name}, fin prévue: {datetime.datetime.fromtimestamp(unmute_time)}")
    bot.loop.create_task(schedule_unmute(guild.id, membre.id, unmute_time))

@bot.tree.command(name="unmute", description="Retire le mute d'un membre")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    membre="Membre à unmute"
)
async def unmute(interaction: discord.Interaction, membre: discord.Member):
    await interaction.response.defer(ephemeral=True)
    mute_role = get_mute_role(interaction.guild)
    if not mute_role:
        await interaction.followup.send("> Le rôle mute n'existe pas.", ephemeral=True)
        return
    if mute_role not in membre.roles:
        await interaction.followup.send("> Ce membre n'est pas mute.", ephemeral=True)
        return
    await membre.remove_roles(mute_role, reason="Unmute via commande")
    try:
        await membre.send(f"Vous avez été unmute sur **{interaction.guild.name}**.")
    except Exception:
        pass
    embed = discord.Embed(
        description=f"> {membre.mention} a été unmute.{INVISIBLE_CHAR}",
        color=discord.Color.green()
    )
    await interaction.followup.send(embed=embed, ephemeral=True)
    # Log dans le salon de mute
    log_embed = discord.Embed(
        title="🔊 Unmute manuel",
        description=f"> **Utilisateur :** {membre.mention}\n> **Par :** {interaction.user.mention}",
        color=discord.Color.green(),
        timestamp=datetime.datetime.now()
    )
    await send_mute_log(interaction.guild, log_embed)
    # Supprime le mute actif si existant
    active_mutes.pop(f"{interaction.guild.id}:{membre.id}", None)
    save_active_mutes(active_mutes)

@bot.tree.command(name="ban", description="Ban un membre du serveur")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    membre="Membre à bannir",
    raison="Raison du ban (optionnel)"
)
async def ban(interaction: discord.Interaction, membre: discord.Member, raison: str = None):
    class ConfirmBanView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
        @discord.ui.button(label="Oui", style=discord.ButtonStyle.success)
        async def confirm(self, interaction2: discord.Interaction, button: discord.ui.Button):
            if interaction2.user.id != interaction.user.id:
                await interaction2.response.send_message("Vous n'êtes pas autorisé à confirmer ce ban.", ephemeral=True)
                return
            try:
                try:
                    await membre.send(
                        f"Vous avez été **banni** du serveur **{interaction.guild.name}**."
                        + (f"\nRaison : {raison}" if raison else "")
                    )
                except Exception:
                    pass
                await membre.ban(reason=raison or f"Banni par {interaction.user} via /ban")
                embed = discord.Embed(
                    description=f"> {membre.mention} a été **banni** du serveur.{INVISIBLE_CHAR}",
                    color=discord.Color.red()
                )
                await interaction2.response.edit_message(content=None, embed=embed, view=None)
                log_embed = discord.Embed(
                    title="⛔ Ban appliqué",
                    description=f"> **Utilisateur :** {membre.mention}\n"
                                f"> **Par :** {interaction.user.mention}\n"
                                f"> **Raison :** {raison or 'Non spécifiée'}",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                await send_mute_log(interaction.guild, log_embed)
            except Exception as e:
                await interaction2.response.edit_message(content=f"> Erreur lors du ban : {e}", view=None)
        @discord.ui.button(label="Non", style=discord.ButtonStyle.danger)
        async def cancel(self, interaction2: discord.Interaction, button: discord.ui.Button):
            if interaction2.user.id != interaction.user.id:
                await interaction2.response.send_message("Vous n'êtes pas autorisé à annuler.", ephemeral=True)
                return
            await interaction2.response.edit_message(content="❌ Ban annulé.", view=None)
    embed = discord.Embed(
        description=f"> Voulez-vous vraiment bannir {membre.mention} ?",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, view=ConfirmBanView(), ephemeral=True)

@bot.tree.command(name="ban_dc", description="Bannit automatiquement une liste prédéfinie d'utilisateurs (usage restreint)")
async def ban_dc(interaction: discord.Interaction):
    # IDs autorisés à exécuter la commande
    AUTORIZED_USERS = [1218248773923373176, 772821169664426025]
    
    # Vérifier si l'utilisateur est autorisé
    if interaction.user.id not in AUTORIZED_USERS:
        await interaction.response.send_message("> ❌ Vous n'êtes pas autorisé à utiliser cette commande.", ephemeral=True)
        return
    
    # Liste des IDs à bannir
    IDS_TO_BAN = [
        1318298813525397617,
        1348904229015781417,
        1359562157901090966,
        1325979264243208268,
        1348836648514752575,
        1349077415099629650,
        1417476939488428055,
        1417415409736486992,
        1417376598918955140,
        1417508551848366110,
        1416769304233377978,
        1417476330043474054,
        1417547623992135871,
        1417383560259698792,
        1417509232760066199,
        1417374039957045360,
        1417401395556122725,
        1417399699446693920,
        1417506082938421331,
        1417486372754817024,
        1417517336138874958,
        1417283355535347822,
        1417369196232445962,
        1417388009485242418
    ]
    
    await interaction.response.defer(ephemeral=True)
    
    banned_count = 0
    already_banned = 0
    not_found = 0
    errors = 0
    
    for user_id in IDS_TO_BAN:
        try:
            # Essayer de récupérer l'utilisateur depuis le serveur
            user = interaction.guild.get_member(user_id)
            
            if user is None:
                # Si pas dans le serveur, essayer de le récupérer depuis Discord
                try:
                    user = await bot.fetch_user(user_id)
                    # Vérifier s'il est déjà banni
                    try:
                        ban_entry = await interaction.guild.fetch_ban(user)
                        already_banned += 1
                        continue
                    except discord.NotFound:
                        # Pas banni, on peut le bannir
                        pass
                except discord.NotFound:
                    not_found += 1
                    continue
                
            if user:
                try:
                    # Tenter d'envoyer un MP avant le ban
                    try:
                        if hasattr(user, 'send'):
                            await user.send(f"Vous avez été banni du serveur **{interaction.guild.name}** par une action automatique.")
                    except:
                        pass  # Ignore si on ne peut pas envoyer de MP
                    
                    # Bannir l'utilisateur
                    await interaction.guild.ban(user, reason=f"Ban automatique par {interaction.user} via /ban_dc")
                    banned_count += 1
                    
                except discord.Forbidden:
                    errors += 1
                except discord.HTTPException:
                    errors += 1
            else:
                not_found += 1
                
        except Exception as e:
            print(f"Erreur lors du ban de {user_id}: {e}")
            errors += 1
    
    # Rapport final
    embed = discord.Embed(
        title="🔨 Bannissements automatiques terminés",
        color=discord.Color.red()
    )
    embed.add_field(name="✅ Utilisateurs bannis", value=str(banned_count), inline=True)
    embed.add_field(name="🔒 Déjà bannis", value=str(already_banned), inline=True)
    embed.add_field(name="❓ Non trouvés", value=str(not_found), inline=True)
    embed.add_field(name="❌ Erreurs", value=str(errors), inline=True)
    embed.add_field(name="📊 Total traité", value=f"{len(IDS_TO_BAN)} utilisateurs", inline=True)
    embed.set_footer(text=f"Exécuté par {interaction.user.display_name}")
    
    await interaction.followup.send(embed=embed, ephemeral=True)
    
    # Log dans le canal de modération si configuré
    log_embed = discord.Embed(
        title="🔨 Ban automatique exécuté",
        description=f"> **Exécuté par :** {interaction.user.mention}\n"
                    f"> **Utilisateurs bannis :** {banned_count}\n"
                    f"> **Total traité :** {len(IDS_TO_BAN)}",
        color=discord.Color.red(),
        timestamp=datetime.datetime.now()
    )
    await send_mute_log(interaction.guild, log_embed)

# === LOG MUTE ===
MUTE_LOG_FILE = os.path.join(DATA_DIR, "mute_log_channel.json")
mute_log_channel_data = {}

def load_mute_log_channel():
    if not os.path.exists(MUTE_LOG_FILE):
        with open(MUTE_LOG_FILE, "w") as f:
            json.dump({}, f)
    try:
        with open(MUTE_LOG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement du log mute: {e}")
        return {}

def save_mute_log_channel(data):
    try:
        with open(MUTE_LOG_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du log mute: {e}")

mute_log_channel_data.update(load_mute_log_channel())

@bot.tree.command(name="setpermission_mute", description="Réapplique les permissions du rôle mute sur tous les salons et catégories")
@app_commands.checks.has_permissions(administrator=True)
async def setpermission_mute(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    mute_role = get_mute_role(guild)
    if not mute_role:
        await interaction.followup.send("> Le rôle mute n'existe pas. Utilisez /creer_role_mute d'abord.", ephemeral=True)
        return
    for category in guild.categories:
        try:
            await category.set_permissions(
                mute_role, 
                send_messages=False, 
                speak=False, 
                add_reactions=False, 
                use_external_emojis=False,
                create_public_threads=False,
                create_private_threads=False,
                connect=False
            )
        except Exception:
            pass
    for channel in guild.channels:
        try:
            await channel.set_permissions(
                mute_role, 
                send_messages=False, 
                speak=False, 
                add_reactions=False, 
                use_external_emojis=False,
                create_public_threads=False,
                create_private_threads=False,
                connect=False
            )
        except Exception:
            pass
    embed = discord.Embed(
        description=f"> Permissions du rôle {mute_role.mention} réappliquées sur tous les salons et catégories avec restrictions complètes.",
        color=EMBED_COLOR
    )
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="setlogmute", description="Définit le salon de logs pour les sanctions mute/unmute")
@app_commands.checks.has_permissions(administrator=True)
async def setlogmute(interaction: discord.Interaction, channel: discord.TextChannel):
    mute_log_channel_data[str(interaction.guild.id)] = channel.id
    save_mute_log_channel(mute_log_channel_data)
    embed = discord.Embed(
        description=f"> Salon de logs mute défini sur {channel.mention}.{INVISIBLE_CHAR}",
        color=EMBED_COLOR
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# === GESTION DES MUTES PERSISTANTS ===
ACTIVE_MUTES_FILE = os.path.join(DATA_DIR, "active_mutes.json")

def load_active_mutes():
    if not os.path.exists(ACTIVE_MUTES_FILE):
        with open(ACTIVE_MUTES_FILE, "w") as f:
            json.dump({}, f)
    try:
        with open(ACTIVE_MUTES_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des mutes actifs: {e}")
        return {}

def save_active_mutes(data):
    try:
        with open(ACTIVE_MUTES_FILE, "w") as f:
            json.dump(data, f, indent=2)
        # Sauvegarder aussi dans PostgreSQL
        save_all_json_to_postgres()
        print(f"[MUTES] Sauvegarde de {len(data)} mutes actifs")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des mutes actifs: {e}")

active_mutes = load_active_mutes()

async def schedule_unmute(guild_id, user_id, unmute_time):
    now = time.time()
    delay = unmute_time - now
    
    if delay > 0:
        print(f"[MUTES] Planification unmute dans {int(delay)}s pour User {user_id} dans Guild {guild_id}")
        await asyncio.sleep(delay)
    
    print(f"[MUTES] Exécution unmute automatique pour User {user_id} dans Guild {guild_id}")
    guild = bot.get_guild(int(guild_id))
    if not guild:
        print(f"[MUTES] Erreur: Guild {guild_id} introuvable")
        return
        
    member = guild.get_member(int(user_id))
    mute_role = get_mute_role(guild)
    
    if member and mute_role and mute_role in member.roles:
        try:
            await member.remove_roles(mute_role, reason="Fin du mute automatique")
            print(f"[MUTES] ✅ Unmute réussi pour {member.name} dans {guild.name}")
            
            try:
                await member.send(f"Votre sanction mute sur **{guild.name}** est terminée.")
            except Exception:
                pass
                
            # Log de l'unmute automatique
            unmute_embed = discord.Embed(
                title="🔊 Mute terminé",
                description=f"> **Utilisateur :** {member.mention}\n> **Fin de la durée automatique**",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            await send_mute_log(guild, unmute_embed)
        except Exception as e:
            print(f"[MUTES] Erreur lors de l'unmute: {e}")
    else:
        print(f"[MUTES] Membre {user_id} déjà unmute ou introuvable dans {guild.name}")
    
    # Nettoyer le mute actif
    active_mutes.pop(f"{guild_id}:{user_id}", None)
    save_active_mutes(active_mutes)

async def restore_mutes_on_start():
    print("[MUTES] Restauration des mutes actifs au démarrage...")
    now = time.time()
    restored_count = 0
    expired_count = 0
    
    for key, mute in list(active_mutes.items()):
        guild_id, user_id = mute["guild_id"], mute["user_id"]
        unmute_time = mute["unmute_time"]
        
        if unmute_time <= now:
            print(f"[MUTES] Mute expiré trouvé: Guild {guild_id}, User {user_id}")
            await schedule_unmute(guild_id, user_id, now)
            expired_count += 1
        else:
            remaining_time = unmute_time - now
            print(f"[MUTES] Mute actif restauré: Guild {guild_id}, User {user_id}, Temps restant: {int(remaining_time)}s")
            bot.loop.create_task(schedule_unmute(guild_id, user_id, unmute_time))
            restored_count += 1
    
    print(f"[MUTES] Restauration terminée: {restored_count} mutes actifs, {expired_count} mutes expirés")

# ===== NOUVELLES COMMANDES =====

class TriView(discord.ui.View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=None)
        self.guild = guild

@bot.tree.command(name="id", description="Enregistre tous les IDs des membres du serveur dans invites.json")
@app_commands.checks.has_permissions(administrator=True)
async def id(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    invites_path = os.path.join(DATA_DIR, "invites.json")
    restore_all_json_from_postgres()
    member_ids = [str(member.id) for member in guild.members if not member.bot]
    # Toujours écrire une liste d'IDs, jamais un objet vide
    if member_ids:
        with open(invites_path, "w") as f:
            json.dump(member_ids, f)
    else:
        with open(invites_path, "w") as f:
            json.dump([], f)
    save_all_json_to_postgres()
    await interaction.followup.send(f"IDs de {len(member_ids)} membres enregistrés dans invites.json.", ephemeral=True)

@bot.tree.command(name="invites", description="Envoie une invitation Discord en MP à tous les membres (admin seulement)")
@app_commands.checks.has_permissions(administrator=True)
async def invites(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    guild_name = guild.name
    invites_path = os.path.join(DATA_DIR, "invites.json")
    
    # Charger les IDs des membres déjà invités
    if os.path.exists(invites_path):
        with open(invites_path, "r") as f:
            invited_ids = set(json.load(f))
    else:
        invited_ids = set()
    
    # Compter les membres éligibles
    total_members = len([m for m in guild.members if not m.bot])
    already_invited = len([m for m in guild.members if not m.bot and str(m.id) in invited_ids])
    
    sent_count = 0
    failed_count = 0
    skipped_count = 0
    
    for member in guild.members:
        if member.bot:
            continue
        
        # Ignorer les membres déjà invités
        if str(member.id) in invited_ids:
            skipped_count += 1
            continue
            
        try:
            # Message d'invitation personnalisé
            invitation_message = f"""⠀⠀ [𝐏𝐀𝐗 𝐑𝐔𝐈𝐍𝐀𝐄 ⱽ²▕▏𝟐𝟎𝟕𝟐](https://discord.gg/paxr)
⠀⠀⠀⠀▬▬▬▬▬▬▬▬▬

> ▪︎ Bonjour / Bonsoir ! Récemment, nous construisions un serveur de A à Z avec des mécaniques et choses plus innovante que sur les anciens New Era, et celui-ci va désormais amorcer son lancement concret en Rôleplay.
> 
> ▪︎ Celui-ci étais en construction depuis un mois, mais il va désormais amorcer son lancement officiel le **vendredi 24 Octobre 2025** à **20h** ! N'hésitez pas à nous rejoindre si vous cherchez des RP Géopolitique dans ce thème, nous vous accueilleront avec grand plaisir.

-# Envoyé depuis {guild_name}"""
            
            await member.send(invitation_message)
            invited_ids.add(str(member.id))
            sent_count += 1
        except Exception:
            failed_count += 1
    
    # Sauvegarder les nouveaux IDs invités
    with open(invites_path, "w") as f:
        json.dump(list(invited_ids), f)
    save_all_json_to_postgres()
    
    await interaction.followup.send(
        f"> **Résultat de l'envoi d'invitations :**\n"
        f"> • Invitations envoyées : **{sent_count}** nouveaux membres\n"
        f"> • Échecs d'envoi : **{failed_count}** membres\n"
        f"> • Déjà invités : **{skipped_count}** membres (ignorés)\n"
        f"> • Total des membres : **{total_members}** (hors bots)\n"
        f"> • Total invités après cette commande : **{len(invited_ids)}** membres",
        ephemeral=True
    )

@bot.tree.command(name="notif", description="Envoie une notification prédéfinie en MP à tous les membres (admin seulement)")
@app_commands.checks.has_permissions(administrator=True)
async def notif(interaction: discord.Interaction):
    await interaction.response.defer()
    
    guild = interaction.guild
    guild_name = guild.name
    
    # IDs des rôles spéciaux
    ROLE_JOUEUR_ID = 1410289640170328244
    ROLE_NON_JOUEUR_ID = 1393344053608710315
    
    # Messages prédéfinis
    message_joueur = f"""⠀⠀ [𝐏𝐀𝐗 𝐑𝐔𝐈𝐍𝐀𝐄 ⱽ²▕▏𝟐𝟎𝟕𝟐](https://discord.gg/paxr)
⠀⠀⠀⠀▬▬▬▬▬▬▬▬▬

> ▪︎ Bonjour / Bonsoir ! Nous vous informons qu'une annonce a été publiée dans ⁠<#1393350471661387846> et que le rôleplay ouvrira le **vendredi 24 octobre 2025 à 20h** !
> ﻿
> ▪︎ Vous pouvez dès à présent consulter l'ensemble des salons utiles pour le RP ci-dessous, si ce n'est pas déjà fait.
> 
> <#1412220875381538888>
> <#1412221123440939183>
> 
> <#1426582085493063841>
> <#1393324090562973776>
> <#1393324354619576362>
> <#1393325798685016256>
> <#1410450325248147560>
> 
> <#1424404204193189999>
> <#1426205177005998263>
> 
> ▪︎ D'autres éléments arriveront dans les prochains jours. En attendant, préparez tranquillement votre RP *(Merci de faire votre contexte dans votre fiche si vous ne l'avez pas faite auparavant)* et soyez prêts pour le lancement !

-# Envoyé depuis {guild_name}"""

    message_non_joueur = f"""⠀⠀ [𝐏𝐀𝐗 𝐑𝐔𝐈𝐍𝐀𝐄 ⱽ²▕▏𝟐𝟎𝟕𝟐](https://discord.gg/paxr)
⠀⠀⠀⠀▬▬▬▬▬▬▬▬▬

> ▪︎ Bonjour / Bonsoir ! Nous vous informons qu'une annonce a été publiée dans ⁠<#1393350471661387846> et que le rôleplay ouvrira le **vendredi 24 octobre 2025 à 20h** !
> ﻿
> ▪︎ Étant donné que vous êtes un non-joueur, nous vous invitons à rejoindre le Rôleplay en consultant les différents salons ci-dessous.
> 
> <#1393609944292655204>
> <#1410453879950413904>
> <#1424787942420775022>
> 
> <#1412220875381538888>
> <#1412221123440939183>
> 
> <#1426582085493063841>
> <#1393324090562973776>
> <#1393324354619576362>
> <#1393325798685016256>
> <#1410450325248147560>
> 
> <#1424404204193189999>
> <#1426205177005998263>
> 
> ▪︎ D'autres éléments arriveront dans les prochains jours. Si vous voulez participer au Rôleplay, faite une fiche et checkez la cartographie - il est toutefois plausible que y ai des régions pris entre temps, le staff sera présent pour vous l'indiquer !

-# Envoyé depuis {guild_name}"""

    sent_joueur = 0
    sent_non_joueur = 0
    failed_count = 0
    
    for member in guild.members:
        if member.bot:
            continue
            
        try:
            # Vérifier les rôles du membre
            member_role_ids = [role.id for role in member.roles]
            
            if ROLE_JOUEUR_ID in member_role_ids:
                await member.send(message_joueur)
                sent_joueur += 1
            elif ROLE_NON_JOUEUR_ID in member_role_ids:
                await member.send(message_non_joueur)
                sent_non_joueur += 1
                
        except Exception:
            failed_count += 1
    
    await interaction.followup.send(
        f"> **Notifications envoyées :**\n"
        f"> • Joueurs contactés : **{sent_joueur}** membres\n"
        f"> • Non-joueurs contactés : **{sent_non_joueur}** membres\n"
        f"> • Échecs d'envoi : **{failed_count}** membres"
    )

# Commande notif_debug supprimée

# === COMMANDES XP/LEVEL ===
@bot.tree.command(name="set_lvl", description="Active le système de niveau (XP)")
@app_commands.checks.has_permissions(administrator=True)
async def set_lvl(interaction: discord.Interaction):
    global xp_system_status
    guild_id = str(interaction.guild.id)
    if xp_system_status["servers"].get(guild_id, False):
        await interaction.response.send_message(
            "Le système de niveau est déjà actif.", ephemeral=True)
        return
    xp_system_status["servers"][guild_id] = True
    save_xp_system_status(xp_system_status)
    await interaction.response.send_message(
        "Système de niveau activé !", ephemeral=True)
    save_all_json_to_postgres()

@bot.tree.command(name="set_channel_lvl", description="Définit le salon de log pour les passages de niveau")
@app_commands.checks.has_permissions(administrator=True)
async def set_channel_lvl(interaction: discord.Interaction, channel: discord.TextChannel):
    lvl_log_channel_data[str(interaction.guild.id)] = channel.id
    save_lvl_log_channel(lvl_log_channel_data)
    await interaction.response.send_message(
        f"✅ Salon de log niveau défini sur {channel.mention}.", ephemeral=True)

@bot.tree.command(name="lvl", description="Affiche votre niveau et progression XP")
async def lvl(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in levels:
        levels[user_id] = {"xp": 0, "level": 1}
        save_levels(levels)
    
    level = levels[user_id]["level"]
    xp_current = levels[user_id]["xp"]
    
    bar = get_progress_bar(xp_current, level)
    xp_needed = xp_for_level(level)
    percent = int((xp_current / xp_needed) * 100) if xp_needed > 0 else 0
    
    # Détection du grade de palier
    palier_roles = {
        10: 1427993128811626606,
        20: 1417893555376230570,
        30: 1417893729066291391,
        40: 1417893878136176680,
        50: 1417894464122261555,
        60: 1417894846844244139,
        70: 1417895041862733986,
        80: 1417895157553958922,
        90: 1417895282443812884,
        100: 1417895415273099404
    }
    palier = (level // 10) * 10
    grade = None
    if palier in palier_roles:
        role_obj = interaction.guild.get_role(palier_roles[palier])
        if role_obj and role_obj in interaction.user.roles:
            grade = role_obj.name
    embed = discord.Embed(
        title=f"Niveau de {interaction.user.display_name}",
        description=f"⠀\n> − **Niveau :** {level}\n> − **Progression :**\n> {bar}\n" + (f"> − **Grade : {grade}**\n⠀" if grade else "⠀"),
        color=0xebe3bd
    )
    embed.set_image(url="https://zupimages.net/up/21/03/vl8j.png")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="reset_levels", description="Remet tous les niveaux à zéro")
@app_commands.checks.has_permissions(administrator=True)
async def reset_levels(interaction: discord.Interaction):
    """Remet tous les niveaux et XP des utilisateurs à zéro."""
    
    # Créer une vue de confirmation
    class ResetConfirmView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.confirmed = False
        
        @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
        async def confirm_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
            if button_interaction.user.id != interaction.user.id:
                await button_interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut confirmer.", ephemeral=True)
                return
            
            self.confirmed = True
            self.stop()
            await button_interaction.response.defer()
        
        @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
        async def cancel_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
            if button_interaction.user.id != interaction.user.id:
                await button_interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut annuler.", ephemeral=True)
                return
            
            self.stop()
            await button_interaction.response.defer()
    
    # Embed de confirmation
    embed = discord.Embed(
        title="⚠️ RESET DES NIVEAUX",
        description="**Êtes-vous sûr de vouloir remettre tous les niveaux à zéro ?**\n\n"
                   f"📊 **Utilisateurs concernés :** {len(levels)}\n"
                   f"⚠️ **Cette action est irréversible !**\n\n"
                   f"Tous les utilisateurs reviendront au niveau 1 avec 0 XP.",
        color=0xff0000
    )
    
    view = ResetConfirmView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    # Attendre la confirmation
    await view.wait()
    
    if not view.confirmed:
        embed = discord.Embed(
            title="❌ Reset annulé",
            description="Le reset des niveaux a été annulé.",
            color=0xff0000
        )
        await interaction.edit_original_response(embed=embed, view=None)
        return
    
    # Effectuer le reset
    users_reset = 0
    for user_id in levels:
        levels[user_id] = {"xp": 0, "level": 1}
        users_reset += 1
    
    # Sauvegarder
    save_levels(levels)
    
    # Résultat
    embed = discord.Embed(
        title="✅ RESET TERMINÉ",
        description=f"**Tous les niveaux ont été remis à zéro !**\n\n"
                   f"👥 **Utilisateurs affectés :** {users_reset}\n"
                   f"📊 **Nouveau niveau :** 1\n"
                   f"⭐ **Nouvelle XP :** 0",
        color=0x00ff00
    )
    
    # Log de l'action
    if interaction.guild.id in log_channel_data:
        log_embed = discord.Embed(
            title="🔄 Reset des Niveaux",
            description=f"**Administrateur :** {interaction.user.mention}\n"
                       f"**Utilisateurs affectés :** {users_reset}\n"
                       f"**Action :** Tous les niveaux remis à 1",
            color=0xff9900,
            timestamp=interaction.created_at
        )
        await send_log(interaction.guild, embed=log_embed)
    
    await interaction.edit_original_response(embed=embed, view=None)

@bot.tree.command(name="classement_lvl", description="Affiche le classement des membres par niveau")
async def classement_lvl(interaction: discord.Interaction):
    # Récupérer les 15 meilleurs niveaux
    classement = sorted(levels.items(), key=lambda x: x[1]["level"], reverse=True)
    per_page = 15
    pages = [classement[i:i+per_page] for i in range(0, len(classement), per_page)]
    def make_embed(page_idx):
        page = pages[page_idx]
        desc = "⠀\n"
        for idx, (user_id, data) in enumerate(page):
            rank = idx + 1 + page_idx * per_page
            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"
            else:
                medal = f"{rank}."
            member = interaction.guild.get_member(int(user_id))
            if member:
                desc += f"> {medal} : {member.mention} - **Niveau {data['level']}**\n"
        desc += "⠀"
        embed = discord.Embed(
            title="🔝 | Classement en Niveaux",
            description=desc,
            color=0x162e50
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1412872314525192233/1417982063839154318/PAX_RUINAE_4.gif?ex=68cc7634&is=68cb24b4&hm=5c7411791192069f1030b0aef0e51be790bb957c288658954070e2cc2f1d862c&")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1412872314525192233/1417981197899792565/Sans_titre_1024_x_1024_px_3.png?ex=68cc7566&is=68cb23e6&hm=8e0c7eb0093be4cb173de373bc050949d1efb52fa2e974de8b3dd2acd3b5deaa&")
        return embed

    # Récupérer les 15 meilleurs niveaux
    classement = sorted(levels.items(), key=lambda x: x[1]["level"], reverse=True)
    per_page = 15
    pages = [classement[i:i+per_page] for i in range(0, len(classement), per_page)]
    def make_embed(page_idx):
        page = pages[page_idx]
        desc = "⠀\n"
        for idx, (user_id, data) in enumerate(page):
            rank = idx + 1 + page_idx * per_page
            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"
            else:
                medal = f"{rank}."
            member = interaction.guild.get_member(int(user_id))
            if member:
                desc += f"> {medal} : {member.mention} - **Niveau {data['level']}**\n"
        desc += "⠀"
        embed = discord.Embed(
            title="🔝 | Classement en Niveaux",
            description=desc,
            color=0x162e50
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1412872314525192233/1417982063839154318/PAX_RUINAE_4.gif?ex=68cc7634&is=68cb24b4&hm=5c7411791192069f1030b0aef0e51be790bb957c288658954070e2cc2f1d862c&")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1412872314525192233/1417981197899792565/Sans_titre_1024_x_1024_px_3.png?ex=68cc7566&is=68cb23e6&hm=8e0c7eb0093be4cb173de373bc050949d1efb52fa2e974de8b3dd2acd3b5deaa&")
        return embed

    class ClassementView(discord.ui.View):
        def __init__(self, pages):
            super().__init__(timeout=None)
            self.pages = pages
            self.page_idx = 0
            self.message = None

        @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
        async def prev(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
            if self.page_idx > 0:
                self.page_idx -= 1
                await interaction_btn.response.edit_message(embed=make_embed(self.page_idx), view=self)

        @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
        async def next(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
            if self.page_idx < len(self.pages) - 1:
                self.page_idx += 1
                await interaction_btn.response.edit_message(embed=make_embed(self.page_idx), view=self)

    view = ClassementView(pages)
    await interaction.response.send_message(embed=make_embed(0), view=view)

@bot.tree.command(name="creer_emprunt", description="Crée un emprunt et attribue la somme au demandeur")
@app_commands.describe(
    somme="Montant à emprunter",
    taux="Taux d'intérêt (%) - détermine la dette totale",
    duree="Durée supposée de l'emprunt (texte libre, informatif seulement)",
    nombre_paiement="Nombre de paiements prévus (informatif seulement)",
    role="Rôle (pays) à débiter - si non spécifié, débit de la Banque centrale"
)
async def creer_emprunt(
    interaction: discord.Interaction,
    somme: int,
    taux: float,
    duree: str,
    nombre_paiement: int = None,
    role: discord.Role = None
):
    await interaction.response.defer(ephemeral=True)
    
    demandeur_id = str(interaction.user.id)
    role_id = str(role.id) if role else None
    banque_centrale_id = "BOT"
    
    # Vérification des montants
    if somme <= 0 or taux < 0:
        await interaction.followup.send("> Paramètres invalides. Le montant doit être positif et le taux non négatif.", ephemeral=True)
        return
    # Vérification du PIB si le demandeur est un pays
    pib = None
    if role:
        # Récupérer le PIB depuis pib_data
        pib_data = load_pib()
        pib_info = pib_data.get(str(role.id), {})
        pib = pib_info.get("pib", None)
        
        # Si le PIB est trouvé et la somme dépasse 50% du PIB, erreur
        if pib and somme > 0.5 * pib:
            await interaction.followup.send(f"> Erreur : L'emprunt ({format_number(somme)}) dépasse 50% du PIB du pays ({format_number(pib)}). Emprunt refusé pour raison de stabilité économique !", ephemeral=True)
            return
    # Débit du rôle ou Banque centrale
    if role:
        balances[role_id] = balances.get(role_id, 0) - somme
        debiteur = role.mention
        print(f"[DEBUG] Débit du pays {role.name} (ID: {role_id}), montant: {somme}")
    else:
        debiteur = "Banque centrale"
        print(f"[DEBUG] Débit de la Banque centrale, montant: {somme}")
    
    # Crédit du demandeur
    balances[demandeur_id] = balances.get(demandeur_id, 0) + somme
    print(f"[DEBUG] Crédit du demandeur {interaction.user.name} (ID: {demandeur_id}), montant: {somme}")
    # Création de l'emprunt
    emprunt = {
        "id": f"{demandeur_id}-{int(time.time())}",
        "demandeur_id": demandeur_id,
        "role_id": role_id,
        "somme": somme,
        "taux": taux,
        "duree": duree,
        "nombre_paiement": nombre_paiement,
        "restant": somme,
        "date_debut": int(time.time()),
        "remboursements": []
    }
    loans.append(emprunt)
    save_loans(loans)
    save_balances(balances)
    
    print(f"[DEBUG] Emprunt créé: demandeur={demandeur_id}, role_id={role_id}, somme={somme}, taux={taux}")
    print(f"[DEBUG] Total emprunts actifs: {len(loans)}")
    
    # Log de la transaction
    log_transaction(
        from_id=role_id if role else banque_centrale_id,
        to_id=demandeur_id,
        amount=somme,
        transaction_type="emprunt",
        guild_id=str(interaction.guild.id)
    )
    save_all_json_to_postgres()
    # Log embed
    embed = discord.Embed(
        title="💸 | Création d'emprunt",
        description=(
            f"> **Demandeur :** {interaction.user.mention}\n"
            f"> **Montant :** {format_number(somme)} {MONNAIE_EMOJI}\n"
            f"> **Taux :** {taux}%\n"
            f"> **Durée prévue :** {duree} (informatif)\n"
            f"> **Nombre de paiements prévus :** {nombre_paiement if nombre_paiement else 'Non défini'}\n"
            f"> **Débiteur :** {debiteur}{INVISIBLE_CHAR}"
        ),
        color=EMBED_COLOR,
        timestamp=datetime.datetime.now()
    )
    await send_log(interaction.guild, embed=embed)
    
    # Log dans le salon staff
    staff_channel_id = 1412876030980391063
    staff_channel = interaction.guild.get_channel(staff_channel_id)
    if staff_channel:
        await staff_channel.send(embed=embed)
    
    # Réponse à l'utilisateur
    confirmation_embed = discord.Embed(
        title="✅ | Emprunt créé avec succès",
        description=(
            f"> **Montant accordé :** {format_number(somme)} {MONNAIE_EMOJI}\n"
            f"> **Taux d'intérêt :** {taux}%\n"
            f"> **Durée prévue :** {duree} (informatif)\n"
            f"> **Montant total à rembourser :** {format_number(int(somme * (1 + taux / 100)))} {MONNAIE_EMOJI}\n"
            f"> **Source :** {debiteur}\n"
            f"> ⚠️ **Note :** La durée est purement informative, aucun remboursement automatique."
        ),
        color=0x00FF00
    )
    await interaction.followup.send(embed=confirmation_embed, ephemeral=True)

# Commande /liste_emprunt : affiche la liste des emprunts du joueur avec pagination
@bot.tree.command(name="liste_emprunt", description="Affiche la liste de vos emprunts")
async def liste_emprunt(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    # Filtrer les emprunts du joueur
    emprunts_user = [e for e in loans if e["demandeur_id"] == user_id]
    if not emprunts_user:
        await interaction.response.send_message("> Vous n'avez aucun emprunt en cours.", ephemeral=True)
        return
    # Pagination : 5 emprunts par page
    pages = []
    for i in range(0, len(emprunts_user), 5):
        emprunts_page = emprunts_user[i:i+5]
        texte = ""
        for idx, emprunt in enumerate(emprunts_page, start=i+1):
            # Calcul du montant à rembourser
            montant_rembourse = int(emprunt["somme"] * (1 + emprunt["taux"] / 100))
            if emprunt["role_id"]:
                # Emprunt auprès d'un rôle
                role_obj = interaction.guild.get_role(int(emprunt["role_id"])) if emprunt["role_id"] else None
                role_name = role_obj.mention if role_obj else "Rôle inconnu"
                texte += (
                    "⠀\n"
                    f"> {idx}. − Emprunt avec {role_name} :\n"
                    f"> − **Durée :** {emprunt['duree']}\n"
                    f"> − **Taux d'intérêt :** {emprunt['taux']}%\n"
                    f"> − **Somme emprunté :** {emprunt['somme']} {MONNAIE_EMOJI}\n"
                    f"> − **Somme à remboursé :** {montant_rembourse} {MONNAIE_EMOJI}\n⠀"
                )
            else:
                # Emprunt auprès de la Banque centrale
                texte += (
                    "⠀\n"
                    f"> {idx}. − Emprunt formulé à la **Banque centrale** :\n"
                    f"> − **Durée :** {emprunt['duree']}\n"
                    f"> − **Taux d'intérêt :** {emprunt['taux']}%\n"
                    f"> − **Somme emprunté :** {emprunt['somme']} {MONNAIE_EMOJI}\n"
                    f"> − **Somme à remboursé :** {montant_rembourse} {MONNAIE_EMOJI}\n⠀"
                )
        embed = discord.Embed(
            title="💰 | Liste des Emprunts",
            description=texte,
            color=EMBED_COLOR
        )
        pages.append(embed)
    # Affichage avec pagination si besoin
    if len(pages) == 1:
        await interaction.response.send_message(embed=pages[0], ephemeral=True)
    else:
        view = PaginationView(pages, interaction.user.id)
        await interaction.response.send_message(embed=pages[0], view=view, ephemeral=True)

# Commande /remboursement : sélectionne un emprunt et effectue un paiement
@bot.tree.command(name="remboursement", description="Rembourse un emprunt en cours")
@app_commands.describe(
    numero_emprunt="Numéro de l'emprunt à rembourser (voir /liste_emprunt)",
    montant="Montant à rembourser"
)
async def remboursement(
    interaction: discord.Interaction,
    numero_emprunt: int,
    montant: int
):
        """
        Permet de rembourser un emprunt en cours en saisissant son numéro (voir /liste_emprunt).
        Le montant à rembourser inclut le taux d'intérêt.
        Si l'emprunt est auprès de la Banque centrale, l'argent est détruit.
        Si l'emprunt est auprès d'un pays (rôle), l'argent est transféré à ce pays.
        """
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)
        emprunts_user = [e for e in loans if e["demandeur_id"] == user_id]
        if not emprunts_user:
            await interaction.followup.send("> Aucun emprunt trouvé pour vous.", ephemeral=True)
            return
        if numero_emprunt < 1 or numero_emprunt > len(emprunts_user):
            await interaction.followup.send(f"> Numéro d'emprunt invalide. Utilisez /liste_emprunt pour voir vos emprunts.", ephemeral=True)
            return
        emprunt = emprunts_user[numero_emprunt - 1]
        # Calcul du montant total à rembourser (somme + intérêts)
        principal = emprunt.get("somme", 0)
        taux = emprunt.get("taux", 0)
        total_remboursement = int(principal * (1 + taux / 100))
        deja_rembourse = sum([r["montant"] for r in emprunt.get("remboursements", [])])
        restant = total_remboursement - deja_rembourse
        if montant <= 0 or montant > restant:
            await interaction.followup.send(f"> Montant invalide. Il reste à rembourser : {restant} {MONNAIE_EMOJI}.", ephemeral=True)
            return
        # Débit du joueur
        if balances.get(user_id, 0) < montant:
            await interaction.followup.send(f"> Fonds insuffisants pour le remboursement.", ephemeral=True)
            return
        balances[user_id] = balances.get(user_id, 0) - montant
        # Crédit du pays ou destruction
        if emprunt["role_id"]:
            # Créditer le pays
            balances[emprunt["role_id"]] = balances.get(emprunt["role_id"], 0) + montant
            destinataire = interaction.guild.get_role(int(emprunt["role_id"])).mention if interaction.guild.get_role(int(emprunt["role_id"])) else "Pays inconnu"
        else:
            destinataire = "Banque centrale (argent détruit)"
        # Mise à jour du remboursement
        if "remboursements" not in emprunt:
            emprunt["remboursements"] = []
        emprunt["remboursements"].append({"montant": montant, "date": int(time.time())})
        restant_apres = restant - montant
        
        # Si l'emprunt est totalement remboursé, le supprimer de la liste
        if restant_apres <= 0:
            loans.remove(emprunt)
            print(f"[DEBUG] Emprunt n°{numero_emprunt} totalement remboursé et supprimé")
        
        save_balances(balances)
        save_loans(loans)
        save_all_json_to_postgres()
        
        # Message de confirmation
        if restant_apres <= 0:
            await interaction.followup.send(
                f"> Emprunt n°{numero_emprunt} totalement remboursé et supprimé ! ✅\n> Destinataire : {destinataire}\n> Montant total remboursé : {format_number(total_remboursement)} {MONNAIE_EMOJI}.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"> Remboursement de {format_number(montant)} {MONNAIE_EMOJI} effectué pour l'emprunt n°{numero_emprunt}.\n> Destinataire : {destinataire}\n> Il reste à rembourser : {format_number(restant_apres)} {MONNAIE_EMOJI}.",
                ephemeral=True
            )

@bot.tree.command(name="reset_debt", description="Supprime toutes les dettes et emprunts du serveur")
@app_commands.checks.has_permissions(administrator=True)
async def reset_debt(interaction: discord.Interaction):
    """Supprime toutes les dettes et emprunts."""
    await interaction.response.defer(ephemeral=True)
    
    # Sauvegarder le nombre d'emprunts avant suppression
    nombre_emprunts = len(loans)
    
    # Calculer le montant total des emprunts
    montant_total = 0
    for emprunt in loans:
        principal = emprunt.get("somme", 0)
        taux = emprunt.get("taux", 0)
        montant_total += int(principal * (1 + taux / 100))
    
    # Vider la liste des emprunts
    loans.clear()
    
    # Sauvegarder les changements
    save_loans(loans)
    save_all_json_to_postgres()
    
    # Log de l'action
    embed_log = discord.Embed(
        title="🗑️ | Réinitialisation des dettes",
        description=(
            f"> **Administrateur :** {interaction.user.mention}\n"
            f"> **Emprunts supprimés :** {nombre_emprunts}\n"
            f"> **Montant total effacé :** {format_number(montant_total)} {MONNAIE_EMOJI}\n"
            f"> **Date :** {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        ),
        color=0xFF6B6B,
        timestamp=datetime.datetime.now()
    )
    await send_log(interaction.guild, embed=embed_log)
    
    # Confirmation à l'utilisateur
    confirmation_embed = discord.Embed(
        title="✅ | Dettes supprimées",
        description=(
            f"> **{nombre_emprunts} emprunts** ont été supprimés\n"
            f"> **Montant total effacé :** {format_number(montant_total)} {MONNAIE_EMOJI}\n"
            f"> Toutes les dettes ont été annulées"
        ),
        color=0x00FF00
    )
    await interaction.followup.send(embed=confirmation_embed, ephemeral=True)

    # === Mise à jour des salons vocaux de stats ===

async def update_stats_voice_channels(guild):
    category_id = 1418006771053887571
    membres_role_id = 1393340583665209514
    joueurs_role_id = 1410289640170328244
    noms_salons = {
        "membres": f"╭【👥】・𝗠embres : ",
        "joueurs": f"╰【✅】・𝗝oueurs : "
    }
    category = guild.get_channel(category_id)
    if not category or not isinstance(category, discord.CategoryChannel):
        print(f"[STATS VOICE] Catégorie non trouvée ou invalide : {category}")
        return
    membres_role = guild.get_role(membres_role_id)
    joueurs_role = guild.get_role(joueurs_role_id)
    membres_count = len(membres_role.members) if membres_role else 0
    joueurs_count = len(joueurs_role.members) if joueurs_role else 0
    # Cherche les salons existants
    membres_channel = None
    joueurs_channel = None
    for channel in category.voice_channels:
        if channel.name.startswith(noms_salons["membres"]):
            membres_channel = channel
        if channel.name.startswith(noms_salons["joueurs"]):
            joueurs_channel = channel
    # Met à jour ou crée le salon Membres
    membres_name = f"{noms_salons['membres']}{membres_count}"
    if membres_channel:
        await membres_channel.edit(name=membres_name)
    else:
        await category.create_voice_channel(name=membres_name)
    # Met à jour ou crée le salon Joueurs
    joueurs_name = f"{noms_salons['joueurs']}{joueurs_count}"
    if joueurs_channel:
        await joueurs_channel.edit(name=joueurs_name)
    else:
        await category.create_voice_channel(name=joueurs_name)

# === Bloc principal déplacé à la toute fin du fichier ===

# === Tâche planifiée pour mise à jour des salons vocaux de stats ===
from discord.ext.tasks import loop

@loop(seconds=600)
async def update_stats_voice_channels_periodically():
    guild = bot.get_guild(PRIMARY_GUILD_ID)
    if guild:
        print("[DEBUG] Mise à jour périodique des salons vocaux de stats")
        await update_stats_voice_channels(guild)

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user.name}')
    await apply_permanent_presence(bot)

    # Migration des données de niveau
    print("🔄 Vérification et migration des données de niveau...")
    migrated = migrate_levels_data()
    if migrated > 0:
        print(f"✅ {migrated} utilisateurs migrés vers le nouveau système de niveau")
    else:
        print("✅ Données de niveau déjà à jour")

    # Initialisation d'Ollama supprimée

    try:
        cmds = await bot.tree.sync()
        print(f"Commandes synchronisées globalement ({len(cmds)}) : {[c.name for c in cmds]}")
    except Exception as exc:
        print(f"[SYNC ERROR] Synchronisation globale échouée : {exc}")

    await restore_mutes_on_start()
    await verify_economy_data(bot)

    guild = bot.get_guild(PRIMARY_GUILD_ID)
    if guild:
        await update_stats_voice_channels(guild)

    if not update_stats_voice_channels_periodically.is_running():
        update_stats_voice_channels_periodically.start()

    calendrier_data = load_calendrier()
    if calendrier_data and calendrier_data["mois_index"] < len(CALENDRIER_MONTHS):
        # Vérifier et rattraper le calendrier si nécessaire
        print("📅 Vérification du calendrier au démarrage...")
        calendrier_rattrape = await check_and_catchup_calendrier()
        if calendrier_rattrape:
            print("✅ Calendrier rattrapé automatiquement")
        else:
            print("✅ Calendrier déjà à jour")
        
        # Démarrer la tâche de mise à jour si pas déjà en cours
        if not calendrier_update_task.is_running():
            calendrier_update_task.start()
            print("🔄 Tâche de mise à jour du calendrier démarrée")
    else:
        print("📅 Aucun calendrier actif ou calendrier terminé")

# === Mise à jour dynamique des salons vocaux de stats ===
@bot.event
async def on_member_update(before, after):
    membres_role_id = WELCOME_ROLE_ID
    joueurs_role_id = 1410289640170328244
    guild = after.guild
    if guild is None:
        return
    before_roles = set(r.id for r in before.roles)
    after_roles = set(r.id for r in after.roles)
    if WELCOME_ROLE_ID not in before_roles and WELCOME_ROLE_ID in after_roles:
        channel = guild.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            try:
                await channel.send(WELCOME_PUBLIC_MESSAGE.format(mention=after.mention))
            except Exception as exc:
                print(f"[WARN] Impossible d'envoyer le message de bienvenue public: {exc}")
        try:
            await after.send(WELCOME_DM_MESSAGE)
        except discord.Forbidden:
            print(f"[WARN] Impossible d'envoyer un DM de bienvenue à {after} (forbidden)")
        except discord.HTTPException as exc:
            print(f"[WARN] Échec de l'envoi du DM de bienvenue: {exc}")
    if membres_role_id in before_roles or membres_role_id in after_roles or joueurs_role_id in before_roles or joueurs_role_id in after_roles:
        print(f"[DEBUG] Changement de rôle détecté pour {after.display_name} (avant: {before_roles}, après: {after_roles})")
        print(f"[DEBUG] Appel de update_stats_voice_channels pour guild: {guild.name} ({guild.id})")
        await update_stats_voice_channels(guild)

    category_id = 1418006771053887571
    membres_role_id = WELCOME_ROLE_ID
    joueurs_role_id = 1410289640170328244
    membres_channel_id = 1418018437485166741
    joueurs_channel_id = 1418018438990925864
    noms_salons = {
        "membres": f"╭【👥】・𝗠embres : ",
        "joueurs": f"╰【✅】・𝗝oueurs : "
    }
    membres_role = guild.get_role(membres_role_id)
    joueurs_role = guild.get_role(joueurs_role_id)
    membres_count = len(membres_role.members) if membres_role else 0
    joueurs_count = len(joueurs_role.members) if joueurs_role else 0
    membres_channel = guild.get_channel(membres_channel_id)
    joueurs_channel = guild.get_channel(joueurs_channel_id) if joueurs_channel_id else None
    membres_name = f"{noms_salons['membres']}{membres_count}"
    joueurs_name = f"{noms_salons['joueurs']}{joueurs_count}"
    # Mise à jour uniquement si le nombre a changé
    if membres_channel:
        if membres_channel.name != membres_name:
            print(f"[DEBUG] Mise à jour du nom du salon Membres: {membres_channel.name} -> {membres_name}")
            await membres_channel.edit(name=membres_name)
        else:
            print(f"[DEBUG] Aucun changement pour le salon Membres")
    else:
        print(f"[DEBUG] Salon Membres non trouvé (ID: {membres_channel_id})")
    if joueurs_channel:
        if joueurs_channel.name != joueurs_name:
            print(f"[DEBUG] Mise à jour du nom du salon Joueurs: {joueurs_channel.name} -> {joueurs_name}")
            await joueurs_channel.edit(name=joueurs_name)
        else:
            print(f"[DEBUG] Aucun changement pour le salon Joueurs")
    else:
        print(f"[DEBUG] Salon Joueurs non modifié (aucun ID fourni)")

@bot.tree.command(name="creer_stats_voice_channels", description="Crée les salons vocaux de stats dans la catégorie stats (temporaire)")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(categorie="Catégorie où créer les salons vocaux de stats")
async def creer_stats_voice_channels(interaction: discord.Interaction, categorie: discord.CategoryChannel):
    await interaction.response.defer(ephemeral=True)
    membres_role_id = 1393340583665209514
    joueurs_role_id = 1410289640170328244
    noms_salons = {
        "membres": f"╭【👥】・𝗠embres : ",
        "joueurs": f"╰【✅】・𝗝oueurs : "
    }
    guild = interaction.guild
    membres_role = guild.get_role(membres_role_id)
    joueurs_role = guild.get_role(joueurs_role_id)
    membres_count = len(membres_role.members) if membres_role else 0
    joueurs_count = len(joueurs_role.members) if joueurs_role else 0
    membres_name = f"{noms_salons['membres']}{membres_count}"
    joueurs_name = f"{noms_salons['joueurs']}{joueurs_count}"
    # Crée les salons vocaux si non existants
    membres_channel = None
    joueurs_channel = None
    for channel in categorie.voice_channels:
        if channel.name.startswith(noms_salons['membres']):
            membres_channel = channel
        if channel.name.startswith(noms_salons['joueurs']):
            joueurs_channel = channel
    if not membres_channel:
        membres_channel = await categorie.create_voice_channel(membres_name)
    if not joueurs_channel:
        joueurs_channel = await categorie.create_voice_channel(joueurs_name)
    embed = discord.Embed(
        description=f"Salons vocaux de stats créés :\n- {membres_channel.mention}\n- {joueurs_channel.mention}",
        color=0xefe7c5
    )
    await interaction.followup.send(embed=embed, ephemeral=True)

# === Commande /guide (présentation serveur) ===
@bot.tree.command(name="guide", description="Guide de présentation du serveur")
async def guide(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🪐 | Guide de Présentation du Serveur",
        description="⠀\n> − Voici le serveur **PAX RUINAE** <:Logo_PaxRuinae:1410270324985168032>, descendant de plusieurs serveurs sous la direction de <@772821169664426025>. Celui-ci se veut le plus ambitieux de ces projets dans le cadre d'un rôleplay **« Nouvelle ère »**, où le but est de créer sa propre nation dans un monde qui a chuté à la suite d’un apocalypse causé par l'homme. Dans ce rôleplay, vous ferez peut-être partie de ses acteurs qui marqueront l'histoire par leur RP ✨.\n> \n> − Dans ce serveur, vous trouverez tout ce dont vous avez besoin avec notamment les éléments au sein du RP qui sont présenter dans des Règlements, des Ressources RP pour présenter quelques autres éléments mineurs à celui-ci.\n> \n> − En premier lieu, il y a la catégorie **« Informations Générales »**. Il y a notamment les différents salons d'annonces : <#1393350471661387846> pour le HRP, et le salon <#1411066244848816179> pour le RP, le salon <#1411066404597268550>, mais également les différents salons liés aux partenariats : le salon <#1410271619930259496> listant les partenariats actifs, le salon <#1411068927978508359> qui liste les différentes conditions si un autre serveur propose un partenariat avec le nôtre, et le salon <#1395547599649378304> qui met en avant la dite pub du serveur.\n> \n> − Il y a également la catégorie **« L'Administration »**. Ici, il y a différents salons qui listent les actions du staff de **PAX RUINAE** <:Logo_PaxRuinae:1410270324985168032>, comme les <#1411053256926302278>, mais également un explicatif des rôles de celui-ci <#1414284229189046385> et de la <#1414283395537572030>.\n> \n> − Enfin, il y a la catégorie **« Règlements du Serveur »**. Elle liste directement tous les règlements dans cette catégorie-ci, à savoir le <#1393318935692312787>, le <#1410450203433111764>, le <#1393324090562973776>, le <#1393324354619576362>, le <#1393325798685016256>, et enfin le <#1410450325248147560>.\n> \n> − <:PX_Attention:1417603257953685616> : Si vous n'avez pas forcément tous les salons dans votre liste, n'oubliez pas d'activer l’option **« Montrer tous les salons »**, cela vous aidera à vous repérer. Dans cette présentation, les salons cités sont __non exhaustifs__ ; il en existe d'autres, plus ou moins importants.\n⠀",
        color=0x162e50
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1412872314525192233/1418276962417512539/PAX_RUINAE.png?ex=68cd88da&is=68cc375a&hm=2d58da59a0d97e4263759860e12b0bf72d7f35785a72d8b1eb08efc1c83310d5&")
    embed.set_image(url="https://cdn.discordapp.com/attachments/1412872314525192233/1418276839624937512/image.png?ex=68cd88bc&is=68cc373c&hm=ad9b769761c9b1c2d4dc6f0a783d3bcaf0ee3c09a48e8cc4fc5a9865458ae806&")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# === CALENDRIER RP ===
CALENDRIER_FILE = os.path.join(DATA_DIR, "calendrier.json")
CALENDRIER_CHANNEL_ID = 1419301872996712458
CALENDRIER_IMAGE_URL = "https://cdn.discordapp.com/attachments/1393317478133661746/1431389849864245298/balance_1.png?ex=68fd3d2e&is=68fbebae&hm=015733b6848f31b9ba2b922cd570066fab64fcf2a0f7ba953363cd876f18b7a1&"
CALENDRIER_COLOR = 0x162e50
CALENDRIER_EMOJI = "<:PX_Calendrier:1417607613587259505>"
CALENDRIER_MONTHS = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
]

def load_calendrier():
    if os.path.exists(CALENDRIER_FILE):
        with open(CALENDRIER_FILE, "r") as f:
            return json.load(f)
    return None

def save_calendrier(data):
    with open(CALENDRIER_FILE, "w") as f:
        json.dump(data, f)

def reset_calendrier():
    if os.path.exists(CALENDRIER_FILE):
        os.remove(CALENDRIER_FILE)

async def check_and_catchup_calendrier():
    """
    Vérifie si le calendrier a pris du retard et le rattrape automatiquement.
    Appelé lors de la reconnexion du bot.
    """
    try:
        # Restaurer depuis PostgreSQL d'abord pour avoir les données les plus récentes
        restore_all_json_from_postgres()
        print("📥 Données restaurées depuis PostgreSQL")
        
        calendrier_data = load_calendrier()
        if not calendrier_data:
            print("📅 Aucun calendrier actif à vérifier")
            return False
        
        # Heure actuelle Paris
        now = datetime.datetime.now(ZoneInfo("Europe/Paris"))
        last_update = calendrier_data.get("last_update")
        
        if not last_update:
            print("📅 Aucune dernière mise à jour trouvée dans le calendrier")
            return False
        
        # Parser la dernière mise à jour
        last_update_dt = datetime.datetime.fromisoformat(last_update)
        if last_update_dt.tzinfo is None:
            last_update_dt = last_update_dt.replace(tzinfo=ZoneInfo("Europe/Paris"))
        else:
            last_update_dt = last_update_dt.astimezone(ZoneInfo("Europe/Paris"))
        
        # Calculer les jours écoulés
        delta = now - last_update_dt
        jours_ecoules = delta.days
        
        print(f"📅 Dernière MAJ calendrier: {last_update_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"📅 Heure actuelle: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"📅 Jours écoulés: {jours_ecoules}")
        
        if jours_ecoules <= 0:
            print("📅 Calendrier à jour, aucun rattrapage nécessaire")
            return False
        
        # Variables de l'état actuel
        mois_index = calendrier_data["mois_index"]
        jour_index = calendrier_data["jour_index"]
        jours_irl_actuel = calendrier_data.get("jours_irl_actuel", 0)
        
        print(f"📅 État avant rattrapage: Mois {mois_index}, Jour {jour_index}, Jours IRL: {jours_irl_actuel}")
        
        # Simuler les jours écoulés
        jours_a_simuler = jours_ecoules
        avancements = 0
        
        channel = bot.get_channel(CALENDRIER_CHANNEL_ID)
        
        while jours_a_simuler > 0 and mois_index < len(CALENDRIER_MONTHS):
            # Déterminer combien de jours IRL pour ce mois (alternance 2j/1j)
            if mois_index % 2 == 0:  # Mois pairs : 2 jours IRL
                jours_requis = 2
            else:  # Mois impairs : 1 jour IRL
                jours_requis = 1
            
            # Incrémenter le compteur de jours IRL
            jours_irl_actuel += 1
            jours_a_simuler -= 1
            
            # Avancer le jour uniquement si on a atteint le nombre de jours requis
            if jours_irl_actuel >= jours_requis:
                if jour_index == 0:
                    jour_index = 1
                    print(f"📅 Avancement: {CALENDRIER_MONTHS[mois_index]} 1/2 → 2/2")
                else:
                    jour_index = 0
                    mois_index += 1
                    if mois_index < len(CALENDRIER_MONTHS):
                        print(f"📅 Avancement: {CALENDRIER_MONTHS[mois_index-1]} 2/2 → {CALENDRIER_MONTHS[mois_index]} 1/2")
                    else:
                        print(f"📅 Calendrier terminé après {CALENDRIER_MONTHS[mois_index-1]} 2/2")
                        break
                
                # Reset le compteur pour le prochain mois
                jours_irl_actuel = 0
                avancements += 1
                
                # Poster le message dans le canal calendrier si disponible
                if channel and mois_index < len(CALENDRIER_MONTHS):
                    mois = CALENDRIER_MONTHS[mois_index]
                    jour_str = "1/2" if jour_index == 0 else "2/2"
                    
                    embed = discord.Embed(
                        description=f"{CALENDRIER_EMOJI} {mois} {calendrier_data['annee']} - {jour_str}\n\n"
                                   f"⚡ Rattrapage automatique du calendrier !\n"
                                   f"Le calendrier a été mis à jour automatiquement.",
                        color=CALENDRIER_COLOR
                    )
                    embed.set_image(url=CALENDRIER_IMAGE_URL)
                    
                    try:
                        message = await channel.send(embed=embed)
                        calendrier_data.setdefault("messages", [])
                        calendrier_data["messages"].append(str(message.id))
                    except Exception as e:
                        print(f"❌ Erreur lors de l'envoi du message de rattrapage: {e}")
        
        # Mettre à jour les données
        calendrier_data["mois_index"] = mois_index
        calendrier_data["jour_index"] = jour_index
        calendrier_data["jours_irl_actuel"] = jours_irl_actuel
        calendrier_data["last_update"] = now.isoformat()
        
        save_calendrier(calendrier_data)
        save_all_json_to_postgres()
        
        print(f"📅 État après rattrapage: Mois {mois_index}, Jour {jour_index}, Jours IRL: {jours_irl_actuel}")
        print(f"✅ Calendrier rattrapé avec {avancements} avancement(s)")
        
        # Vérifier et terminer automatiquement les développements dans tous les serveurs
        if avancements > 0:
            total_completed = 0
            for guild in bot.guilds:
                guild_id = str(guild.id)
                developments_completed = check_and_complete_developments(guild_id)
                total_completed += developments_completed
                if developments_completed > 0:
                    print(f"📅 Rattrapage automatique: {developments_completed} développements terminés dans {guild.name}")
            
            if total_completed > 0:
                print(f"📅 Total développements terminés lors du rattrapage: {total_completed}")
        
        # Arrêter la tâche si calendrier terminé
        if mois_index >= len(CALENDRIER_MONTHS):
            if calendrier_update_task.is_running():
                calendrier_update_task.stop()
                print("📅 Calendrier terminé, tâche automatique arrêtée")
        
        return avancements > 0
        
    except Exception as e:
        print(f"❌ Erreur lors du rattrapage du calendrier: {e}")
        return False

def calculate_fin_with_calendar(duree_mois):
    """
    Calcule la date de fin d'un développement en tenant compte du calendrier RP
    
    NOUVELLE LOGIQUE : Alternance 2 jours IRL (mois pairs) / 1 jour IRL (mois impairs)
    """
    calendrier_data = load_calendrier()
    if not calendrier_data:
        # Si pas de calendrier, utilise l'ancien système (approximation)
        return time.time() + (duree_mois * 1.5 * 24 * 3600)  # 1.5 jour moyen par mois
    
    mois_actuel = calendrier_data.get("mois_index", 0)
    annee_actuelle = calendrier_data.get("annee", 2025)
    
    # Calcule le mois de fin RP
    mois_fin = (mois_actuel + duree_mois) % 12
    annee_fin = annee_actuelle + ((mois_actuel + duree_mois) // 12)
    
    # Utilise la fonction de conversion pour avoir le timestamp IRL exact
    return calculate_real_timestamp_from_calendar(mois_fin, annee_fin)

def calculate_real_timestamp_from_calendar(mois_fin_rp, annee_fin_rp):
    """
    Convertit une date RP (mois, année) en timestamp réel IRL
    basé sur l'avancement du calendrier qui se met à jour à minuit heure Paris
    
    NOUVELLE LOGIQUE : Alternance 2 jours IRL (mois pairs) / 1 jour IRL (mois impairs)
    Chaque mois RP a 2 demi-mois (1/2 et 2/2)
    Le calendrier avance chaque nuit à minuit heure Paris
    """
    calendrier_data = load_calendrier()
    if not calendrier_data:
        # Fallback si pas de calendrier
        return int(time.time() + (30 * 24 * 3600))  # Dans 30 jours
    
    mois_actuel_rp = calendrier_data.get("mois_index", 0)
    annee_actuelle_rp = calendrier_data.get("annee", 2025)
    jour_actuel = calendrier_data.get("jour_index", 0)  # 0 = 1/2, 1 = 2/2
    
    # Calculer la différence en mois RP
    mois_total_actuel = annee_actuelle_rp * 12 + mois_actuel_rp
    mois_total_fin = annee_fin_rp * 12 + mois_fin_rp
    
    mois_difference = mois_total_fin - mois_total_actuel
    
    # Le calendrier se met à jour à minuit heure Paris (CET/CEST selon la saison)
    # 1 mois RP = 2 jours IRL (1/2 puis 2/2)
    # Utiliser ZoneInfo pour gérer automatiquement CET/CEST
    
    # Obtenir l'heure actuelle à Paris (gère automatiquement CET/CEST)
    now_paris = datetime.datetime.now(ZoneInfo("Europe/Paris"))
    
    # Calculer le prochain minuit à Paris
    demain = now_paris.date() + datetime.timedelta(days=1)
    next_midnight_paris = datetime.datetime.combine(demain, datetime.time(0, 0, 0), tzinfo=ZoneInfo("Europe/Paris"))
    
    # CORRECTION : Ajouter 1 heure pour compenser le décalage d'affichage Discord
    # Discord affiche 23h00 au lieu de 00h00 à cause du fuseau horaire local
    next_midnight_paris = next_midnight_paris + datetime.timedelta(hours=1)
    
    # NOUVELLE LOGIQUE : Calculer combien de jours IRL selon l'alternance 2j/1j
    jours_irl_necessaires = 0
    
    if mois_difference > 0:
        # Finir le mois actuel si on est sur 1/2
        if jour_actuel == 0:  # Actuellement 1/2
            # Déterminer les jours restants pour ce mois selon son type
            mois_type = mois_actuel_rp % 2  # 0 = pair (2j), 1 = impair (1j)
            if mois_type == 0:  # Mois pair = 2 jours IRL
                jours_irl_necessaires += 1  # 1 jour pour finir (passer à 2/2)
            else:  # Mois impair = 1 jour IRL (déjà fini après 1/2)
                jours_irl_necessaires += 0  # Déjà terminé
            
            # Calculer les mois suivants
            for i in range(1, mois_difference):
                mois_futur = (mois_actuel_rp + i) % 12
                if mois_futur % 2 == 0:  # Mois pair
                    jours_irl_necessaires += 2
                else:  # Mois impair
                    jours_irl_necessaires += 1
        else:  # Actuellement 2/2, commencer par les mois complets suivants
            for i in range(mois_difference):
                mois_futur = (mois_actuel_rp + i + 1) % 12
                if mois_futur % 2 == 0:  # Mois pair
                    jours_irl_necessaires += 2
                else:  # Mois impair
                    jours_irl_necessaires += 1
    elif mois_difference == 0:
        # Même mois RP
        if jour_actuel == 0:  # Actuellement 1/2
            mois_type = mois_actuel_rp % 2
            if mois_type == 0:  # Mois pair = 2 jours, développement finit à 2/2
                jours_irl_necessaires = 1
            else:  # Mois impair = 1 jour, développement déjà fini
                jours_irl_necessaires = 0
        else:  # Actuellement 2/2, développement fini
            jours_irl_necessaires = 0
    
    # Calculer le timestamp final
    fin_timestamp = next_midnight_paris + datetime.timedelta(days=jours_irl_necessaires)
    
    # Convertir en timestamp UTC
    return int(fin_timestamp.timestamp())

def get_rp_date_from_timestamp(timestamp):
    """
    Extrait la date RP (mois, année) d'un timestamp de fin de développement
    
    Logique : 1 mois RP = 2 jours IRL
    """
    calendrier_data = load_calendrier()
    if not calendrier_data:
        return None, None
        
    mois_actuel = calendrier_data.get("mois_index", 0)
    annee_actuelle = calendrier_data.get("annee", 2025)
    jour_actuel = calendrier_data.get("jour_index", 0)
    
    # Calculer la différence en secondes depuis maintenant
    diff_seconds = timestamp - time.time()
    diff_jours = diff_seconds / (24 * 3600)  # Différence en jours IRL
    
    # Convertir les jours IRL en mois RP (1 mois RP = 2 jours IRL)
    # Si on est sur 1/2 d'un mois, il faut 1 jour pour finir ce mois
    mois_restants = diff_jours / 2.0  # Approximation
    
    # Calculer le mois et l'année de fin
    mois_fin = (mois_actuel + int(mois_restants)) % 12
    annee_fin = annee_actuelle + ((mois_actuel + int(mois_restants)) // 12)
    
    return mois_fin, annee_fin

def format_discord_timestamp(timestamp):
    """
    Formate un timestamp pour l'affichage Discord avec date complète
    """
    return f"<t:{int(timestamp)}:f>"

def format_development_end_info(dev):
    """
    Formate les informations de fin d'un développement avec timestamp Discord et date RP
    Prend en compte le nouveau système de statut
    """
    statut = dev.get('statut', 'en_cours')
    
    # Si le développement est marqué comme terminé
    if statut == 'termine':
        date_fin_reelle = dev.get('date_fin_reelle')
        if date_fin_reelle:
            try:
                date_formatee = format_paris_time(date_fin_reelle)
                return f"✅ **TERMINÉ** (le {date_formatee})"
            except:
                return "✅ **TERMINÉ**"
        return "✅ **TERMINÉ**"
    
    # Pour les développements en cours
    fin_timestamp = dev.get('fin_timestamp', 0)
    if fin_timestamp <= time.time():
        return "⚠️ **À TERMINER** (deadline dépassée)"
    
    # Timestamp Discord formaté
    discord_timestamp = format_discord_timestamp(fin_timestamp)
    
    # Date RP si disponible
    calendrier_data = load_calendrier()
    if calendrier_data:
        mois_fin, annee_fin = get_rp_date_from_timestamp(fin_timestamp)
        if mois_fin is not None and annee_fin is not None:
            nom_mois = CALENDRIER_MONTHS[mois_fin] if mois_fin < len(CALENDRIER_MONTHS) else "Mois inconnu"
            return f"⏳ **EN COURS**\n📅 Fin RP: **{nom_mois} {annee_fin}**\n🕐 Fin IRL: {discord_timestamp}"
    
    # Fallback sans calendrier
    temps_restant = fin_timestamp - time.time()
    jours = int(temps_restant // 86400)
    heures = int((temps_restant % 86400) // 3600)
    return f"⏳ **EN COURS**\n⏰ Fin dans {jours}j {heures}h\n🕐 Date: {discord_timestamp}"

from discord.ext.tasks import loop
import datetime

@bot.tree.command(name="calendrier", description="Lance le calendrier RP pour une année donnée")
@app_commands.describe(annee="Année RP à lancer (ex: 2025)")
@app_commands.checks.has_permissions(administrator=True)
async def calendrier(interaction: discord.Interaction, annee: int):
    # Initialisation ou reprise
    calendrier_data = load_calendrier()
    if calendrier_data:
        await interaction.response.send_message(f"> Un calendrier est déjà en cours pour l'année {calendrier_data['annee']} ! Utilisez /reset-calendrier pour recommencer.", ephemeral=True)
        return
    
    # Créer les données du calendrier
    calendrier_data = {
        "annee": annee,
        "mois_index": 0,
        "jour_index": 0, # 0 = 1/2, 1 = 2/2
        "last_update": None,
        "messages": [],
        "skip_first_midnight": False,  # Ne plus ignorer le premier passage
        "jours_irl_actuel": 0  # Compteur pour alterner 2j/1j
    }
    save_calendrier(calendrier_data)
    save_all_json_to_postgres()  # Sauvegarder dans PostgreSQL
    
    # Envoyer immédiatement le premier message du calendrier
    channel = bot.get_channel(CALENDRIER_CHANNEL_ID)
    if channel:
        mois_nom = CALENDRIER_MONTHS[0]  # Janvier
        
        embed = discord.Embed(
            title=f"{CALENDRIER_EMOJI} Calendrier RP - {mois_nom} {annee}",
            description=f"{CALENDRIER_EMOJI} {mois_nom} {annee} - 1/2\n\n"
                       f"Le calendrier RP a commencé !\n"
                       f"Nous sommes maintenant en {mois_nom} {annee}.",
            color=CALENDRIER_COLOR
        )
        
        embed.set_image(url=CALENDRIER_IMAGE_URL)
        embed.set_footer(text="Calendrier RP • Alternance 2j/1j IRL")
        
        try:
            message = await channel.send(embed=embed)
            calendrier_data["messages"] = [str(message.id)]
            
            # Marquer la première mise à jour comme faite
            now = datetime.datetime.now(ZoneInfo("Europe/Paris"))
            calendrier_data["last_update"] = now.isoformat()
            save_calendrier(calendrier_data)
            save_all_json_to_postgres()
            
        except Exception as e:
            print(f"Erreur lors de l'envoi du premier message calendrier: {e}")
    
    # Démarrer la tâche pour les mises à jour futures
    calendrier_update_task.start()
    
    await interaction.response.send_message(f"> Calendrier RP lancé pour l'année {annee}. Le premier message a été envoyé et les mises à jour se feront chaque jour à minuit (heure Paris).", ephemeral=True)

@bot.tree.command(name="reset-calendrier", description="Réinitialise le calendrier RP")
@app_commands.checks.has_permissions(administrator=True)
async def reset_calendrier_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    # Arrête la tâche si elle tourne
    if calendrier_update_task.is_running():
        calendrier_update_task.stop()
    # Supprime les messages précédemment envoyés
    calendrier_data = load_calendrier()
    deleted_count = 0
    channel = bot.get_channel(CALENDRIER_CHANNEL_ID)
    message_ids = []
    if calendrier_data:
        message_ids = [int(mid) for mid in calendrier_data.get("messages", []) if str(mid).isdigit()]

    # Fallback: si aucun ID stocké, tenter de retrouver les messages récents du bot
    async def delete_message(message_id: int) -> None:
        nonlocal deleted_count
        if not channel:
            return
        try:
            message = await channel.fetch_message(message_id)
            await message.delete()
            deleted_count += 1
        except (discord.NotFound, discord.Forbidden):
            pass
        except discord.HTTPException:
            pass

    if channel:
        if not message_ids:
            message_ids = []
            async for message in channel.history(limit=100):
                if message.author != bot.user:
                    continue
                if not message.embeds:
                    continue
                embed = message.embeds[0]
                embed_desc = embed.description or ""
                if embed.image and embed.image.url == CALENDRIER_IMAGE_URL:
                    message_ids.append(message.id)
                    continue
                if CALENDRIER_EMOJI in embed_desc:
                    message_ids.append(message.id)
        for mid in message_ids:
            await delete_message(int(mid))

    # Supprime le fichier calendrier.json
    reset_calendrier()

    # Supprime également la sauvegarde PostgreSQL pour éviter une restauration au redémarrage
    remote_deleted = False
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        try:
            import psycopg2  # type: ignore

            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM json_backups WHERE filename = %s", ("calendrier.json",))
                    remote_deleted = cur.rowcount > 0
                conn.commit()
        except Exception as e:
            print(f"[DEBUG] Échec suppression calendrier.json dans PostgreSQL : {e}")

    await interaction.followup.send(
        f"> Le calendrier RP a été totalement réinitialisé. Tous les effets de /calendrier sont annulés."
        + (f" ({deleted_count} message(s) supprimé(s))." if deleted_count else "")
        + (" Sauvegarde PostgreSQL nettoyée." if remote_deleted else ""),
        ephemeral=True
    )

@bot.tree.command(name="pass_mois", description="📅 Fait avancer le calendrier RP jusqu'au mois suivant")
@app_commands.checks.has_permissions(administrator=True)
async def pass_mois_cmd(interaction: discord.Interaction):
    """Fait avancer le calendrier RP jusqu'au mois suivant en respectant la logique d'alternance."""
    await interaction.response.defer(ephemeral=True)
    
    # Vérifier qu'un calendrier est actif
    calendrier_data = load_calendrier()
    if not calendrier_data:
        await interaction.followup.send(
            "❌ Aucun calendrier RP n'est actuellement actif.\n"
            "Utilisez `/calendrier` pour en lancer un.",
            ephemeral=True
        )
        return
    
    # Vérifier que le calendrier n'est pas terminé
    if calendrier_data["mois_index"] >= len(CALENDRIER_MONTHS):
        await interaction.followup.send(
            "❌ Le calendrier RP est déjà terminé.\n"
            "Utilisez `/calendrier` pour lancer une nouvelle année.",
            ephemeral=True
        )
        return
    
    # État actuel
    mois_actuel = calendrier_data["mois_index"]
    jour_actuel = calendrier_data["jour_index"]
    jours_irl_actuel = calendrier_data.get("jours_irl_actuel", 0)
    annee = calendrier_data["annee"]
    
    # Simuler l'avancement jusqu'au prochain mois
    sim_mois = mois_actuel
    sim_jour = jour_actuel
    sim_jours_irl = jours_irl_actuel
    jours_simules = 0
    
    # Continuer jusqu'à atteindre le prochain mois
    while sim_mois == mois_actuel and sim_mois < len(CALENDRIER_MONTHS):
        # Déterminer combien de jours IRL pour ce mois (alternance 2j/1j)
        if sim_mois % 2 == 0:  # Mois pairs : 2 jours IRL
            jours_requis = 2
        else:  # Mois impairs : 1 jour IRL
            jours_requis = 1
        
        # Incrémenter le compteur de jours IRL
        sim_jours_irl += 1
        jours_simules += 1
        
        # Avancer le jour uniquement si on a atteint le nombre de jours requis
        if sim_jours_irl >= jours_requis:
            if sim_jour == 0:
                sim_jour = 1  # 1/2 → 2/2
            else:
                sim_jour = 0  # 2/2 → 1/2 du mois suivant
                sim_mois += 1
            
            # Reset le compteur pour le prochain cycle
            sim_jours_irl = 0
    
    # Vérifier qu'on n'a pas dépassé la fin du calendrier
    if sim_mois >= len(CALENDRIER_MONTHS):
        await interaction.followup.send(
            f"❌ Impossible d'avancer au mois suivant : le calendrier se terminerait.\n"
            f"Mois actuel : **{CALENDRIER_MONTHS[mois_actuel]} {annee}**\n"
            f"Il s'agit du dernier mois de l'année RP.",
            ephemeral=True
        )
        return
    
    # Créer l'embed de confirmation
    embed_confirm = discord.Embed(
        title="📅 Confirmation d'Avancement",
        color=0xff6600
    )
    
    mois_actuel_nom = CALENDRIER_MONTHS[mois_actuel]
    nouveau_mois_nom = CALENDRIER_MONTHS[sim_mois]
    jour_actuel_str = "1/2" if jour_actuel == 0 else "2/2"
    nouveau_jour_str = "1/2" if sim_jour == 0 else "2/2"
    
    description = f"**Calendrier RP actuel :**\n"
    description += f"📅 {mois_actuel_nom} {annee} - {jour_actuel_str}\n"
    description += f"🕐 Jours IRL actuels : {jours_irl_actuel}\n\n"
    description += f"**Après avancement :**\n"
    description += f"📅 {nouveau_mois_nom} {annee} - {nouveau_jour_str}\n"
    description += f"🕐 Jours IRL simulés : {jours_simules}\n\n"
    description += f"⚡ Cette action va faire avancer le calendrier jour par jour jusqu'au mois suivant.\n"
    description += f"🔄 La logique d'alternance 2j/1j sera respectée.\n"
    description += f"🔬 **Tous les développements expirés seront finalisés.**\n\n"
    description += f"Confirmez-vous cet avancement ?"
    
    embed_confirm.description = description
    
    # Créer les boutons de confirmation
    view = discord.ui.View(timeout=60)
    
    # Bouton Confirmer
    async def confirmer_avancement(button_interaction):
        await button_interaction.response.defer()
        
        try:
            # Recharger les données pour être sûr
            calendrier_data_fresh = load_calendrier()
            if not calendrier_data_fresh:
                await button_interaction.followup.send(
                    "❌ Le calendrier a été supprimé entre temps.",
                    ephemeral=True
                )
                return
            
            # Re-simuler l'avancement pour obtenir l'état final
            temp_mois = calendrier_data_fresh["mois_index"]
            temp_jour = calendrier_data_fresh["jour_index"]
            temp_jours_irl = calendrier_data_fresh.get("jours_irl_actuel", 0)
            mois_initial = temp_mois
            avancements = 0
            
            # Simuler pas à pas jusqu'au prochain mois
            channel = bot.get_channel(CALENDRIER_CHANNEL_ID)
            
            while temp_mois == mois_initial and temp_mois < len(CALENDRIER_MONTHS):
                # Déterminer combien de jours IRL pour ce mois (alternance 2j/1j)
                if temp_mois % 2 == 0:  # Mois pairs : 2 jours IRL
                    jours_requis = 2
                else:  # Mois impairs : 1 jour IRL
                    jours_requis = 1
                
                # Incrémenter le compteur de jours IRL
                temp_jours_irl += 1
                
                # Avancer le jour uniquement si on a atteint le nombre de jours requis
                if temp_jours_irl >= jours_requis:
                    if temp_jour == 0:
                        temp_jour = 1  # 1/2 → 2/2
                        avancements += 1
                    else:
                        temp_jour = 0  # 2/2 → 1/2 du mois suivant
                        temp_mois += 1
                        avancements += 1
                    
                    # Reset le compteur pour le prochain cycle
                    temp_jours_irl = 0
                    
                    # Poster un message pour chaque avancement significatif
                    if channel and temp_mois <= len(CALENDRIER_MONTHS):
                        if temp_mois < len(CALENDRIER_MONTHS):
                            mois_nom = CALENDRIER_MONTHS[temp_mois]
                            jour_str = "1/2" if temp_jour == 0 else "2/2"
                            
                            embed = discord.Embed(
                                description=f"{CALENDRIER_EMOJI} {mois_nom} {annee} - {jour_str}\n\n"
                                           f"⚡ **Avancement administratif du calendrier !**\n"
                                           f"Le calendrier a été avancé manuellement pas à pas.",
                                color=CALENDRIER_COLOR
                            )
                            embed.set_image(url=CALENDRIER_IMAGE_URL)
                            
                            try:
                                message = await channel.send(embed=embed)
                                calendrier_data_fresh.setdefault("messages", [])
                                calendrier_data_fresh["messages"].append(str(message.id))
                            except Exception as e:
                                print(f"❌ Erreur lors de l'envoi du message calendrier: {e}")
            
            # Mettre à jour le calendrier avec l'état final
            now = datetime.datetime.now(ZoneInfo("Europe/Paris"))
            calendrier_data_fresh["mois_index"] = temp_mois
            calendrier_data_fresh["jour_index"] = temp_jour
            calendrier_data_fresh["jours_irl_actuel"] = temp_jours_irl
            calendrier_data_fresh["last_update"] = now.isoformat()
            
            # Sauvegarder
            save_calendrier(calendrier_data_fresh)
            
            # Vérifier et terminer automatiquement les développements dans tous les serveurs
            total_completed = 0
            for guild in bot.guilds:
                guild_id = str(guild.id)
                developments_completed = check_and_complete_developments(guild_id)
                total_completed += developments_completed
                if developments_completed > 0:
                    print(f"📅 Avancement manuel: {developments_completed} développements terminés dans {guild.name}")
            
            # Sauvegarder dans PostgreSQL
            save_all_json_to_postgres()
            
            # Embed de succès
            nouveau_mois_nom = CALENDRIER_MONTHS[calendrier_data['mois']]
            nouveau_jour_str = f"{calendrier_data['jour']}/{calendrier_data['alternance']}"
            
            success_embed = discord.Embed(
                title="✅ Calendrier Avancé",
                description=f"**Ancien état :** {mois_actuel_nom} {annee} - {jour_actuel_str}\n"
                           f"**Nouvel état :** {nouveau_mois_nom} {annee} - {nouveau_jour_str}\n\n"
                           f"📱 Messages postés : {avancements}\n"
                           f"🔬 Développements finalisés : {total_completed}\n"
                           f"💾 Sauvegarde PostgreSQL : ✅ Effectuée",
                color=0x00ff00
            )
            
            await button_interaction.followup.send(embed=success_embed, ephemeral=True)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue lors de l'avancement :\n```{str(e)}```",
                color=0xff0000
            )
            await button_interaction.followup.send(embed=error_embed, ephemeral=True)
    
    # Bouton pour avancer d'un seul jour IRL
    async def avancer_un_jour(button_interaction):
        await button_interaction.response.defer()
        
        try:
            # Recharger les données pour être sûr
            calendrier_data_fresh = load_calendrier()
            temp_mois = calendrier_data_fresh['mois_index']
            temp_jour = calendrier_data_fresh['jour_index']
            temp_jours_irl = calendrier_data_fresh.get('jours_irl_actuel', 0)
            annee = calendrier_data_fresh['annee']
            
            # Avancer d'un seul jour IRL
            temp_jours_irl += 1
            
            # Vérifier si c'est le moment d'avancer le jour RP selon l'alternance
            # Mois pairs (0,2,4...) = 2 jours IRL, Mois impairs (1,3,5...) = 1 jour IRL
            if temp_mois % 2 == 0:  # Mois pairs : 2 jours IRL
                alternance_actuelle = 2
            else:  # Mois impairs : 1 jour IRL
                alternance_actuelle = 1
            
            if temp_jours_irl >= alternance_actuelle:
                # Avancer d'un jour RP
                if temp_jour == 0:
                    temp_jour = 1  # 1/2 → 2/2
                else:
                    temp_jour = 0  # 2/2 → 1/2 du mois suivant
                    temp_mois += 1
                
                # Reset le compteur pour le prochain cycle
                temp_jours_irl = 0
            
            # Sauvegarder les nouvelles données
            calendrier_data_fresh['mois_index'] = temp_mois
            calendrier_data_fresh['jour_index'] = temp_jour
            calendrier_data_fresh['jours_irl_actuel'] = temp_jours_irl
            save_calendrier(calendrier_data_fresh)
            
            # Poster un message si on a changé de jour RP
            if temp_jours_irl == 0:  # On vient de changer de jour RP
                channel = bot.get_channel(CALENDRIER_CHANNEL_ID)
                if channel and temp_mois < len(CALENDRIER_MONTHS):
                    mois_nom = CALENDRIER_MONTHS[temp_mois]
                    jour_str = "1/2" if temp_jour == 0 else "2/2"
                    
                    embed = discord.Embed(
                        description=f"{CALENDRIER_EMOJI} {mois_nom} {annee} - {jour_str}\n\n"
                                   f"⏱️ **Avancement d'un jour IRL !**\n"
                                   f"Le calendrier a été avancé manuellement.",
                        color=CALENDRIER_COLOR
                    )
                    embed.set_image(url=CALENDRIER_IMAGE_URL)
                    
                    try:
                        message = await channel.send(embed=embed)
                        calendrier_data_fresh.setdefault("messages", [])
                        calendrier_data_fresh["messages"].append(str(message.id))
                        save_calendrier(calendrier_data_fresh)
                    except Exception as e:
                        print(f"❌ Erreur lors de l'envoi du message calendrier: {e}")
            
            # Finaliser les développements si nécessaire
            total_completed = check_and_complete_developments(button_interaction.guild.id)
            
            # Sauvegarder dans PostgreSQL
            save_all_json_to_postgres()
            
            # Embed de succès
            nouveau_mois_nom = CALENDRIER_MONTHS[calendrier_data_fresh['mois_index']]
            nouveau_jour_str = "1/2" if calendrier_data_fresh['jour_index'] == 0 else "2/2"
            
            # Calculer l'alternance pour l'affichage
            if calendrier_data_fresh['mois_index'] % 2 == 0:
                alternance_affichage = 2
            else:
                alternance_affichage = 1
            
            success_embed = discord.Embed(
                title="✅ Calendrier Avancé (+1 jour IRL)",
                description=f"**Nouvel état :** {nouveau_mois_nom} {annee} - {nouveau_jour_str}\n"
                           f"🕐 Jours IRL : {calendrier_data_fresh['jours_irl_actuel']}/{alternance_affichage}\n\n"
                           f"🔬 Développements finalisés : {total_completed}\n"
                           f"💾 Sauvegarde PostgreSQL : ✅ Effectuée",
                color=0x00ff00
            )
            
            await button_interaction.followup.send(embed=success_embed, ephemeral=True)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue lors de l'avancement :\n```{str(e)}```",
                color=0xff0000
            )
            await button_interaction.followup.send(embed=error_embed, ephemeral=True)
    
    # Bouton Annuler
    async def annuler_avancement(button_interaction):
        await button_interaction.response.defer()
        cancel_embed = discord.Embed(
            title="❌ Avancement Annulé",
            description="L'avancement du calendrier a été annulé.",
            color=0xffa500
        )
        await button_interaction.followup.send(embed=cancel_embed, ephemeral=True)
    
    confirm_button = discord.ui.Button(
        label="Avancer d'un mois",
        style=discord.ButtonStyle.primary,
        emoji="⚡"
    )
    confirm_button.callback = confirmer_avancement
    
    one_day_button = discord.ui.Button(
        label="Avancer d'1 jour IRL",
        style=discord.ButtonStyle.success,
        emoji="⏱️"
    )
    one_day_button.callback = avancer_un_jour
    
    cancel_button = discord.ui.Button(
        label="Annuler",
        style=discord.ButtonStyle.secondary,
        emoji="❌"
    )
    cancel_button.callback = annuler_avancement
    
    view.add_item(confirm_button)
    view.add_item(one_day_button)
    view.add_item(cancel_button)
    
    await interaction.followup.send(embed=embed_confirm, view=view, ephemeral=True)

async def generate_help_banner(
    sections: typing.List[typing.Tuple[str, typing.List[typing.Tuple[str, str]]]]
) -> typing.Optional[io.BytesIO]:
    """Construit une image composite pour l'en-tête de l'aide (séparateur + bannière + texte)."""
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(HELP_HEADER_IMAGE_URL) as resp:
                resp.raise_for_status()
                base_bytes = await resp.read()
        base_image = Image.open(io.BytesIO(base_bytes)).convert("RGBA")
    except Exception as exc:
        print(f"[HELP] Impossible de récupérer l'image de base : {exc}")
        base_image = Image.new("RGBA", (960, 360), (48, 60, 122, 255))

    card_margin = 42
    card_padding = 40
    max_inner_width = 980
    scale_ratio = min(max_inner_width / base_image.width, 1.0)
    new_size = (
        max(1, int(base_image.width * scale_ratio)),
        max(1, int(base_image.height * scale_ratio))
    )
    base_image = base_image.resize(new_size, Image.LANCZOS)

    separator_font_path_candidates = [
        "/System/Library/Fonts/SFNSRounded.ttf",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/Library/Fonts/Arial Unicode.ttf"
    ]

    def load_font(size: int) -> ImageFont.FreeTypeFont:
        for path in separator_font_path_candidates:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    separator_font = load_font(34)
    title_font = load_font(46)
    body_font = load_font(30)

    def measure(text: str, font: ImageFont.ImageFont) -> typing.Tuple[int, int]:
        if hasattr(font, "getbbox"):
            bbox = font.getbbox(text)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        width, height = font.getsize(text)
        return width, height

    wrap_width = 60
    line_spacing = 8
    section_spacing = 24

    info_blocks = [
        ("Besoin d'un coup de main ?", title_font, (245, 240, 255), 28),
        (
            "Les commandes sont triées selon les autorisations nécessaires. Utilise-les via la barre slash.",
            body_font,
            (215, 210, 225),
            16,
        ),
        (
            "Les sections ci-dessous regroupent tout pour l'administration comme pour les membres.",
            body_font,
            (215, 210, 225),
            16,
        ),
        (
            "Astuce : tape '/' puis les premières lettres de la commande pour la retrouver instantanément.",
            body_font,
            (215, 210, 225),
            section_spacing,
        ),
    ]

    section_title_font = load_font(32)
    bullet_font = body_font

    layout_lines: typing.List[typing.Dict[str, typing.Any]] = []

    def append_text_block(text: str, font: ImageFont.ImageFont, color: typing.Tuple[int, int, int], *, spacing_after: int, wrap: bool = True, bullet: bool = False) -> None:
        if wrap and font != title_font:
            wrapper = textwrap.TextWrapper(width=wrap_width, subsequent_indent="    " if bullet else "")
            lines = wrapper.wrap(text)
        else:
            lines = [text]
        for idx, line in enumerate(lines):
            spacing = line_spacing if idx < len(lines) - 1 else spacing_after
            layout_lines.append({
                "text": line,
                "font": font,
                "color": color,
                "spacing": spacing
            })

    for text, font, color, spacing_after in info_blocks:
        append_text_block(text, font, color, spacing_after=spacing_after, wrap=True, bullet=False)

    for title, commands in sections:
        append_text_block(title, section_title_font, (240, 232, 255), spacing_after=12, wrap=False)
        for name, description in commands:
            formatted = f"• {name} — {description}"
            append_text_block(formatted, bullet_font, (210, 205, 222), spacing_after=10, wrap=True, bullet=True)
        if layout_lines:
            layout_lines[-1]["spacing"] += section_spacing

    if layout_lines:
        layout_lines[-1]["spacing"] = 0

    total_text_height = 0
    for entry in layout_lines:
        _, h = measure(entry["text"], entry["font"])
        total_text_height += h + entry["spacing"]

    _, separator_height = measure(HELP_HEADER_SEPARATOR, separator_font)

    card_width = max(base_image.width + card_padding * 2, max_inner_width + card_padding * 2)
    card_height = (
        card_padding * 2
        + separator_height
        + 24  # espace après le séparateur
        + base_image.height
        + 36  # espace après l'image
        + total_text_height
    )

    canvas_width = card_width + card_margin * 2
    canvas_height = card_height + card_margin * 2

    background_color = (15, 10, 24)
    card_color = (30, 21, 43)
    banner = Image.new("RGB", (canvas_width, canvas_height), background_color)
    draw = ImageDraw.Draw(banner)

    card_rect = (
        card_margin,
        card_margin,
        card_margin + card_width,
        card_margin + card_height
    )
    draw.rounded_rectangle(card_rect, radius=38, fill=card_color)

    sep_width, _ = measure(HELP_HEADER_SEPARATOR, separator_font)
    sep_x = card_margin + (card_width - sep_width) // 2
    sep_y = card_margin + 10
    draw.text((sep_x, sep_y), HELP_HEADER_SEPARATOR, font=separator_font, fill=(210, 205, 220))

    image_x = card_margin + (card_width - base_image.width) // 2
    image_y = sep_y + separator_height + 24
    banner.paste(base_image, (image_x, image_y))

    text_y = image_y + base_image.height + 36
    text_x = card_margin + card_padding
    for entry in layout_lines:
        draw.text((text_x, text_y), entry["text"], font=entry["font"], fill=entry["color"])
        _, h = measure(entry["text"], entry["font"])
        text_y += h + entry["spacing"]

    output = io.BytesIO()
    banner.save(output, format="PNG")
    output.seek(0)
    return output

HAS_ADVANCED_HELP_VIEW = all(
    hasattr(discord.ui, attr)
    for attr in (
        "LayoutView",
        "Container",
        "MediaGallery",
        "MediaGalleryItem",
        "Separator",
        "SeparatorSpacing",
        "TextDisplay",
    )
)

if HAS_ADVANCED_HELP_VIEW:
    class Components(discord.ui.LayoutView):
        container1 = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=HELP_VIEW_TOP_URL,
                ),
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="⠀\n> /\n⠀"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=HELP_VIEW_BOTTOM_URL,
                ),
            ),
            accent_colour=discord.Colour(1519957),
        )

        def __init__(self, content: str) -> None:
            super().__init__()
            try:
                text_display = self.container1.children[2]
                if isinstance(text_display, discord.ui.TextDisplay):
                    text_display.content = content
            except Exception:
                pass
else:
    Components = None  # type: ignore[assignment]

@bot.tree.command(name="help", description="Affiche la liste complète des commandes du bot")
async def help_command(interaction: discord.Interaction):
    # Vérifier si l'utilisateur est administrateur
    is_admin = interaction.user.guild_permissions.administrator
    
    # Commandes membres organisées par catégorie
    economie_membres = [
        ("/balance", "Consulte le budget et dette/PIB de ton pays."),
        ("/classement_eco", "Affiche le classement des pays par budget."),
        ("/payer", "Transfère des fonds vers un autre pays ou la banque."),
        ("/creer_emprunt", "Crée un emprunt avec un tiers."),
        ("/liste_emprunt", "Liste tes emprunts en cours."),
        ("/remboursement", "Effectue un paiement sur un emprunt en cours."),
    ]
    
    xp_et_autre_membres = [
        ("/lvl", "Affiche ton niveau et ta progression XP."),
        ("/classement_lvl", "Affiche le classement des membres par niveau."),
        ("/developpements", "Consulte tes développements technologiques."),
        ("/help", "Affiche cette fenêtre d'aide."),
    ]
    
    if is_admin:
        # Commandes administrateur organisées par catégorie
        gestion_pays = [
            ("/creer_pays", "Crée un pays avec ses salons et rôles associés."),
            ("/modifier_pays", "Met à jour le nom, PIB, capitale ou dirigeant d'un pays."),
            ("/supprimer_pays", "Supprime un pays et nettoie ses données."),
            ("/modifier_image_pays", "Met à jour l'image utilisée pour un pays."),
            ("/creer_drapeau", "Génère un emoji drapeau à partir d'une image."),
        ]
        
        economie_admin = [
            ("/add_money", "Ajoute des fonds au budget ou PIB d'un pays."),
            ("/remove_money", "Retire des fonds du budget ou PIB d'un pays."),
            ("/reset_economie", "Réinitialise toutes les données économiques."),
            ("/reset_debt", "Supprime toutes les dettes et emprunts du serveur."),
        ]

        moderation = [
            ("/purge", "Supprime jusqu'à 1000 messages dans un salon."),
            ("/creer_role_mute", "Crée le rôle mute et applique les permissions."),
            ("/mute", "Mute un membre pour une durée définie."),
            ("/unmute", "Retire le mute d'un membre."),
            ("/ban", "Bannit un membre du serveur après confirmation."),
            ("/setpermission_mute", "Réapplique les permissions du rôle mute partout."),
            ("/warn", "Donne un avertissement à un utilisateur."),
            ("/user_warn", "Affiche les avertissements d'un utilisateur."),
            ("/remove_warn", "Retire un avertissement spécifique."),
        ]
        
        configuration_logs = [
            ("/setlogeconomy", "Définit le salon de logs pour l'économie."),
            ("/setlogpays", "Configure le salon de logs des actions liées aux pays."),
            ("/setlogmute", "Définit le salon de logs pour les sanctions."),
            ("/set_lvl", "Active ou désactive le système de niveaux."),
            ("/set_channel_lvl", "Choisit le salon de logs des passages de niveau."),
            ("/categorie", "Applique les permissions de catégorie aux salons."),
            ("/creer_webhook", "Crée un webhook dans le salon courant."),
        ]
        
        outils_rp = [
            ("/guide", "Guide de présentation du serveur."),
            ("/calendrier", "Lance les annonces du calendrier RP."),
            ("/reset-calendrier", "Réinitialise le calendrier RP en cours."),
            ("/creer_stats_voice_channels", "Génère les salons vocaux de statistiques."),
            ("/bilan_techno", "Génère un bilan technologique militaire avec coûts."),
        ]

        sections_data = [
            ("🏛️ Gestion des Pays", gestion_pays),
            ("💰 Économie & Finance", economie_admin),
            ("🛡️ Modération", moderation),
            ("⚙️ Configuration & Logs", configuration_logs),
            ("🎭 Outils RP", outils_rp),
            ("👥 Économie Membres", economie_membres),
            ("⭐ XP & Divers", xp_et_autre_membres),
        ]
        
        embed = discord.Embed(
            title="Centre d'aide - Mode Administrateur",
            description=(
                "Commandes organisées par catégorie. "
                "Utilise la barre slash pour accéder à toutes les fonctionnalités."
            ),
            color=EMBED_COLOR,
        )
    else:
        # Seules les commandes membres pour les non-admins
        sections_data = [
            ("💰 Économie & Emprunts", economie_membres),
            ("⭐ XP & Divers", xp_et_autre_membres),
        ]
        
        embed = discord.Embed(
            title="Centre d'aide",
            description=(
                "Voici toutes les commandes organisées par catégorie. "
                "Utilise la barre slash pour les exécuter."
            ),
            color=EMBED_COLOR,
        )

    embed.set_thumbnail(url=HELP_THUMBNAIL_URL)
    embed.set_footer(text="Astuce : tape '/' puis le nom de la commande pour voir ses options.")

    for title, commands in sections_data:
        field_lines = [f"`{name}` — {description}" for name, description in commands]
        embed.add_field(name=title, value="\n".join(field_lines), inline=False)

    summary_lines: typing.List[str] = []
    for title, commands in sections_data:
        summary_lines.append(f"**{title}**")
        summary_lines.extend(f"`{name}` — {description}" for name, description in commands)
        summary_lines.append("")
    while summary_lines and not summary_lines[-1]:
        summary_lines.pop()

    condensed_summary = "\n".join(summary_lines)
    if len(condensed_summary) > 1800:
        condensed_summary = condensed_summary[:1797] + "…"
    block_content = f"⠀\n> " + "\n> ".join(condensed_summary.splitlines()) + "\n⠀"

    response_kwargs: dict[str, typing.Any] = {"embed": embed, "ephemeral": True}
    if Components is not None and HAS_ADVANCED_HELP_VIEW:
        response_kwargs["view"] = Components(block_content)  # type: ignore[call-arg]

    await interaction.response.send_message(**response_kwargs)

@loop(minutes=1)
async def calendrier_update_task():
    calendrier_data = load_calendrier()
    if not calendrier_data:
        calendrier_update_task.stop()
        return
    
    # Vérifier si on doit avancer (minuit heure Paris)
    now = datetime.datetime.now(ZoneInfo("Europe/Paris"))
    
    # Vérifier si c'est minuit (ou proche de minuit)
    if now.hour != 0:
        return
    
    last_update = calendrier_data.get("last_update")
    if last_update:
        last_update_dt = datetime.datetime.fromisoformat(last_update)
        # Convertir vers le fuseau horaire de Paris si nécessaire
        if last_update_dt.tzinfo is None:
            last_update_dt = last_update_dt.replace(tzinfo=ZoneInfo("Europe/Paris"))
        else:
            last_update_dt = last_update_dt.astimezone(ZoneInfo("Europe/Paris"))
        if last_update_dt.date() == now.date():
            return # déjà mis à jour aujourd'hui
    
    # Ignorer le premier passage à minuit
    if calendrier_data.get("skip_first_midnight", False):
        calendrier_data["skip_first_midnight"] = False
        calendrier_data["last_update"] = now.isoformat()
        save_calendrier(calendrier_data)
        save_all_json_to_postgres()  # Sauvegarder dans PostgreSQL
        return
    
    # Logique d'alternance : 2 jours IRL puis 1 jour IRL
    # Pour 18 jours total : 12 mois * 1.5 jour moyen = 18 jours
    # Pattern : 2j, 1j, 2j, 1j, 2j, 1j... (soit 6 cycles = 18 jours)
    jours_irl_actuel = calendrier_data.get("jours_irl_actuel", 0)
    
    # Déterminer combien de jours IRL pour ce mois (alternance 2j/1j)
    if calendrier_data["mois_index"] % 2 == 0:  # Mois pairs : 2 jours IRL
        jours_requis = 2
    else:  # Mois impairs : 1 jour IRL
        jours_requis = 1
    
    # Avancer le calendrier
    mois_index = calendrier_data["mois_index"]
    jour_index = calendrier_data["jour_index"]
    
    if mois_index >= len(CALENDRIER_MONTHS):
        calendrier_update_task.stop()
        return
    
    mois = CALENDRIER_MONTHS[mois_index]
    jour_str = "1/2" if jour_index == 0 else "2/2"
    
    # Poster le message
    channel = bot.get_channel(CALENDRIER_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            description=f"{CALENDRIER_EMOJI} {mois} {calendrier_data['annee']} - {jour_str}\n\n"
                       f"Le calendrier RP continue !\n"
                       f"Nous sommes maintenant en {mois} {calendrier_data['annee']}.",
            color=CALENDRIER_COLOR
        )
        embed.set_image(url=CALENDRIER_IMAGE_URL)
        message = await channel.send(embed=embed)
        calendrier_data.setdefault("messages", [])
        calendrier_data["messages"].append(str(message.id))
    
    # Incrémenter le compteur de jours IRL
    jours_irl_actuel += 1
    calendrier_data["jours_irl_actuel"] = jours_irl_actuel
    
    # Avancer le jour uniquement si on a atteint le nombre de jours requis
    if jours_irl_actuel >= jours_requis:
        if jour_index == 0:
            calendrier_data["jour_index"] = 1
        else:
            calendrier_data["jour_index"] = 0
            calendrier_data["mois_index"] += 1
        
        # Reset le compteur pour le prochain mois
        calendrier_data["jours_irl_actuel"] = 0
    
    calendrier_data["last_update"] = now.isoformat()
    save_calendrier(calendrier_data)
    save_all_json_to_postgres()  # Sauvegarder dans PostgreSQL
    
    # Vérifier et terminer automatiquement les développements dans tous les serveurs
    for guild in bot.guilds:
        guild_id = str(guild.id)
        developments_completed = check_and_complete_developments(guild_id)
        if developments_completed > 0:
            print(f"[DEBUG] Calendrier automatique: {developments_completed} développements terminés dans {guild.name}")
    
    # Stop si Décembre 2/2 passé
    if calendrier_data["mois_index"] >= len(CALENDRIER_MONTHS):
        calendrier_update_task.stop()

@bot.tree.command(name="debug_heure", description="Debug : affiche les informations d'heure pour le calendrier")
@app_commands.checks.has_permissions(administrator=True)
async def debug_heure(interaction: discord.Interaction):
    """Debug des informations d'heure pour le calendrier."""
    from datetime import datetime
    
    # Heure actuelle Paris
    now_paris = datetime.now(ZoneInfo("Europe/Paris"))
    
    # Heure UTC
    now_utc = datetime.now(ZoneInfo("UTC"))
    
    # Informations sur le fuseau horaire
    tz_name = now_paris.tzname()  # CET ou CEST
    offset = now_paris.utcoffset().total_seconds() / 3600  # Décalage en heures
    
    # Calendrier
    calendrier_data = load_calendrier()
    last_update = calendrier_data.get("last_update") if calendrier_data else None
    
    embed = discord.Embed(
        title="🕐 Debug Heure - Calendrier",
        color=0x3498db
    )
    
    embed.add_field(
        name="🌍 Heure Paris", 
        value=f"`{now_paris.strftime('%Y-%m-%d %H:%M:%S %Z')}`\nFuseau: **{tz_name}** (UTC{offset:+.0f})",
        inline=False
    )
    
    embed.add_field(
        name="🌐 Heure UTC", 
        value=f"`{now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}`",
        inline=False
    )
    
    if calendrier_data:
        embed.add_field(
            name="📅 Calendrier RP", 
            value=f"Mois: **{calendrier_data['mois_index']}** | Jour: **{calendrier_data['jour_index']}**\nDernière MAJ: `{last_update}`",
            inline=False
        )
    
    embed.add_field(
        name="⏰ Condition Minuit", 
        value=f"Heure actuelle: **{now_paris.hour}h**\nCondition minuit: **{'✅ OUI' if now_paris.hour == 0 else '❌ NON'}**",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# === COMMANDES D'AVERTISSEMENT ===

@bot.tree.command(name="warn", description="Donne un avertissement à un utilisateur")
@app_commands.checks.has_permissions(administrator=True)
async def warn(interaction: discord.Interaction, utilisateur: discord.Member, raison: str):
    """Donne un avertissement à un utilisateur."""
    global warnings
    
    await interaction.response.defer(ephemeral=True)
    
    user_id = str(utilisateur.id)
    guild_id = str(interaction.guild.id)
    
    # Initialiser les données du serveur si nécessaire
    if guild_id not in warnings:
        warnings[guild_id] = {}
    
    # Initialiser les données de l'utilisateur si nécessaire
    if user_id not in warnings[guild_id]:
        warnings[guild_id][user_id] = {"warns": [], "next_id": 1}
    
    # Créer l'avertissement
    warn_id = warnings[guild_id][user_id]["next_id"]
    warn_data = {
        "id": warn_id,
        "raison": raison,
        "moderateur": interaction.user.id,
        "date": datetime.datetime.now().isoformat()
    }
    
    # Ajouter l'avertissement
    warnings[guild_id][user_id]["warns"].append(warn_data)
    warnings[guild_id][user_id]["next_id"] += 1
    
    # Sauvegarder
    save_warnings(warnings)
    
    # Créer l'embed de confirmation
    embed = discord.Embed(
        title="⚠️ Avertissement donné",
        description=f"**Utilisateur :** {utilisateur.mention}\n"
                   f"**Avertissement :** #{warn_id}\n"
                   f"**Raison :** {raison}\n"
                   f"**Modérateur :** {interaction.user.mention}",
        color=SANCTION_COLOR,
        timestamp=datetime.datetime.now()
    )
    embed.set_image(url="https://zupimages.net/up/21/03/vl8j.png")
    
    await interaction.followup.send(embed=embed)
    
    # Log dans le salon des sanctions
    log_embed = discord.Embed(
        title="⚠️ Avertissement",
        description=f"**Utilisateur :** {utilisateur.mention} ({utilisateur.id})\n"
                   f"**Avertissement :** #{warn_id}\n"
                   f"**Raison :** {raison}\n"
                   f"**Modérateur :** {interaction.user.mention}",
        color=SANCTION_COLOR,
        timestamp=datetime.datetime.now()
    )
    log_embed.set_image(url="https://zupimages.net/up/21/03/vl8j.png")
    
    await send_mute_log(interaction.guild, log_embed)

@bot.tree.command(name="user_warn", description="Affiche les avertissements d'un utilisateur")
@app_commands.checks.has_permissions(administrator=True)
async def user_warn(interaction: discord.Interaction, utilisateur: discord.Member):
    """Affiche les avertissements d'un utilisateur."""
    global warnings
    
    await interaction.response.defer(ephemeral=True)
    
    user_id = str(utilisateur.id)
    guild_id = str(interaction.guild.id)
    
    # Vérifier s'il y a des avertissements
    if guild_id not in warnings or user_id not in warnings[guild_id] or not warnings[guild_id][user_id]["warns"]:
        embed = discord.Embed(
            title="📋 Avertissements",
            description=f"**Utilisateur :** {utilisateur.mention}\n**Aucun avertissement trouvé.**",
            color=SANCTION_COLOR
        )
        embed.set_image(url="https://zupimages.net/up/21/03/vl8j.png")
        await interaction.followup.send(embed=embed)
        return
    
    # Créer la liste des avertissements
    warns_list = warnings[guild_id][user_id]["warns"]
    warn_count = len(warns_list)
    
    # Créer l'embed
    embed = discord.Embed(
        title="📋 Avertissements",
        description=f"**Utilisateur :** {utilisateur.mention}\n"
                   f"**Nombre total :** {warn_count} avertissement{'s' if warn_count > 1 else ''}",
        color=SANCTION_COLOR,
        timestamp=datetime.datetime.now()
    )
    embed.set_image(url="https://zupimages.net/up/21/03/vl8j.png")
    
    # Ajouter chaque avertissement
    for warn_data in warns_list:
        moderateur = interaction.guild.get_member(warn_data["moderateur"])
        mod_name = moderateur.display_name if moderateur else "Modérateur inconnu"
        
        date_obj = datetime.datetime.fromisoformat(warn_data["date"])
        date_str = date_obj.strftime("%d/%m/%Y à %H:%M")
        
        embed.add_field(
            name=f"⚠️ Avertissement #{warn_data['id']}",
            value=f"**Raison :** {warn_data['raison']}\n"
                  f"**Modérateur :** {mod_name}\n"
                  f"**Date :** {date_str}",
            inline=False
        )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="remove_warn", description="Retire un avertissement spécifique")
@app_commands.checks.has_permissions(administrator=True)
async def remove_warn(interaction: discord.Interaction, utilisateur: discord.Member, numero_avertissement: int):
    """Retire un avertissement spécifique."""
    global warnings
    
    await interaction.response.defer(ephemeral=True)
    
    user_id = str(utilisateur.id)
    guild_id = str(interaction.guild.id)
    
    # Vérifier s'il y a des avertissements
    if guild_id not in warnings or user_id not in warnings[guild_id] or not warnings[guild_id][user_id]["warns"]:
        embed = discord.Embed(
            title="❌ Erreur",
            description=f"**Utilisateur :** {utilisateur.mention}\n**Aucun avertissement trouvé.**",
            color=SANCTION_COLOR
        )
        embed.set_image(url="https://zupimages.net/up/21/03/vl8j.png")
        await interaction.followup.send(embed=embed)
        return
    
    # Chercher l'avertissement à supprimer
    warns_list = warnings[guild_id][user_id]["warns"]
    warn_to_remove = None
    warn_index = None
    
    for i, warn_data in enumerate(warns_list):
        if warn_data["id"] == numero_avertissement:
            warn_to_remove = warn_data
            warn_index = i
            break
    
    if warn_to_remove is None:
        embed = discord.Embed(
            title="❌ Erreur",
            description=f"**Avertissement #{numero_avertissement} introuvable** pour {utilisateur.mention}.",
            color=SANCTION_COLOR
        )
        embed.set_image(url="https://zupimages.net/up/21/03/vl8j.png")
        await interaction.followup.send(embed=embed)
        return
    
    # Supprimer l'avertissement
    warnings[guild_id][user_id]["warns"].pop(warn_index)
    save_warnings(warnings)
    
    # Créer l'embed de confirmation
    embed = discord.Embed(
        title="✅ Avertissement supprimé",
        description=f"**Utilisateur :** {utilisateur.mention}\n"
                   f"**Avertissement :** #{numero_avertissement}\n"
                   f"**Raison originale :** {warn_to_remove['raison']}\n"
                   f"**Supprimé par :** {interaction.user.mention}",
        color=SANCTION_COLOR,
        timestamp=datetime.datetime.now()
    )
    embed.set_image(url="https://zupimages.net/up/21/03/vl8j.png")
    
    await interaction.followup.send(embed=embed)
    
    # Log dans le salon des sanctions
    log_embed = discord.Embed(
        title="🗑️ Avertissement supprimé",
        description=f"**Utilisateur :** {utilisateur.mention} ({utilisateur.id})\n"
                   f"**Avertissement :** #{numero_avertissement}\n"
                   f"**Raison originale :** {warn_to_remove['raison']}\n"
                   f"**Supprimé par :** {interaction.user.mention}",
        color=SANCTION_COLOR,
        timestamp=datetime.datetime.now()
    )
    log_embed.set_image(url="https://zupimages.net/up/21/03/vl8j.png")
    
    await send_mute_log(interaction.guild, log_embed)

@bot.tree.command(name="bonus_xp", description="Active un bonus XP temporaire pendant 2 heures")
@app_commands.checks.has_permissions(administrator=True)
async def bonus_xp(interaction: discord.Interaction):
    """Active un bonus XP de 3 XP par message + 2 XP tous les 10 caractères pendant 2 heures."""
    global bonus_xp_active
    
    await interaction.response.defer(ephemeral=True)
    
    guild_id = str(interaction.guild.id)
    import time
    
    # Vérifier si un bonus est déjà actif
    if guild_id in bonus_xp_active and time.time() < bonus_xp_active[guild_id]:
        remaining_time = bonus_xp_active[guild_id] - time.time()
        remaining_minutes = int(remaining_time // 60)
        remaining_seconds = int(remaining_time % 60)
        
        embed = discord.Embed(
            title="⚠️ Bonus XP déjà actif",
            description=f"Un bonus XP est déjà en cours !\n"
                       f"**Temps restant :** {remaining_minutes}m {remaining_seconds}s",
            color=EMBED_COLOR,
            timestamp=datetime.datetime.now()
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Activer le bonus pour 2 heures (7200 secondes = 2 * 60 * 60)
    end_time = time.time() + (2 * 60 * 60)  # 2 heures explicitement
    bonus_xp_active[guild_id] = end_time
    
    # Calculer l'heure de fin
    end_datetime = datetime.datetime.fromtimestamp(end_time)
    end_time_str = end_datetime.strftime("%H:%M:%S")
    
    # Créer l'embed de confirmation
    embed = discord.Embed(
        title="🚀 Bonus XP activé !",
        description=f"**Bonus actif pendant 2 heures !**\n\n"
                   f"📈 **Bonus :**\n"
                   f"> • +3 XP par message\n"
                   f"> • +2 XP tous les 10 caractères\n"
                   f"> • Cumulable avec les autres bonus\n\n"
                   f"⏰ **Fin prévue :** {end_time_str}\n"
                   f"👤 **Activé par :** {interaction.user.mention}",
        color=EMBED_COLOR,
        timestamp=datetime.datetime.now()
    )
    
    await interaction.followup.send(embed=embed)
    
    # Log dans le salon général
    log_embed = discord.Embed(
        title="🚀 Bonus XP activé",
        description=f"**Durée :** 2 heures\n"
                   f"**Bonus :** +3 XP/message + 2 XP/10 caractères\n"
                   f"**Fin prévue :** {end_time_str}\n"
                   f"**Activé par :** {interaction.user.mention}",
        color=EMBED_COLOR,
        timestamp=datetime.datetime.now()
    )
    
    await send_log(interaction.guild, embed=log_embed)

@bot.tree.command(name="remove_bonus_xp", description="Retire le bonus XP actif avant la fin")
@app_commands.checks.has_permissions(administrator=True)
async def remove_bonus_xp(interaction: discord.Interaction):
    """Retire le bonus XP actif avant la fin des 2 heures."""
    global bonus_xp_active
    
    await interaction.response.defer(ephemeral=True)
    
    guild_id = str(interaction.guild.id)
    import time
    
    # Vérifier s'il y a un bonus actif
    if guild_id not in bonus_xp_active:
        embed = discord.Embed(
            title="⚠️ Aucun bonus XP actif",
            description="Il n'y a actuellement aucun bonus XP actif sur ce serveur.",
            color=EMBED_COLOR,
            timestamp=datetime.datetime.now()
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Vérifier si le bonus est encore valide
    if time.time() >= bonus_xp_active[guild_id]:
        # Bonus déjà expiré
        del bonus_xp_active[guild_id]
        embed = discord.Embed(
            title="⚠️ Bonus XP déjà expiré",
            description="Le bonus XP avait déjà expiré naturellement.",
            color=EMBED_COLOR,
            timestamp=datetime.datetime.now()
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Calculer le temps restant avant suppression
    remaining_time = bonus_xp_active[guild_id] - time.time()
    remaining_minutes = int(remaining_time // 60)
    remaining_seconds = int(remaining_time % 60)
    
    # Supprimer le bonus
    del bonus_xp_active[guild_id]
    
    # Créer l'embed de confirmation
    embed = discord.Embed(
        title="🛑 Bonus XP retiré",
        description=f"**Le bonus XP a été retiré avec succès !**\n\n"
                   f"⏰ **Temps restant qui a été annulé :** {remaining_minutes}m {remaining_seconds}s\n"
                   f"👤 **Retiré par :** {interaction.user.mention}\n\n"
                   f"💡 *Le système XP reprend son fonctionnement normal.*",
        color=EMBED_COLOR,
        timestamp=datetime.datetime.now()
    )
    
    await interaction.followup.send(embed=embed)
    
    # Log dans le salon général
    log_embed = discord.Embed(
        title="🛑 Bonus XP retiré",
        description=f"**Retiré par :** {interaction.user.mention}\n"
                   f"**Temps restant annulé :** {remaining_minutes}m {remaining_seconds}s\n"
                   f"**Raison :** Arrêt manuel par un administrateur",
        color=EMBED_COLOR,
        timestamp=datetime.datetime.now()
    )
    
    await send_log(interaction.guild, embed=log_embed)

@bot.tree.command(name="categorie", description="Applique les permissions de catégorie aux salons (en plus des permissions existantes)")
@app_commands.checks.has_permissions(administrator=True)
async def categorie(interaction: discord.Interaction, categorie: discord.CategoryChannel, salon: discord.TextChannel = None):
    """Applique les permissions de catégorie aux salons en conservant les permissions existantes."""
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Déterminer les salons à traiter
        if salon:
            # Un salon spécifique
            channels_to_process = [salon]
            scope_text = f"salon {salon.mention}"
        else:
            # Tous les salons de la catégorie
            channels_to_process = [channel for channel in categorie.channels if isinstance(channel, discord.TextChannel)]
            scope_text = f"catégorie **{categorie.name}** ({len(channels_to_process)} salons)"
        
        if not channels_to_process:
            embed = discord.Embed(
                title="⚠️ Aucun salon trouvé",
                description="Aucun salon textuel trouvé dans cette catégorie.",
                color=EMBED_COLOR
            )
            await interaction.followup.send(embed=embed)
            return
        
        print(f"[DEBUG] Application des permissions de catégorie {categorie.name} sur {len(channels_to_process)} salon(s)")
        
        # Traitement des salons
        processed_count = 0
        error_count = 0
        
        for channel in channels_to_process:
            try:
                print(f"[DEBUG] Traitement du salon {channel.name}")
                
                # Récupérer les permissions actuelles du salon
                current_overwrites = dict(channel.overwrites)
                print(f"[DEBUG] Permissions actuelles: {len(current_overwrites)} règles")
                
                # Récupérer les permissions de la catégorie
                category_overwrites = dict(categorie.overwrites)
                print(f"[DEBUG] Permissions de catégorie: {len(category_overwrites)} règles")
                
                # Fusionner les permissions : catégorie en base + salon par-dessus
                merged_overwrites = {}
                
                # 1. Ajouter toutes les permissions de catégorie
                for target, overwrite in category_overwrites.items():
                    merged_overwrites[target] = overwrite
                    print(f"[DEBUG] Ajout permission catégorie pour {target}")
                
                # 2. Appliquer les permissions spécifiques du salon par-dessus
                for target, overwrite in current_overwrites.items():
                    if target in merged_overwrites:
                        # Fusionner les permissions (permissions du salon prioritaires)
                        category_perms = merged_overwrites[target]
                        
                        # Créer un nouvel overwrite qui combine les deux
                        combined_perms = {}
                        
                        # Commencer avec les permissions de catégorie
                        for perm_name, perm_value in category_perms:
                            combined_perms[perm_name] = perm_value
                        
                        # Appliquer les permissions du salon par-dessus (priorité)
                        for perm_name, perm_value in overwrite:
                            if perm_value is not None:  # Seulement si explicitement défini
                                combined_perms[perm_name] = perm_value
                        
                        # Créer le nouvel overwrite
                        merged_overwrites[target] = discord.PermissionOverwrite(**combined_perms)
                        print(f"[DEBUG] Fusion des permissions pour {target}")
                    else:
                        # Nouvelle permission spécifique au salon
                        merged_overwrites[target] = overwrite
                        print(f"[DEBUG] Ajout permission salon pour {target}")
                
                # Appliquer les nouvelles permissions
                await channel.edit(overwrites=merged_overwrites)
                processed_count += 1
                print(f"[DEBUG] Permissions appliquées avec succès sur {channel.name}")
                
                # Petit délai pour éviter les rate limits
                await asyncio.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                print(f"[ERROR] Erreur lors du traitement de {channel.name}: {e}")
        
        # Créer l'embed de confirmation
        if error_count == 0:
            embed = discord.Embed(
                title="✅ Permissions de catégorie appliquées",
                description=f"**Cible :** {scope_text}\n"
                           f"**Salons traités :** {processed_count}\n"
                           f"**Catégorie source :** {categorie.mention}\n"
                           f"**Permissions :** Catégorie + permissions existantes conservées",
                color=EMBED_COLOR,
                timestamp=datetime.datetime.now()
            )
        else:
            embed = discord.Embed(
                title="⚠️ Permissions partiellement appliquées",
                description=f"**Cible :** {scope_text}\n"
                           f"**Salons traités :** {processed_count}\n"
                           f"**Erreurs :** {error_count}\n"
                           f"**Catégorie source :** {categorie.mention}",
                color=EMBED_COLOR,
                timestamp=datetime.datetime.now()
            )
        
        await interaction.followup.send(embed=embed)
        
        # Log dans le salon des logs
        log_embed = discord.Embed(
            title="🔧 Permissions de catégorie appliquées",
            description=f"**Administrateur :** {interaction.user.mention}\n"
                       f"**Cible :** {scope_text}\n"
                       f"**Catégorie source :** {categorie.mention}\n"
                       f"**Salons traités :** {processed_count}/{len(channels_to_process)}",
            color=EMBED_COLOR,
            timestamp=datetime.datetime.now()
        )
        
        await send_log(interaction.guild, embed=log_embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erreur",
            description=f"Une erreur est survenue lors de l'application des permissions :\n```{str(e)}```",
            color=EMBED_COLOR
        )
        await interaction.followup.send(embed=embed)
        print(f"[ERROR] Erreur dans la commande categorie: {e}")

@bot.tree.command(name="creer_webhook", description="Crée un webhook dans le salon courant")
@app_commands.describe(
    nom="Nom du webhook",
    avatar="Image à utiliser comme avatar du webhook"
)
async def creer_webhook(interaction: discord.Interaction, nom: str, avatar: discord.Attachment = None):
    """Crée un webhook dans le salon courant avec vérification des permissions."""
    
    # Vérifier les permissions de l'utilisateur
    if not interaction.channel.permissions_for(interaction.user).manage_webhooks:
        embed = discord.Embed(
            title="❌ Permissions insuffisantes",
            description="Vous devez avoir la permission **Gérer les webhooks** dans ce salon pour utiliser cette commande.",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Vérifier que le bot a les permissions nécessaires
    if not interaction.channel.permissions_for(interaction.guild.me).manage_webhooks:
        embed = discord.Embed(
            title="❌ Permissions du bot insuffisantes",
            description="Le bot n'a pas la permission **Gérer les webhooks** dans ce salon.",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Traiter l'avatar si fourni
        avatar_bytes = None
        if avatar:
            # Vérifier que c'est une image
            if not avatar.content_type.startswith('image/'):
                embed = discord.Embed(
                    title="❌ Fichier invalide",
                    description="Le fichier fourni doit être une image (PNG, JPG, GIF, etc.).",
                    color=0xff0000,
                    timestamp=datetime.datetime.now()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Vérifier la taille (max 8MB)
            if avatar.size > 8 * 1024 * 1024:
                embed = discord.Embed(
                    title="❌ Fichier trop volumineux",
                    description="L'image ne doit pas dépasser 8 MB.",
                    color=0xff0000,
                    timestamp=datetime.datetime.now()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Lire les données de l'image
            avatar_bytes = await avatar.read()
        
        # Créer le webhook
        webhook = await interaction.channel.create_webhook(
            name=nom,
            avatar=avatar_bytes,
            reason=f"Webhook créé par {interaction.user} via commande /creer_webhook"
        )
        
        # Créer l'embed de succès avec l'URL
        embed = discord.Embed(
            title="✅ Webhook créé avec succès",
            description=f"**Nom :** {webhook.name}\n"
                       f"**Salon :** {interaction.channel.mention}\n"
                       f"**ID :** `{webhook.id}`",
            color=EMBED_COLOR,
            timestamp=datetime.datetime.now()
        )
        
        # Ajouter l'avatar si présent
        if webhook.avatar:
            embed.set_thumbnail(url=webhook.display_avatar.url)
        
        # Ajouter l'URL du webhook dans un champ séparé pour faciliter la copie
        embed.add_field(
            name="🔗 URL du webhook",
            value=f"```{webhook.url}```",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Utilisation",
            value="L'URL a également été envoyée en message privé pour faciliter la copie sur mobile.",
            inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Envoyer l'URL en MP sans embed pour faciliter la copie sur mobile
        try:
            dm_message = f"🔗 **Webhook créé dans #{interaction.channel.name}**\n\nURL du webhook :\n{webhook.url}"
            await interaction.user.send(dm_message)
        except discord.Forbidden:
            # Si l'utilisateur a les MPs fermés, on l'informe dans la réponse
            error_embed = discord.Embed(
                title="⚠️ Message privé non envoyé",
                description="Impossible d'envoyer l'URL en message privé (MPs fermés). Vous pouvez copier l'URL depuis le message ci-dessus.",
                color=0xffa500,
                timestamp=datetime.datetime.now()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
        
        # Log dans le salon des logs
        log_embed = discord.Embed(
            title="🔗 Webhook créé",
            description=f"**Créateur :** {interaction.user.mention}\n"
                       f"**Salon :** {interaction.channel.mention}\n"
                       f"**Nom du webhook :** {webhook.name}\n"
                       f"**ID :** `{webhook.id}`",
            color=EMBED_COLOR,
            timestamp=datetime.datetime.now()
        )
        
        if webhook.avatar:
            log_embed.set_thumbnail(url=webhook.display_avatar.url)
        
        await send_log(interaction.guild, embed=log_embed)
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ Permissions insuffisantes",
            description="Le bot n'a pas les permissions nécessaires pour créer un webhook dans ce salon.",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except discord.HTTPException as e:
        embed = discord.Embed(
            title="❌ Erreur lors de la création",
            description=f"Une erreur est survenue lors de la création du webhook :\n```{str(e)}```",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erreur inattendue",
            description=f"Une erreur inattendue est survenue :\n```{str(e)}```",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        print(f"[ERROR] Erreur dans la commande creer_webhook: {e}")

# === SYSTÈME DE DÉBAT ===

# Configuration du système de débat
DEBAT_ROLE_ID = 1426763928943333436
DEBAT_CHANNEL_ID = 1412796642477871268

@bot.tree.command(name="debat", description="Attribue le rôle débat à un ou plusieurs membres")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    membre1="Premier membre à qui attribuer le rôle débat",
    membre2="Deuxième membre (optionnel)",
    membre3="Troisième membre (optionnel)",
    membre4="Quatrième membre (optionnel)",
    membre5="Cinquième membre (optionnel)"
)
async def debat(
    interaction: discord.Interaction, 
    membre1: discord.Member,
    membre2: discord.Member = None,
    membre3: discord.Member = None,
    membre4: discord.Member = None,
    membre5: discord.Member = None
):
    """Attribue le rôle débat à un ou plusieurs membres avec message d'information."""
    
    try:
        # Récupérer le rôle débat
        debat_role = interaction.guild.get_role(DEBAT_ROLE_ID)
        if not debat_role:
            await interaction.response.send_message("❌ Le rôle débat n'a pas été trouvé sur ce serveur.", ephemeral=True)
            return
        
        # Collecter tous les membres non-None
        membres = [membre for membre in [membre1, membre2, membre3, membre4, membre5] if membre is not None]
        
        # Supprimer les doublons en conservant l'ordre
        membres_uniques = []
        for membre in membres:
            if membre not in membres_uniques:
                membres_uniques.append(membre)
        
        membres_traités = []
        membres_avec_role = []
        membres_erreur = []
        
        # Traiter chaque membre
        for membre in membres_uniques:
            try:
                # Vérifier si le membre a déjà le rôle
                if debat_role in membre.roles:
                    membres_avec_role.append(membre)
                    continue
                
                # Attribuer le rôle
                await membre.add_roles(debat_role, reason=f"Rôle débat attribué par {interaction.user}")
                
                membres_traités.append(membre)
                print(f"[DEBAT] Rôle attribué à {membre.display_name} par {interaction.user.display_name}")
                
            except Exception as e:
                print(f"[ERROR] Erreur pour {membre.display_name}: {e}")
                membres_erreur.append(membre)
        
        # Répondre à l'administrateur avec la confirmation
        confirmation_parts = []
        
        if membres_traités:
            confirmation_parts.append("**✅ Rôles attribués avec succès :**")
            for membre in membres_traités:
                confirmation_parts.append(f"• {membre.mention}")
        
        if membres_avec_role:
            confirmation_parts.append("\n**⚠️ Membres ayant déjà le rôle :**")
            for membre in membres_avec_role:
                confirmation_parts.append(f"• {membre.mention}")
        
        if membres_erreur:
            confirmation_parts.append("\n**❌ Erreurs :**")
            for membre in membres_erreur:
                confirmation_parts.append(f"• {membre.mention}")
        
        if not confirmation_parts:
            confirmation_parts.append("❌ Aucune action effectuée.")
        
        await interaction.response.send_message(
            "\n".join(confirmation_parts),
            ephemeral=True
        )
        
        # Envoyer un message temporaire à chaque membre traité
        # Le message apparaît brièvement dans le salon puis se supprime automatiquement
        import asyncio
        for membre in membres_traités:
            try:
                message_content = f"{membre.mention}\n> <:PX_Info:1423870991712653442> | Merci d'aller dans le salon <#{DEBAT_CHANNEL_ID}> afin de ne pas polluer la discussion."
                
                # Envoyer le message temporaire
                temp_message = await interaction.channel.send(content=message_content)
                
                # Programmer la suppression automatique après 8 secondes
                async def delete_after_delay():
                    await asyncio.sleep(8)
                    try:
                        await temp_message.delete()
                    except:
                        pass
                
                asyncio.create_task(delete_after_delay())
                
            except Exception as e:
                print(f"[ERROR] Impossible d'envoyer le message à {membre.display_name}: {e}")
        
    except discord.Forbidden:
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ Je n'ai pas les permissions nécessaires pour attribuer ce rôle.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Je n'ai pas les permissions nécessaires pour attribuer ce rôle.", ephemeral=True)
    except discord.Forbidden:
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ Je n'ai pas les permissions nécessaires pour attribuer ce rôle.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Je n'ai pas les permissions nécessaires pour attribuer ce rôle.", ephemeral=True)
    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)
        print(f"[ERROR] Erreur dans la commande debat: {e}")
        if not interaction.response.is_done():
            await interaction.response.send_message(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)
        print(f"[ERROR] Erreur dans la commande debat: {e}")

# === SYSTÈME D'ACTION TECHNOLOGIQUE ===

@bot.tree.command(name="action_tech", description="Calcule le coefficient technologique d'une action")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    qualite="Qualité d'écriture - Clarté, structure, richesse du contenu (1-5)",
    applicabilite="Applicabilité - Possibilité à mettre en œuvre (1-5)",
    impact="Impact - Importance stratégique et bénéfices apportés (1-5)"
)
async def action_tech(
    interaction: discord.Interaction,
    qualite: int,
    applicabilite: int,
    impact: int
):
    """Calcule et attribue les points technologiques selon les critères de qualité."""
    
    # Vérification des valeurs
    if not (1 <= qualite <= 5):
        await interaction.response.send_message("❌ La qualité doit être entre 1 et 5.", ephemeral=True)
        return
    
    if not (1 <= applicabilite <= 5):
        await interaction.response.send_message("❌ L'applicabilité doit être entre 1 et 5.", ephemeral=True)
        return
    
    if not (1 <= impact <= 5):
        await interaction.response.send_message("❌ L'impact doit être entre 1 et 5.", ephemeral=True)
        return
    
    # Calcul des coefficients selon les critères
    # Base : 5 points technologiques
    points_base = 5.0
    
    # Coefficient Qualité (Q) : ×2 max
    # Échelle : 1=×0.4, 2=×0.8, 3=×1.2, 4=×1.6, 5=×2.0
    coeff_qualite = (qualite * 2.0) / 5
    
    # Coefficient Applicabilité (A) : ×1.25 max  
    # Échelle : 1=×0.25, 2=×0.5, 3=×0.75, 4=×1.0, 5=×1.25
    coeff_applicabilite = (applicabilite * 1.25) / 5
    
    # Coefficient Impact (M) : ×1.5 max
    # Échelle : 1=×0.3, 2=×0.6, 3=×0.9, 4=×1.2, 5=×1.5
    coeff_impact = (impact * 1.5) / 5
    
    # Calcul du total
    total_coefficient = coeff_qualite + coeff_applicabilite + coeff_impact
    points_finaux = points_base * total_coefficient
    
    # Détermination de la notation générale
    moyenne = (qualite + applicabilite + impact) / 3
    if moyenne >= 4.5:
        notation = "Excellent"
        emoji = "🏆"
        couleur = 0x00ff00  # Vert
    elif moyenne >= 3.5:
        notation = "Très Bien"
        emoji = "🥇"
        couleur = 0x32cd32  # Vert lime
    elif moyenne >= 2.5:
        notation = "Bien"
        emoji = "🥈"
        couleur = 0xffd700  # Or
    elif moyenne >= 1.5:
        notation = "Passable"
        emoji = "🥉"
        couleur = 0xffa500  # Orange
    else:
        notation = "Insuffisant"
        emoji = "❌"
        couleur = 0xff0000  # Rouge
    
    # Construction de l'embed de résultat
    embed = discord.Embed(
        title=f"{emoji} Évaluation Action Technologique",
        description=f"**Notation générale :** {notation}",
        color=couleur
    )
    
    # Détails des critères
    embed.add_field(
        name="📊 Évaluation Détaillée",
        value=(
            f"**🎯 Qualité d'Écriture :** {qualite}/5 (×{coeff_qualite:.2f})\n"
            f"*Clarté, structure, richesse du contenu*\n\n"
            f"**⚙️ Applicabilité :** {applicabilite}/5 (×{coeff_applicabilite:.2f})\n"
            f"*Possibilité de mise en œuvre*\n\n"
            f"**🎖️ Impact :** {impact}/5 (×{coeff_impact:.2f})\n"
            f"*Importance stratégique et bénéfices*"
        ),
        inline=False
    )
    
    # Calcul final
    embed.add_field(
        name="🧮 Calcul Final",
        value=(
            f"**Base :** {points_base} points technologiques\n"
            f"**Coefficient total :** ×{total_coefficient:.2f}\n"
            f"**Points attribués :** {points_finaux:.2f} points"
        ),
        inline=False
    )
    
    # Barème de notation
    embed.add_field(
        name="📋 Barème de Notation",
        value=(
            "**5/5 :** Exceptionnel\n"
            "**4/5 :** Très bon\n"
            "**3/5 :** Bon\n"
            "**2/5 :** Moyen\n"
            "**1/5 :** Faible"
        ),
        inline=True
    )
    
    # Coefficients max
    embed.add_field(
        name="⚡ Coefficients Max",
        value=(
            "**Qualité :** ×2.0\n"
            "**Applicabilité :** ×1.25\n"
            "**Impact :** ×1.5\n"
            "**Total max :** ×4.75"
        ),
        inline=True
    )
    
    embed.set_footer(
        text=f"Évalué par {interaction.user.display_name} • Moyenne: {moyenne:.1f}/5"
    )
    
    # Envoyer le résultat
    await interaction.response.send_message(embed=embed)
    
    # Log dans le salon d'économie si configuré
    try:
        log_embed = discord.Embed(
            title="📊 Action Technologique Évaluée",
            description=(
                f"**Évaluateur :** {interaction.user.mention}\n"
                f"**Points attribués :** {points_finaux:.2f}\n"
                f"**Notation :** {notation} ({moyenne:.1f}/5)"
            ),
            color=couleur,
            timestamp=datetime.datetime.now()
        )
        
        log_embed.add_field(
            name="Critères",
            value=f"Q:{qualite}/5 • A:{applicabilite}/5 • I:{impact}/5",
            inline=False
        )
        
        await send_log(interaction.guild, embed=log_embed)
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'envoi du log action_tech: {e}")

@action_tech.error
async def action_tech_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Gestionnaire d'erreur pour la commande action_tech."""
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Une erreur s'est produite lors de l'exécution de la commande.", ephemeral=True)
        print(f"[ERROR] Erreur dans action_tech: {error}")

# === SYSTÈME DE BACKUP SERVEUR ===

# Vue pour la confirmation de backup avec code
class BackupConfirmView(discord.ui.Modal, title="Confirmation de Backup"):
    def __init__(self, guild_id):
        super().__init__()
        self.guild_id = guild_id
    
    code = discord.ui.TextInput(
        label="Code de confirmation",
        placeholder="Entrez le code de confirmation...",
        required=True,
        max_length=6
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.code.value != "240806":
            await interaction.response.send_message("❌ Code de confirmation incorrect !", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        
        try:
            # Créer la structure de backup
            backup_data = {
                "guild_info": {
                    "name": guild.name,
                    "description": guild.description,
                    "icon_url": str(guild.icon.url) if guild.icon else None,
                    "banner_url": str(guild.banner.url) if guild.banner else None,
                    "splash_url": str(guild.splash.url) if guild.splash else None,
                    "verification_level": str(guild.verification_level),
                    "default_notifications": str(guild.default_notifications),
                    "explicit_content_filter": str(guild.explicit_content_filter),
                    "preferred_locale": str(guild.preferred_locale),
                    "afk_timeout": guild.afk_timeout,
                    "mfa_level": guild.mfa_level,
                    "vanity_url": guild.vanity_url_code,
                    "premium_tier": guild.premium_tier,
                    "system_channel_flags": guild.system_channel_flags.value if guild.system_channel_flags else None,
                    "features": list(guild.features)
                },
                "roles": [],
                "categories": [],
                "channels": [],
                "threads": [],
                "webhooks": [],
                "emojis": [],
                "stickers": [],
                "members": [],
                "bans": [],
                "invites": [],
                "messages": {},
                "backup_timestamp": datetime.datetime.now().isoformat()
            }
            
            # Sauvegarder les rôles
            for role in guild.roles:
                if not role.is_default():  # Ignorer @everyone
                    role_data = {
                        "name": role.name,
                        "color": role.color.value,
                        "hoist": role.hoist,
                        "mentionable": role.mentionable,
                        "permissions": role.permissions.value,
                        "position": role.position,
                        "icon_url": str(role.icon.url) if role.icon else None,
                        "unicode_emoji": role.unicode_emoji
                    }
                    backup_data["roles"].append(role_data)
            
            # Sauvegarder les catégories
            for category in guild.categories:
                category_data = {
                    "name": category.name,
                    "position": category.position,
                    "nsfw": category.nsfw,
                    "overwrites": {}
                }
                
                # Permissions de la catégorie
                for target, overwrite in category.overwrites.items():
                    if isinstance(target, discord.Role):
                        category_data["overwrites"][f"role_{target.name}"] = {
                            "allow": overwrite.pair()[0].value,
                            "deny": overwrite.pair()[1].value
                        }
                    elif isinstance(target, discord.Member):
                        category_data["overwrites"][f"member_{target.id}"] = {
                            "allow": overwrite.pair()[0].value,
                            "deny": overwrite.pair()[1].value
                        }
                
                backup_data["categories"].append(category_data)
            
            # Sauvegarder les salons
            for channel in guild.channels:
                if isinstance(channel, discord.CategoryChannel):
                    continue  # Déjà traité
                
                channel_data = {
                    "name": channel.name,
                    "type": str(channel.type),
                    "position": channel.position,
                    "category": channel.category.name if channel.category else None,
                    "overwrites": {},
                    "nsfw": getattr(channel, 'nsfw', False)
                }
                
                # Attributs spécifiques selon le type
                if isinstance(channel, discord.TextChannel):
                    channel_data.update({
                        "topic": channel.topic,
                        "slowmode_delay": channel.slowmode_delay,
                        "default_auto_archive_duration": channel.default_auto_archive_duration,
                        "default_thread_slowmode_delay": getattr(channel, 'default_thread_slowmode_delay', 0)
                    })
                elif isinstance(channel, discord.VoiceChannel):
                    channel_data.update({
                        "bitrate": channel.bitrate,
                        "user_limit": channel.user_limit,
                        "rtc_region": str(channel.rtc_region) if channel.rtc_region else None
                    })
                elif isinstance(channel, discord.ForumChannel):
                    channel_data.update({
                        "topic": channel.topic,
                        "slowmode_delay": channel.slowmode_delay,
                        "default_auto_archive_duration": channel.default_auto_archive_duration,
                        "default_sort_order": str(channel.default_sort_order) if channel.default_sort_order else None,
                        "default_layout": str(channel.default_layout) if channel.default_layout else None,
                        "available_tags": [{"name": tag.name, "emoji": str(tag.emoji) if tag.emoji else None, "moderated": tag.moderated} for tag in channel.available_tags]
                    })
                elif isinstance(channel, discord.StageChannel):
                    channel_data.update({
                        "bitrate": channel.bitrate,
                        "user_limit": channel.user_limit,
                        "rtc_region": str(channel.rtc_region) if channel.rtc_region else None,
                        "topic": channel.topic
                    })
                
                # Permissions du salon
                for target, overwrite in channel.overwrites.items():
                    if isinstance(target, discord.Role):
                        channel_data["overwrites"][f"role_{target.name}"] = {
                            "allow": overwrite.pair()[0].value,
                            "deny": overwrite.pair()[1].value
                        }
                    elif isinstance(target, discord.Member):
                        channel_data["overwrites"][f"member_{target.id}"] = {
                            "allow": overwrite.pair()[0].value,
                            "deny": overwrite.pair()[1].value
                        }
                
                backup_data["channels"].append(channel_data)
            
            # Sauvegarder les fils de discussion
            for channel in guild.text_channels:
                try:
                    async for thread in channel.archived_threads(limit=None):
                        thread_data = {
                            "name": thread.name,
                            "parent_channel": channel.name,
                            "auto_archive_duration": thread.auto_archive_duration,
                            "slowmode_delay": thread.slowmode_delay,
                            "locked": thread.locked,
                            "archived": thread.archived,
                            "invitable": getattr(thread, 'invitable', True),
                            "type": str(thread.type),
                            "created_at": thread.created_at.isoformat() if thread.created_at else None
                        }
                        backup_data["threads"].append(thread_data)
                    
                    # Fils actifs
                    for thread in channel.threads:
                        thread_data = {
                            "name": thread.name,
                            "parent_channel": channel.name,
                            "auto_archive_duration": thread.auto_archive_duration,
                            "slowmode_delay": thread.slowmode_delay,
                            "locked": thread.locked,
                            "archived": thread.archived,
                            "invitable": getattr(thread, 'invitable', True),
                            "type": str(thread.type),
                            "created_at": thread.created_at.isoformat() if thread.created_at else None
                        }
                        backup_data["threads"].append(thread_data)
                except:
                    pass  # Ignorer les erreurs de permissions
            
            # Sauvegarder les webhooks
            for channel in guild.text_channels:
                try:
                    webhooks = await channel.webhooks()
                    for webhook in webhooks:
                        webhook_data = {
                            "name": webhook.name,
                            "channel": channel.name,
                            "avatar_url": str(webhook.avatar.url) if webhook.avatar else None,
                            "url": webhook.url
                        }
                        backup_data["webhooks"].append(webhook_data)
                except:
                    pass  # Ignorer les erreurs de permissions
            
            # Sauvegarder les emojis
            for emoji in guild.emojis:
                emoji_data = {
                    "name": emoji.name,
                    "animated": emoji.animated,
                    "url": str(emoji.url),
                    "available": emoji.available,
                    "managed": emoji.managed,
                    "require_colons": emoji.require_colons,
                    "roles": [role.name for role in emoji.roles] if emoji.roles else []
                }
                backup_data["emojis"].append(emoji_data)
            
            # Sauvegarder les stickers
            for sticker in guild.stickers:
                sticker_data = {
                    "name": sticker.name,
                    "description": sticker.description,
                    "emoji": str(sticker.emoji) if sticker.emoji else None,
                    "format": str(sticker.format),
                    "available": sticker.available,
                    "url": str(sticker.url)
                }
                backup_data["stickers"].append(sticker_data)
            
            # Sauvegarder les membres (info de base uniquement)
            for member in guild.members:
                if not member.bot:  # Ignorer les bots
                    member_data = {
                        "id": member.id,
                        "name": member.name,
                        "display_name": member.display_name,
                        "discriminator": member.discriminator,
                        "avatar_url": str(member.avatar.url) if member.avatar else None,
                        "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                        "roles": [role.name for role in member.roles if not role.is_default()],
                        "premium_since": member.premium_since.isoformat() if member.premium_since else None,
                        "nick": member.nick
                    }
                    backup_data["members"].append(member_data)
            
            # Sauvegarder les bannissements
            try:
                async for ban in guild.bans():
                    ban_data = {
                        "user_id": ban.user.id,
                        "user_name": ban.user.name,
                        "reason": ban.reason
                    }
                    backup_data["bans"].append(ban_data)
            except:
                pass  # Ignorer les erreurs de permissions
            
            # Sauvegarder les invitations
            try:
                invites = await guild.invites()
                for invite in invites:
                    invite_data = {
                        "code": invite.code,
                        "channel": invite.channel.name if invite.channel else None,
                        "inviter": invite.inviter.name if invite.inviter else None,
                        "uses": invite.uses,
                        "max_uses": invite.max_uses,
                        "max_age": invite.max_age,
                        "temporary": invite.temporary,
                        "created_at": invite.created_at.isoformat() if invite.created_at else None,
                        "expires_at": invite.expires_at.isoformat() if invite.expires_at else None
                    }
                    backup_data["invites"].append(invite_data)
            except:
                pass  # Ignorer les erreurs de permissions
            
            # Sauvegarder les messages (limité aux 1000 derniers par salon)
            await interaction.edit_original_response(content="📨 Sauvegarde des messages en cours...")
            
            for channel in guild.text_channels:
                try:
                    messages = []
                    async for message in channel.history(limit=1000):
                        message_data = {
                            "id": message.id,
                            "author": message.author.name,
                            "author_id": message.author.id,
                            "content": message.content,
                            "timestamp": message.created_at.isoformat(),
                            "edited_at": message.edited_at.isoformat() if message.edited_at else None,
                            "pinned": message.pinned,
                            "tts": message.tts,
                            "embeds": [embed.to_dict() for embed in message.embeds],
                            "attachments": [{"filename": att.filename, "url": att.url} for att in message.attachments],
                            "reactions": [{"emoji": str(reaction.emoji), "count": reaction.count} for reaction in message.reactions]
                        }
                        messages.append(message_data)
                    
                    if messages:
                        backup_data["messages"][channel.name] = messages
                except:
                    pass  # Ignorer les erreurs de permissions
            
            # Sauvegarder dans un fichier JSON
            filename = f"backup_{guild.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(DATA_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            # Calculer les statistiques
            stats = {
                "Rôles": len(backup_data["roles"]),
                "Catégories": len(backup_data["categories"]),
                "Salons": len(backup_data["channels"]),
                "Fils": len(backup_data["threads"]),
                "Webhooks": len(backup_data["webhooks"]),
                "Emojis": len(backup_data["emojis"]),
                "Stickers": len(backup_data["stickers"]),
                "Membres": len(backup_data["members"]),
                "Bannissements": len(backup_data["bans"]),
                "Invitations": len(backup_data["invites"]),
                "Salons avec messages": len(backup_data["messages"])
            }
            
            # Créer l'embed de confirmation
            embed = discord.Embed(
                title="✅ Backup Terminée",
                description=f"La sauvegarde complète du serveur **{guild.name}** a été créée avec succès !",
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            
            stats_text = "\n".join([f"**{key} :** {value}" for key, value in stats.items()])
            embed.add_field(
                name="📊 Statistiques de la Backup",
                value=stats_text,
                inline=False
            )
            
            embed.add_field(
                name="📁 Fichier",
                value=f"`{filename}`",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Note",
                value="Cette backup contient tous les éléments du serveur. Gardez ce fichier en sécurité !",
                inline=False
            )
            
            embed.set_footer(text=f"Backup créée par {interaction.user.display_name}")
            
            # Message de confirmation avec mention
            confirmation_message = f"🎉 **{interaction.user.mention}** Votre backup a été créée avec succès !\n📁 Fichier : `{filename}`"
            
            await interaction.edit_original_response(content=confirmation_message, embed=embed)
            
            # Envoyer aussi un message de confirmation dans le salon (non éphémère)
            try:
                confirmation_embed = discord.Embed(
                    title="✅ Backup Créée",
                    description=(
                        f"Une backup du serveur **{guild.name}** a été créée avec succès !\n\n"
                        f"📁 **Fichier :** `{filename}`\n"
                        f"👤 **Créée par :** {interaction.user.mention}\n"
                        f"📊 **Éléments sauvegardés :** {sum(stats.values())} au total\n"
                        f"⏰ **Horodatage :** {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"
                    ),
                    color=0x00ff00,
                    timestamp=datetime.datetime.now()
                )
                
                stats_text = "\n".join([f"• **{key} :** {value}" for key, value in stats.items()])
                confirmation_embed.add_field(
                    name="📈 Détails de la Sauvegarde",
                    value=stats_text,
                    inline=False
                )
                
                confirmation_embed.add_field(
                    name="🔒 Sécurité",
                    value="Cette backup contient des données sensibles. Stockez-la en lieu sûr !",
                    inline=False
                )
                
                # Envoyer dans le salon actuel
                await interaction.followup.send(embed=confirmation_embed)
                
            except Exception as follow_error:
                print(f"[ERROR] Erreur lors de l'envoi du message de confirmation : {follow_error}")
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Erreur de Backup",
                description=f"Une erreur s'est produite lors de la création de la backup :\n```{str(e)}```",
                color=0xff0000
            )
            await interaction.edit_original_response(content=None, embed=error_embed)
            print(f"[ERROR] Erreur lors de la backup: {e}")

@bot.tree.command(name="backup", description="Crée une sauvegarde complète du serveur")
@app_commands.checks.has_permissions(administrator=True)
async def backup(interaction: discord.Interaction):
    """Crée une backup complète du serveur avec confirmation par code."""
    
    # Embed d'avertissement
    embed = discord.Embed(
        title="⚠️ Backup du Serveur",
        description=(
            "Vous êtes sur le point de créer une **sauvegarde complète** du serveur.\n\n"
            "**Cette backup incluera :**\n"
            "🏛️ Informations du serveur\n"
            "🎭 Tous les rôles et permissions\n"
            "📁 Toutes les catégories\n"
            "💬 Tous les salons (texte, vocal, forum, stage)\n"
            "🧵 Tous les fils de discussion\n"
            "🔗 Tous les webhooks\n"
            "😄 Tous les emojis et stickers\n"
            "👥 Informations des membres\n"
            "🚫 Liste des bannissements\n"
            "🎟️ Invitations actives\n"
            "📨 Messages récents (100 derniers par salon)\n\n"
            "**⚠️ Attention :** Cette opération peut prendre plusieurs minutes selon la taille du serveur."
        ),
        color=0xff9900
    )
    
    embed.add_field(
        name="🔐 Confirmation Requise",
        value="Pour confirmer cette action, cliquez sur le bouton ci-dessous et entrez le code de confirmation.",
        inline=False
    )
    
    embed.set_footer(text="Cette action nécessite les permissions administrateur")
    
    # Vue avec bouton de confirmation
    view = discord.ui.View()
    
    confirm_button = discord.ui.Button(
        label="Confirmer la Backup",
        style=discord.ButtonStyle.danger,
        emoji="💾"
    )
    
    async def confirm_callback(button_interaction):
        if button_interaction.user.id != interaction.user.id:
            await button_interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut confirmer.", ephemeral=True)
            return
        
        modal = BackupConfirmView(interaction.guild.id)
        await button_interaction.response.send_modal(modal)
    
    confirm_button.callback = confirm_callback
    view.add_item(confirm_button)
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@backup.error
async def backup_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Gestionnaire d'erreur pour la commande backup."""
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Une erreur s'est produite lors de l'exécution de la commande.", ephemeral=True)
        print(f"[ERROR] Erreur dans backup: {error}")

# Classe pour la sélection de backup avec menu déroulant
class BackupSelectView(discord.ui.View):
    def __init__(self, backup_files):
        super().__init__(timeout=None)
        self.backup_files = backup_files
        
        # Menu déroulant pour sélectionner la backup
        options = []
        for filename in backup_files:
            # Extraire les infos du nom de fichier
            parts = filename.replace('.json', '').split('_')
            if len(parts) >= 3:
                server_name = '_'.join(parts[1:-2]) if len(parts) > 3 else parts[1]
                date_part = parts[-2]
                time_part = parts[-1]
                
                # Formater la date et l'heure
                try:
                    date_formatted = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                    time_formatted = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
                    label = f"{server_name} - {date_formatted} {time_formatted}"
                except:
                    label = filename.replace('.json', '')
                
                options.append(discord.SelectOption(
                    label=label[:100],  # Limite Discord
                    description=f"Backup du serveur {server_name}"[:100],
                    value=filename
                ))
        
        if options:
            self.select_backup = discord.ui.Select(
                placeholder="Choisissez une backup à restaurer...",
                options=options[:25]  # Limite Discord de 25 options
            )
            self.select_backup.callback = self.backup_selected
            self.add_item(self.select_backup)
    
    async def backup_selected(self, interaction: discord.Interaction):
        """Callback quand une backup est sélectionnée."""
        filename = self.select_backup.values[0]
        
        # Confirmation avant restauration
        embed = discord.Embed(
            title="⚠️ Confirmation de Restauration",
            description=(
                f"Vous êtes sur le point de **RESTAURER** la backup :\n"
                f"📁 `{filename}`\n\n"
                "**🚨 ATTENTION CRITIQUE :**\n"
                "• **TOUS les éléments actuels du serveur seront SUPPRIMÉS**\n"
                "• Cette action est **IRRÉVERSIBLE**\n"
                "• Le serveur sera entièrement reconstruit selon la backup\n\n"
                "**Éléments qui seront restaurés :**\n"
                "🎭 Rôles • 📁 Catégories • 💬 Salons\n"
                "🧵 Fils • 🔗 Webhooks • 😄 Emojis\n"
                "👥 Membres (rôles) • 🚫 Bans\n\n"
                "⏱️ **Temps estimé :** 5-30 minutes selon la taille"
            ),
            color=0xff0000
        )
        
        # Boutons de confirmation finale
        confirm_view = discord.ui.View(timeout=None)
        
        confirm_btn = discord.ui.Button(
            label="CONFIRMER LA RESTAURATION",
            style=discord.ButtonStyle.danger,
            emoji="💥"
        )
        
        cancel_btn = discord.ui.Button(
            label="Annuler",
            style=discord.ButtonStyle.secondary,
            emoji="❌"
        )
        
        async def confirm_restore(btn_interaction):
            if btn_interaction.user.id != interaction.user.id:
                await btn_interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut confirmer.", ephemeral=True)
                return
            
            await btn_interaction.response.defer()
            await self.restore_backup(btn_interaction, filename)
        
        async def cancel_restore(btn_interaction):
            if btn_interaction.user.id != interaction.user.id:
                await btn_interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut annuler.", ephemeral=True)
                return
            
            cancel_embed = discord.Embed(
                title="❌ Restauration Annulée",
                description="La restauration de la backup a été annulée.",
                color=0x808080
            )
            await btn_interaction.response.edit_message(embed=cancel_embed, view=None)
        
        confirm_btn.callback = confirm_restore
        cancel_btn.callback = cancel_restore
        
        confirm_view.add_item(confirm_btn)
        confirm_view.add_item(cancel_btn)
        
        await interaction.response.edit_message(embed=embed, view=confirm_view)
    
    async def restore_backup(self, interaction: discord.Interaction, filename: str):
        """Restaure une backup complète."""
        try:
            filepath = os.path.join(DATA_DIR, filename)
            
            # Charger les données de backup
            with open(filepath, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            guild = interaction.guild
            
            # Embed de progression
            progress_embed = discord.Embed(
                title="🔄 Restauration en cours...",
                description="Suppression des éléments actuels...",
                color=0xff9900
            )
            await interaction.edit_original_response(embed=progress_embed, view=None)
            
            # 1. Supprimer tous les salons existants (sauf celui où on écrit)
            current_channel = interaction.channel
            progress_embed.description = "🗑️ Suppression des salons existants..."
            await interaction.edit_original_response(embed=progress_embed)
            
            for channel in list(guild.channels):
                if channel.id != current_channel.id and not isinstance(channel, discord.CategoryChannel):
                    try:
                        await channel.delete(reason="Restauration de backup")
                    except:
                        pass
            
            # 2. Supprimer les catégories
            for category in list(guild.categories):
                try:
                    await category.delete(reason="Restauration de backup")
                except:
                    pass
            
            # 3. Supprimer les rôles (sauf @everyone et rôles protégés)
            progress_embed.description = "🎭 Suppression des rôles existants..."
            await interaction.edit_original_response(embed=progress_embed)
            
            for role in list(guild.roles):
                if not role.is_default() and not role.is_bot_managed() and not role.is_premium_subscriber():
                    try:
                        await role.delete(reason="Restauration de backup")
                    except:
                        pass
            
            # 4. Recréer les rôles
            progress_embed.description = "🎭 Création des rôles..."
            await interaction.edit_original_response(embed=progress_embed)
            
            role_mapping = {}  # Pour mapper les anciens noms aux nouveaux rôles
            
            # Trier les rôles par position (du plus bas au plus haut)
            sorted_roles = sorted(backup_data.get("roles", []), key=lambda r: r.get("position", 0))
            
            for role_data in sorted_roles:
                try:
                    permissions = discord.Permissions(role_data.get("permissions", 0))
                    new_role = await guild.create_role(
                        name=role_data["name"],
                        color=discord.Color(role_data.get("color", 0)),
                        hoist=role_data.get("hoist", False),
                        mentionable=role_data.get("mentionable", False),
                        permissions=permissions,
                        reason="Restauration de backup"
                    )
                    role_mapping[role_data["name"]] = new_role
                except Exception as e:
                    print(f"Erreur création rôle {role_data['name']}: {e}")
            
            # 5. Recréer les catégories
            progress_embed.description = "📁 Création des catégories..."
            await interaction.edit_original_response(embed=progress_embed)
            
            category_mapping = {}
            
            for category_data in backup_data.get("categories", []):
                try:
                    # Créer les overwrites
                    overwrites = {}
                    for target_name, overwrite_data in category_data.get("overwrites", {}).items():
                        if target_name.startswith("role_"):
                            role_name = target_name[5:]  # Enlever "role_"
                            if role_name in role_mapping:
                                allow = discord.Permissions(overwrite_data.get("allow", 0))
                                deny = discord.Permissions(overwrite_data.get("deny", 0))
                                overwrites[role_mapping[role_name]] = discord.PermissionOverwrite.from_pair(allow, deny)
                    
                    new_category = await guild.create_category(
                        name=category_data["name"],
                        overwrites=overwrites,
                        reason="Restauration de backup"
                    )
                    category_mapping[category_data["name"]] = new_category
                except Exception as e:
                    print(f"Erreur création catégorie {category_data['name']}: {e}")
            
            # 6. Recréer les salons
            progress_embed.description = "💬 Création des salons..."
            await interaction.edit_original_response(embed=progress_embed)
            
            channel_mapping = {}
            
            # Trier les salons par position
            sorted_channels = sorted(backup_data.get("channels", []), key=lambda c: c.get("position", 0))
            
            for channel_data in sorted_channels:
                try:
                    # Déterminer la catégorie
                    category = None
                    if channel_data.get("category") and channel_data["category"] in category_mapping:
                        category = category_mapping[channel_data["category"]]
                    
                    # Créer les overwrites
                    overwrites = {}
                    for target_name, overwrite_data in channel_data.get("overwrites", {}).items():
                        if target_name.startswith("role_"):
                            role_name = target_name[5:]
                            if role_name in role_mapping:
                                allow = discord.Permissions(overwrite_data.get("allow", 0))
                                deny = discord.Permissions(overwrite_data.get("deny", 0))
                                overwrites[role_mapping[role_name]] = discord.PermissionOverwrite.from_pair(allow, deny)
                    
                    # Créer selon le type
                    channel_type = channel_data.get("type", "text")
                    
                    if "text" in channel_type.lower():
                        new_channel = await guild.create_text_channel(
                            name=channel_data["name"],
                            category=category,
                            topic=channel_data.get("topic"),
                            slowmode_delay=channel_data.get("slowmode_delay", 0),
                            nsfw=channel_data.get("nsfw", False),
                            overwrites=overwrites,
                            reason="Restauration de backup"
                        )
                    elif "voice" in channel_type.lower():
                        new_channel = await guild.create_voice_channel(
                            name=channel_data["name"],
                            category=category,
                            bitrate=min(channel_data.get("bitrate", 64000), guild.bitrate_limit),
                            user_limit=channel_data.get("user_limit", 0),
                            overwrites=overwrites,
                            reason="Restauration de backup"
                        )
                    elif "forum" in channel_type.lower():
                        # Les forums nécessitent des permissions spéciales
                        new_channel = await guild.create_forum(
                            name=channel_data["name"],
                            category=category,
                            topic=channel_data.get("topic"),
                            overwrites=overwrites,
                            reason="Restauration de backup"
                        )
                    elif "stage" in channel_type.lower():
                        new_channel = await guild.create_stage_channel(
                            name=channel_data["name"],
                            category=category,
                            topic=channel_data.get("topic"),
                            overwrites=overwrites,
                            reason="Restauration de backup"
                        )
                    else:
                        # Par défaut, salon texte
                        new_channel = await guild.create_text_channel(
                            name=channel_data["name"],
                            category=category,
                            overwrites=overwrites,
                            reason="Restauration de backup"
                        )
                    
                    channel_mapping[channel_data["name"]] = new_channel
                    
                except Exception as e:
                    print(f"Erreur création salon {channel_data['name']}: {e}")
            
            # 7. Restaurer les rôles des membres
            progress_embed.description = "👥 Restauration des rôles des membres..."
            await interaction.edit_original_response(embed=progress_embed)
            
            for member_data in backup_data.get("members", []):
                try:
                    member = guild.get_member(member_data["id"])
                    if member:
                        # Assigner les rôles
                        roles_to_add = []
                        for role_name in member_data.get("roles", []):
                            if role_name in role_mapping:
                                roles_to_add.append(role_mapping[role_name])
                        
                        if roles_to_add:
                            await member.add_roles(*roles_to_add, reason="Restauration de backup")
                        
                        # Restaurer le surnom
                        if member_data.get("nick") and member_data["nick"] != member.display_name:
                            try:
                                await member.edit(nick=member_data["nick"], reason="Restauration de backup")
                            except:
                                pass
                except Exception as e:
                    print(f"Erreur restauration membre {member_data.get('name', 'Unknown')}: {e}")
            
            # 8. Finalisation
            progress_embed.title = "✅ Restauration Terminée"
            progress_embed.description = (
                f"La backup **{filename}** a été restaurée avec succès !\n\n"
                f"**Éléments restaurés :**\n"
                f"🎭 Rôles : {len(backup_data.get('roles', []))}\n"
                f"📁 Catégories : {len(backup_data.get('categories', []))}\n"
                f"💬 Salons : {len(backup_data.get('channels', []))}\n"
                f"👥 Membres traités : {len(backup_data.get('members', []))}\n\n"
                f"⚠️ **Note :** Les messages, webhooks et emojis nécessitent une restauration manuelle."
            )
            progress_embed.color = 0x00ff00
            
            await interaction.edit_original_response(embed=progress_embed)
            
        except FileNotFoundError:
            error_embed = discord.Embed(
                title="❌ Fichier non trouvé",
                description=f"Le fichier de backup `{filename}` n'existe pas.",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=error_embed, view=None)
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Erreur de Restauration",
                description=f"Une erreur s'est produite lors de la restauration :\n```{str(e)}```",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=error_embed, view=None)
            print(f"[ERROR] Erreur lors de la restauration: {e}")

@bot.tree.command(name="select_backup", description="Sélectionne et restaure une backup du serveur")
@app_commands.checks.has_permissions(administrator=True)
async def select_backup(interaction: discord.Interaction):
    """Permet de sélectionner et restaurer une backup existante."""
    
    # Chercher tous les fichiers de backup
    backup_files = []
    if os.path.exists(DATA_DIR):
        for filename in os.listdir(DATA_DIR):
            if filename.startswith("backup_") and filename.endswith(".json"):
                backup_files.append(filename)
    
    if not backup_files:
        embed = discord.Embed(
            title="❌ Aucune Backup Trouvée",
            description="Aucun fichier de backup n'a été trouvé dans le dossier data/.",
            color=0xff0000
        )
        embed.add_field(
            name="💡 Suggestion",
            value="Utilisez `/backup` pour créer une sauvegarde d'abord.",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Trier les fichiers par date (plus récent en premier)
    backup_files.sort(reverse=True)
    
    # Créer l'embed de sélection
    embed = discord.Embed(
        title="🔄 Sélection de Backup",
        description=(
            f"**{len(backup_files)} backup(s) disponible(s)**\n\n"
            "Sélectionnez la backup à restaurer dans le menu ci-dessous.\n\n"
            "⚠️ **ATTENTION :** La restauration supprimera **TOUT** le contenu actuel du serveur !"
        ),
        color=0x0099ff
    )
    
    embed.add_field(
        name="📋 Backups Disponibles",
        value=f"Utilisez le menu déroulant pour voir les {len(backup_files)} backup(s)",
        inline=False
    )
    
    embed.set_footer(text="Cette action nécessite les permissions administrateur")
    
    # Créer la vue avec le menu déroulant
    view = BackupSelectView(backup_files)
    
    if not view.children:  # Aucun select menu créé (pas de backups valides)
        embed.description = "❌ Aucune backup valide trouvée."
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@select_backup.error
async def select_backup_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Gestionnaire d'erreur pour la commande select_backup."""
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Une erreur s'est produite lors de l'exécution de la commande.", ephemeral=True)
        print(f"[ERROR] Erreur dans select_backup: {error}")

# Vue pour la confirmation de suppression de backup avec code
class DeleteBackupConfirmView(discord.ui.Modal, title="Confirmation de Suppression"):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
    
    code = discord.ui.TextInput(
        label="Code de confirmation",
        placeholder="Entrez le code de confirmation pour supprimer...",
        required=True,
        max_length=6
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.code.value != "240806":
            await interaction.response.send_message("❌ Code de confirmation incorrect !", ephemeral=True)
            return
        
        try:
            filepath = os.path.join(DATA_DIR, self.filename)
            
            # Vérifier que le fichier existe
            if not os.path.exists(filepath):
                await interaction.response.send_message(
                    f"❌ Le fichier `{self.filename}` n'existe pas.",
                    ephemeral=True
                )
                return
            
            # Charger les informations de la backup avant suppression
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                server_name = backup_data.get("guild_info", {}).get("name", "Serveur Inconnu")
                backup_timestamp = backup_data.get("backup_timestamp", "Date inconnue")
                
                # Calculer les statistiques
                stats = {
                    "Rôles": len(backup_data.get("roles", [])),
                    "Catégories": len(backup_data.get("categories", [])),
                    "Salons": len(backup_data.get("channels", [])),
                    "Fils": len(backup_data.get("threads", [])),
                    "Webhooks": len(backup_data.get("webhooks", [])),
                    "Emojis": len(backup_data.get("emojis", [])),
                    "Stickers": len(backup_data.get("stickers", [])),
                    "Membres": len(backup_data.get("members", [])),
                    "Bannissements": len(backup_data.get("bans", [])),
                    "Invitations": len(backup_data.get("invites", [])),
                    "Salons avec messages": len(backup_data.get("messages", {}))
                }
                
            except (json.JSONDecodeError, KeyError):
                server_name = "Serveur Inconnu"
                backup_timestamp = "Date inconnue"
                stats = {"Éléments": "Impossible de lire"}
            
            # Supprimer le fichier
            os.remove(filepath)
            
            # Créer l'embed de confirmation de suppression
            embed = discord.Embed(
                title="🗑️ Backup Supprimée",
                description=f"La backup **{self.filename}** a été supprimée avec succès !",
                color=0xff6600,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(
                name="📋 Informations de la Backup Supprimée",
                value=(
                    f"**Serveur :** {server_name}\n"
                    f"**Date de création :** {backup_timestamp[:19] if len(backup_timestamp) > 19 else backup_timestamp}\n"
                    f"**Supprimée par :** {interaction.user.mention}"
                ),
                inline=False
            )
            
            if isinstance(stats.get("Éléments"), str):
                embed.add_field(
                    name="⚠️ Contenu",
                    value="Impossible de lire le contenu (fichier corrompu)",
                    inline=False
                )
            else:
                stats_text = "\n".join([f"• **{key} :** {value}" for key, value in stats.items()])
                embed.add_field(
                    name="📊 Contenu Supprimé",
                    value=stats_text,
                    inline=False
                )
            
            embed.add_field(
                name="⚠️ Action Irréversible",
                value="Cette backup ne peut plus être récupérée. Assurez-vous d'avoir une copie si nécessaire.",
                inline=False
            )
            
            embed.set_footer(text=f"Suppression effectuée par {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
            
            # Message de confirmation dans le salon (non éphémère)
            try:
                public_embed = discord.Embed(
                    title="🗑️ Backup Supprimée",
                    description=(
                        f"Une backup a été supprimée du système.\n\n"
                        f"📁 **Fichier :** `{self.filename}`\n"
                        f"🏛️ **Serveur :** {server_name}\n"
                        f"👤 **Supprimée par :** {interaction.user.mention}\n"
                        f"⏰ **Suppression :** {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"
                    ),
                    color=0xff6600,
                    timestamp=datetime.datetime.now()
                )
                
                public_embed.add_field(
                    name="🔒 Sécurité",
                    value="Action irréversible effectuée avec code de confirmation.",
                    inline=False
                )
                
                await interaction.followup.send(embed=public_embed)
                
            except Exception as follow_error:
                print(f"[ERROR] Erreur lors de l'envoi du message public de suppression : {follow_error}")
            
        except FileNotFoundError:
            await interaction.response.send_message(
                f"❌ Le fichier `{self.filename}` n'existe pas.",
                ephemeral=True
            )
        except PermissionError:
            await interaction.response.send_message(
                f"❌ Permissions insuffisantes pour supprimer le fichier `{self.filename}`.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erreur lors de la suppression : {str(e)}",
                ephemeral=True
            )
            print(f"[ERROR] Erreur lors de la suppression de backup: {e}")

# Classe pour la sélection de backup à supprimer
class DeleteBackupSelectView(discord.ui.View):
    def __init__(self, backup_files):
        super().__init__(timeout=None)
        self.backup_files = backup_files
        
        # Menu déroulant pour sélectionner la backup à supprimer
        options = []
        for filename in backup_files:
            # Extraire les infos du nom de fichier
            parts = filename.replace('.json', '').split('_')
            if len(parts) >= 3:
                server_name = '_'.join(parts[1:-2]) if len(parts) > 3 else parts[1]
                date_part = parts[-2]
                time_part = parts[-1]
                
                # Formater la date et l'heure
                try:
                    date_formatted = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                    time_formatted = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
                    label = f"{server_name} - {date_formatted} {time_formatted}"
                except:
                    label = filename.replace('.json', '')
                
                options.append(discord.SelectOption(
                    label=label[:100],  # Limite Discord
                    description=f"Supprimer la backup de {server_name}"[:100],
                    value=filename,
                    emoji="🗑️"
                ))
        
        if options:
            self.select_backup = discord.ui.Select(
                placeholder="Choisissez une backup à supprimer...",
                options=options[:25]  # Limite Discord de 25 options
            )
            self.select_backup.callback = self.backup_selected
            self.add_item(self.select_backup)
    
    async def backup_selected(self, interaction: discord.Interaction):
        """Callback quand une backup est sélectionnée pour suppression."""
        filename = self.select_backup.values[0]
        
        # Confirmation avant suppression
        embed = discord.Embed(
            title="⚠️ Confirmation de Suppression",
            description=(
                f"Vous êtes sur le point de **SUPPRIMER DÉFINITIVEMENT** la backup :\n"
                f"📁 `{filename}`\n\n"
                "**🚨 ATTENTION CRITIQUE :**\n"
                "• Cette action est **IRRÉVERSIBLE**\n"
                "• Le fichier sera **DÉFINITIVEMENT SUPPRIMÉ**\n"
                "• Aucune récupération ne sera possible\n"
                "• Assurez-vous d'avoir une copie si nécessaire\n\n"
                "Pour confirmer cette suppression définitive, cliquez sur le bouton ci-dessous et entrez le code de confirmation."
            ),
            color=0xff0000
        )
        
        # Bouton de confirmation finale
        confirm_view = discord.ui.View(timeout=None)
        
        confirm_btn = discord.ui.Button(
            label="SUPPRIMER DÉFINITIVEMENT",
            style=discord.ButtonStyle.danger,
            emoji="🗑️"
        )
        
        cancel_btn = discord.ui.Button(
            label="Annuler",
            style=discord.ButtonStyle.secondary,
            emoji="❌"
        )
        
        async def confirm_delete(btn_interaction):
            if btn_interaction.user.id != interaction.user.id:
                await btn_interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut confirmer.", ephemeral=True)
                return
            
            modal = DeleteBackupConfirmView(filename)
            await btn_interaction.response.send_modal(modal)
        
        async def cancel_delete(btn_interaction):
            if btn_interaction.user.id != interaction.user.id:
                await btn_interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut annuler.", ephemeral=True)
                return
            
            cancel_embed = discord.Embed(
                title="❌ Suppression Annulée",
                description="La suppression de la backup a été annulée.",
                color=0x808080
            )
            await btn_interaction.response.edit_message(embed=cancel_embed, view=None)
        
        confirm_btn.callback = confirm_delete
        cancel_btn.callback = cancel_delete
        
        confirm_view.add_item(confirm_btn)
        confirm_view.add_item(cancel_btn)
        
        await interaction.response.edit_message(embed=embed, view=confirm_view)

@bot.tree.command(name="supprimer_backup", description="Supprime définitivement une backup du serveur")
@app_commands.checks.has_permissions(administrator=True)
async def supprimer_backup(interaction: discord.Interaction):
    """Permet de supprimer définitivement une backup existante."""
    
    # Chercher tous les fichiers de backup
    backup_files = []
    if os.path.exists(DATA_DIR):
        for filename in os.listdir(DATA_DIR):
            if filename.startswith("backup_") and filename.endswith(".json"):
                backup_files.append(filename)
    
    if not backup_files:
        embed = discord.Embed(
            title="❌ Aucune Backup Trouvée",
            description="Aucun fichier de backup n'a été trouvé dans le dossier data/.",
            color=0xff0000
        )
        embed.add_field(
            name="💡 Information",
            value="Il n'y a actuellement aucune backup à supprimer.",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Trier les fichiers par date (plus récent en premier)
    backup_files.sort(reverse=True)
    
    # Créer l'embed de sélection
    embed = discord.Embed(
        title="🗑️ Suppression de Backup",
        description=(
            f"**{len(backup_files)} backup(s) disponible(s) pour suppression**\n\n"
            "Sélectionnez la backup à supprimer dans le menu ci-dessous.\n\n"
            "⚠️ **ATTENTION :** Cette action est **IRRÉVERSIBLE** !\n"
            "🔐 **Code de confirmation requis :** 240806"
        ),
        color=0xff6600
    )
    
    embed.add_field(
        name="📋 Backups Disponibles",
        value=f"Utilisez le menu déroulant pour voir les {len(backup_files)} backup(s)",
        inline=False
    )
    
    embed.add_field(
        name="🚨 Avertissement",
        value="Une fois supprimée, une backup ne peut plus être récupérée. Assurez-vous d'avoir une copie de sauvegarde si nécessaire.",
        inline=False
    )
    
    embed.set_footer(text="Cette action nécessite les permissions administrateur")
    
    # Créer la vue avec le menu déroulant
    view = DeleteBackupSelectView(backup_files)
    
    if not view.children:  # Aucun select menu créé (pas de backups valides)
        embed.description = "❌ Aucune backup valide trouvée."
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@supprimer_backup.error
async def supprimer_backup_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Gestionnaire d'erreur pour la commande supprimer_backup."""
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Une erreur s'est produite lors de l'exécution de la commande.", ephemeral=True)
        print(f"[ERROR] Erreur dans supprimer_backup: {error}")

# === SYSTÈME DE TECHNOLOGIES MILITAIRES ===

# Vue pour le bouton de confirmation de développement technologique
class TechnoConfirmView(discord.ui.View):
    def __init__(self, user_id, role, cout_dev, nom_techno, nom_developpement, categorie, nom_categorie, cout_unite, mois, image, unit_multiplier):
        super().__init__(timeout=None)  # Durée indéfinie
        self.user_id = user_id
        self.role = role
        self.cout_dev = cout_dev
        self.nom_techno = nom_techno
        self.nom_developpement = nom_developpement
        self.categorie = categorie
        self.nom_categorie = nom_categorie
        self.cout_unite = cout_unite
        self.mois = mois
        self.image = image
        self.unit_multiplier = unit_multiplier
    
    @discord.ui.button(label="Confirmer le développement", style=discord.ButtonStyle.green, emoji="🔬")
    async def confirmer_developpement(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Protection contre les double-clics
        if button.disabled:
            await interaction.response.send_message("❌ Cette confirmation a déjà été traitée.", ephemeral=True)
            return
            
        # Désactiver le bouton immédiatement pour éviter les double-clics
        button.disabled = True
        
        # Vérifier que l'utilisateur a bien le rôle du pays concerné
        if self.role not in interaction.user.roles:
            await interaction.response.send_message(f"❌ Vous devez avoir le rôle {self.role.mention} pour confirmer ce développement.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Charger les données du calendrier
        calendrier_data = load_calendrier()
        
        # Vérifier le budget du rôle
        role_id = str(self.role.id)
        budget_actuel = balances.get(role_id, 0)
        
        if budget_actuel < self.cout_dev:
            embed = discord.Embed(
                title="❌ Budget insuffisant",
                description=f"**Coût du développement :** {format_number(self.cout_dev)} {MONNAIE_EMOJI}\n"
                           f"**Budget actuel :** {format_number(budget_actuel)} {MONNAIE_EMOJI}\n"
                           f"**Manquant :** {format_number(self.cout_dev - budget_actuel)} {MONNAIE_EMOJI}",
                color=0xff0000,
                timestamp=datetime.datetime.now()
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Déterminer le domaine de la technologie
        domaine_tech = get_domaine_from_tech(self.nom_techno)
        
        # Charger les centres technologiques
        centres_data = load_centres_tech()
        guild_id = str(interaction.guild.id)
        
        centres_compatibles = []
        if guild_id in centres_data and role_id in centres_data[guild_id]:
            for centre in centres_data[guild_id][role_id]:
                if centre["specialisation"] == domaine_tech:
                    centres_compatibles.append(centre)
        
        if not centres_compatibles:
            embed = discord.Embed(
                title="❌ Aucun centre compatible",
                description=f"**Domaine requis :** {domaine_tech}\n"
                           f"Vous devez avoir un centre technologique spécialisé en **{domaine_tech}** pour développer cette technologie.\n"
                           f"Utilisez `/centre_tech` pour créer un centre avec cette spécialisation.",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Vérifier les emplacements disponibles
        centre_choisi = None
        for centre in centres_compatibles:
            # Compter les développements en cours dans ce centre (pas les terminés)
            developpements_data = load_developpements()
            nb_dev_en_cours = 0
            if guild_id in developpements_data and role_id in developpements_data[guild_id]:
                for dev in developpements_data[guild_id][role_id]:
                    centre_nom = centre.get("nom", centre.get("localisation", ""))
                    if (dev.get("centre_attache") == centre_nom and 
                        dev.get("statut", "en_cours") == "en_cours"):
                        nb_dev_en_cours += 1
            
            if nb_dev_en_cours < centre["emplacements_max"]:
                centre_choisi = centre
                break
        
        if not centre_choisi:
            embed = discord.Embed(
                title="❌ Centres saturés",
                description=f"Tous vos centres **{domaine_tech}** sont pleins.\n"
                           f"Améliorez un centre existant avec `/amelioration` ou créez un nouveau centre.",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Vérifier qu'il n'y a pas déjà un développement identique en cours
        developpements_existants = load_developpements()
        guild_id = str(interaction.guild.id)
        
        if guild_id in developpements_existants and role_id in developpements_existants[guild_id]:
            for dev_existant in developpements_existants[guild_id][role_id]:
                # Vérifier seulement les développements en cours (pas terminés)
                statut_existant = dev_existant.get("statut", "en_cours")
                if (dev_existant.get("nom") == self.nom_developpement and 
                    dev_existant.get("technologie") == self.nom_techno and
                    statut_existant == "en_cours" and
                    dev_existant.get("fin_timestamp", 0) > time.time()):  # Encore en cours
                    embed = discord.Embed(
                        title="❌ Développement déjà en cours",
                        description=f"Un développement identique est déjà en cours :\n"
                                   f"**Nom :** {self.nom_developpement}\n"
                                   f"**Technologie :** {self.nom_techno}\n"
                                   f"Attendez qu'il se termine avant d'en lancer un nouveau.",
                        color=0xff0000
                    )
                    await interaction.followup.send(embed=embed)
                    return
        
        # Déduire le coût du budget
        balances[role_id] = budget_actuel - self.cout_dev
        save_balances(balances)
        save_all_json_to_postgres()
        
        # Calculer la durée avec bonus du centre (niveau 3 = -1 mois)
        duree_finale = self.mois
        if centre_choisi["niveau"] == 3:
            duree_finale = max(1, self.mois - 1)  # Au minimum 1 mois
        
        # Calculer le timestamp de fin avec le système de calendrier
        fin_timestamp = calculate_fin_with_calendar(duree_finale)
        
        # Sauvegarder le développement dans le JSON
        developpements = load_developpements()
        
        if guild_id not in developpements:
            developpements[guild_id] = {}
        if role_id not in developpements[guild_id]:
            developpements[guild_id][role_id] = []
        
        # Créer l'entrée de développement
        developpement_data = {
            "nom": self.nom_developpement,
            "technologie": self.nom_techno,
            "categorie": self.categorie,
            "nom_categorie": self.nom_categorie,
            "cout_dev": self.cout_dev,
            "cout_unite": self.cout_unite,
            "unit_multiplier": self.unit_multiplier,
            "mois": duree_finale,
            "image": self.image,
            "date_creation": datetime.datetime.now().isoformat(),
            "createur": interaction.user.id,
            "centre_attache": centre_choisi.get("nom", centre_choisi.get("localisation", "")),
            "domaine": domaine_tech,
            "fin_timestamp": fin_timestamp,
            "statut": "en_cours",  # Statut par défaut pour les nouveaux développements
            # Ajouter le contexte RP pour le calcul de fin selon le calendrier
            "mois_creation_rp": calendrier_data.get("mois_index", 0),
            "annee_creation_rp": calendrier_data.get("annee", 2025)
        }
        
        developpements[guild_id][role_id].append(developpement_data)
        save_developpements(developpements)
        
        # Créer l'embed de confirmation
        bonus_text = f" (-1 mois grâce au centre niveau 3)" if centre_choisi["niveau"] == 3 and duree_finale != self.mois else ""
        
        # Calculer les dates de fin
        calendrier_data = load_calendrier()
        date_info = ""
        if calendrier_data:
            mois_actuel = calendrier_data.get("mois_index", 0)
            annee_actuelle = calendrier_data.get("annee", 2025)
            mois_fin = (mois_actuel + duree_finale) % 12
            annee_fin = annee_actuelle + ((mois_actuel + duree_finale) // 12)
            nom_mois_fin = CALENDRIER_MONTHS[mois_fin] if mois_fin < len(CALENDRIER_MONTHS) else "Mois inconnu"
            
            # Calculer le timestamp réel IRL
            real_timestamp = calculate_real_timestamp_from_calendar(mois_fin, annee_fin)
            discord_timestamp = format_discord_timestamp(real_timestamp)
            
            date_info = f"**Fin RP :** {nom_mois_fin} {annee_fin}\n**Fin IRL :** {discord_timestamp}\n"
        else:
            # Fallback sans calendrier
            discord_timestamp = format_discord_timestamp(fin_timestamp)
            date_info = f"**Date de fin :** {discord_timestamp}\n"
        
        embed = discord.Embed(
            title="✅ Développement confirmé !",
            description=f"**Nom :** {self.nom_developpement}\n"
                       f"**Technologie :** {self.nom_techno}\n"
                       f"**Pays :** {self.role.mention}\n"
                       f"**Centre :** {centre_choisi['localisation']} ({domaine_tech})\n"
                       f"**Durée :** {duree_finale} mois{bonus_text}\n"
                       f"{date_info}"
                       f"**Coût payé :** {format_number(self.cout_dev)} {MONNAIE_EMOJI}\n"
                       f"**Nouveau budget :** {format_number(balances[role_id])} {MONNAIE_EMOJI}",
            color=EMBED_COLOR,
            timestamp=datetime.datetime.now()
        )
        
        await interaction.followup.send(embed=embed)
        
        # Log dans le salon des logs
        log_embed = discord.Embed(
            title="🔬 Développement technologique",
            description=f"**Pays :** {self.role.mention}\n"
                       f"**Nom :** {self.nom_developpement}\n"
                       f"**Technologie :** {self.nom_techno}\n"
                       f"**Centre :** {centre_choisi['localisation']}\n"
                       f"**Durée :** {duree_finale} mois\n"
                       f"**Coût :** {format_number(self.cout_dev)} {MONNAIE_EMOJI}\n"
                       f"**Développé par :** {interaction.user.mention}",
            color=EMBED_COLOR,
            timestamp=datetime.datetime.now()
        )
        
        # Envoyer le log
        await send_log(interaction.guild, embed=log_embed)
        
        # Désactiver tous les boutons de la vue pour éviter les double-clics
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        
        # Mettre à jour le message original avec les boutons désactivés
        try:
            # Essayer de mettre à jour le message original depuis la view
            original_message = getattr(self, 'message', None)
            if original_message:
                await original_message.edit(view=self)
        except:
            # Si ça échoue, ce n'est pas grave
            pass

# === SYSTÈME DE ROLL GÉNÉRAL ===

import random

# Fichier pour stocker les généraux améliorés
GENERAUX_FILE = os.path.join(DATA_DIR, "generaux.json")

def load_generaux():
    """Charge les données des généraux depuis le fichier."""
    if not os.path.exists(GENERAUX_FILE):
        # Créer le fichier avec un dictionnaire vide si il n'existe pas
        try:
            with open(GENERAUX_FILE, "w") as f:
                json.dump({}, f, indent=2)
            print(f"[INFO] Fichier {GENERAUX_FILE} créé.")
        except Exception as e:
            print(f"[ERROR] Erreur lors de la création de {GENERAUX_FILE}: {e}")
        return {}
    try:
        with open(GENERAUX_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement des généraux: {e}")
        return {}

def save_generaux(data):
    """Sauvegarde les données des généraux dans le fichier."""
    try:
        with open(GENERAUX_FILE, "w") as f:
            json.dump(data, f, indent=2)
        save_all_json_to_postgres()
    except Exception as e:
        print(f"[ERROR] Erreur lors de la sauvegarde des généraux: {e}")

def format_stars(current, max_stars=5):
    """Formate les étoiles pour l'affichage (★ remplie, ☆ vide)."""
    filled = "★" * current
    empty = "☆" * (max_stars - current)
    return filled + empty

def get_pays_roll_count(pays):
    """Récupère le nombre de rolls effectués pour un pays (définitif, pas quotidien)."""
    generaux_data = load_generaux()
    pays_key = f"pays_{pays.lower()}"
    
    if pays_key not in generaux_data:
        generaux_data[pays_key] = {"roll_count": 0}
        save_generaux(generaux_data)
    
    return generaux_data[pays_key].get("roll_count", 0)

def increment_pays_roll_count(pays):
    """Incrémente le nombre de rolls d'un pays (définitif)."""
    generaux_data = load_generaux()
    pays_key = f"pays_{pays.lower()}"
    
    if pays_key not in generaux_data:
        generaux_data[pays_key] = {"roll_count": 0}
    
    generaux_data[pays_key]["roll_count"] = generaux_data[pays_key].get("roll_count", 0) + 1
    save_generaux(generaux_data)
    return generaux_data[pays_key]["roll_count"]

def reset_pays_roll_count(pays):
    """Remet à zéro le nombre de rolls d'un pays."""
    generaux_data = load_generaux()
    pays_key = f"pays_{pays.lower()}"
    
    if pays_key in generaux_data:
        generaux_data[pays_key]["roll_count"] = 0
        save_generaux(generaux_data)
        return True
    return False

def decrement_pays_roll_count(pays):
    """Décrémente le nombre de rolls d'un pays (pour récupérer un roll)."""
    generaux_data = load_generaux()
    pays_key = f"pays_{pays.lower()}"
    
    if pays_key not in generaux_data:
        generaux_data[pays_key] = {"roll_count": 0}
    
    current_count = generaux_data[pays_key].get("roll_count", 0)
    if current_count > 0:
        generaux_data[pays_key]["roll_count"] = current_count - 1
        save_generaux(generaux_data)
        return True
    return False

def get_user_roll_count(user_id):
    """Récupère le nombre de rolls effectués par un utilisateur aujourd'hui."""
    generaux_data = load_generaux()
    user_key = str(user_id)
    
    if user_key not in generaux_data:
        generaux_data[user_key] = {"roll_count": 0, "last_roll_date": ""}
    
    # Vérifier si c'est un nouveau jour
    today = datetime.now().strftime("%Y-%m-%d")
    if generaux_data[user_key]["last_roll_date"] != today:
        generaux_data[user_key]["roll_count"] = 0
        generaux_data[user_key]["last_roll_date"] = today
        save_generaux(generaux_data)
    
    return generaux_data[user_key]["roll_count"]

def increment_user_roll_count(user_id):
    """Incrémente le nombre de rolls d'un utilisateur pour aujourd'hui."""
    generaux_data = load_generaux()
    user_key = str(user_id)
    
    if user_key not in generaux_data:
        generaux_data[user_key] = {"roll_count": 0, "last_roll_date": ""}
    
    today = datetime.now().strftime("%Y-%m-%d")
    if generaux_data[user_key]["last_roll_date"] != today:
        generaux_data[user_key]["roll_count"] = 0
        generaux_data[user_key]["last_roll_date"] = today
    
    generaux_data[user_key]["roll_count"] += 1
    save_generaux(generaux_data)
    return generaux_data[user_key]["roll_count"]

# Classes pour la sélection de pays
class CountrySelectionView(discord.ui.View):
    """Vue pour sélectionner un pays parmi les rôles de l'utilisateur."""
    
    def __init__(self, user_id, country_roles, ecole, domaine):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.country_roles = country_roles
        self.ecole = ecole
        self.domaine = domaine
        
        # Créer un sélecteur avec les pays de l'utilisateur (éliminer les doublons)
        unique_countries = {}
        for role in country_roles:
            unique_countries[role.name] = role
        
        options = []
        for country_name in list(unique_countries.keys())[:25]:  # Discord limite à 25 options
            options.append(discord.SelectOption(
                label=country_name,
                value=country_name,
                description=f"Créer un général pour {country_name}"
            ))
        
        select = discord.ui.Select(
            placeholder="Choisissez votre pays...",
            options=options
        )
        select.callback = self.country_selected
        self.add_item(select)
    
    async def country_selected(self, interaction: discord.Interaction):
        """Callback quand un pays est sélectionné."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser cette interaction.", ephemeral=True)
            return
        
        # Récupérer le pays sélectionné
        pays = interaction.data["values"][0]
        
        # Exécuter la logique de roll_general avec le pays sélectionné
        await self.execute_roll_general(interaction, pays)
    
    async def execute_roll_general(self, interaction, pays):
        """Exécute la logique de roll_general avec le pays sélectionné."""
        # Vérifier le nombre de rolls effectués pour ce pays (limite définitive)
        current_rolls = get_pays_roll_count(pays)
        
        if current_rolls >= 3:
            embed = discord.Embed(
                title="❌ Limite de rolls atteinte",
                description=f"Le pays **{pays}** a déjà effectué ses **3 rolls de général** autorisés.",
                color=0xff4444
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Continuer avec la logique de génération du général...
        # (copier le reste de la logique de roll_general ici)
        await self.generate_general(interaction, pays)
    
    async def generate_general(self, interaction, pays):
        """Génère le général avec la logique complète."""
        # Conversion du bonus d'école
        bonus_ecole = int(self.ecole)
        
        # Roll de base (1-100) + bonus d'école, plafonné à 100
        roll_base = random.randint(1, 100)
        roll_final = min(roll_base + bonus_ecole, 100)
        
        # Détermination du type de général selon le roll final
        if roll_final <= 19:
            type_general = "Général médiocre"
            nb_traits_negatifs = 3
            nb_traits_positifs = 1
            nb_specialites = 0
        elif roll_final <= 39:
            type_general = "Général peu expérimenté"
            nb_traits_negatifs = 2
            nb_traits_positifs = 2
            nb_specialites = 0
        elif roll_final <= 59:
            type_general = "Général expérimenté"
            nb_traits_negatifs = 1
            nb_traits_positifs = 2
            nb_specialites = 0
        elif roll_final <= 95:
            type_general = "Grand Général"
            nb_traits_negatifs = 1
            nb_traits_positifs = 3
            nb_specialites = 1
        else:  # 96-100+
            type_general = "Excellent Général"
            nb_traits_negatifs = 0
            nb_traits_positifs = 3
            nb_specialites = 2
        
        # Listes des traits de personnalité (selon le document officiel)
        traits_positifs_base = [
            "Personnalité publique", "Courageux", "Inflexible"
            # "Héros de guerre" retiré - uniquement attribuable par commande admin
        ]
        traits_negatifs_base = [
            "Alcoolique", "Drogué", "Lâche", "Connexion politique", "Vieux jeu", 
            "Paranoïaque", "Colérique"
        ]
        
        # Traits de commandement selon le domaine (basés sur le document officiel)
        traits_commandement = {
            "terrestre": [
                "Planificateur", "Officier de cavalerie", "Officier d'infanterie", "Officier des blindés",
                "Officier du génie", "Officier de reconnaissance", "Officier des opérations spéciales",
                "Conquérant", "Ours polaire", "Montagnard", "Renard du désert", "Renard des marais",
                "Combattant des plaines", "Rat de la jungle", "Éclaireur", "Spécialiste du combat urbain",
                "Major de promotion"
            ],
            "marine": [
                "Créateur de blocus", "Loup de mer", "Observateur", "Protecteur de la flotte",
                "Maître tacticien", "Cœur de fer", "Contrôleur aérien", "Loup des mers glacées",
                "Combattant côtier", "Expert de haute mer", "Expert de basse mer", "Major de promotion"
            ],
            "aerien": [
                "Aigle des cieux", "Protecteur du ciel", "Destructeur méticuleux",
                "Théoricien du support rapproché", "Poséidon"
            ]
        }
        
        # Sélection des traits positifs
        traits_positifs_selectionnes = []
        if nb_traits_positifs > 0:
            # Stratège de génie : 1% de chance de base + 5% supplémentaires si roll > 95
            chance_genie = 1
            if roll_final > 95:
                chance_genie = 5
            
            if random.randint(1, 100) <= chance_genie:
                traits_positifs_selectionnes.append("Stratège de génie")
                nb_traits_positifs -= 1
            
            # Officier de carrière : 25% de chance
            if nb_traits_positifs > 0 and random.randint(1, 100) <= 25:
                traits_positifs_selectionnes.append("Officier de carrière")
                nb_traits_positifs -= 1
            
            # Compléter avec les autres traits positifs
            if nb_traits_positifs > 0:
                traits_restants = random.sample(traits_positifs_base, min(nb_traits_positifs, len(traits_positifs_base)))
                traits_positifs_selectionnes.extend(traits_restants)
        
        # Sélection des traits négatifs
        traits_negatifs_selectionnes = []
        if nb_traits_negatifs > 0:
            # Incompétent : 1% de chance de base + 5% supplémentaires si roll < 16, mais seulement si Stratège de génie n'est pas déjà présent
            if "Stratège de génie" not in traits_positifs_selectionnes:
                chance_incompetent = 1
                if roll_final < 16:
                    chance_incompetent = 5
                
                if random.randint(1, 100) <= chance_incompetent:
                    traits_negatifs_selectionnes.append("Incompétent")
                    nb_traits_negatifs -= 1
            
            # Compléter avec les autres traits négatifs
            if nb_traits_negatifs > 0:
                # Créer une liste des traits négatifs disponibles
                traits_negatifs_disponibles = traits_negatifs_base.copy()
                
                # Vérifier les conflits : si "Courageux" est dans les traits positifs, retirer "Lâche"
                if "Courageux" in traits_positifs_selectionnes and "Lâche" in traits_negatifs_disponibles:
                    traits_negatifs_disponibles.remove("Lâche")
                
                # Vérifier les conflits : si "Stratège de génie" est dans les traits positifs, retirer "Incompétent"
                if "Stratège de génie" in traits_positifs_selectionnes and "Incompétent" in traits_negatifs_disponibles:
                    traits_negatifs_disponibles.remove("Incompétent")
                
                # Sélectionner les traits négatifs sans conflit
                traits_restants = random.sample(traits_negatifs_disponibles, min(nb_traits_negatifs, len(traits_negatifs_disponibles)))
                traits_negatifs_selectionnes.extend(traits_restants)
        
        # Sélection des traits de commandement (spécialisations)
        traits_commandement_selectionnes = []
        if nb_specialites > 0 and self.domaine in traits_commandement:
            traits_commandement_selectionnes = random.sample(
                traits_commandement[self.domaine], 
                min(nb_specialites, len(traits_commandement[self.domaine]))
            )
        
        # Construction de l'embed de résultat
        embed = discord.Embed(
            title="🎲 Général généré - Confirmation requise",
            color=EMBED_COLOR
        )
        
        # Formatage du résultat
        result_text = f"> − **Résultat du Roll :** {roll_final}\n"
        result_text += f"> − **Type de Général tiré :** {type_general}\n"
        
        # Traits positifs
        result_text += "> − **Traits positifs :**\n"
        if traits_positifs_selectionnes:
            result_text += f"> - {', '.join(traits_positifs_selectionnes)}\n"
        else:
            result_text += "> - Aucun\n"
        
        # Traits négatifs
        result_text += "> − **Traits négatifs :**\n"
        if traits_negatifs_selectionnes:
            result_text += f"> - {', '.join(traits_negatifs_selectionnes)}\n"
        else:
            result_text += "> - Aucun\n"
        
        # Traits de commandement
        result_text += "> − **Traits de commandement :**\n"
        if traits_commandement_selectionnes:
            result_text += f"> - {', '.join(traits_commandement_selectionnes)}\n"
        else:
            result_text += "> - Aucun trait de commandement\n"
        
        embed.description = result_text
        embed.set_image(url=IMAGE_URL)
        
        # Informations supplémentaires en footer
        ecole_names = {
            "0": "Petite école",
            "5": "École militaire moyenne", 
            "10": "Grande École militaire",
            "15": "Académie militaire",
            "30": "Complexe Universitaire militaire"
        }
        
        # Incrémenter le compteur de rolls pour le pays
        new_roll_count = increment_pays_roll_count(pays)
        
        embed.set_footer(
            text=f"École: {ecole_names[self.ecole]} | Domaine: {self.domaine.capitalize()} | Roll de base: {roll_base} (+{bonus_ecole}) | Rolls: {new_roll_count}/3 | Pays: {pays}"
        )
        
        # Préparer les données du général pour la confirmation
        general_data = {
            "type": type_general,
            "domaine": self.domaine,
            "ecole": ecole_names[self.ecole],
            "roll_final": roll_final,
            "traits_positifs": traits_positifs_selectionnes,
            "traits_negatifs": traits_negatifs_selectionnes,
            "traits_commandement": traits_commandement_selectionnes
        }
        
        # Créer la vue de confirmation
        view = GeneralConfirmationView(interaction.user.id, pays, general_data)
        
        embed.add_field(
            name="⚠️ Action requise",
            value="Cliquez sur le bouton ci-dessous pour confirmer et nommer votre général.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view)

# Classes pour la promotion en maréchal et l'amélioration des généraux
class PromotionMarshalView(discord.ui.View):
    """Vue pour sélectionner un général à promouvoir en maréchal."""
    
    def __init__(self, user_id, generaux_eligibles, pays=None):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.generaux_eligibles = generaux_eligibles
        self.pays = pays
        
        # Créer un sélecteur avec les généraux éligibles
        options = []
        for general in generaux_eligibles[:25]:  # Discord limite à 25 options
            # Afficher le pays dans la description si on a plusieurs pays
            pays_info = f" - {general.get('pays', 'Pays inconnu')}" if not pays else ""
            options.append(discord.SelectOption(
                label=f"⭐" * general["stars"] + f" {general['nom']}",
                value=f"{general['user_id']}:{general['nom']}",
                description=f"Général {general['stars']}⭐ - Terrestre{pays_info}"
            ))
        
        select = discord.ui.Select(
            placeholder="Choisissez le général à promouvoir...",
            options=options
        )
        select.callback = self.general_selected
        self.add_item(select)
    
    async def general_selected(self, interaction: discord.Interaction):
        """Callback quand un général est sélectionné pour promotion."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser cette interaction.", ephemeral=True)
            return
        
        # Récupérer le général sélectionné
        user_id, nom_general = interaction.data["values"][0].split(":", 1)
        
        # Trouver le général dans la liste
        general_selectionne = None
        for general in self.generaux_eligibles:
            if general["user_id"] == user_id and general["nom"] == nom_general:
                general_selectionne = general
                break
        
        if not general_selectionne:
            await interaction.response.send_message("❌ Erreur lors de la sélection du général.", ephemeral=True)
            return
        
        # Créer la vue de sélection des traits de maréchal
        view = TraitMarshalSelectionView(self.user_id, general_selectionne, self.pays)
        
        embed = discord.Embed(
            title="🎖️ Sélection du trait de maréchal",
            description=f"Sélectionnez le trait de maréchal pour **{nom_general}** :",
            color=EMBED_COLOR
        )
        
        # Vérifier les traits actuels pour les prérequis et exclusions
        traits_actuels = general_selectionne["info"].get("traits_positifs", []) + general_selectionne["info"].get("traits_commandement", [])
        traits_disponibles = []
        
        for trait_nom, trait_info in TRAITS_MARECHAUX.items():
            # Vérifier les prérequis
            peut_avoir = True
            if trait_info["prerequis"]:
                peut_avoir = any(prereq.lower() in [t.lower() for t in traits_actuels] for prereq in trait_info["prerequis"])
            
            if peut_avoir:
                traits_disponibles.append(f"**{trait_nom}**\n{trait_info['description']}")
        
        if traits_disponibles:
            embed.add_field(
                name="Traits de maréchal disponibles",
                value="\n\n".join(traits_disponibles[:5]),  # Limiter pour éviter les embeds trop longs
                inline=False
            )
        
        embed.add_field(
            name="ℹ️ Promotion",
            value=f"• Général : **{nom_general}** ({general_selectionne['stars']}⭐)\n"
                  f"• Pays : **{self.pays}**\n"
                  f"• Domaine : Terrestre",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class TraitMarshalSelectionView(discord.ui.View):
    """Vue pour sélectionner le trait de maréchal à attribuer."""
    
    def __init__(self, user_id, general_data, pays):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.general_data = general_data
        self.pays = pays
        
        # Créer un sélecteur avec les traits de maréchal disponibles
        traits_actuels = general_data["info"].get("traits_positifs", []) + general_data["info"].get("traits_commandement", [])
        
        options = []
        for trait_nom, trait_info in TRAITS_MARECHAUX.items():
            # Vérifier les prérequis
            peut_avoir = True
            if trait_info["prerequis"]:
                peut_avoir = any(prereq.lower() in [t.lower() for t in traits_actuels] for prereq in trait_info["prerequis"])
            
            if peut_avoir:
                description = trait_info["description"][:100]  # Limiter la description
                if trait_info.get("rare"):
                    description = f"🔥 {description}"
                
                options.append(discord.SelectOption(
                    label=trait_nom,
                    value=trait_nom,
                    description=description
                ))
        
        if options:
            select = discord.ui.Select(
                placeholder="Choisissez le trait de maréchal...",
                options=options[:25]  # Discord limite à 25 options
            )
            select.callback = self.trait_selected
            self.add_item(select)
    
    async def trait_selected(self, interaction: discord.Interaction):
        """Callback quand un trait de maréchal est sélectionné."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser cette interaction.", ephemeral=True)
            return
        
        trait_selectionne = interaction.data["values"][0]
        
        # Effectuer la promotion
        generaux_data = load_generaux()
        user_id = self.general_data["user_id"]
        nom_general = self.general_data["nom"]
        
        if user_id in generaux_data and "generaux" in generaux_data[user_id]:
            if nom_general in generaux_data[user_id]["generaux"]:
                # Marquer comme maréchal
                generaux_data[user_id]["generaux"][nom_general]["est_marechal"] = True
                generaux_data[user_id]["generaux"][nom_general]["trait_marechal"] = trait_selectionne
                
                # Réduire les traits de général au minimum (garder seulement les traits de personnalité)
                traits_personnalite = generaux_data[user_id]["generaux"][nom_general].get("traits_positifs", [])
                generaux_data[user_id]["generaux"][nom_general]["traits_commandement_reduits"] = generaux_data[user_id]["generaux"][nom_general].get("traits_commandement", [])
                generaux_data[user_id]["generaux"][nom_general]["traits_commandement"] = []
                
                # Sauvegarder
                save_generaux(generaux_data)
                
                embed = discord.Embed(
                    title="🎖️ Promotion réussie !",
                    description=f"**{nom_general}** a été promu **Maréchal** !",
                    color=0x00ff88
                )
                
                embed.add_field(
                    name="Nouveau statut",
                    value=f"• **Rang :** Maréchal\n"
                          f"• **Trait de maréchal :** {trait_selectionne}\n"
                          f"• **Pays :** {self.pays}",
                    inline=False
                )
                
                embed.add_field(
                    name="Effet de la promotion",
                    value="• Les traits de général sont réduits au minimum\n"
                          "• Le trait de maréchal s'applique à toute l'armée/théâtre\n"
                          "• Commandement étendu sur les opérations militaires",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("❌ Général non trouvé.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Erreur lors de la promotion.", ephemeral=True)

class AmeliorationGeneralView(discord.ui.View):
    """Vue pour sélectionner un général à améliorer."""
    
    def __init__(self, user_id, generaux_ameliorables, pays):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.generaux_ameliorables = generaux_ameliorables
        self.pays = pays
        
        # Créer un sélecteur avec les généraux améliorables
        options = []
        for general in generaux_ameliorables[:25]:  # Discord limite à 25 options
            nb_ameliorations = len(general["traits_ameliorables"])
            options.append(discord.SelectOption(
                label=f"⭐" * general["stars"] + f" {general['nom']}",
                value=f"{general['user_id']}:{general['nom']}",
                description=f"{nb_ameliorations} améliorations possibles"
            ))
        
        select = discord.ui.Select(
            placeholder="Choisissez le général à améliorer...",
            options=options
        )
        select.callback = self.general_selected
        self.add_item(select)
    
    async def general_selected(self, interaction: discord.Interaction):
        """Callback quand un général est sélectionné pour amélioration."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser cette interaction.", ephemeral=True)
            return
        
        # Récupérer le général sélectionné
        user_id, nom_general = interaction.data["values"][0].split(":", 1)
        
        # Trouver le général dans la liste
        general_selectionne = None
        for general in self.generaux_ameliorables:
            if general["user_id"] == user_id and general["nom"] == nom_general:
                general_selectionne = general
                break
        
        if not general_selectionne:
            await interaction.response.send_message("❌ Erreur lors de la sélection du général.", ephemeral=True)
            return
        
        # Créer la vue de sélection des traits à améliorer
        view = TraitAmeliorationSelectionView(self.user_id, general_selectionne, self.pays)
        
        embed = discord.Embed(
            title="⚡ Sélection de l'amélioration",
            description=f"Sélectionnez le trait à améliorer pour **{nom_general}** :",
            color=EMBED_COLOR
        )
        
        # Afficher les améliorations disponibles
        ameliorations_list = []
        for trait in general_selectionne["traits_ameliorables"][:5]:  # Limiter l'affichage
            trait_info = TRAITS_AMELIORATION[trait]
            ameliorations_list.append(f"**{trait}**\n{trait_info['description']}")
        
        if ameliorations_list:
            embed.add_field(
                name="Améliorations disponibles",
                value="\n\n".join(ameliorations_list),
                inline=False
            )
        
        embed.add_field(
            name="ℹ️ Général",
            value=f"• Nom : **{nom_general}** ({general_selectionne['stars']}⭐)\n"
                  f"• Pays : **{self.pays}**\n"
                  f"• Traits actuels : {len(general_selectionne['info'].get('traits_commandement', []))}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class TraitAmeliorationSelectionView(discord.ui.View):
    """Vue pour sélectionner le trait à améliorer."""
    
    def __init__(self, user_id, general_data, pays):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.general_data = general_data
        self.pays = pays
        
        # Créer un sélecteur avec les traits améliorables
        options = []
        for trait in general_data["traits_ameliorables"]:
            trait_info = TRAITS_AMELIORATION[trait]
            description = trait_info["description"][:100]  # Limiter la description
            if trait_info.get("rare"):
                description = f"🔥 {description}"
            
            options.append(discord.SelectOption(
                label=trait,
                value=trait,
                description=description
            ))
        
        if options:
            select = discord.ui.Select(
                placeholder="Choisissez l'amélioration...",
                options=options[:25]  # Discord limite à 25 options
            )
            select.callback = self.trait_selected
            self.add_item(select)
    
    async def trait_selected(self, interaction: discord.Interaction):
        """Callback quand un trait d'amélioration est sélectionné."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser cette interaction.", ephemeral=True)
            return
        
        trait_selectionne = interaction.data["values"][0]
        trait_info = TRAITS_AMELIORATION[trait_selectionne]
        
        # Effectuer l'amélioration
        generaux_data = load_generaux()
        user_id = self.general_data["user_id"]
        nom_general = self.general_data["nom"]
        
        if user_id in generaux_data and "generaux" in generaux_data[user_id]:
            if nom_general in generaux_data[user_id]["generaux"]:
                # Ajouter le trait amélioré
                if "traits_commandement" not in generaux_data[user_id]["generaux"][nom_general]:
                    generaux_data[user_id]["generaux"][nom_general]["traits_commandement"] = []
                
                generaux_data[user_id]["generaux"][nom_general]["traits_commandement"].append(trait_selectionne)
                
                # Retirer le trait de base s'il est remplacé
                traits_prerequis = trait_info["prerequis"]
                traits_actuels = generaux_data[user_id]["generaux"][nom_general]["traits_commandement"]
                
                for prereq in traits_prerequis:
                    if prereq in traits_actuels:
                        traits_actuels.remove(prereq)
                        break
                
                # Sauvegarder
                save_generaux(generaux_data)
                
                embed = discord.Embed(
                    title="⚡ Amélioration réussie !",
                    description=f"Le trait **{trait_selectionne}** a été ajouté à **{nom_general}** !",
                    color=0x00ff88
                )
                
                embed.add_field(
                    name="Nouveau trait",
                    value=f"• **{trait_selectionne}**\n{trait_info['description']}",
                    inline=False
                )
                
                embed.add_field(
                    name="Effet de l'amélioration",
                    value="• Le trait de base a été remplacé par sa version améliorée\n"
                          "• Les bonus sont maintenant plus importants\n"
                          "• Cette amélioration est permanente",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("❌ Général non trouvé.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Erreur lors de l'amélioration.", ephemeral=True)

# Classes pour la confirmation du général avec nom
class GeneralConfirmationView(discord.ui.View):
    """Vue pour confirmer la création d'un général avec attribution d'un nom."""
    
    def __init__(self, user_id, pays, general_data):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.pays = pays
        self.general_data = general_data
    
    @discord.ui.button(label="Confirmer et nommer le général", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm_general(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser cette interaction.", ephemeral=True)
            return
            
        # Afficher le modal pour nommer le général
        modal = GeneralNamingModal(self.pays, self.general_data)
        await interaction.response.send_modal(modal)

class GeneralNamingModal(discord.ui.Modal):
    """Modal pour nommer un général après confirmation."""
    
    def __init__(self, pays, general_data):
        super().__init__(title=f"Nommer le général")
        self.pays = pays
        self.general_data = general_data
        
        self.nom_general = discord.ui.TextInput(
            label="Nom du Général",
            placeholder="Entrez le nom de votre général...",
            max_length=50,
            required=True
        )
        
        self.add_item(self.nom_general)
    
    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        nom_general = self.nom_general.value
        pays_key = self.pays.lower()
        
        # Charger les données des généraux
        generaux_data = load_generaux()
        
        # Initialiser les données utilisateur si nécessaire
        if user_id not in generaux_data:
            generaux_data[user_id] = {"generaux": {}}
        
        if "generaux" not in generaux_data[user_id]:
            generaux_data[user_id]["generaux"] = {}
        
        # Vérifier si le nom n'existe pas déjà
        if nom_general in generaux_data[user_id]["generaux"]:
            embed = discord.Embed(
                title="❌ Nom déjà utilisé",
                description=f"Vous avez déjà un général nommé **{nom_general}**. Choisissez un autre nom.",
                color=0xff4444
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Calculer les étoiles initiales selon les traits
        initial_stars = 1  # Par défaut 1 étoile
        
        # Vérifier les traits spéciaux
        if "Stratège de génie" in self.general_data["traits_positifs"]:
            initial_stars = 3
        elif "Incompétent" in self.general_data["traits_negatifs"]:
            initial_stars = 0
        
        # Créer le général avec toutes ses données
        general_info = {
            "stars": initial_stars,
            "pays": self.pays,
            "type": self.general_data["type"],
            "domaine": self.general_data["domaine"],
            "ecole": self.general_data["ecole"],
            "roll_final": self.general_data["roll_final"],
            "traits_positifs": self.general_data["traits_positifs"],
            "traits_negatifs": self.general_data["traits_negatifs"],
            "traits_commandement": self.general_data["traits_commandement"],
            "experience": 0
        }
        
        generaux_data[user_id]["generaux"][nom_general] = general_info
        save_generaux(generaux_data)
        
        # Créer l'embed de confirmation
        embed = discord.Embed(
            title="✅ Général créé avec succès !",
            description=f"**{nom_general}** a été ajouté à votre armée de **{self.pays}** !",
            color=0x00ff88
        )
        
        # Ajouter les détails du général
        embed.add_field(
            name="📊 Informations",
            value=f"**Type :** {self.general_data['type']}\n"
                  f"**Domaine :** {self.general_data['domaine'].capitalize()}\n"
                  f"**Roll :** {self.general_data['roll_final']}\n"
                  f"**Étoiles :** {format_stars(initial_stars)}",
            inline=True
        )
        
        traits_text = ""
        if self.general_data["traits_positifs"]:
            traits_text += f"**Positifs :** {', '.join(self.general_data['traits_positifs'])}\n"
        if self.general_data["traits_negatifs"]:
            traits_text += f"**Négatifs :** {', '.join(self.general_data['traits_negatifs'])}\n"
        if self.general_data["traits_commandement"]:
            traits_text += f"**Commandement :** {', '.join(self.general_data['traits_commandement'])}"
        
        if traits_text:
            embed.add_field(
                name="🎯 Traits",
                value=traits_text,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roll_general", description="Génère un général aléatoire avec traits et spécialités")
@app_commands.describe(
    ecole="École militaire du général (influence le bonus de base)",
    domaine="Domaine de spécialisation du général"
)
@app_commands.choices(ecole=[
    discord.app_commands.Choice(name="Petite école (+0)", value="0"),
    discord.app_commands.Choice(name="École militaire moyenne (+5)", value="5"),
    discord.app_commands.Choice(name="Grande École militaire (+10)", value="10"),
    discord.app_commands.Choice(name="Académie militaire (+15)", value="15"),
    discord.app_commands.Choice(name="Complexe Universitaire militaire (+30)", value="30")
])
@app_commands.choices(domaine=[
    discord.app_commands.Choice(name="Terrestre", value="terrestre"),
    discord.app_commands.Choice(name="Aérien", value="aerien"),
    discord.app_commands.Choice(name="Marine", value="marine")
])
async def roll_general(interaction: discord.Interaction, ecole: str, domaine: str):
    """Génère un général aléatoire avec traits et spécialités selon le domaine."""
    
    # Fonction pour vérifier si un rôle est un rôle de pays
    def is_country_role(role):
        """Vérifie si un rôle est un rôle de pays en regardant s'il a de l'argent dans le système économique."""
        role_id = str(role.id)
        # Un rôle est considéré comme un pays s'il existe dans le système de balances
        # ou s'il existe dans pays_images (rôles pays créés)
        if role_id in balances:
            return True
        
        # Vérifier aussi dans pays_images pour les rôles pays récemment créés
        pays_images_data = load_pays_images()
        return role_id in pays_images_data
    
    # Obtenir les rôles de pays de l'utilisateur
    user_country_roles = []
    
    for role in interaction.user.roles:
        if is_country_role(role):
            user_country_roles.append(role)
    
    # Si l'utilisateur n'a aucun rôle de pays
    if not user_country_roles:
        embed = discord.Embed(
            title="❌ Aucun rôle de pays",
            description="Vous n'avez aucun rôle de pays. Contactez un administrateur pour obtenir un rôle de pays.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Si l'utilisateur a plusieurs rôles de pays, créer un sélecteur
    if len(user_country_roles) > 1:
        embed = discord.Embed(
            title="🏛️ Sélection du pays",
            description="Vous avez plusieurs rôles de pays. Sélectionnez le pays pour lequel vous voulez créer un général :",
            color=EMBED_COLOR
        )
        
        view = CountrySelectionView(interaction.user.id, user_country_roles, ecole, domaine)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        return
    
    # Si l'utilisateur a un seul rôle de pays, l'utiliser directement
    pays = user_country_roles[0].name
    
    # Créer une instance de la vue et exécuter la génération directement
    country_view = CountrySelectionView(interaction.user.id, user_country_roles, ecole, domaine)
    await country_view.execute_roll_general(interaction, pays)
    return  # Arrêter ici pour éviter la duplication
    
    # Vérifier le nombre de rolls effectués pour ce pays (limite définitive)
    current_rolls = get_pays_roll_count(pays)
    
    if current_rolls >= 3:
        embed = discord.Embed(
            title="❌ Limite de rolls atteinte",
            description=f"Le pays **{pays}** a déjà effectué ses **3 rolls de général** autorisés.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
# === COMMANDE DE TEST POUR LES GÉNÉRAUX ===

@bot.tree.command(name="roll_general_test", description="Version de test pour générer des généraux (sans limite de rolls)")
@app_commands.describe(
    ecole="École militaire du général (influence le bonus de base)",
    domaine="Domaine de spécialisation du général"
)
@app_commands.choices(ecole=[
    discord.app_commands.Choice(name="Petite école (+0)", value="0"),
    discord.app_commands.Choice(name="École militaire moyenne (+5)", value="5"),
    discord.app_commands.Choice(name="Grande École militaire (+10)", value="10"),
    discord.app_commands.Choice(name="Académie militaire (+15)", value="15"),
    discord.app_commands.Choice(name="Complexe Universitaire militaire (+30)", value="30")
])
@app_commands.choices(domaine=[
    discord.app_commands.Choice(name="Terrestre", value="terrestre"),
    discord.app_commands.Choice(name="Aérien", value="aerien"),
    discord.app_commands.Choice(name="Marine", value="marine")
])
async def roll_general_test(interaction: discord.Interaction, ecole: str, domaine: str):
    """Version de test de la génération de général (sans limite de rolls)."""
    
    # Conversion du bonus d'école
    bonus_ecole = int(ecole)
    
    # Roll de base (1-100) + bonus d'école, plafonné à 100
    roll_base = random.randint(1, 100)
    roll_final = min(roll_base + bonus_ecole, 100)
    
    # Détermination du type de général selon le roll final
    if roll_final <= 19:
        type_general = "Général médiocre"
        nb_traits_negatifs = 3
        nb_traits_positifs = 1
        nb_specialites = 0
    elif roll_final <= 39:
        type_general = "Général peu expérimenté"
        nb_traits_negatifs = 2
        nb_traits_positifs = 2
        nb_specialites = 0
    elif roll_final <= 59:
        type_general = "Général expérimenté"
        nb_traits_negatifs = 1
        nb_traits_positifs = 2
        nb_specialites = 0
    elif roll_final <= 95:
        type_general = "Grand Général"
        nb_traits_negatifs = 1
        nb_traits_positifs = 3
        nb_specialites = 1
    else:  # 96-100+
        type_general = "Excellent Général"
        nb_traits_negatifs = 0
        nb_traits_positifs = 3
        nb_specialites = 2
    
    # NOUVEAUX TRAITS (selon le document officiel)
    # Traits de personnalité
    traits_positifs_base = [
        "Personnalité publique", "Courageux", "Inflexible"
        # "Héros de guerre" retiré - uniquement attribuable par commande admin
    ]
    traits_negatifs_base = [
        "Alcoolique", "Drogué", "Lâche", "Connexion politique", "Vieux jeu", 
        "Paranoïaque", "Colérique"
    ]
    
    # Traits de commandement selon le domaine
    traits_commandement = {
        "terrestre": [
            "Planificateur", "Officier de cavalerie", "Officier d'infanterie", "Officier des blindés",
            "Officier du génie", "Officier de reconnaissance", "Officier des opérations spéciales",
            "Conquérant", "Ours polaire", "Montagnard", "Renard du désert", "Renard des marais",
            "Combattant des plaines", "Rat de la jungle", "Éclaireur", "Spécialiste du combat urbain",
            "Major de promotion"
        ],
        "marine": [
            "Créateur de blocus", "Loup de mer", "Observateur", "Protecteur de la flotte",
            "Maître tacticien", "Cœur de fer", "Contrôleur aérien", "Loup des mers glacées",
            "Combattant côtier", "Expert de haute mer", "Expert de basse mer", "Major de promotion"
        ],
        "aerien": [
            "Aigle des cieux", "Protecteur du ciel", "Destructeur méticuleux",
            "Théoricien du support rapproché", "Poséidon"
        ]
    }
    
    # Sélection des traits positifs
    traits_positifs_selectionnes = []
    if nb_traits_positifs > 0:
        # Stratège de génie : 1% de chance de base + 5% supplémentaires si roll > 95
        chance_genie = 1
        if roll_final > 95:
            chance_genie = 5
        
        if random.randint(1, 100) <= chance_genie:
            traits_positifs_selectionnes.append("Stratège de génie")
            nb_traits_positifs -= 1
        
        # Officier de carrière : 25% de chance
        if nb_traits_positifs > 0 and random.randint(1, 100) <= 25:
            traits_positifs_selectionnes.append("Officier de carrière")
            nb_traits_positifs -= 1
        
        # Compléter avec les autres traits positifs
        if nb_traits_positifs > 0:
            traits_restants = random.sample(traits_positifs_base, min(nb_traits_positifs, len(traits_positifs_base)))
            traits_positifs_selectionnes.extend(traits_restants)
    
    # Sélection des traits négatifs
    traits_negatifs_selectionnes = []
    if nb_traits_negatifs > 0:
        # Incompétent : 1% de chance de base + 5% supplémentaires si roll < 16, mais seulement si Stratège de génie n'est pas déjà présent
        if "Stratège de génie" not in traits_positifs_selectionnes:
            chance_incompetent = 1
            if roll_final < 16:
                chance_incompetent = 5
            
            if random.randint(1, 100) <= chance_incompetent:
                traits_negatifs_selectionnes.append("Incompétent")
                nb_traits_negatifs -= 1
        
        # Compléter avec les autres traits négatifs
        if nb_traits_negatifs > 0:
            # Créer une liste des traits négatifs disponibles
            traits_negatifs_disponibles = traits_negatifs_base.copy()
            
            # Vérifier les conflits : si "Courage" est dans les traits positifs, retirer "Lâche"
            if "Courage" in traits_positifs_selectionnes and "Lâche" in traits_negatifs_disponibles:
                traits_negatifs_disponibles.remove("Lâche")
            
            # Vérifier les conflits : si "Stratège de génie" est dans les traits positifs, retirer "Incompétent"
            if "Stratège de génie" in traits_positifs_selectionnes and "Incompétent" in traits_negatifs_disponibles:
                traits_negatifs_disponibles.remove("Incompétent")
            
            # Sélectionner les traits négatifs sans conflit
            traits_restants = random.sample(traits_negatifs_disponibles, min(nb_traits_negatifs, len(traits_negatifs_disponibles)))
            traits_negatifs_selectionnes.extend(traits_restants)
    
    # Sélection des traits de commandement (spécialisations)
    traits_commandement_selectionnes = []
    if nb_specialites > 0 and domaine in traits_commandement:
        traits_commandement_selectionnes = random.sample(
            traits_commandement[domaine], 
            min(nb_specialites, len(traits_commandement[domaine]))
        )
    
    # Construction de l'embed de résultat
    embed = discord.Embed(
        title="🎲 Génération du Général (TEST)",
        color=EMBED_COLOR
    )
    
    # Formatage du résultat
    result_text = f"> − **Résultat du Roll :** {roll_final}\n"
    result_text += f"> − **Type de Général tiré :** {type_general}\n"
    
    # Traits positifs
    result_text += "> − **Traits positifs :**\n"
    if traits_positifs_selectionnes:
        result_text += f"> - {', '.join(traits_positifs_selectionnes)}\n"
    else:
        result_text += "> - Aucun\n"
    
    # Traits négatifs
    result_text += "> − **Traits négatifs :**\n"
    if traits_negatifs_selectionnes:
        result_text += f"> - {', '.join(traits_negatifs_selectionnes)}\n"
    else:
        result_text += "> - Aucun\n"
    
    # Traits de commandement
    result_text += "> − **Traits de commandement :**\n"
    if traits_commandement_selectionnes:
        result_text += f"> - {', '.join(traits_commandement_selectionnes)}\n"
    else:
        result_text += "> - Aucun trait de commandement\n"
    
    embed.description = result_text
    embed.set_image(url=IMAGE_URL)
    
    # Informations supplémentaires en footer
    ecole_names = {
        "0": "Petite école",
        "5": "École militaire moyenne", 
        "10": "Grande École militaire",
        "15": "Académie militaire",
        "30": "Complexe Universitaire militaire"
    }
    
    embed.set_footer(
        text=f"École: {ecole_names[ecole]} | Domaine: {domaine.capitalize()} | Roll de base: {roll_base} (+{bonus_ecole}) | MODE TEST"
    )
    
    await interaction.response.send_message(embed=embed)

# === NOUVELLE COMMANDE MES GÉNÉRAUX ===

@bot.tree.command(name="mes_generaux", description="Affiche vos généraux par domaine avec menu de sélection")
async def mes_generaux(interaction: discord.Interaction):
    """Affiche vos généraux organisés par domaine (terrestre, aérien, maritime)."""
    
    user_id = str(interaction.user.id)
    generaux_data = load_generaux()
    
    # Vérifier si l'utilisateur a un rôle de pays
    def get_user_country_role(user):
        """Retourne le rôle de pays de l'utilisateur."""
        pays_images_data = load_pays_images()
        
        for role in user.roles:
            role_id = str(role.id)
            # Un rôle est considéré comme un pays s'il existe dans le système de balances
            # ou s'il existe dans pays_images (rôles pays créés)
            if role_id in balances or role_id in pays_images_data:
                return role
        return None
    
    user_country_role = get_user_country_role(interaction.user)
    if not user_country_role:
        embed = discord.Embed(
            title="❌ Aucun pays détecté",
            description="Vous devez avoir un rôle de pays pour utiliser cette commande.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    user_country = user_country_role.name.lower()
    
    # Vérifier si l'utilisateur a des généraux de son pays
    user_generaux = []
    if user_id in generaux_data and "generaux" in generaux_data[user_id]:
        for nom, data in generaux_data[user_id]["generaux"].items():
            # Vérifier que le général appartient au pays de l'utilisateur
            if data.get("pays", "").lower() == user_country:
                user_generaux.append({
                    "nom": nom,
                    "data": data,
                    "domaine": data.get("domaine", "").lower()
                })
    
    if not user_generaux:
        embed = discord.Embed(
            title="📋 Vos Généraux",
            description=f"Vous n'avez encore aucun général pour **{user_country_role.name}**.\n\n"
                       "Utilisez `/roll_general` pour créer des généraux !",
            color=EMBED_COLOR
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Organiser les généraux par domaine
    generaux_par_domaine = {
        "terrestre": [],
        "aérien": [],
        "maritime": []
    }
    
    for general in user_generaux:
        domaine = general["domaine"]
        if domaine in generaux_par_domaine:
            generaux_par_domaine[domaine].append(general)
    
    # Créer l'embed principal
    embed = discord.Embed(
        title=f"🏛️ Vos Généraux - {user_country_role.name}",
        description="Choisissez un domaine pour voir vos généraux :",
        color=EMBED_COLOR
    )
    
    # Ajouter un résumé par domaine
    for domaine, generaux in generaux_par_domaine.items():
        if generaux:
            total_stars = sum(g["data"].get("stars", 0) for g in generaux)
            emoji = {"terrestre": "🏔️", "aérien": "✈️", "maritime": "🌊"}[domaine]
            embed.add_field(
                name=f"{emoji} {domaine.capitalize()}",
                value=f"{len(generaux)} généraux • {total_stars} étoiles",
                inline=True
            )
    
    # Créer la vue avec les boutons de domaine
    view = MesGenerauxView(generaux_par_domaine, user_id, user_country_role.name)
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class MesGenerauxView(discord.ui.View):
    """Vue pour afficher les généraux par domaine."""
    
    def __init__(self, generaux_par_domaine, user_id, pays_name):
        super().__init__(timeout=300)
        self.generaux_par_domaine = generaux_par_domaine
        self.user_id = user_id
        self.pays_name = pays_name
        
        # Ajouter les boutons pour chaque domaine qui a des généraux
        domaines_info = {
            "terrestre": {"emoji": "🏔️", "style": discord.ButtonStyle.primary},
            "aérien": {"emoji": "✈️", "style": discord.ButtonStyle.secondary},
            "maritime": {"emoji": "🌊", "style": discord.ButtonStyle.success}
        }
        
        for domaine, info in domaines_info.items():
            if self.generaux_par_domaine[domaine]:  # Seulement si on a des généraux dans ce domaine
                count = len(self.generaux_par_domaine[domaine])
                button = discord.ui.Button(
                    label=f"{domaine.capitalize()} ({count})",
                    emoji=info["emoji"],
                    style=info["style"],
                    custom_id=f"domaine_{domaine}"
                )
                button.callback = self.create_domaine_callback(domaine)
                self.add_item(button)
    
    def create_domaine_callback(self, domaine):
        """Crée le callback pour un bouton de domaine."""
        async def domaine_callback(interaction: discord.Interaction):
            generaux = self.generaux_par_domaine[domaine]
            
            if not generaux:
                embed = discord.Embed(
                    title=f"❌ Aucun général {domaine}",
                    description=f"Vous n'avez aucun général dans le domaine {domaine}.",
                    color=0xff4444
                )
                await interaction.response.edit_message(embed=embed, view=self)
                return
            
            # Créer l'embed pour le domaine sélectionné
            emoji = {"terrestre": "🏔️", "aérien": "✈️", "maritime": "🌊"}[domaine]
            embed = discord.Embed(
                title=f"{emoji} Généraux {domaine.capitalize()} - {self.pays_name}",
                description="Sélectionnez un général pour voir ses détails :",
                color=EMBED_COLOR
            )
            
            # Créer la vue avec le menu déroulant pour ce domaine
            view = GenerauxDomaineView(generaux, self.user_id, self.pays_name, domaine, self)
            
            await interaction.response.edit_message(embed=embed, view=view)
        
        return domaine_callback

class GenerauxDomaineView(discord.ui.View):
    """Vue pour sélectionner un général dans un domaine spécifique."""
    
    def __init__(self, generaux, user_id, pays_name, domaine, parent_view):
        super().__init__(timeout=300)
        self.generaux = generaux
        self.user_id = user_id
        self.pays_name = pays_name
        self.domaine = domaine
        self.parent_view = parent_view
        
        # Créer le menu déroulant avec les généraux du domaine
        options = []
        for i, general in enumerate(generaux[:25]):  # Limite Discord
            stars_display = format_stars(general["data"].get("stars", 0))
            type_general = general["data"].get("type", "Général")
            options.append(discord.SelectOption(
                label=f"{general['nom']} ({stars_display})",
                value=str(i),
                description=f"{type_general} • {self.pays_name}"
            ))
        
        select = discord.ui.Select(
            placeholder="Choisissez un général pour voir ses détails...",
            options=options
        )
        select.callback = self.general_selected_callback
        self.add_item(select)
        
        # Bouton de retour
        back_button = discord.ui.Button(
            label="Retour",
            emoji="↩️",
            style=discord.ButtonStyle.gray
        )
        back_button.callback = self.back_callback
        self.add_item(back_button)
    
    async def general_selected_callback(self, interaction: discord.Interaction):
        selected_index = int(interaction.data["values"][0])
        selected_general = self.generaux[selected_index]
        
        # Créer l'embed détaillé du général
        embed = discord.Embed(
            title=f"👨‍💼 {selected_general['nom']}",
            color=EMBED_COLOR
        )
        
        # Informations de base
        data = selected_general["data"]
        stars_display = format_stars(data.get("stars", 0))
        embed.add_field(
            name="📋 Informations de base",
            value=f"**Pays :** {self.pays_name}\n"
                  f"**Domaine :** {self.domaine.capitalize()}\n"
                  f"**Type :** {data.get('type', 'Général')}\n"
                  f"**Étoiles :** {stars_display}",
            inline=False
        )
        
        # Traits
        traits_sections = []
        
        # Traits positifs
        if "traits_positifs" in data and data["traits_positifs"]:
            traits_sections.append(f"**✨ Traits positifs :**\n• " + "\n• ".join(data["traits_positifs"]))
        
        # Traits négatifs
        if "traits_negatifs" in data and data["traits_negatifs"]:
            traits_sections.append(f"**💀 Traits négatifs :**\n• " + "\n• ".join(data["traits_negatifs"]))
        
        # Traits de commandement
        if "traits_commandement" in data and data["traits_commandement"]:
            traits_sections.append(f"**⚔️ Traits de commandement :**\n• " + "\n• ".join(data["traits_commandement"]))
        
        # Traits d'amélioration
        if "traits_amelioration" in data and data["traits_amelioration"]:
            traits_sections.append(f"**🔧 Traits d'amélioration :**\n• " + "\n• ".join(data["traits_amelioration"]))
        
        # Traits de maréchal
        if "traits_marechaux" in data and data["traits_marechaux"]:
            traits_sections.append(f"**👑 Traits de maréchal :**\n• " + "\n• ".join(data["traits_marechaux"]))
        
        if traits_sections:
            embed.add_field(
                name="🎯 Traits",
                value="\n\n".join(traits_sections),
                inline=False
            )
        else:
            embed.add_field(
                name="🎯 Traits",
                value="Aucun trait particulier",
                inline=False
            )
        
        # Expérience (si disponible)
        if "experience" in data:
            experience = data["experience"]
            embed.add_field(
                name="💪 Expérience",
                value=f"{experience}% vers la prochaine étoile",
                inline=True
            )
        
        # Statistiques spéciales (si disponibles)
        stats_info = []
        if "bonus_ecole" in data:
            stats_info.append(f"**École :** +{data['bonus_ecole']}")
        if "roll_final" in data:
            stats_info.append(f"**Roll final :** {data['roll_final']}")
        
        if stats_info:
            embed.add_field(
                name="📊 Statistiques",
                value="\n".join(stats_info),
                inline=True
            )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def back_callback(self, interaction: discord.Interaction):
        # Retourner à la vue principale
        embed = discord.Embed(
            title=f"🏛️ Vos Généraux - {self.pays_name}",
            description="Choisissez un domaine pour voir vos généraux :",
            color=EMBED_COLOR
        )
        
        # Ajouter un résumé par domaine
        for domaine, generaux in self.parent_view.generaux_par_domaine.items():
            if generaux:
                total_stars = sum(g["data"].get("stars", 0) for g in generaux)
                emoji = {"terrestre": "🏔️", "aérien": "✈️", "maritime": "🌊"}[domaine]
                embed.add_field(
                    name=f"{emoji} {domaine.capitalize()}",
                    value=f"{len(generaux)} généraux • {total_stars} étoiles",
                    inline=True
                )
        
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

# === COMMANDES ADMIN POUR LES GÉNÉRAUX ===

@bot.tree.command(name="trait", description="[ADMIN] Gérer les traits d'un général")
@app_commands.describe(
    pays="Rôle du pays"
)
async def manage_trait(interaction: discord.Interaction, pays: discord.Role):
    """Permet aux admins de gérer les traits d'un général d'un pays."""
    
    # Vérifier les permissions admin
    if not interaction.user.guild_permissions.administrator and interaction.user.id not in ADMIN_IDS:
        embed = discord.Embed(
            title="❌ Permission refusée",
            description="Cette commande est réservée aux administrateurs.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Vérifier que le rôle est bien un rôle de pays
    def is_country_role(role):
        """Vérifie si un rôle est un rôle de pays en regardant s'il a de l'argent dans le système économique."""
        role_id = str(role.id)
        # Un rôle est considéré comme un pays s'il existe dans le système de balances
        # ou s'il existe dans pays_images (rôles pays créés)
        if role_id in balances:
            return True
        
        # Vérifier aussi dans pays_images pour les rôles pays récemment créés
        pays_images_data = load_pays_images()
        return role_id in pays_images_data
    
    if not is_country_role(pays):
        embed = discord.Embed(
            title="❌ Rôle invalide",
            description=f"Le rôle **{pays.name}** n'est pas reconnu comme un rôle de pays.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Charger tous les généraux pour trouver ceux du pays
    generaux_data = load_generaux()
    pays_name = pays.name.lower()
    
    # Trouver tous les généraux du pays spécifié
    generaux_pays = []
    for user_id, user_data in generaux_data.items():
        if "generaux" in user_data:
            for nom_general, general_info in user_data["generaux"].items():
                if general_info.get("pays", "").lower() == pays_name:
                    generaux_pays.append({
                        "user_id": user_id,
                        "nom": nom_general,
                        "stars": general_info.get("stars", 0),
                        "info": general_info
                    })
    
    if not generaux_pays:
        embed = discord.Embed(
            title="❌ Aucun général trouvé",
            description=f"Aucun général n'a été trouvé pour le pays **{pays.name}**.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Créer la vue avec le menu déroulant pour sélectionner le général
    view = GeneralTraitManagementView(generaux_pays, pays.name)
    
    embed = discord.Embed(
        title="🎯 Gestion des Traits - Sélection du Général",
        description=f"Sélectionnez le général de **{pays.name}** dont vous voulez gérer les traits :",
        color=EMBED_COLOR
    )
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class GeneralTraitManagementView(discord.ui.View):
    """Vue pour sélectionner un général et gérer ses traits."""
    
    def __init__(self, generaux_pays, pays):
        super().__init__(timeout=300)
        self.generaux_pays = generaux_pays
        self.pays = pays
        
        # Créer le menu déroulant pour sélectionner le général
        options = []
        for i, general in enumerate(generaux_pays[:25]):
            stars_display = format_stars(general["stars"])
            options.append(discord.SelectOption(
                label=f"{general['nom']} ({stars_display})",
                value=str(i),
                description=f"Général de {pays}"
            ))
        
        select = discord.ui.Select(
            placeholder="Choisissez un général...",
            options=options
        )
        select.callback = self.select_general_callback
        self.add_item(select)
    
    async def select_general_callback(self, interaction: discord.Interaction):
        selected_index = int(interaction.data["values"][0])
        selected_general = self.generaux_pays[selected_index]
        
        # Créer la vue pour choisir l'action (ajouter/supprimer)
        view = TraitActionView(selected_general, self.pays)
        
        embed = discord.Embed(
            title="⚡ Action sur les Traits",
            description=f"**Général sélectionné :** {selected_general['nom']} ({format_stars(selected_general['stars'])})\n"
                       f"**Pays :** {self.pays}\n\n"
                       f"Que voulez-vous faire ?",
            color=EMBED_COLOR
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class TraitActionView(discord.ui.View):
    """Vue pour choisir si on veut ajouter ou supprimer un trait."""
    
    def __init__(self, selected_general, pays):
        super().__init__(timeout=300)
        self.selected_general = selected_general
        self.pays = pays
        
        # Bouton pour ajouter un trait
        add_button = discord.ui.Button(
            label="Ajouter un trait",
            style=discord.ButtonStyle.success,
            emoji="➕"
        )
        add_button.callback = self.add_trait_callback
        self.add_item(add_button)
        
        # Bouton pour supprimer un trait
        remove_button = discord.ui.Button(
            label="Supprimer un trait",
            style=discord.ButtonStyle.danger,
            emoji="➖"
        )
        remove_button.callback = self.remove_trait_callback
        self.add_item(remove_button)
    
    async def add_trait_callback(self, interaction: discord.Interaction):
        # Créer la vue pour sélectionner la catégorie de trait
        view = TraitCategorySelectionView(self.selected_general, self.pays)
        
        embed = discord.Embed(
            title="📂 Sélection de Catégorie",
            description=f"**Général :** {self.selected_general['nom']}\n"
                       f"**Pays :** {self.pays}\n\n"
                       f"Sélectionnez d'abord la catégorie de trait à ajouter :",
            color=0x00ff88
        )
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def remove_trait_callback(self, interaction: discord.Interaction):
        # Charger les traits actuels du général
        generaux_data = load_generaux()
        user_id = self.selected_general["user_id"]
        nom_general = self.selected_general["nom"]
        general_info = generaux_data[user_id]["generaux"][nom_general]
        
        # Collecter tous les traits du général avec leurs catégories
        categorized_traits = {}
        if "traits_positifs" in general_info:
            categorized_traits["Traits de Personnalité Positifs"] = general_info["traits_positifs"]
        if "traits_negatifs" in general_info:
            categorized_traits["Traits de Personnalité Négatifs"] = general_info["traits_negatifs"]
        if "traits_commandement" in general_info:
            categorized_traits["Traits de Commandement"] = general_info["traits_commandement"]
        if "traits_amelioration" in general_info:
            categorized_traits["Traits d'Amélioration"] = general_info["traits_amelioration"]
        if "traits_marechaux" in general_info:
            categorized_traits["Traits de Maréchal"] = general_info["traits_marechaux"]
        
        # Aplatir la liste pour la compatibilité
        all_traits = []
        for category_traits in categorized_traits.values():
            all_traits.extend(category_traits)
        
        if not all_traits:
            embed = discord.Embed(
                title="❌ Aucun trait à supprimer",
                description=f"Le général **{nom_general}** n'a aucun trait à supprimer.",
                color=0xff4444
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return
        
        # Créer la vue pour sélectionner le trait à supprimer
        view = RemoveTraitSelectionView(self.selected_general, self.pays, categorized_traits)
        
        embed = discord.Embed(
            title="➖ Supprimer un Trait",
            description=f"**Général :** {self.selected_general['nom']}\n"
                       f"**Pays :** {self.pays}\n\n"
                       f"Sélectionnez le trait à supprimer :",
            color=0xff4444
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class TraitCategorySelectionView(discord.ui.View):
    """Vue pour sélectionner la catégorie de trait à ajouter."""
    
    def __init__(self, selected_general, pays):
        super().__init__(timeout=300)
        self.selected_general = selected_general
        self.pays = pays
        
        # Récupérer le domaine du général
        generaux_data = load_generaux()
        user_id = selected_general["user_id"]
        nom_general = selected_general["nom"]
        general_info = generaux_data[user_id]["generaux"][nom_general]
        self.domaine = general_info.get("domaine", "terrestre")
        
        # Créer les options de catégorie
        options = [
            discord.SelectOption(
                label="Traits de Personnalité Positifs",
                value="positifs",
                description="Courageux, Personnalité publique, Stratège de génie, etc.",
                emoji="✨"
            ),
            discord.SelectOption(
                label="Traits de Personnalité Négatifs",
                value="negatifs",
                description="Alcoolique, Lâche, Incompétent, etc.",
                emoji="💀"
            ),
            discord.SelectOption(
                label=f"Traits de Commandement ({self.domaine.capitalize()})",
                value="commandement",
                description=f"Traits spécialisés pour le domaine {self.domaine}",
                emoji="⚔️"
            )
        ]
        
        # Ajouter les traits d'amélioration seulement si c'est un général terrestre
        if self.domaine == "terrestre":
            options.append(discord.SelectOption(
                label="Traits d'Amélioration (Terrestre)",
                value="amelioration",
                description="Expert de la cavalerie, Expert des chars, etc.",
                emoji="🔧"
            ))
        
        # Ajouter les traits de maréchal seulement si c'est un général terrestre 3⭐
        if self.domaine == "terrestre" and selected_general["stars"] >= 3:
            options.append(discord.SelectOption(
                label="Traits de Maréchal (3⭐ Terrestre)",
                value="marechaux",
                description="Magicien de la logistique, Attaquant agressif, etc.",
                emoji="👑"
            ))
        
        select = discord.ui.Select(
            placeholder="Choisissez une catégorie de trait...",
            options=options
        )
        select.callback = self.category_selected_callback
        self.add_item(select)
    
    async def category_selected_callback(self, interaction: discord.Interaction):
        category = interaction.data["values"][0]
        
        # Créer la vue pour sélectionner le trait spécifique
        view = AddTraitSelectionView(self.selected_general, self.pays, category, self.domaine)
        
        category_names = {
            "positifs": "Traits de Personnalité Positifs",
            "negatifs": "Traits de Personnalité Négatifs", 
            "commandement": f"Traits de Commandement ({self.domaine.capitalize()})",
            "amelioration": "Traits d'Amélioration",
            "marechaux": "Traits de Maréchal"
        }
        
        embed = discord.Embed(
            title="➕ Ajouter un Trait",
            description=f"**Général :** {self.selected_general['nom']}\n"
                       f"**Pays :** {self.pays}\n"
                       f"**Catégorie :** {category_names[category]}\n\n"
                       f"Sélectionnez le trait à ajouter :",
            color=0x00ff88
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class AddTraitSelectionView(discord.ui.View):
    """Vue pour sélectionner le trait à ajouter selon la catégorie."""
    
    def __init__(self, selected_general, pays, category, domaine):
        super().__init__(timeout=300)
        self.selected_general = selected_general
        self.pays = pays
        self.category = category
        self.domaine = domaine
        
        # Définir les traits selon la catégorie sélectionnée
        traits_by_category = self.get_traits_by_category()
        
        # Créer le menu déroulant avec les traits de la catégorie
        options = []
        for i, trait in enumerate(traits_by_category[:25]):  # Limite Discord
            options.append(discord.SelectOption(
                label=trait,
                value=str(i),
                description=f"Trait de {self.get_category_display_name()}"
            ))
        
        if not options:
            # Si pas de traits disponibles, ajouter une option vide
            options.append(discord.SelectOption(
                label="Aucun trait disponible",
                value="none",
                description="Cette catégorie n'a pas de traits disponibles"
            ))
        
        select = discord.ui.Select(
            placeholder="Choisissez le trait à ajouter...",
            options=options
        )
        select.callback = self.add_trait_callback
        self.add_item(select)
    
    def get_category_display_name(self):
        names = {
            "positifs": "personnalité positive",
            "negatifs": "personnalité négative",
            "commandement": f"commandement {self.domaine}",
            "amelioration": "amélioration",
            "marechaux": "maréchal"
        }
        return names.get(self.category, "trait")
    
    def get_traits_by_category(self):
        """Retourne la liste des traits selon la catégorie sélectionnée."""
        if self.category == "positifs":
            return [
                "Personnalité publique", "Courageux", "Inflexible", "Stratège de génie", 
                "Officier de carrière", "Héros de guerre"
            ]
        elif self.category == "negatifs":
            return [
                "Alcoolique", "Drogué", "Lâche", "Connexion politique", "Vieux jeu", 
                "Paranoïaque", "Colérique", "Incompétent"
            ]
        elif self.category == "commandement":
            # Traits de commandement selon le domaine
            if self.domaine == "terrestre":
                return [
                    "Planificateur", "Officier de cavalerie", "Officier d'infanterie", "Officier des blindés",
                    "Officier du génie", "Officier de reconnaissance", "Officier des opérations spéciales",
                    "Conquérant", "Ours polaire", "Montagnard", "Renard du désert", "Renard des marais",
                    "Combattant des plaines", "Rat de la jungle", "Éclaireur", "Spécialiste du combat urbain",
                    "Major de promotion"
                ]
            elif self.domaine == "marine":
                return [
                    "Créateur de blocus", "Loup de mer", "Observateur", "Protecteur de la flotte",
                    "Maître tacticien", "Cœur de fer", "Contrôleur aérien", "Loup des mers glacées",
                    "Combattant côtier", "Expert de haute mer", "Expert de basse mer", "Major de promotion"
                ]
            elif self.domaine == "aerien":
                return [
                    "Aigle des cieux", "Protecteur du ciel", "Destructeur méticuleux",
                    "Théoricien du support rapproché", "Poséidon"
                ]
        elif self.category == "amelioration":
            # Traits d'amélioration (seulement terrestre)
            return list(TRAITS_AMELIORATION.keys())
        elif self.category == "marechaux":
            # Traits de maréchal (seulement terrestre 3⭐)
            return list(TRAITS_MARECHAUX.keys())
        
        return []
    
    async def add_trait_callback(self, interaction: discord.Interaction):
        selected_value = interaction.data["values"][0]
        
        if selected_value == "none":
            embed = discord.Embed(
                title="❌ Aucun trait disponible",
                description="Cette catégorie n'a pas de traits disponibles.",
                color=0xff4444
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return
        
        trait_index = int(selected_value)
        traits_list = self.get_traits_by_category()
        selected_trait = traits_list[trait_index]
        
        # Charger les données actuelles
        generaux_data = load_generaux()
        user_id = self.selected_general["user_id"]
        nom_general = self.selected_general["nom"]
        
        # Déterminer dans quelle liste ajouter le trait
        trait_list_mapping = {
            "positifs": "traits_positifs",
            "negatifs": "traits_negatifs",
            "commandement": "traits_commandement",
            "amelioration": "traits_amelioration",
            "marechaux": "traits_marechaux"
        }
        
        trait_list = trait_list_mapping[self.category]
        
        # Ajouter le trait
        if trait_list not in generaux_data[user_id]["generaux"][nom_general]:
            generaux_data[user_id]["generaux"][nom_general][trait_list] = []
        
        if selected_trait not in generaux_data[user_id]["generaux"][nom_general][trait_list]:
            generaux_data[user_id]["generaux"][nom_general][trait_list].append(selected_trait)
            save_generaux(generaux_data)
            
            embed = discord.Embed(
                title="✅ Trait ajouté",
                description=f"Le trait **{selected_trait}** a été ajouté au général **{nom_general}** de **{self.pays}**.",
                color=0x00ff88
            )
        else:
            embed = discord.Embed(
                title="⚠️ Trait déjà présent",
                description=f"Le général **{nom_general}** possède déjà le trait **{selected_trait}**.",
                color=0xffaa00
            )
        
        await interaction.response.edit_message(embed=embed, view=None)

class RemoveTraitSelectionView(discord.ui.View):
    """Vue pour sélectionner le trait à supprimer."""
    
    def __init__(self, selected_general, pays, categorized_traits):
        super().__init__(timeout=300)
        self.selected_general = selected_general
        self.pays = pays
        self.categorized_traits = categorized_traits
        
        # Créer le menu déroulant avec les traits organisés par catégorie
        options = []
        trait_mapping = {}  # Pour mapper les valeurs aux traits et catégories
        option_index = 0
        
        for category, traits in categorized_traits.items():
            for trait in traits:
                # Raccourcir les noms de catégorie pour l'affichage
                category_short = category.replace("Traits de ", "").replace("Personnalité ", "")
                options.append(discord.SelectOption(
                    label=trait,
                    value=str(option_index),
                    description=f"Catégorie: {category_short}"
                ))
                trait_mapping[str(option_index)] = {"trait": trait, "category": category}
                option_index += 1
                
                if len(options) >= 25:  # Limite Discord
                    break
            if len(options) >= 25:
                break
        
        self.trait_mapping = trait_mapping
        
        select = discord.ui.Select(
            placeholder="Choisissez le trait à supprimer...",
            options=options
        )
        select.callback = self.remove_trait_callback
        self.add_item(select)
    
    async def remove_trait_callback(self, interaction: discord.Interaction):
        selected_value = interaction.data["values"][0]
        trait_info = self.trait_mapping[selected_value]
        selected_trait = trait_info["trait"]
        
        # Charger les données actuelles
        generaux_data = load_generaux()
        user_id = self.selected_general["user_id"]
        nom_general = self.selected_general["nom"]
        general_info = generaux_data[user_id]["generaux"][nom_general]
        
        # Trouver et supprimer le trait
        trait_removed = False
        for trait_list in ["traits_positifs", "traits_negatifs", "traits_commandement", "traits_amelioration", "traits_marechaux"]:
            if trait_list in general_info and selected_trait in general_info[trait_list]:
                general_info[trait_list].remove(selected_trait)
                trait_removed = True
                break
        
        if trait_removed:
            save_generaux(generaux_data)
            embed = discord.Embed(
                title="✅ Trait supprimé",
                description=f"Le trait **{selected_trait}** a été supprimé du général **{nom_general}** de **{self.pays}**.",
                color=0x00ff88
            )
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible de supprimer le trait **{selected_trait}**.",
                color=0xff4444
            )
        
        await interaction.response.edit_message(embed=embed, view=None)

@bot.tree.command(name="general_experience", description="[ADMIN] Ajouter de l'expérience à un général")
@app_commands.describe(
    pourcentage="Pourcentage d'expérience à ajouter (0-100)",
    pays="Rôle du pays dont le général doit recevoir de l'expérience"
)
async def add_experience(interaction: discord.Interaction, pourcentage: int, pays: discord.Role):
    """Permet aux admins d'ajouter de l'expérience à un général."""
    
    # Vérifier les permissions admin
    if not interaction.user.guild_permissions.administrator and interaction.user.id not in ADMIN_IDS:
        embed = discord.Embed(
            title="❌ Permission refusée",
            description="Cette commande est réservée aux administrateurs.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if pourcentage < 0 or pourcentage > 100:
        embed = discord.Embed(
            title="❌ Pourcentage invalide",
            description="Le pourcentage doit être entre 0 et 100.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Vérifier que le rôle est bien un rôle de pays
    def is_country_role(role):
        """Vérifie si un rôle est un rôle de pays en regardant s'il a de l'argent dans le système économique."""
        role_id = str(role.id)
        # Un rôle est considéré comme un pays s'il existe dans le système de balances
        # ou s'il existe dans pays_images (rôles pays créés)
        if role_id in balances:
            return True
        
        # Vérifier aussi dans pays_images pour les rôles pays récemment créés
        pays_images_data = load_pays_images()
        return role_id in pays_images_data
    
    if not is_country_role(pays):
        embed = discord.Embed(
            title="❌ Rôle invalide",
            description=f"Le rôle **{pays.name}** n'est pas reconnu comme un rôle de pays.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Rechercher les généraux du pays
    generaux_data = load_generaux()
    pays_name = pays.name.lower()
    
    generaux_pays = []
    for user_id, user_data in generaux_data.items():
        if "generaux" in user_data:
            for nom_general, general_info in user_data["generaux"].items():
                if general_info.get("pays", "").lower() == pays_name:
                    generaux_pays.append({
                        "user_id": user_id,
                        "nom": nom_general,
                        "stars": general_info.get("stars", 0),
                        "experience": general_info.get("experience", 0)
                    })
    
    if not generaux_pays:
        embed = discord.Embed(
            title="❌ Aucun général trouvé",
            description=f"Aucun général n'a été trouvé pour le pays **{pays.name}**.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    view = ExperienceSelectionView(generaux_pays, pourcentage, pays.name)
    
    embed = discord.Embed(
        title="📈 Ajout d'Expérience",
        description=f"Sélectionnez le général de **{pays.name}** auquel ajouter **{pourcentage}%** d'expérience :",
        color=EMBED_COLOR
    )
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ExperienceSelectionView(discord.ui.View):
    """Vue pour sélectionner un général et lui ajouter de l'expérience."""
    
    def __init__(self, generaux_pays, pourcentage, pays):
        super().__init__(timeout=None)
        self.generaux_pays = generaux_pays
        self.pourcentage = pourcentage
        self.pays = pays
        
        options = []
        for i, general in enumerate(generaux_pays[:25]):
            stars_display = format_stars(general["stars"])
            options.append(discord.SelectOption(
                label=f"{general['nom']} ({stars_display})",
                value=str(i),
                description=f"XP: {general['experience']}%"
            ))
        
        select = discord.ui.Select(
            placeholder="Choisissez un général...",
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        selected_index = int(interaction.data["values"][0])
        selected_general = self.generaux_pays[selected_index]
        
        generaux_data = load_generaux()
        user_id = selected_general["user_id"]
        nom_general = selected_general["nom"]
        
        # Ajouter l'expérience
        current_exp = generaux_data[user_id]["generaux"][nom_general].get("experience", 0)
        new_exp = min(current_exp + self.pourcentage, 100)
        generaux_data[user_id]["generaux"][nom_general]["experience"] = new_exp
        
        save_generaux(generaux_data)
        
        embed = discord.Embed(
            title="✅ Expérience ajoutée",
            description=f"**{self.pourcentage}%** d'expérience ajoutée au général **{nom_general}** de **{self.pays}**.\n"
                       f"Expérience: {current_exp}% → {new_exp}%",
            color=0x00ff88
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="general_gestion", description="[ADMIN] Gérer les généraux (supprimer/renommer)")
@app_commands.describe(
    pays="Rôle du pays",
    action="Action à effectuer"
)
@app_commands.choices(action=[
    discord.app_commands.Choice(name="Supprimer (tuer)", value="kill"),
    discord.app_commands.Choice(name="Renommer", value="rename")
])
async def manage_general(interaction: discord.Interaction, pays: discord.Role, action: str):
    """Permet aux admins de gérer les généraux (supprimer ou renommer)."""
    
    # Vérifier les permissions admin
    if not interaction.user.guild_permissions.administrator and interaction.user.id not in ADMIN_IDS:
        embed = discord.Embed(
            title="❌ Permission refusée",
            description="Cette commande est réservée aux administrateurs.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Vérifier que le rôle est bien un rôle de pays
    def is_country_role(role):
        """Vérifie si un rôle est un rôle de pays en regardant s'il a de l'argent dans le système économique."""
        role_id = str(role.id)
        # Un rôle est considéré comme un pays s'il existe dans le système de balances
        # ou s'il existe dans pays_images (rôles pays créés)
        if role_id in balances:
            return True
        
        # Vérifier aussi dans pays_images pour les rôles pays récemment créés
        pays_images_data = load_pays_images()
        return role_id in pays_images_data
    
    if not is_country_role(pays):
        embed = discord.Embed(
            title="❌ Rôle invalide",
            description=f"Le rôle **{pays.name}** n'est pas reconnu comme un rôle de pays.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    generaux_data = load_generaux()
    pays_name = pays.name.lower()
    
    generaux_pays = []
    for user_id, user_data in generaux_data.items():
        if "generaux" in user_data:
            for nom_general, general_info in user_data["generaux"].items():
                if general_info.get("pays", "").lower() == pays_name:
                    generaux_pays.append({
                        "user_id": user_id,
                        "nom": nom_general,
                        "stars": general_info.get("stars", 0),
                        "type": general_info.get("type", "Inconnu")
                    })
    
    if not generaux_pays:
        embed = discord.Embed(
            title="❌ Aucun général trouvé",
            description=f"Aucun général n'a été trouvé pour le pays **{pays.name}**.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    view = ManagementSelectionView(generaux_pays, action, pays.name)
    
    action_text = "supprimer" if action == "kill" else "renommer"
    embed = discord.Embed(
        title=f"🔧 Gestion des Généraux - {action_text.capitalize()}",
        description=f"Sélectionnez le général de **{pays.name}** à {action_text} :",
        color=EMBED_COLOR
    )
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ManagementSelectionView(discord.ui.View):
    """Vue pour gérer les généraux (supprimer/renommer)."""
    
    def __init__(self, generaux_pays, action, pays):
        super().__init__(timeout=None)
        self.generaux_pays = generaux_pays
        self.action = action
        self.pays = pays
        
        options = []
        for i, general in enumerate(generaux_pays[:25]):
            stars_display = format_stars(general["stars"])
            options.append(discord.SelectOption(
                label=f"{general['nom']} ({stars_display})",
                value=str(i),
                description=f"{general['type']}"
            ))
        
        select = discord.ui.Select(
            placeholder="Choisissez un général...",
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        selected_index = int(interaction.data["values"][0])
        selected_general = self.generaux_pays[selected_index]
        
        if self.action == "kill":
            # Supprimer le général
            generaux_data = load_generaux()
            user_id = selected_general["user_id"]
            nom_general = selected_general["nom"]
            
            del generaux_data[user_id]["generaux"][nom_general]
            save_generaux(generaux_data)
            
            embed = discord.Embed(
                title="💀 Général supprimé",
                description=f"Le général **{nom_general}** de **{self.pays}** a été supprimé (tué au combat).",
                color=0xff4444
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        elif self.action == "rename":
            # Afficher un modal pour renommer
            modal = RenameGeneralModal(selected_general, self.pays)
            await interaction.response.send_modal(modal)

class RenameGeneralModal(discord.ui.Modal):
    """Modal pour renommer un général."""
    
    def __init__(self, general_info, pays):
        super().__init__(title=f"Renommer le général - {pays}")
        self.general_info = general_info
        self.pays = pays
        
        self.nouveau_nom = discord.ui.TextInput(
            label="Nouveau nom du général",
            placeholder="Entrez le nouveau nom...",
            default=general_info["nom"],
            max_length=50,
            required=True
        )
        
        self.add_item(self.nouveau_nom)
    
    async def on_submit(self, interaction: discord.Interaction):
        nouveau_nom = self.nouveau_nom.value
        ancien_nom = self.general_info["nom"]
        user_id = self.general_info["user_id"]
        
        generaux_data = load_generaux()
        
        # Vérifier que le nouveau nom n'existe pas déjà
        if nouveau_nom in generaux_data[user_id]["generaux"]:
            embed = discord.Embed(
                title="❌ Nom déjà utilisé",
                description=f"Un général nommé **{nouveau_nom}** existe déjà.",
                color=0xff4444
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Renommer le général
        general_data = generaux_data[user_id]["generaux"][ancien_nom]
        generaux_data[user_id]["generaux"][nouveau_nom] = general_data
        del generaux_data[user_id]["generaux"][ancien_nom]
        
        save_generaux(generaux_data)
        
        embed = discord.Embed(
            title="✅ Général renommé",
            description=f"Le général **{ancien_nom}** de **{self.pays}** a été renommé en **{nouveau_nom}**.",
            color=0x00ff88
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# === CLASSE POUR LA SÉLECTION DE GÉNÉRAL À SUPPRIMER ===

class GeneralDeletionView(discord.ui.View):
    def __init__(self, pays_role, generaux_list):
        super().__init__(timeout=None)
        self.pays_role = pays_role
        self.generaux_list = generaux_list
        
        # Créer le menu déroulant avec les généraux
        options = []
        for general_name, general_data in generaux_list:
            # Créer une description courte du général
            type_general = general_data.get("type", "Inconnu")
            domaine = general_data.get("domaine", "Inconnu")
            experience = general_data.get("experience", 0)
            
            description = f"{type_general} | {domaine.capitalize()} | XP: {experience}"
            
            options.append(discord.SelectOption(
                label=general_name,
                description=description[:100],  # Limiter à 100 caractères
                value=general_name
            ))
        
        if options:
            self.add_item(GeneralDeletionSelect(options, pays_role))

class GeneralDeletionSelect(discord.ui.Select):
    def __init__(self, options, pays_role):
        super().__init__(
            placeholder="Choisissez le général à supprimer...",
            options=options,
            min_values=1,
            max_values=1
        )
        self.pays_role = pays_role
    
    async def callback(self, interaction: discord.Interaction):
        general_name = self.values[0]
        
        # Charger les données des généraux
        generaux_data = load_generaux()
        
        # Trouver l'utilisateur qui possède ce général
        user_found = None
        for user_id, user_data in generaux_data.items():
            if general_name in user_data.get("generaux", {}):
                user_found = user_id
                break
        
        if not user_found:
            await interaction.response.send_message(
                f"❌ Général **{general_name}** introuvable.", 
                ephemeral=True
            )
            return
        
        # Supprimer le général
        del generaux_data[user_found]["generaux"][general_name]
        save_generaux(generaux_data)
        
        # Décrémenter le compteur de rolls du pays (donner un roll en plus)
        success = decrement_pays_roll_count(self.pays_role.name)
        
        # Récupérer le nouveau nombre de rolls
        new_roll_count = get_pays_roll_count(self.pays_role.name)
        
        embed = discord.Embed(
            title="✅ Général supprimé",
            description=f"Le général **{general_name}** du pays **{self.pays_role.name}** a été supprimé.\n\n"
                       f"**Nouveau nombre de rolls utilisés :** {new_roll_count}/3\n"
                       f"**Rolls disponibles :** {3 - new_roll_count}/3",
            color=0x00ff88
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# === COMMANDE RESET ROLL ===

@bot.tree.command(name="reset_roll", description="[ADMIN] Réinitialise les slots de roll d'un pays")
@app_commands.describe(
    pays="Rôle du pays dont réinitialiser les slots de roll",
    supprimer_un_general="Si True, permet de supprimer un seul général pour récupérer un roll"
)
@app_commands.choices(supprimer_un_general=[
    discord.app_commands.Choice(name="Non - Reset complet (tous les rolls)", value="false"),
    discord.app_commands.Choice(name="Oui - Supprimer un général spécifique", value="true")
])
async def reset_roll(interaction: discord.Interaction, pays: discord.Role, supprimer_un_general: str = "false"):
    """Permet aux admins de réinitialiser les slots de roll d'un pays."""
    
    # Vérifier les permissions admin
    if not interaction.user.guild_permissions.administrator and interaction.user.id not in ADMIN_IDS:
        embed = discord.Embed(
            title="❌ Permission refusée",
            description="Cette commande est réservée aux administrateurs.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Vérifier que le rôle est bien un rôle de pays
    def is_country_role(role):
        """Vérifie si un rôle est un rôle de pays en regardant s'il a de l'argent dans le système économique."""
        role_id = str(role.id)
        # Un rôle est considéré comme un pays s'il existe dans le système de balances
        # ou s'il existe dans pays_images (rôles pays créés)
        if role_id in balances:
            return True
        
        # Vérifier aussi dans pays_images pour les rôles pays récemment créés
        pays_images_data = load_pays_images()
        return role_id in pays_images_data
    
    if not is_country_role(pays):
        embed = discord.Embed(
            title="❌ Rôle invalide",
            description=f"Le rôle **{pays.name}** n'est pas reconnu comme un rôle de pays.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Récupérer le nombre de rolls actuel
    current_rolls = get_pays_roll_count(pays.name)
    
    # Vérifier le mode choisi
    if supprimer_un_general == "true":
        # Mode suppression d'un seul général
        
        # Charger les données des généraux pour trouver ceux du pays
        generaux_data = load_generaux()
        generaux_du_pays = []
        
        for user_id, user_data in generaux_data.items():
            if user_id.startswith("pays_"):
                continue  # Ignorer les entrées de compteur de pays
            
            for general_name, general_data in user_data.get("generaux", {}).items():
                # Vérifier si ce général appartient au pays concerné
                general_pays = general_data.get("pays", "")
                if general_pays.lower() == pays.name.lower():
                    generaux_du_pays.append((general_name, general_data))
        
        if not generaux_du_pays:
            embed = discord.Embed(
                title="❌ Aucun général trouvé",
                description=f"Le pays **{pays.name}** n'a aucun général à supprimer.",
                color=0xff4444
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Créer la vue avec menu déroulant
        view = GeneralDeletionView(pays, generaux_du_pays)
        
        embed = discord.Embed(
            title="🗑️ Suppression d'un général",
            description=f"Choisissez le général du pays **{pays.name}** à supprimer.\n\n"
                       f"**Rolls actuels :** {current_rolls}/3 utilisés\n"
                       f"**Après suppression :** {max(0, current_rolls-1)}/3 utilisés\n\n"
                       f"⚠️ Cette action est irréversible !",
            color=0xffa500
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    else:
        # Mode reset complet (comportement original)
        success = reset_pays_roll_count(pays.name)
        
        if success or current_rolls > 0:
            embed = discord.Embed(
                title="✅ Slots de roll réinitialisés",
                description=f"Les slots de roll du pays **{pays.name}** ont été réinitialisés.\n\n"
                           f"**Avant :** {current_rolls}/3 rolls utilisés\n"
                           f"**Après :** 0/3 rolls utilisés\n\n"
                           f"Le pays peut maintenant effectuer 3 nouveaux rolls de généraux.",
                color=0x00ff88
            )
        else:
            embed = discord.Embed(
                title="ℹ️ Aucune action nécessaire",
                description=f"Le pays **{pays.name}** n'avait aucun roll enregistré.\n\n"
                           f"Les slots sont déjà disponibles (0/3 rolls utilisés).",
                color=EMBED_COLOR
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# === CONSTANTES POUR LES TRAITS AMÉLIORÉS ET MARÉCHAUX ===

# Traits de maréchaux (pour généraux terrestres 3⭐ uniquement)
TRAITS_MARECHAUX = {
    "Magicien de la logistique": {
        "description": "Bonus modéré à la logistique des unités sous le commandement du maréchal",
        "prerequis": ["Planificateur"],
        "exclusif": "Planificateur minutieux"
    },
    "Planificateur minutieux": {
        "description": "Bonus modéré à la planification des unités sous commandement du maréchal",
        "prerequis": ["Planificateur"],
        "exclusif": "Magicien de la logistique"
    },
    "Partisan de la défense": {
        "description": "Léger bonus à la défense des unités sous commandement du maréchal",
        "prerequis": [],
        "exclusif": "Partisan de l'offensive"
    },
    "Partisan de l'offensive": {
        "description": "Léger bonus à l'attaque des unités sous commandement du maréchal",
        "prerequis": [],
        "exclusif": "Partisan de la défense"
    },
    "Défenseur inébranlable": {
        "description": "Bonus modéré à la défense des unités sous commandement du maréchal (trait rare)",
        "prerequis": [],
        "exclusif": "Attaquant agressif",
        "rare": True
    },
    "Attaquant agressif": {
        "description": "Bonus modéré à l'attaque des unités sous commandement du maréchal (trait rare)",
        "prerequis": [],
        "exclusif": "Défenseur inébranlable",
        "rare": True
    },
    "Charismatique": {
        "description": "Bonus modéré au moral des troupes sous le commandement du maréchal + bonus de propagande",
        "prerequis": ["Personnalité publique"],
        "exclusif": None
    }
}

# Traits d'amélioration (traits de commandement améliorés)
TRAITS_AMELIORATION = {
    # Améliorations pour généraux terrestres
    "Expert de la cavalerie": {
        "description": "Bonus modéré d'attaque et léger bonus de défense pour unités équines/motorisées/mécanisées",
        "prerequis": ["Officier de cavalerie"],
        "exclusif": ["Expert des chars", "Expert du combat combiné"],
        "type": "terrestre"
    },
    "Expert des chars": {
        "description": "Bonus modéré d'attaque et de logistique pour les unités de chars",
        "prerequis": ["Officier des blindés"],
        "exclusif": ["Expert de la cavalerie", "Expert du combat combiné"],
        "type": "terrestre"
    },
    "Expert du combat combiné": {
        "description": "Bonus modéré d'attaque et de logistique pour toute unité motorisée/mécanisée/blindée (trait rare)",
        "prerequis": ["Officier de cavalerie", "Officier des blindés"],
        "exclusif": ["Expert de la cavalerie", "Expert des chars"],
        "type": "terrestre",
        "rare": True
    },
    "Expert de l'infanterie": {
        "description": "Bonus modéré d'attaque et de planification pour les unités d'infanterie",
        "prerequis": ["Officier d'infanterie"],
        "exclusif": ["Entranché"],
        "type": "terrestre"
    },
    "Entranché": {
        "description": "Bonus modéré de défense et de logistique pour les unités d'infanterie",
        "prerequis": ["Officier d'infanterie"],
        "exclusif": ["Expert de l'infanterie"],
        "type": "terrestre"
    },
    "Destructeur de forteresses": {
        "description": "Bonus modéré lors des assauts contre positions fortifiées + léger bonus aux autres opérations du génie",
        "prerequis": ["Officier du génie"],
        "exclusif": [],
        "type": "terrestre"
    },
    "Guérilleros": {
        "description": "Bonus modéré aux opérations de reconnaissance, attaques surprises et actions de guérilla",
        "prerequis": ["Officier de reconnaissance"],
        "exclusif": [],
        "type": "terrestre"
    },
    "Embusqué": {
        "description": "Bonus modéré aux attaques de commandos et forces spéciales au-delà des lignes ennemies",
        "prerequis": ["Officier des opérations spéciales"],
        "exclusif": ["Parachutiste"],
        "type": "terrestre"
    },
    "Parachutiste": {
        "description": "Bonus modéré à la défense et logistique de toutes les unités parachutistes",
        "prerequis": ["Officier des opérations spéciales"],
        "exclusif": ["Embusqué"],
        "type": "terrestre"
    },
    "Grenouille": {
        "description": "Bonus modéré aux attaques amphibies et débarquements",
        "prerequis": ["Conquérant"],
        "exclusif": [],
        "type": "terrestre"
    },
    "Prêtre des neiges": {
        "description": "Bonus modéré de logistique, d'attaque et de défense en terrain neigeux",
        "prerequis": ["Ours polaire"],
        "exclusif": [],
        "type": "terrestre"
    },
    "Adaptable": {
        "description": "Léger bonus à tous les types de terrain (trait très rare)",
        "prerequis": ["ours polaire", "montagnard", "renard du désert", "renard des marais", "combattant des plaines", "rat de la jungle", "éclaireur", "spécialiste du combat urbain"],
        "exclusif": [],
        "type": "terrestre",
        "rare": True
    }
}

# === COMMANDES DE PROMOTION ET D'AMÉLIORATION ===

@bot.tree.command(name="promouvoir", description="Promouvoir un général terrestre en maréchal")
async def promouvoir_marechal(interaction: discord.Interaction):
    """Permet de promouvoir un général terrestre éligible en maréchal."""
    
    # Obtenir les rôles de pays de l'utilisateur en vérifiant s'ils ont de l'argent
    def is_country_role(role):
        """Vérifie si un rôle est un rôle de pays en regardant s'il a de l'argent dans le système économique."""
        role_id = str(role.id)
        # Un rôle est considéré comme un pays s'il existe dans le système de balances
        return role_id in balances
    
    user_country_roles = []
    for role in interaction.user.roles:
        if is_country_role(role):
            user_country_roles.append(role)
    
    if not user_country_roles:
        embed = discord.Embed(
            title="❌ Aucun rôle de pays",
            description="Vous n'avez aucun rôle de pays. Vous devez avoir un rôle de pays pour promouvoir ses généraux.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Charger tous les généraux pour trouver ceux éligibles
    generaux_data = load_generaux()
    
    # Trouver tous les généraux terrestres éligibles pour tous les pays de l'utilisateur
    generaux_eligibles = []
    for user_id, user_data in generaux_data.items():
        if "generaux" in user_data:
            for nom_general, general_info in user_data["generaux"].items():
                # Vérifier si le général appartient à un des pays de l'utilisateur
                general_pays = general_info.get("pays", "").lower()
                for role in user_country_roles:
                    if (role.name.lower() == general_pays and 
                        general_info.get("domaine", "") == "terrestre" and
                        not general_info.get("est_marechal", False)):
                        
                        # Vérifier les critères d'éligibilité
                        stars = general_info.get("stars", 0)
                        traits = general_info.get("traits", [])
                        
                        # Éligible si 3⭐ ou plus, OU si 2⭐ avec "Officier de carrière"
                        if (stars >= 3 or (stars == 2 and "Officier de carrière" in traits)):
                            generaux_eligibles.append({
                                "user_id": user_id,
                                "nom": nom_general,
                                "stars": stars,
                                "pays": role.name,
                                "info": general_info
                            })
                        break
    
    if not generaux_eligibles:
        # Lister les pays de l'utilisateur pour le message d'erreur
        pays_list = [role.name for role in user_country_roles]
        pays_str = ", ".join(pays_list)
        
        embed = discord.Embed(
            title="❌ Aucun général éligible",
            description=f"Aucun général terrestre éligible n'a été trouvé pour vos pays : **{pays_str}**.\n\n"
                       f"**Critères requis :**\n"
                       f"• Minimum 3⭐ (ou 2⭐ avec trait 'Officier de carrière')\n"
                       f"• Domaine terrestre\n"
                       f"• Pas encore maréchal",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Créer la vue de sélection pour la promotion
    view = PromotionMarshalView(interaction.user.id, generaux_eligibles, None)
    
    embed = discord.Embed(
        title="🎖️ Promotion en Maréchal",
        description="Sélectionnez le général à promouvoir en maréchal :",
        color=EMBED_COLOR
    )
    
    # Ajouter la liste des généraux éligibles avec leur pays
    generaux_list = []
    for general in generaux_eligibles:
        generaux_list.append(f"⭐" * general["stars"] + f" **{general['nom']}** ({general['pays']})")
    
    embed.add_field(
        name="Généraux éligibles",
        value="\n".join(generaux_list),
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Promotion en maréchal",
        value="• Le général recevra un trait de maréchal\n"
              "• Ses traits de général seront réduits au minimum\n"
              "• Le trait de maréchal s'appliquera à toute l'armée/théâtre",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="amelioration_general", description="[ADMIN] Améliorer un trait de commandement d'un général")
@app_commands.describe(
    pays="Rôle du pays dont le général doit être amélioré"
)
async def amelioration_general(interaction: discord.Interaction, pays: discord.Role):
    """Permet aux admins d'améliorer un trait de commandement d'un général."""
    
    # Vérifier les permissions admin
    if not interaction.user.guild_permissions.administrator and interaction.user.id not in ADMIN_IDS:
        embed = discord.Embed(
            title="❌ Permission refusée",
            description="Cette commande est réservée aux administrateurs.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Vérifier que le rôle est bien un rôle de pays
    def is_country_role(role):
        """Vérifie si un rôle est un rôle de pays en regardant s'il a de l'argent dans le système économique."""
        role_id = str(role.id)
        # Un rôle est considéré comme un pays s'il existe dans le système de balances
        # ou s'il existe dans pays_images (rôles pays créés)
        if role_id in balances:
            return True
        
        # Vérifier aussi dans pays_images pour les rôles pays récemment créés
        pays_images_data = load_pays_images()
        return role_id in pays_images_data
    
    if not is_country_role(pays):
        embed = discord.Embed(
            title="❌ Rôle invalide",
            description=f"Le rôle **{pays.name}** n'est pas reconnu comme un rôle de pays.",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Charger tous les généraux pour trouver ceux du pays
    generaux_data = load_generaux()
    pays_name = pays.name.lower()
    
    # Trouver tous les généraux du pays spécifié
    generaux_pays = []
    for user_id, user_data in generaux_data.items():
        if "generaux" in user_data:
            for nom_general, general_info in user_data["generaux"].items():
                if general_info.get("pays", "").lower() == pays_name:
                    # Vérifier si le général a des traits améliorables
                    traits_ameliorables = []
                    traits_actuels = general_info.get("traits_commandement", [])
                    
                    for trait_ameliore, info_ameliore in TRAITS_AMELIORATION.items():
                        # Vérifier si le général a les prérequis
                        if any(prereq.lower() in [t.lower() for t in traits_actuels] for prereq in info_ameliore["prerequis"]):
                            # Vérifier qu'il n'a pas déjà ce trait amélioré
                            if trait_ameliore.lower() not in [t.lower() for t in traits_actuels]:
                                # Vérifier les exclusions
                                if not any(exclu.lower() in [t.lower() for t in traits_actuels] for exclu in info_ameliore["exclusif"]):
                                    traits_ameliorables.append(trait_ameliore)
                    
                    if traits_ameliorables:
                        generaux_pays.append({
                            "user_id": user_id,
                            "nom": nom_general,
                            "stars": general_info.get("stars", 0),
                            "info": general_info,
                            "traits_ameliorables": traits_ameliorables
                        })
    
    if not generaux_pays:
        embed = discord.Embed(
            title="❌ Aucun général améliorable",
            description=f"Aucun général du pays **{pays.name}** n'a de traits améliorables.\n\n"
                       f"**Pour qu'un trait soit améliorable :**\n"
                       f"• Le général doit avoir le trait prérequis\n"
                       f"• Il ne doit pas déjà avoir le trait amélioré\n"
                       f"• Il ne doit pas avoir de traits exclusifs",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Créer la vue de sélection pour l'amélioration
    view = AmeliorationGeneralView(interaction.user.id, generaux_pays, pays.name)
    
    embed = discord.Embed(
        title="⚡ Amélioration de Général",
        description=f"Sélectionnez le général du pays **{pays.name}** à améliorer :",
        color=EMBED_COLOR
    )
    
    # Ajouter la liste des généraux améliorables
    generaux_list = []
    for general in generaux_pays:
        nb_ameliorations = len(general["traits_ameliorables"])
        generaux_list.append(f"⭐" * general["stars"] + f" **{general['nom']}** ({nb_ameliorations} améliorations possibles)")
    
    embed.add_field(
        name="Généraux améliorables",
        value="\n".join(generaux_list),
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Amélioration de traits",
        value="• Les traits de commandement peuvent être améliorés\n"
              "• L'amélioration remplace le trait de base\n"
              "• Certaines améliorations sont exclusives entre elles",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# === SYSTÈME DE TECHNOLOGIES MILITAIRES ===

# Chemin du fichier pour les développements technologiques
DEVELOPPEMENTS_FILE = os.path.join(DATA_DIR, "developpements.json")

def load_developpements():
    """Charge les développements technologiques depuis le fichier."""
    if not os.path.exists(DEVELOPPEMENTS_FILE):
        return {}
    try:
        with open(DEVELOPPEMENTS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement des développements: {e}")
        return {}

def save_developpements(data):
    """Sauvegarde les développements technologiques dans le fichier."""
    try:
        with open(DEVELOPPEMENTS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        save_all_json_to_postgres()
    except Exception as e:
        print(f"[ERROR] Erreur lors de la sauvegarde des développements: {e}")

# Fonction d'autocomplétion pour les engins selon la catégorie
async def engin_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> typing.List[app_commands.Choice[str]]:
    """Autocomplétion dynamique pour les engins selon la catégorie sélectionnée."""
    
    # Récupérer la catégorie sélectionnée depuis l'interaction
    try:
        # Dans Discord.py, nous devons récupérer la valeur depuis le namespace
        categorie_value = interaction.namespace.categorie if hasattr(interaction, 'namespace') and hasattr(interaction.namespace, 'categorie') else None
        
        if not categorie_value:
            # Si pas de catégorie sélectionnée, montrer toutes les options
            return [
                app_commands.Choice(name="Sélectionnez d'abord une catégorie", value="none")
            ]
        
        # Définir les engins par catégorie
        engins_par_categorie = {
            "vehicules_terrestres": [
                ("char_leger", "Char léger"),
                ("char_moyen", "Char Moyen"),
                ("char_lourd", "Char Lourd"),
                ("ifv", "IFV"),
                ("apc", "APC"),
                ("chasseur_chars", "Chasseur de chars"),
                ("char_super_lourd", "Char super lourd"),
                ("lance_roquettes", "Lance-roquettes multiple"),
            ],
            "artillerie": [
                ("artillerie_campagne", "Artillerie de campagne (70-160mm)"),
                ("artillerie_lourde", "Artillerie lourde (+160mm)"),
                ("artillerie_legere", "Artillerie légère (-70mm)"),
                ("mortier_infanterie", "Mortier d'infanterie (-70mm)"),
                ("mortier_campagne", "Mortier de campagne (70-120mm)"),
                ("mortier_lourd", "Mortier lourd (+120mm)"),
                ("canon_anti_aerien", "Canon anti-aérien"),
                ("canon_anti_char", "Canon anti-char"),
                ("spag", "SPAG"),
            ],
            "batiments_guerre": [
                ("destroyer", "Destroyer"),
                ("cuirasse", "Cuirassé"),
                ("croiseur_leger", "Croiseur léger"),
                ("croiseur_lourd", "Croiseur Lourd"),
                ("fregate", "Frégate"),
                ("porte_helicoptere", "Porte-Hélicoptère"),
                ("porte_avion", "Porte-Avion"),
                ("porte_avion_leger", "Porte-Avion léger"),
                ("porte_avion_nucleaire", "Porte-Avion (Propulsion nucléaire)"),
                ("sous_marin_diesel", "Sous-marin (Diesel)"),
                ("snle", "SNLE"),
                ("sna", "SNA"),
                ("corvette", "Corvette"),
                ("patrouilleur", "Patrouilleur"),
                ("barge_debarquement", "Barge de Débarquement"),
            ],
            "appareils_aeriens": [
                ("avion_multirole", "Avion multirôle"),
                ("avion_attaque_sol", "Avion d'attaque au sol"),
                ("avion_chasse", "Avion de chasse (interception)"),
                ("bombardier_tactique", "Bombardier tactique"),
                ("bombardier_strategique", "Bombardier stratégique"),
                ("avion_reconnaissance", "Avion de reconnaissance"),
                ("avion_transport", "Avion de transport (matériel/troupe)"),
                ("awacs", "AWACS"),
                ("helicoptere_attaque", "Hélicoptère d'attaque"),
                ("helicoptere_reconnaissance", "Hélicoptère de reconnaissance"),
                ("helicoptere_transport", "Hélicoptère de transport"),
                ("drone_reconnaissance", "Drone de reconnaissance"),
                ("drone_suicide", "Drone suicide"),
                ("drone_attaque", "Drone d'Attaque"),
            ],
            "missiles": [
                ("srbm", "SRBM (300-1000km)"),
                ("mrbm", "MRBM (1000-3000km)"),
                ("icbm", "ICBM (+5500km)"),
                ("irbm", "IRBM (3500-5500km)"),
                ("brbm", "BRBM (-300km)"),
                ("sam", "SAM"),
                ("atgm", "ATGM"),
                ("manpads", "MANPADS"),
            ],
        }
        
        # Récupérer les engins pour la catégorie sélectionnée
        engins = engins_par_categorie.get(categorie_value, [])
        
        # Filtrer selon l'input utilisateur et limiter à 25 résultats
        filtered_engins = [
            app_commands.Choice(name=name, value=value)
            for value, name in engins
            if current.lower() in name.lower()
        ][:25]
        
        return filtered_engins
        
    except Exception:
        # En cas d'erreur, retourner les options de base
        return [
            app_commands.Choice(name="Char léger", value="char_leger"),
            app_commands.Choice(name="Destroyer", value="destroyer"),
            app_commands.Choice(name="Avion multirôle", value="avion_multirole"),
            app_commands.Choice(name="SRBM (300-1000km)", value="srbm"),
        ]

@bot.tree.command(name="bilan_techno", description="Génère un bilan technologique avec coûts aléatoires pour développement")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    pays="Rôle (pays) pour lequel générer le bilan technologique",
    nom="Nom à donner à ce développement technologique",
    categorie="Catégorie technologique à développer",
    engin="Type d'engin spécifique à développer",
    image="URL de l'image pour illustrer le développement technologique (optionnel)"
)
@app_commands.choices(categorie=[
    discord.app_commands.Choice(name="Véhicules Terrestres", value="vehicules_terrestres"),
    discord.app_commands.Choice(name="Artillerie", value="artillerie"),
    discord.app_commands.Choice(name="Bâtiments de guerre", value="batiments_guerre"),
    discord.app_commands.Choice(name="Appareils aériens", value="appareils_aeriens"),
    discord.app_commands.Choice(name="Missiles", value="missiles")
])
@app_commands.autocomplete(engin=engin_autocomplete)
async def bilan_techno(interaction: discord.Interaction, pays: discord.Role, nom: str, categorie: str, engin: str, image: str = None):
    """Génère un bilan technologique avec coûts et durées aléatoires pour un engin spécifique."""
    
    await interaction.response.defer()
    
    # Vérifier que l'utilisateur a le rôle pays mentionné
    if pays not in interaction.user.roles:
        embed = discord.Embed(
            title="❌ Accès refusé",
            description=f"Vous devez avoir le rôle {pays.mention} pour générer un bilan technologique pour ce pays.",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    # Données technologiques basées sur le CSV (excluant les armes à feu)
    technologies = {
        "vehicules_terrestres": {
            "name": "Véhicules Terrestres",
            "engins": {
                "char_leger": {"name": "Char léger", "dev_range": (8, 11), "cout_range": (70, 120), "unit_multiplier": 1000, "mois_range": (7, 10)},
                "char_moyen": {"name": "Char Moyen", "dev_range": (8, 13), "cout_range": (130, 200), "unit_multiplier": 1000, "mois_range": (7, 11)},
                "char_lourd": {"name": "Char Lourd", "dev_range": (13, 15), "cout_range": (350, 500), "unit_multiplier": 1000, "mois_range": (10, 15)},
                "ifv": {"name": "IFV", "dev_range": (7, 11), "cout_range": (90, 160), "unit_multiplier": 1000, "mois_range": (7, 13)},
                "apc": {"name": "APC", "dev_range": (6, 10), "cout_range": (80, 145), "unit_multiplier": 1000, "mois_range": (7, 12)},
                "chasseur_chars": {"name": "Chasseur de chars", "dev_range": (11, 17), "cout_range": (135, 200), "unit_multiplier": 1000, "mois_range": (9, 13)},
                "char_super_lourd": {"name": "Char super lourd", "dev_range": (20, 25), "cout_range": (400, 500), "unit_multiplier": 1000, "mois_range": (9, 12)},
                "lance_roquettes": {"name": "Lance-roquettes multiple", "dev_range": (9, 15), "cout_range": (120, 200), "unit_multiplier": 1000, "mois_range": (8, 13)},
            }
        },
        
        "artillerie": {
            "name": "Artillerie",
            "engins": {
                "artillerie_campagne": {"name": "Artillerie de campagne (70-160mm)", "dev_range": (5, 10), "cout_range": (10, 20), "unit_multiplier": 1000, "mois_range": (4, 6)},
                "artillerie_lourde": {"name": "Artillerie lourde (+160mm)", "dev_range": (8, 13), "cout_range": (30, 50), "unit_multiplier": 1000, "mois_range": (5, 8)},
                "artillerie_legere": {"name": "Artillerie légère (-70mm)", "dev_range": (3, 5), "cout_range": (5, 10), "unit_multiplier": 1000, "mois_range": (3, 5)},
                "mortier_infanterie": {"name": "Mortier d'infanterie (-70mm)", "dev_range": (4, 6), "cout_range": (700, 900), "unit_multiplier": 1, "mois_range": (3, 6)},
                "mortier_campagne": {"name": "Mortier de campagne (70-120mm)", "dev_range": (5, 8), "cout_range": (800, 1000), "unit_multiplier": 1, "mois_range": (4, 7)},
                "mortier_lourd": {"name": "Mortier lourd (+120mm)", "dev_range": (5, 10), "cout_range": (1000, 1500), "unit_multiplier": 1, "mois_range": (6, 9)},
                "canon_anti_aerien": {"name": "Canon anti-aérien", "dev_range": (3, 5), "cout_range": (5, 15), "unit_multiplier": 1000, "mois_range": (3, 6)},
                "canon_anti_char": {"name": "Canon anti-char", "dev_range": (3, 5), "cout_range": (5, 15), "unit_multiplier": 1000, "mois_range": (3, 6)},
                "spag": {"name": "SPAG", "dev_range": (9, 15), "cout_range": (150, 300), "unit_multiplier": 1000, "mois_range": (7, 12)},
            }
        },
        
        "batiments_guerre": {
            "name": "Bâtiments de guerre",
            "engins": {
                "destroyer": {"name": "Destroyer", "dev_range": (20, 25), "cout_range": (500, 1000), "unit_multiplier": 1000, "mois_range": (6, 12)},
                "cuirasse": {"name": "Cuirassé", "dev_range": (40, 50), "cout_range": (2, 5), "unit_multiplier": 1000000, "mois_range": (10, 15)},
                "croiseur_leger": {"name": "Croiseur léger", "dev_range": (30, 35), "cout_range": (800, 1500), "unit_multiplier": 1000, "mois_range": (8, 12)},
                "croiseur_lourd": {"name": "Croiseur Lourd", "dev_range": (40, 45), "cout_range": (1, 2), "unit_multiplier": 1000000, "mois_range": (10, 15)},
                "fregate": {"name": "Frégate", "dev_range": (15, 20), "cout_range": (300, 700), "unit_multiplier": 1000, "mois_range": (6, 10)},
                "porte_helicoptere": {"name": "Porte-Hélicoptère", "dev_range": (35, 45), "cout_range": (2, 5), "unit_multiplier": 1000000, "mois_range": (10, 15)},
                "porte_avion": {"name": "Porte-Avion", "dev_range": (50, 80), "cout_range": (5, 10), "unit_multiplier": 1000000, "mois_range": (10, 18)},
                "porte_avion_leger": {"name": "Porte-Avion léger", "dev_range": (25, 40), "cout_range": (2, 4), "unit_multiplier": 1000000, "mois_range": (10, 15)},
                "porte_avion_nucleaire": {"name": "Porte-Avion (Propulsion nucléaire)", "dev_range": (100, 150), "cout_range": (50, 80), "unit_multiplier": 1000000, "mois_range": (24, 24)},
                "sous_marin_diesel": {"name": "Sous-marin (Diesel)", "dev_range": (15, 30), "cout_range": (500, 2000), "unit_multiplier": 1000, "mois_range": (8, 15)},
                "snle": {"name": "SNLE", "dev_range": (30, 70), "cout_range": (10, 30), "unit_multiplier": 1000000, "mois_range": (10, 18)},
                "sna": {"name": "SNA", "dev_range": (30, 70), "cout_range": (10, 30), "unit_multiplier": 1000000, "mois_range": (10, 18)},
                "corvette": {"name": "Corvette", "dev_range": (20, 30), "cout_range": (400, 800), "unit_multiplier": 1000, "mois_range": (6, 10)},
                "patrouilleur": {"name": "Patrouilleur", "dev_range": (5, 10), "cout_range": (100, 500), "unit_multiplier": 1000, "mois_range": (3, 5)},
                "barge_debarquement": {"name": "Barge de Débarquement", "dev_range": (2, 5), "cout_range": (100, 300), "unit_multiplier": 1000, "mois_range": (3, 5)},
            }
        },
        
        "appareils_aeriens": {
            "name": "Appareils aériens",
            "engins": {
                "avion_multirole": {"name": "Avion multirôle", "dev_range": (10, 15), "cout_range": (350, 700), "unit_multiplier": 1000, "mois_range": (8, 12)},
                "avion_attaque_sol": {"name": "Avion d'attaque au sol", "dev_range": (10, 20), "cout_range": (300, 600), "unit_multiplier": 1000, "mois_range": (6, 12)},
                "avion_chasse": {"name": "Avion de chasse (interception)", "dev_range": (10, 20), "cout_range": (300, 600), "unit_multiplier": 1000, "mois_range": (6, 12)},
                "bombardier_tactique": {"name": "Bombardier tactique", "dev_range": (20, 25), "cout_range": (500, 700), "unit_multiplier": 1000, "mois_range": (8, 12)},
                "bombardier_strategique": {"name": "Bombardier stratégique", "dev_range": (30, 35), "cout_range": (750, 1000), "unit_multiplier": 1000, "mois_range": (10, 12)},
                "avion_reconnaissance": {"name": "Avion de reconnaissance", "dev_range": (5, 10), "cout_range": (200, 300), "unit_multiplier": 1000, "mois_range": (6, 9)},
                "avion_transport": {"name": "Avion de transport (matériel/troupe)", "dev_range": (10, 20), "cout_range": (500, 700), "unit_multiplier": 1000, "mois_range": (6, 12)},
                "awacs": {"name": "AWACS", "dev_range": (10, 20), "cout_range": (300, 500), "unit_multiplier": 1000, "mois_range": (6, 12)},
                "helicoptere_attaque": {"name": "Hélicoptère d'attaque", "dev_range": (9, 15), "cout_range": (100, 300), "unit_multiplier": 1000, "mois_range": (6, 12)},
                "helicoptere_reconnaissance": {"name": "Hélicoptère de reconnaissance", "dev_range": (5, 10), "cout_range": (75, 200), "unit_multiplier": 1000, "mois_range": (6, 9)},
                "helicoptere_transport": {"name": "Hélicoptère de transport", "dev_range": (9, 15), "cout_range": (200, 400), "unit_multiplier": 1000, "mois_range": (6, 12)},
                "drone_reconnaissance": {"name": "Drone de reconnaissance", "dev_range": (3, 5), "cout_range": (150, 500), "unit_multiplier": 1000, "mois_range": (3, 6)},
                "drone_suicide": {"name": "Drone suicide", "dev_range": (1, 2), "cout_range": (10, 30), "unit_multiplier": 1000, "mois_range": (3, 6)},
                "drone_attaque": {"name": "Drone d'Attaque", "dev_range": (5, 15), "cout_range": (300, 1000), "unit_multiplier": 1000, "mois_range": (6, 12)},
            }
        },
        
        "missiles": {
            "name": "Missiles",
            "engins": {
                "srbm": {"name": "SRBM (300-1000km)", "dev_range": (20, 25), "cout_range": (500, 2000), "unit_multiplier": 1000, "mois_range": (8, 15)},
                "mrbm": {"name": "MRBM (1000-3000km)", "dev_range": (35, 50), "cout_range": (5, 20), "unit_multiplier": 1000000, "mois_range": (12, 18)},
                "icbm": {"name": "ICBM (+5500km)", "dev_range": (150, 300), "cout_range": (50, 50), "unit_multiplier": 1000000, "mois_range": (24, 24)},
                "irbm": {"name": "IRBM (3500-5500km)", "dev_range": (50, 75), "cout_range": (25, 25), "unit_multiplier": 1000000, "mois_range": (12, 24)},
                "brbm": {"name": "BRBM (-300km)", "dev_range": (15, 20), "cout_range": (500, 1500), "unit_multiplier": 1000, "mois_range": (8, 12)},
                "sam": {"name": "SAM", "dev_range": (20, 25), "cout_range": (500, 2000), "unit_multiplier": 1000, "mois_range": (8, 15)},
                "atgm": {"name": "ATGM", "dev_range": (5, 7), "cout_range": (1500, 2000), "unit_multiplier": 1, "mois_range": (5, 8)},
                "manpads": {"name": "MANPADS", "dev_range": (5, 8), "cout_range": (1700, 2200), "unit_multiplier": 1, "mois_range": (5, 8)},
            }
        }
    }
    
    # Vérifier que la catégorie existe
    if categorie not in technologies:
        embed = discord.Embed(
            title="❌ Erreur",
            description="Catégorie technologique non trouvée.",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    # Vérifier que l'engin existe dans la catégorie
    if engin not in technologies[categorie]["engins"]:
        embed = discord.Embed(
            title="❌ Erreur",
            description=f"Engin non trouvé dans la catégorie {technologies[categorie]['name']}.",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    # Récupérer les spécifications de l'engin
    import random
    engin_specs = technologies[categorie]["engins"][engin]
    
    # Générer les valeurs aléatoires
    cout_dev = random.randint(engin_specs["dev_range"][0], engin_specs["dev_range"][1]) * 1000000  # En millions
    cout_unite = random.randint(engin_specs["cout_range"][0], engin_specs["cout_range"][1]) * engin_specs["unit_multiplier"]
    mois = random.randint(engin_specs["mois_range"][0], engin_specs["mois_range"][1])
    
    # Créer l'embed de résultat
    embed = discord.Embed(
        title="📊 Bilan Technologique Militaire",
        description=f"**Pays :** {pays.mention}\n"
                   f"**Nom :** {nom}\n"
                   f"**Catégorie :** {technologies[categorie]['name']}\n"
                   f"**Technologie :** {engin_specs['name']}\n"
                   f"**Généré pour :** {interaction.user.mention}",
        color=EMBED_COLOR,
        timestamp=datetime.datetime.now()
    )
    
    if image:
        embed.set_image(url=image)
    
    # Ajouter les détails techniques
    embed.add_field(
        name="💰 Coût de développement",
        value=f"{format_number(cout_dev)} {MONNAIE_EMOJI}",
        inline=True
    )
    
    embed.add_field(
        name="🏭 Prix unitaire",
        value=f"{format_unit_cost(cout_unite, engin_specs['unit_multiplier'])} {MONNAIE_EMOJI}",
        inline=True
    )
    
    embed.add_field(
        name="⏱️ Durée de développement",
        value=f"{mois} mois",
        inline=True
    )
    
    embed.add_field(
        name="ℹ️ Informations",
        value=f"*Coûts générés par le Bot selon le Tableur*\n\n"
              f"**Fourchette de Coût de Développement :**\n"
              f"- {engin_specs['dev_range'][0]} / {engin_specs['dev_range'][1]} millions\n\n"
              f"**Fourchette de Coût à l'Unité :**\n"
              f"- {format_unit_range(engin_specs['cout_range'][0], engin_specs['cout_range'][1], engin_specs['unit_multiplier'])}",
        inline=False
    )
    
    # Créer la vue avec le bouton de confirmation
    view = TechnoConfirmView(interaction.user.id, pays, cout_dev, engin_specs['name'], nom, categorie, technologies[categorie]['name'], cout_unite, mois, image, engin_specs['unit_multiplier'])
    
    await interaction.followup.send(embed=embed, view=view)

# === COMMANDE POUR VOIR LES DÉVELOPPEMENTS ===

# Vue pour la sélection de catégorie dans /developpements
class DeveloppementsCategorieView(discord.ui.View):
    def __init__(self, user_id, pays_roles, developpements_data):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.pays_roles = pays_roles  # Liste des rôles pays de l'utilisateur
        self.developpements_data = developpements_data
        
        # Créer les boutons pour chaque catégorie disponible
        categories_disponibles = set()
        for role_id in [str(role.id) for role in pays_roles]:
            if role_id in developpements_data:
                # Nouvelle structure : developpements_data[role_id] est une liste
                if isinstance(developpements_data[role_id], list):
                    # Extraire les catégories des développements dans la liste
                    for dev in developpements_data[role_id]:
                        if isinstance(dev, dict) and "categorie" in dev:
                            categories_disponibles.add(dev["categorie"])
                else:
                    # Ancienne structure : developpements_data[role_id] est un dict
                    categories_disponibles.update(developpements_data[role_id].keys())
        
        if not categories_disponibles:
            return
        
        # Mapping des noms de catégories
        categories_noms = {
            "vehicules_terrestres": "Véhicules Terrestres",
            "artillerie": "Artillerie",
            "batiments_guerre": "Bâtiments de guerre",
            "appareils_aeriens": "Appareils aériens",
            "missiles": "Missiles"
        }
        
        for i, categorie in enumerate(sorted(categories_disponibles)):
            nom_categorie = categories_noms.get(categorie, categorie)
            button = discord.ui.Button(
                label=nom_categorie,
                custom_id=f"cat_{categorie}",
                style=discord.ButtonStyle.primary,
                row=i // 5  # 5 boutons par ligne max
            )
            button.callback = self.categorie_callback
            self.add_item(button)
    
    async def categorie_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'initiateur peut naviguer.", ephemeral=True)
            return
        
        categorie = interaction.data['custom_id'].replace('cat_', '')
        
        # Créer la vue de navigation des développements
        view = DeveloppementsNavigationView(self.user_id, self.pays_roles, self.developpements_data, categorie, 0)
        embed = view.create_embed()
        
        await interaction.response.edit_message(embed=embed, view=view)

# Vue pour la navigation des développements dans une catégorie
class DeveloppementsNavigationView(discord.ui.View):
    def __init__(self, user_id, pays_roles, developpements_data, categorie, page):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.pays_roles = pays_roles
        self.developpements_data = developpements_data
        self.categorie = categorie
        self.page = page
        
        # Collecter tous les développements de cette catégorie
        self.all_developpements = []
        for role in pays_roles:
            role_id = str(role.id)
            if role_id in developpements_data:
                # Nouvelle structure : developpements_data[role_id] est une liste
                if isinstance(developpements_data[role_id], list):
                    for dev in developpements_data[role_id]:
                        if isinstance(dev, dict) and dev.get("categorie") == categorie:
                            dev_copy = dev.copy()
                            dev_copy['role'] = role
                            self.all_developpements.append(dev_copy)
                else:
                    # Ancienne structure : developpements_data[role_id] est un dict
                    if categorie in developpements_data[role_id]:
                        for dev in developpements_data[role_id][categorie]:
                            dev_copy = dev.copy()
                            dev_copy['role'] = role
                            self.all_developpements.append(dev_copy)
        
        # Ajouter les boutons de navigation
        if len(self.all_developpements) > 1:
            self.add_navigation_buttons()
        
        # Bouton retour
        retour_button = discord.ui.Button(label="← Retour aux catégories", style=discord.ButtonStyle.secondary)
        retour_button.callback = self.retour_callback
        self.add_item(retour_button)
    
    def add_navigation_buttons(self):
        # Bouton précédent
        prev_button = discord.ui.Button(emoji="⬅️", style=discord.ButtonStyle.secondary, disabled=self.page == 0)
        prev_button.callback = self.prev_callback
        self.add_item(prev_button)
        
        # Bouton suivant
        next_button = discord.ui.Button(emoji="➡️", style=discord.ButtonStyle.secondary, disabled=self.page >= len(self.all_developpements) - 1)
        next_button.callback = self.next_callback
        self.add_item(next_button)
    
    def create_embed(self):
        if not self.all_developpements:
            return discord.Embed(
                title="📋 Développements Technologiques",
                description="Aucun développement trouvé dans cette catégorie.",
                color=EMBED_COLOR
            )
        
        dev = self.all_developpements[self.page]
        categories_noms = {
            "vehicules_terrestres": "Véhicules Terrestres",
            "artillerie": "Artillerie",
            "batiments_guerre": "Bâtiments de guerre",
            "appareils_aeriens": "Appareils aériens",
            "missiles": "Missiles"
        }
        
        embed = discord.Embed(
            title="📋 Développements Technologiques",
            description=f"**Catégorie :** {categories_noms.get(self.categorie, self.categorie)}\n"
                       f"**Page :** {self.page + 1}/{len(self.all_developpements)}",
            color=EMBED_COLOR,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="🏷️ Nom du développement",
            value=dev['nom'],
            inline=True
        )
        
        embed.add_field(
            name="🔧 Technologie",
            value=dev['technologie'],
            inline=True
        )
        
        embed.add_field(
            name="🏛️ Pays",
            value=dev['role'].mention,
            inline=True
        )
        
        embed.add_field(
            name="💰 Coût de développement",
            value=f"{format_number(dev['cout_dev'])} {MONNAIE_EMOJI}",
            inline=True
        )
        
        embed.add_field(
            name="🏭 Prix unitaire",
            value=f"{format_unit_cost(dev['cout_unite'], dev.get('unit_multiplier', 1000))} {MONNAIE_EMOJI}",
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Durée",
            value=f"{dev['mois']} mois",
            inline=True
        )
        
        # Ajouter les informations de fin avec le nouveau système de statut
        statut = dev.get('statut', 'en_cours')
        fin_timestamp = dev.get('fin_timestamp', 0)
        
        if statut == 'termine':
            # Développement marqué comme terminé
            date_fin_reelle = dev.get('date_fin_reelle')
            if date_fin_reelle:
                try:
                    date_formatee = format_paris_time(date_fin_reelle)
                    embed.add_field(
                        name="✅ Statut",
                        value=f"**TERMINÉ** (le {date_formatee})",
                        inline=False
                    )
                except:
                    embed.add_field(
                        name="✅ Statut",
                        value="**TERMINÉ**",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="✅ Statut",
                    value="**TERMINÉ**",
                    inline=False
                )
        elif fin_timestamp > 0:
            if fin_timestamp > time.time():
                # Développement en cours
                calendrier_data = load_calendrier()
                if calendrier_data:
                    mois_fin, annee_fin = get_rp_date_from_timestamp(fin_timestamp)
                    if mois_fin is not None and annee_fin is not None:
                        nom_mois = CALENDRIER_MONTHS[mois_fin] if mois_fin < len(CALENDRIER_MONTHS) else "Mois inconnu"
                        discord_timestamp = format_discord_timestamp(fin_timestamp)
                        embed.add_field(
                            name="⏳ En cours - Date de fin",
                            value=f"**RP :** {nom_mois} {annee_fin}\n**IRL :** {discord_timestamp}",
                            inline=False
                        )
                    else:
                        discord_timestamp = format_discord_timestamp(fin_timestamp)
                        embed.add_field(
                            name="⏳ En cours - Date de fin",
                            value=discord_timestamp,
                            inline=False
                        )
                else:
                    discord_timestamp = format_discord_timestamp(fin_timestamp)
                    embed.add_field(
                        name="⏳ En cours - Date de fin",
                        value=discord_timestamp,
                        inline=False
                    )
            else:
                # Développement dont le délai est dépassé mais pas encore marqué comme terminé
                embed.add_field(
                    name="⚠️ Statut",
                    value="**À TERMINER** (délai dépassé)",
                    inline=False
                )
        else:
            # Pas de timestamp
            embed.add_field(
                name="🔄 Statut",
                value="**EN COURS** (pas de délai défini)",
                inline=False
            )
        
        # Ajouter le centre attaché si disponible
        if dev.get('centre_attache'):
            embed.add_field(
                name="🏭 Centre de recherche",
                value=dev['centre_attache'],
                inline=True
            )
        
        if dev.get('date_creation'):
            try:
                date_creation = datetime.datetime.fromisoformat(dev['date_creation'])
                embed.add_field(
                    name="📅 Date de création",
                    value=date_creation.strftime("%d/%m/%Y à %H:%M"),
                    inline=False
                )
            except:
                pass
        
        if dev.get('image'):
            embed.set_image(url=dev['image'])
        
        return embed
    
    async def prev_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'initiateur peut naviguer.", ephemeral=True)
            return
        
        if self.page > 0:
            new_view = DeveloppementsNavigationView(self.user_id, self.pays_roles, self.developpements_data, self.categorie, self.page - 1)
            embed = new_view.create_embed()
            await interaction.response.edit_message(embed=embed, view=new_view)
    
    async def next_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'initiateur peut naviguer.", ephemeral=True)
            return
        
        if self.page < len(self.all_developpements) - 1:
            new_view = DeveloppementsNavigationView(self.user_id, self.pays_roles, self.developpements_data, self.categorie, self.page + 1)
            embed = new_view.create_embed()
            await interaction.response.edit_message(embed=embed, view=new_view)
    
    async def retour_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'initiateur peut naviguer.", ephemeral=True)
            return
        
        # Retourner à la sélection de catégorie
        view = DeveloppementsCategorieView(self.user_id, self.pays_roles, self.developpements_data)
        
        embed = discord.Embed(
            title="📋 Développements Technologiques",
            description="Sélectionnez une catégorie pour voir vos développements :",
            color=EMBED_COLOR
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

@bot.tree.command(name="developpements", description="Affiche vos développements technologiques")
async def developpements(interaction: discord.Interaction):
    """Affiche les développements technologiques de l'utilisateur."""
    
    await interaction.response.defer(ephemeral=True)
    
    # Charger les développements
    developpements_data = load_developpements()
    guild_id = str(interaction.guild.id)
    
    if guild_id not in developpements_data:
        embed = discord.Embed(
            title="📋 Développements Technologiques",
            description="Aucun développement technologique trouvé sur ce serveur.",
            color=EMBED_COLOR
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Trouver les rôles pays de l'utilisateur
    pays_roles = []
    for role in interaction.user.roles:
        role_id = str(role.id)
        if role_id in developpements_data[guild_id]:
            pays_roles.append(role)
    
    if not pays_roles:
        embed = discord.Embed(
            title="📋 Développements Technologiques",
            description="Vous n'avez aucun développement technologique.",
            color=EMBED_COLOR
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Créer la vue de sélection de catégorie
    view = DeveloppementsCategorieView(interaction.user.id, pays_roles, developpements_data[guild_id])
    
    embed = discord.Embed(
        title="📋 Développements Technologiques",
        description="Sélectionnez une catégorie pour voir vos développements :",
        color=EMBED_COLOR
    )
    
    await interaction.followup.send(embed=embed, view=view)

# === COMMANDES CENTRES TECHNOLOGIQUES ===

@bot.tree.command(name="centre_tech", description="Créer un centre technologique")
@app_commands.describe(
    nom="Nom du centre technologique",
    localisation="Localisation géographique du centre",
    specialisation="Spécialisation du centre technologique"
)
@app_commands.choices(specialisation=[
    discord.app_commands.Choice(name="Terrestre", value="Terrestre"),
    discord.app_commands.Choice(name="Aérien", value="Aérien"),
    discord.app_commands.Choice(name="Marine", value="Marine"),
    discord.app_commands.Choice(name="Armes de Destruction Massive", value="Armes de Destruction Massive"),
    discord.app_commands.Choice(name="Spatial", value="Spatial")
])
async def centre_tech(interaction: discord.Interaction, nom: str, localisation: str, specialisation: str):
    """Crée un nouveau centre technologique."""
    await interaction.response.defer()
    
    # Vérifier que l'utilisateur a un rôle pays
    user_roles = [r for r in interaction.user.roles if str(r.id) in balances]
    if not user_roles:
        # Essayer de trouver dans pays_images
        pays_images_data = load_pays_images()
        user_roles = [r for r in interaction.user.roles if str(r.id) in pays_images_data]
    
    if not user_roles:
        await interaction.followup.send("> Vous devez avoir un rôle pays pour créer un centre technologique.", ephemeral=True)
        return
    
    pays_role = user_roles[0]
    pays_id = str(pays_role.id)
    
    # Vérifier le budget
    if pays_id not in balances:
        balances[pays_id] = 0
    
    budget_actuel = balances[pays_id]
    if budget_actuel < CENTRE_COUT_BASE:
        await interaction.followup.send(
            f"> Fonds insuffisants ! Coût : {format_number(CENTRE_COUT_BASE)} {MONNAIE_EMOJI}, "
            f"Budget actuel : {format_number(budget_actuel)} {MONNAIE_EMOJI}",
            ephemeral=True
        )
        return
    
    # Charger les centres existants
    centres_data = load_centres_tech()
    guild_id = str(interaction.guild.id)
    
    if guild_id not in centres_data:
        centres_data[guild_id] = {}
    if pays_id not in centres_data[guild_id]:
        centres_data[guild_id][pays_id] = []
    
    # Vérifier si un centre avec ce nom existe déjà
    for centre in centres_data[guild_id][pays_id]:
        if centre.get("nom", centre.get("localisation", "")).lower() == nom.lower():
            await interaction.followup.send(f"> Un centre technologique nommé **{nom}** existe déjà.", ephemeral=True)
            return
    
    # Créer le centre
    nouveau_centre = {
        "nom": nom,
        "localisation": localisation,
        "specialisation": specialisation,
        "niveau": 1,
        "emplacements_max": get_centre_emplacements(1),
        "developpements": [],  # Technologies en développement dans ce centre
        "date_creation": int(time.time())
    }
    
    centres_data[guild_id][pays_id].append(nouveau_centre)
    
    # Déduire le coût
    balances[pays_id] -= CENTRE_COUT_BASE
    save_balances(balances)
    save_centres_tech(centres_data)
    
    # Embed de confirmation
    embed = discord.Embed(
        title="🏭 Centre Technologique Créé",
        description=(
            f"⠀\n"
            f"> 🏷️ **Nom :** {nom}\n"
            f"> 📍 **Localisation :** {localisation}\n"
            f"> 🔬 **Spécialisation :** {specialisation}\n"
            f"> 📊 **Niveau :** 1\n"
            f"> 🔧 **Emplacements :** {nouveau_centre['emplacements_max']}\n"
            f"> 💰 **Coût :** {format_number(CENTRE_COUT_BASE)} {MONNAIE_EMOJI}\n"
            f"> 💳 **Budget restant :** {format_number(balances[pays_id])} {MONNAIE_EMOJI}\n⠀"
        ),
        color=0x00ff00
    )
    
    await interaction.followup.send(embed=embed)

async def centre_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """Auto-complétion pour les centres technologiques."""
    # Vérifier que l'utilisateur a un rôle pays
    user_roles = [r for r in interaction.user.roles if str(r.id) in balances]
    if not user_roles:
        pays_images_data = load_pays_images()
        user_roles = [r for r in interaction.user.roles if str(r.id) in pays_images_data]
    
    if not user_roles:
        return []
    
    pays_id = str(user_roles[0].id)
    guild_id = str(interaction.guild.id)
    
    # Charger les centres
    centres_data = load_centres_tech()
    if guild_id not in centres_data or pays_id not in centres_data[guild_id]:
        return []
    
    choices = []
    for centre in centres_data[guild_id][pays_id]:
        nom_centre = centre.get("nom", centre.get("localisation", "Centre"))
        if current.lower() in nom_centre.lower():
            choices.append(app_commands.Choice(name=nom_centre, value=nom_centre))
    
    return choices[:25]  # Limiter à 25 résultats

@bot.tree.command(name="amelioration", description="Améliorer un centre technologique")
@app_commands.describe(centre="Nom du centre à améliorer")
@app_commands.autocomplete(centre=centre_autocomplete)
async def amelioration(interaction: discord.Interaction, centre: str):
    """Améliore un centre technologique."""
    await interaction.response.defer()
    
    # Vérifier que l'utilisateur a un rôle pays
    user_roles = [r for r in interaction.user.roles if str(r.id) in balances]
    if not user_roles:
        pays_images_data = load_pays_images()
        user_roles = [r for r in interaction.user.roles if str(r.id) in pays_images_data]
    
    if not user_roles:
        await interaction.followup.send("> Vous devez avoir un rôle pays pour améliorer un centre.", ephemeral=True)
        return
    
    pays_role = user_roles[0]
    pays_id = str(pays_role.id)
    
    # Charger les centres
    centres_data = load_centres_tech()
    guild_id = str(interaction.guild.id)
    
    if guild_id not in centres_data or pays_id not in centres_data[guild_id]:
        await interaction.followup.send("> Vous n'avez aucun centre technologique.", ephemeral=True)
        return
    
    # Trouver le centre
    centre_trouve = None
    for c in centres_data[guild_id][pays_id]:
        # Chercher par nom en priorité, sinon par localisation pour compatibilité
        nom_centre = c.get("nom", c.get("localisation", ""))
        if nom_centre.lower() == centre.lower():
            centre_trouve = c
            break
    
    if not centre_trouve:
        await interaction.followup.send(f"> Centre technologique **{centre}** introuvable.", ephemeral=True)
        return
    
    # Vérifier le niveau maximum
    if centre_trouve["niveau"] >= 3:
        await interaction.followup.send(f"> Le centre **{centre}** est déjà au niveau maximum (3).", ephemeral=True)
        return
    
    # Vérifier le budget
    cout_amelioration = get_centre_cout_amelioration(centre_trouve["niveau"])
    budget_actuel = balances.get(pays_id, 0)
    
    if budget_actuel < cout_amelioration:
        await interaction.followup.send(
            f"> Fonds insuffisants ! Coût d'amélioration : {format_number(cout_amelioration)} {MONNAIE_EMOJI}, "
            f"Budget actuel : {format_number(budget_actuel)} {MONNAIE_EMOJI}",
            ephemeral=True
        )
        return
    
    # Effectuer l'amélioration
    ancien_niveau = centre_trouve["niveau"]
    centre_trouve["niveau"] += 1
    centre_trouve["emplacements_max"] = get_centre_emplacements(centre_trouve["niveau"])
    
    # Déduire le coût
    balances[pays_id] -= cout_amelioration
    save_balances(balances)
    save_centres_tech(centres_data)
    
    # Déterminer les effets de l'amélioration
    effets = []
    if centre_trouve["niveau"] == 2:
        effets.append("+1 emplacement de recherche")
    elif centre_trouve["niveau"] == 3:
        effets.append("+1 emplacement de recherche")
        effets.append("Réduction de 1 mois pour les développements")
    
    # Embed de confirmation
    embed = discord.Embed(
        title="⬆️ Centre Technologique Amélioré",
        description=(
            f"⠀\n"
            f"> 📍 **Centre :** {centre_trouve['localisation']}\n"
            f"> 📊 **Niveau :** {ancien_niveau} → {centre_trouve['niveau']}\n"
            f"> 🔧 **Emplacements :** {get_centre_emplacements(ancien_niveau)} → {centre_trouve['emplacements_max']}\n"
            f"> ✨ **Nouveaux effets :**\n" + 
            "\n".join(f"> • {effet}" for effet in effets) + "\n"
            f"> 💰 **Coût :** {format_number(cout_amelioration)} {MONNAIE_EMOJI}\n"
            f"> 💳 **Budget restant :** {format_number(balances[pays_id])} {MONNAIE_EMOJI}\n⠀"
        ),
        color=0x0099ff
    )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="gestion_centres", description="Gérer vos centres technologiques")
async def gestion_centres(interaction: discord.Interaction):
    """Affiche la gestion des centres technologiques."""
    await interaction.response.defer(ephemeral=True)
    
    # Vérifier que l'utilisateur a un rôle pays
    user_roles = [r for r in interaction.user.roles if str(r.id) in balances]
    if not user_roles:
        pays_images_data = load_pays_images()
        user_roles = [r for r in interaction.user.roles if str(r.id) in pays_images_data]
    
    if not user_roles:
        await interaction.followup.send("> Vous devez avoir un rôle pays pour gérer les centres.", ephemeral=True)
        return
    
    pays_role = user_roles[0]
    pays_id = str(pays_role.id)
    
    # Charger les centres et développements
    centres_data = load_centres_tech()
    developpements_data = load_developpements()
    guild_id = str(interaction.guild.id)
    
    if guild_id not in centres_data or pays_id not in centres_data[guild_id]:
        embed = discord.Embed(
            title="🏭 Gestion des Centres Technologiques",
            description="⠀\n> Vous n'avez aucun centre technologique.\n> Utilisez `/centre_tech` pour en créer un.\n⠀",
            color=EMBED_COLOR
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    centres = centres_data[guild_id][pays_id]
    
    # Construire l'affichage
    description = "⠀\n"
    
    for i, centre in enumerate(centres, 1):
        # Compter les développements en cours dans ce centre (seulement ceux en cours)
        developpements_en_cours = []
        if guild_id in developpements_data and pays_id in developpements_data[guild_id]:
            for dev in developpements_data[guild_id][pays_id]:
                centre_nom = centre.get("nom", centre.get("localisation", ""))
                if (dev.get("centre_attache") == centre_nom and 
                    dev.get("statut", "en_cours") == "en_cours"):
                    developpements_en_cours.append(dev)
        
        emplacements_utilises = len(developpements_en_cours)
        emplacements_max = centre["emplacements_max"]
        
        nom_centre = centre.get("nom", centre.get("localisation", f"Centre {i}"))
        description += f"> **{i}. {nom_centre}**\n"
        if centre.get("nom") and centre.get("localisation"):
            description += f"> 📍 Localisation : {centre['localisation']}\n"
        description += f"> 🔬 Spécialisation : {centre['specialisation']}\n"
        description += f"> 📊 Niveau : {centre['niveau']}/3\n"
        description += f"> 🔧 Emplacements : {emplacements_utilises}/{emplacements_max}\n"
        
        if developpements_en_cours:
            description += f"> 🚧 **Développements en cours :**\n"
            for dev in developpements_en_cours:
                fin_timestamp = dev.get('fin_timestamp', 0)
                if fin_timestamp > time.time():
                    # Calculer la date RP de fin
                    calendrier_data = load_calendrier()
                    if calendrier_data:
                        mois_fin, annee_fin = get_rp_date_from_timestamp(fin_timestamp)
                        if mois_fin is not None and annee_fin is not None:
                            nom_mois = CALENDRIER_MONTHS[mois_fin] if mois_fin < len(CALENDRIER_MONTHS) else "Mois inconnu"
                            discord_timestamp = format_discord_timestamp(fin_timestamp)
                            description += f"> • **{dev['nom']}**\n"
                            description += f">   📅 Fin RP: {nom_mois} {annee_fin}\n"
                            description += f">   🕐 Fin IRL: {discord_timestamp}\n"
                        else:
                            temps_restant = fin_timestamp - time.time()
                            jours = int(temps_restant // 86400)
                            heures = int((temps_restant % 86400) // 3600)
                            description += f"> • {dev['nom']} (fin dans {jours}j {heures}h)\n"
                    else:
                        temps_restant = fin_timestamp - time.time()
                        jours = int(temps_restant // 86400)
                        heures = int((temps_restant % 86400) // 3600)
                        discord_timestamp = format_discord_timestamp(fin_timestamp)
                        description += f"> • **{dev['nom']}**\n"
                        description += f">   ⏰ Fin dans {jours}j {heures}h\n"
                        description += f">   🕐 Date: {discord_timestamp}\n"
                else:
                    description += f"> • {dev['nom']} (✅ Terminé)\n"
        else:
            description += f"> 💤 Aucun développement en cours\n"
        
        if centre["niveau"] < 3:
            cout = get_centre_cout_amelioration(centre["niveau"])
            description += f"> 💰 Amélioration : {format_number(cout)} {MONNAIE_EMOJI}\n"
        
        description += "⠀\n"
    
    embed = discord.Embed(
        title="🏭 Gestion des Centres Technologiques",
        description=description,
        color=EMBED_COLOR
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

def is_development_completed_by_calendar(dev, calendrier_data):
    """
    Détermine si un développement est terminé selon le calendrier RP actuel
    au lieu du temps réel IRL
    """
    if not calendrier_data or not isinstance(dev, dict):
        return False
    
    # Récupérer les données du développement
    date_creation = dev.get('date_creation')
    duree_mois = dev.get('mois', 0)
    
    if not date_creation or duree_mois <= 0:
        return False
    
    try:
        # Convertir la date de création en datetime
        date_creation_dt = datetime.datetime.fromisoformat(date_creation)
        
        # Calculer le mois et l'année de création selon le calendrier RP
        # On suppose que le développement a été créé au mois actuel du calendrier
        # quand il a été créé
        
        # Récupérer l'état actuel du calendrier
        mois_actuel = calendrier_data.get("mois_index", 0)
        annee_actuelle = calendrier_data.get("annee", 2025)
        
        # Calculer combien de mois se sont écoulés depuis la création
        # Si le développement a été créé récemment, on calcule depuis quand
        # Sinon, on utilise la durée prévue
        
        # Pour simplifier : si le calendrier actuel a avancé de plus de mois
        # que la durée du développement depuis sa création logique, alors il est terminé
        
        # Récupérer les métadonnées du développement si disponibles
        mois_creation = dev.get('mois_creation_rp')
        annee_creation = dev.get('annee_creation_rp')
        
        # Si pas de métadonnées, estimer à partir de la date
        if mois_creation is None or annee_creation is None:
            # Estimer que le développement a été créé il y a quelques mois
            # En mars 2025 pour les tests existants
            mois_creation = 2  # Mars (index 2)
            annee_creation = 2025
        
        # Calculer combien de mois se sont écoulés
        mois_ecoules = (annee_actuelle - annee_creation) * 12 + (mois_actuel - mois_creation)
        
        # Le développement est terminé si plus de mois se sont écoulés que sa durée
        return mois_ecoules >= duree_mois
        
    except:
        # En cas d'erreur, utiliser la méthode par timestamp
        fin_timestamp = dev.get('fin_timestamp', 0)
        if fin_timestamp > 0:
            return fin_timestamp <= time.time()
        return False

def check_and_complete_developments(guild_id):
    """
    Vérifie tous les développements en cours et marque comme terminés ceux qui sont finis
    selon la logique du calendrier RP (plus précise que le temps réel)
    Les développements terminés restent visibles mais sont marqués avec statut='termine'
    """
    developpements_data = load_developpements()
    calendrier_data = load_calendrier()
    
    if not calendrier_data or guild_id not in developpements_data:
        return 0
    
    developments_completed = 0
    
    for role_id, devs in developpements_data[guild_id].items():
        if not isinstance(devs, list):
            continue
            
        for dev in devs:
            if not isinstance(dev, dict):
                continue
            
            # Vérifier si le développement n'est pas déjà terminé
            statut_actuel = dev.get('statut', 'en_cours')
            
            if statut_actuel == 'termine':
                continue
            
            # Vérifier si le développement est terminé selon le calendrier RP
            if is_development_completed_by_calendar(dev, calendrier_data):
                # Marquer le développement comme terminé
                dev['statut'] = 'termine'
                dev['date_fin_reelle'] = get_paris_time()
                print(f"[DEBUG] Développement marqué comme terminé par calendrier RP: {dev.get('nom', 'Inconnu')} pour le rôle {role_id}")
                developments_completed += 1
    
    # Sauvegarder les changements si des développements ont été terminés
    if developments_completed > 0:
        save_developpements(developpements_data)
        save_all_json_to_postgres()
        print(f"[DEBUG] {developments_completed} développements marqués comme terminés selon le calendrier RP")
    
    return developments_completed

@bot.tree.command(name="test_calendrier", description="🧪 Avancer le calendrier RP pour tester les développements")
@app_commands.describe(
    mois="Nombre de mois à avancer (1-12)",
    code="Code de sécurité pour les tests"
)
@app_commands.checks.has_permissions(administrator=True)
async def test_calendrier(interaction: discord.Interaction, mois: int, code: str):
    await interaction.response.defer(ephemeral=True)
    
    # Vérification du code de sécurité
    if code != "240806":
        await interaction.followup.send("❌ Code de sécurité incorrect.", ephemeral=True)
        return
    
    # Validation des paramètres
    if mois < 1 or mois > 12:
        await interaction.followup.send("❌ Le nombre de mois doit être entre 1 et 12.", ephemeral=True)
        return
    
    # Charger le calendrier
    calendrier_data = load_calendrier()
    if not calendrier_data:
        await interaction.followup.send("❌ Aucun calendrier actif. Utilisez `/calendrier` d'abord.", ephemeral=True)
        return
    
    # Sauvegarder l'état actuel
    ancien_mois = calendrier_data.get("mois_index", 0)
    ancienne_annee = calendrier_data.get("annee", 2025)
    ancien_nom_mois = CALENDRIER_MONTHS[ancien_mois] if ancien_mois < len(CALENDRIER_MONTHS) else "Inconnu"
    
    # Avancer le calendrier
    nouveau_mois_index = ancien_mois + mois
    nouvelle_annee = ancienne_annee
    
    # Gérer le passage d'année
    while nouveau_mois_index >= 12:
        nouveau_mois_index -= 12
        nouvelle_annee += 1
    
    calendrier_data["mois_index"] = nouveau_mois_index
    calendrier_data["annee"] = nouvelle_annee
    
    # Sauvegarder
    save_calendrier(calendrier_data)
    save_all_json_to_postgres()  # Sauvegarder dans PostgreSQL
    
    # Vérifier et terminer automatiquement les développements terminés
    guild_id = str(interaction.guild.id)
    developments_completed = check_and_complete_developments(guild_id)
    
    # Nouveau nom du mois
    nouveau_nom_mois = CALENDRIER_MONTHS[nouveau_mois_index] if nouveau_mois_index < len(CALENDRIER_MONTHS) else "Inconnu"
    
    # Construire le message de statut des développements
    dev_status = ""
    if developments_completed > 0:
        dev_status = f"\n✅ {developments_completed} développement(s) marqué(s) comme terminé(s) !"
    else:
        dev_status = f"\n🔬 Aucun développement terminé"
    
    # Afficher le résultat avec simulation de développement
    message = f"🧪 **Test d'Avancement du Calendrier**\n\n" \
             f"**Calendrier avancé de {mois} mois**\n" \
             f"📅 Avant : {ancien_nom_mois} {ancienne_annee}\n" \
             f"📅 Après : {nouveau_nom_mois} {nouvelle_annee}{dev_status}\n\n" \
             f"🔬 **Test de développement :**\n" \
             f"• Un développement de 3 mois commencé maintenant\n" \
             f"• Finira en : {CALENDRIER_MONTHS[(nouveau_mois_index + 3) % 12]} {nouvelle_annee + ((nouveau_mois_index + 3) // 12)}\n\n" \
             f"⚠️ Ceci est un test avec le code de sécurité !\n" \
             f"Test effectué par {interaction.user.display_name}"
    
    await interaction.followup.send(message, ephemeral=True)

@bot.tree.command(name="reset_tech", description="🚨 Reset tous les centres et développements d'un pays")
@app_commands.describe(
    pays="Le pays à reset (mention)",
    code="Code de sécurité requis"
)
async def reset_tech(interaction: discord.Interaction, pays: discord.Role, code: str):
    await interaction.response.defer(ephemeral=True)
    
    # Vérification du code de sécurité
    if code != "240806":
        await interaction.followup.send("❌ Code de sécurité incorrect.", ephemeral=True)
        return
    
    # Vérification des permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("❌ Seuls les administrateurs peuvent utiliser cette commande.", ephemeral=True)
        return
    
    guild_id = str(interaction.guild.id)
    role_id = str(pays.id)
    
    # Reset des centres technologiques
    centres_data = load_centres_tech()
    centres_resetted = 0
    if guild_id in centres_data and role_id in centres_data[guild_id]:
        centres_resetted = len(centres_data[guild_id][role_id])
        del centres_data[guild_id][role_id]
        save_centres_tech(centres_data)
    
    # Reset des développements technologiques
    developpements_data = load_developpements()
    developpements_resetted = 0
    if guild_id in developpements_data and role_id in developpements_data[guild_id]:
        developpements_resetted = len(developpements_data[guild_id][role_id])
        del developpements_data[guild_id][role_id]
        save_developpements(developpements_data)
    
    # Sauvegarder dans PostgreSQL
    save_all_json_to_postgres()
    
    embed = discord.Embed(
        title="🚨 Reset Technologique Complet",
        description=f"**Pays :** {pays.mention}\n\n"
                   f"**🏭 Centres supprimés :** {centres_resetted}\n"
                   f"**🔬 Développements annulés :** {developpements_resetted}\n\n"
                   f"**✅ Toutes les données technologiques ont été remises à zéro.**\n"
                   f"**� L'économie du pays n'a pas été affectée.**\n"
                   f"**💾 Sauvegarde PostgreSQL effectuée.**",
        color=0xff4444
    )
    message = f"🚨 **Reset Technologique Complet**\n\n" \
             f"**Pays :** {pays.mention}\n" \
             f"🏭 Centres supprimés : {centres_resetted}\n" \
             f"🔬 Développements annulés : {developpements_resetted}\n\n" \
             f"✅ Toutes les données technologiques ont été remises à zéro.\n" \
             f"💰 L'économie du pays n'a pas été affectée.\n" \
             f"💾 Sauvegarde PostgreSQL effectuée.\n\n" \
             f"Reset effectué par {interaction.user.display_name}"
    
    await interaction.followup.send(message, ephemeral=True)

class SupprimerCentreView(discord.ui.View):
    def __init__(self, centres_data, guild_id, role_id, role_name):
        super().__init__(timeout=300)
        self.centres_data = centres_data
        self.guild_id = guild_id
        self.role_id = role_id
        self.role_name = role_name
        
        # Créer le menu déroulant avec les centres
        if guild_id in centres_data and role_id in centres_data[guild_id]:
            centres = centres_data[guild_id][role_id]
            if centres:
                options = []
                for i, centre in enumerate(centres):
                    nom_centre = centre.get("nom", centre.get("localisation", f"Centre {i+1}"))
                    localisation = centre.get("localisation", "Localisation inconnue")
                    specialisation = centre.get("specialisation", "Spécialisation inconnue")
                    niveau = centre.get("niveau", 1)
                    
                    # Description courte pour le menu
                    description = f"Niv.{niveau} - {specialisation}"
                    if centre.get("localisation"):
                        description += f" ({localisation})"
                    
                    options.append(discord.SelectOption(
                        label=nom_centre[:100],  # Limite Discord
                        description=description[:100],  # Limite Discord
                        value=str(i),
                        emoji="🏭"
                    ))
                
                self.centre_select.options = options
            else:
                # Aucun centre à supprimer
                self.centre_select.disabled = True
        else:
            self.centre_select.disabled = True

    @discord.ui.select(
        placeholder="Sélectionnez le centre à supprimer...",
        min_values=1,
        max_values=1
    )
    async def centre_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.defer()
        
        try:
            centre_index = int(select.values[0])
            centres = self.centres_data[self.guild_id][self.role_id]
            
            if 0 <= centre_index < len(centres):
                centre_a_supprimer = centres[centre_index]
                nom_centre = centre_a_supprimer.get("nom", centre_a_supprimer.get("localisation", f"Centre {centre_index+1}"))
                
                # Vérifier s'il y a des développements en cours dans ce centre
                developpements_data = load_developpements()
                developpements_en_cours = []
                
                if (self.guild_id in developpements_data and 
                    self.role_id in developpements_data[self.guild_id]):
                    for dev in developpements_data[self.guild_id][self.role_id]:
                        if (dev.get("centre_attache") == nom_centre and 
                            dev.get("statut", "en_cours") == "en_cours"):
                            developpements_en_cours.append(dev)
                
                # Créer l'embed de confirmation
                embed = discord.Embed(
                    title="🗑️ Confirmation de Suppression",
                    color=0xff4444
                )
                
                description = f"**Centre à supprimer :** {nom_centre}\n"
                if centre_a_supprimer.get("localisation"):
                    description += f"**📍 Localisation :** {centre_a_supprimer['localisation']}\n"
                description += f"**🔬 Spécialisation :** {centre_a_supprimer['specialisation']}\n"
                description += f"**📊 Niveau :** {centre_a_supprimer['niveau']}/3\n"
                description += f"**🏭 Pays :** {self.role_name}\n\n"
                
                if developpements_en_cours:
                    description += f"⚠️ **ATTENTION :** Ce centre a {len(developpements_en_cours)} développement(s) en cours :\n"
                    for dev in developpements_en_cours:
                        description += f"• {dev['nom']}\n"
                    description += "\n**Ces développements seront également supprimés !**\n\n"
                
                description += "**Cette action est irréversible.** Confirmez-vous la suppression ?"
                embed.description = description
                
                # Créer les boutons de confirmation
                view = discord.ui.View(timeout=60)
                
                # Bouton Confirmer
                async def confirmer_suppression(button_interaction):
                    await button_interaction.response.defer()
                    
                    try:
                        # Recharger les données pour être sûr
                        centres_data_fresh = load_centres_tech()
                        developpements_data_fresh = load_developpements()
                        
                        # Supprimer le centre
                        centres_supprimes = 0
                        if (self.guild_id in centres_data_fresh and 
                            self.role_id in centres_data_fresh[self.guild_id] and
                            centre_index < len(centres_data_fresh[self.guild_id][self.role_id])):
                            
                            centre_supprime = centres_data_fresh[self.guild_id][self.role_id].pop(centre_index)
                            centres_supprimes = 1
                            
                            # Si plus de centres, supprimer la clé du pays
                            if not centres_data_fresh[self.guild_id][self.role_id]:
                                del centres_data_fresh[self.guild_id][self.role_id]
                                # Si plus de pays dans le serveur, supprimer la clé du serveur
                                if not centres_data_fresh[self.guild_id]:
                                    del centres_data_fresh[self.guild_id]
                            
                            save_centres_tech(centres_data_fresh)
                        
                        # Supprimer les développements liés
                        developpements_supprimes = 0
                        if (self.guild_id in developpements_data_fresh and 
                            self.role_id in developpements_data_fresh[self.guild_id]):
                            
                            developpements_restants = []
                            for dev in developpements_data_fresh[self.guild_id][self.role_id]:
                                if dev.get("centre_attache") != nom_centre:
                                    developpements_restants.append(dev)
                                else:
                                    developpements_supprimes += 1
                            
                            if developpements_restants:
                                developpements_data_fresh[self.guild_id][self.role_id] = developpements_restants
                            else:
                                del developpements_data_fresh[self.guild_id][self.role_id]
                                # Si plus de pays dans le serveur, supprimer la clé du serveur
                                if not developpements_data_fresh[self.guild_id]:
                                    del developpements_data_fresh[self.guild_id]
                            
                            save_developpements(developpements_data_fresh)
                        
                        # Sauvegarder dans PostgreSQL
                        save_all_json_to_postgres()
                        
                        # Embed de succès
                        success_embed = discord.Embed(
                            title="✅ Centre Supprimé",
                            description=f"**Centre :** {nom_centre}\n"
                                       f"**Pays :** {self.role_name}\n\n"
                                       f"🏭 Centres supprimés : {centres_supprimes}\n"
                                       f"🔬 Développements annulés : {developpements_supprimes}\n\n"
                                       f"💾 Sauvegarde PostgreSQL effectuée.",
                            color=0x00ff00
                        )
                        
                        await button_interaction.followup.send(embed=success_embed, ephemeral=True)
                        
                    except Exception as e:
                        error_embed = discord.Embed(
                            title="❌ Erreur",
                            description=f"Une erreur est survenue lors de la suppression :\n```{str(e)}```",
                            color=0xff0000
                        )
                        await button_interaction.followup.send(embed=error_embed, ephemeral=True)
                
                # Bouton Annuler
                async def annuler_suppression(button_interaction):
                    await button_interaction.response.defer()
                    cancel_embed = discord.Embed(
                        title="❌ Suppression Annulée",
                        description="La suppression du centre a été annulée.",
                        color=0xffa500
                    )
                    await button_interaction.followup.send(embed=cancel_embed, ephemeral=True)
                
                confirm_button = discord.ui.Button(
                    label="Confirmer la suppression",
                    style=discord.ButtonStyle.danger,
                    emoji="🗑️"
                )
                confirm_button.callback = confirmer_suppression
                
                cancel_button = discord.ui.Button(
                    label="Annuler",
                    style=discord.ButtonStyle.secondary,
                    emoji="❌"
                )
                cancel_button.callback = annuler_suppression
                
                view.add_item(confirm_button)
                view.add_item(cancel_button)
                
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                
            else:
                error_embed = discord.Embed(
                    title="❌ Erreur",
                    description="Centre invalide sélectionné.",
                    color=0xff0000
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue :\n```{str(e)}```",
                color=0xff0000
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

@bot.tree.command(name="supprimer_centre", description="🗑️ Supprimer un centre technologique d'un pays")
@app_commands.describe(
    pays="Le pays dont supprimer un centre"
)
@app_commands.checks.has_permissions(administrator=True)
async def supprimer_centre(interaction: discord.Interaction, pays: discord.Role):
    """Supprimer un centre technologique d'un pays spécifique."""
    await interaction.response.defer(ephemeral=True)
    
    guild_id = str(interaction.guild.id)
    role_id = str(pays.id)
    
    # Charger les centres technologiques
    centres_data = load_centres_tech()
    
    # Vérifier si le pays a des centres
    if (guild_id not in centres_data or 
        role_id not in centres_data[guild_id] or 
        not centres_data[guild_id][role_id]):
        
        embed = discord.Embed(
            title="❌ Aucun Centre",
            description=f"**Pays :** {pays.mention}\n\n"
                       f"Ce pays n'a aucun centre technologique à supprimer.",
            color=0xff4444
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    centres = centres_data[guild_id][role_id]
    
    # Créer l'embed d'information
    embed = discord.Embed(
        title="🗑️ Suppression de Centre Technologique",
        description=f"**Pays :** {pays.mention}\n"
                   f"**Centres disponibles :** {len(centres)}\n\n"
                   f"Sélectionnez le centre à supprimer dans le menu ci-dessous.\n"
                   f"⚠️ **Attention :** Cette action supprimera également tous les développements en cours dans ce centre.",
        color=0xff6600
    )
    
    # Créer la vue avec le menu déroulant
    view = SupprimerCentreView(centres_data, guild_id, role_id, pays.name)
    
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="force_sync_postgres", description="Force la synchronisation des données avec PostgreSQL")
@app_commands.checks.has_permissions(administrator=True)
async def force_sync_postgres(interaction: discord.Interaction):
    """Force la synchronisation manuelle avec PostgreSQL."""
    await interaction.response.defer(ephemeral=True)
    
    try:
        import subprocess
        result = subprocess.run([
            "python3", "backup_json_to_postgres.py"
        ], cwd=BASE_DIR, capture_output=True, text=True, timeout=None)
        
        if result.returncode == 0:
            # Compter les réussites dans le output
            success_count = result.stdout.count("✅ Backup de") if "✅ Backup de" in result.stdout else 0
            
            embed = discord.Embed(
                title="✅ Synchronisation PostgreSQL réussie",
                description=f"**Fichiers synchronisés :** {success_count}\n"
                           f"**Base de données :** Mise à jour\n"
                           f"**Statut :** Toutes les données sont sauvegardées",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="❌ Erreur de synchronisation",
                description=f"**Erreur :** {result.stderr[:500]}...",
                color=0xff0000
            )
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erreur de synchronisation",
            description=f"**Erreur :** {str(e)}",
            color=0xff0000
        )
    
    await interaction.followup.send(embed=embed, ephemeral=True)



# === COMMANDES OLLAMA SUPPRIMÉES ===

if __name__ == "__main__":
    # Toujours restaurer les fichiers JSON depuis PostgreSQL avant tout chargement local
    restore_all_json_from_postgres()
    # Recharge l'état XP après restauration
    xp_system_status = load_xp_system_status()
    load_all_data()
    # Charger les niveaux XP au démarrage
    levels = load_levels()
    lvl_log_channel_data = load_lvl_log_channel()
    # Créer le fichier levels.json si absent
    if not os.path.exists(LVL_FILE):
        with open(LVL_FILE, "w") as f:
            json.dump({}, f)
    
    check_duplicate_json_files()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(exit_handler)
    print("Démarrage du bot...")
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Erreur lors du démarrage du bot: {e}")
        save_balances(balances)
        sys.exit(1)
