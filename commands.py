from discord.ext import commands
import discord  # Assurez-vous d'importer discord si ce n'est pas déjà fait
from config import bot, logger, verified_emails, CSV_FILE
import smtplib
from email.message import EmailMessage
import random
import string
import re
import os
import csv
import asyncio

# Sauvegarder les e-mails vérifiés dans le fichier CSV
def save_verified_email(email, user_id):
    logger.info(f"Enregistrement de l'e-mail {email} vérifié pour l'utilisateur {user_id} dans le fichier {CSV_FILE}.")
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([email, user_id])

# Fonction pour supprimer un e-mail du fichier CSV
def delete_verified_email(email):
    if not os.path.exists(CSV_FILE):
        return False
    
    lines = []
    deleted = False

    with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] != email:
                lines.append(row)
            else:
                deleted = True

    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    return deleted

# Générer un code de vérification aléatoire
def generate_verification_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Valider l'adresse e-mail
def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@'+os.getenv("MAIL_DOMAIN")+'$', email) is not None

# Envoyer l'e-mail de vérification
def send_verification_email(email, code):
    msg = EmailMessage()
    msg.set_content(f"Bonjour,\n\nVotre code de vérification est : {code}")
    msg['Subject'] = 'Code de vérification Discord'
    msg['From'] = os.getenv("SMTP_EMAIL")
    msg['To'] = email

    try:
        with smtplib.SMTP(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT")) as server:
            server.starttls()
            server.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'e-mail à {email}: {e}")
        return False

# Définir la classe de commandes
class VerificationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Commande !verif
    @commands.command(name="verif")
    async def verif(self, ctx):
        mail_domain = os.getenv("MAIL_DOMAIN")
        if ctx.guild is not None:
            await ctx.message.delete()
            await ctx.send("On se retrouve en MP pour la vérification !", delete_after=10)
            await ctx.author.send("Veuillez entrer votre adresse e-mail @"+mail_domain+" :")

            def check(m):
                return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

            attempts = 0  # Initialiser le compteur de tentatives

            while attempts < 3:
                try:
                    email_message = await self.bot.wait_for('message', check=check, timeout=120.0)
                    email = email_message.content.strip()

                    if not is_valid_email(email):
                        attempts += 1
                        if attempts < 3:
                            await ctx.author.send(f"Adresse e-mail invalide. Assurez-vous d'utiliser une adresse e-mail @"+mail_domain+f". Tentative {attempts}/3")
                        else:
                            await ctx.author.send("Adresse e-mail incorrecte à 3 reprises. La procédure de vérification est annulée.")
                            return
                        continue

                    if email in verified_emails:
                        await ctx.author.send("Cette adresse e-mail est déjà utilisée par un autre utilisateur.Veuillez contacter l'équipe de modération pour plus d'informations.")
                        return

                    code = generate_verification_code()

                    if send_verification_email(email, code):
                        await ctx.author.send("Un e-mail avec un code de vérification vous a été envoyé. Veuillez entrer le code reçu :")
                    
                        attempts = 0
                        max_attempts = 3
                    
                        while attempts < max_attempts:
                            try:
                                code_message = await self.bot.wait_for('message', check=check, timeout=300.0)
                                entered_code = code_message.content.strip()
                    
                                if entered_code == code:
                                    verified_emails[email] = ctx.author.id
                                    save_verified_email(email, ctx.author.id)
                                    await ctx.author.send("Vérification réussie ! Vous avez désormais le role " + os.getenv("ROLE_NAME")+ " sur le serveur !")
                                    
                                    verified_role = discord.utils.get(ctx.guild.roles, name=os.getenv("ROLE_NAME"))
                                    if verified_role:
                                        await ctx.author.add_roles(verified_role)
                                    else:
                                        await ctx.author.send("Le rôle n'a pas été trouvé. Veuillez contacter l'équipe de modération.")
                                        logger.error(f"Le rôle {os.getenv('ROLE_NAME')} n'a pas été trouvé sur le serveur.")
                                    return
                    
                                else:
                                    attempts += 1
                                    if attempts < max_attempts:
                                        await ctx.author.send(f"Code incorrect. Il vous reste {max_attempts - attempts} tentative(s). Veuillez réessayer :")
                                    else:
                                        await ctx.author.send("Code incorrect à 3 reprises. La procédure de vérification a échoué. Veuillez réessayer la commande `!verif`.")
                                        return
                    
                            except asyncio.TimeoutError:
                                await ctx.author.send("Le temps de vérification a expiré. Veuillez réessayer la commande `!verif`.")
                                return
                    else:
                        await ctx.author.send("Une erreur est survenue lors de l'envoi de l'e-mail. Veuillez réessayer plus tard.")
                        return

                except asyncio.TimeoutError:
                    await ctx.author.send("Le temps imparti pour entrer l'adresse e-mail est écoulé. Veuillez réessayer la commande `!verif`.")
                    return
        else:
            await ctx.author.send("Cette commande ne peut être exécutée que sur le serveur Discord.")

    # Commande !delete
    @commands.command(name="delete")
    @commands.has_permissions(administrator=True)
    async def delete_email(self, ctx, email: str):
        if email not in verified_emails:
            await ctx.send(f"Cet e-mail n'est pas vérifié : {email}")
            return

        if delete_verified_email(email):
            del verified_emails[email]
            await ctx.send(f"L'e-mail {email} a été supprimé de la liste des e-mails vérifiés.")
            logger.info(f"L'e-mail {email} a été supprimé par {ctx.author.name} ({ctx.author.id})")
        else:
            await ctx.send(f"Impossible de supprimer l'e-mail {email}. Veuillez réessayer.")

    # Gérer les erreurs d'autorisations
    @delete_email.error
    async def delete_email_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.message.delete()
            await ctx.send("Vous devez être administrateur pour utiliser cette commande.", delete_after=10)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Veuillez fournir un e-mail à supprimer. Exemple : `!delete user@domain.com`", delete_after=10)
    # Commande !help
    @commands.command(name="help")
    async def help_command(self, ctx):
        mail_domain = os.getenv("MAIL_DOMAIN")

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        # Vérifier si l'utilisateur est administrateur
        is_admin = ctx.author.guild_permissions.administrator
        
        # Créer le message d'aide
        help_message = "**Liste des commandes disponibles :**\n1. `!verif` : Démarre la procédure de vérification de votre adresse e-mail @"+mail_domain+".\n2. `!help` : Affiche ce message d'aide."
        
        # Ajouter la commande !delete si l'utilisateur est administrateur
        if is_admin:
            help_message += "\n3. `!delete [email]` : Supprime un e-mail de la liste des e-mails vérifiés (réservé aux administrateurs)."

        # Envoyer le message d'aide
        await ctx.send(help_message, delete_after=10)



# Charger cette extension
async def setup(bot):
    await bot.add_cog(VerificationCommands(bot))
