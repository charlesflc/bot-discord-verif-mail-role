import logging
import discord
from discord.ext import commands
import os
import csv
import nest_asyncio
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Appliquer nest_asyncio pour que le bot fonctionne correctement dans un Jupyter Notebook (plus facile pour le développement)
nest_asyncio.apply()

# Configurer le logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler()  # Envoie les logs à la console (visible dans les logs du conteneur)
    ]
)
logger = logging.getLogger(__name__)

# Informations pour l'envoi d'e-mails
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ROLE_NAME = os.getenv("ROLE_NAME")

# Chemin du fichier CSV pour stocker les e-mails vérifiés
CSV_FILE = os.getenv("CSV_FILE")

# Chargement du TOKEN Discord
TOKEN = os.getenv("DISCORD_TOKEN")

# Charger les e-mails vérifiés à partir du fichier CSV
def load_verified_emails():
    if not os.path.exists(CSV_FILE):
        return {}

    with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        return {rows[0]: int(rows[1]) for rows in reader}

    # Charger les e-mails vérifiés à partir du fichier CSV
    with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # Ignorer la ligne d'en-tête
        return {rows[0]: int(rows[1]) for rows in reader}

# Initialiser les e-mails vérifiés
verified_emails = load_verified_emails()

# Créer une instance du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
