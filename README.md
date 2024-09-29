# Discord Bot Mail to Role 

Ce bot Discord permet de vérifier si les membres d'un serveur ont une adresse e-mail se terminant par `@domain.tldr`. Si l'utilisateur utilise une adresse valide, le bot leur attribue un rôle spécifique sur le serveur.

## Fonctionnalités

- Vérification de l'adresse e-mail des utilisateurs.
- Gestion des rôles : attribue automatiquement un rôle spécifique aux utilisateurs avec une adresse valide.
- Gestion des erreurs et tentatives : limite à 3 les tentatives de saisie incorrecte du code de vérification.
- Commandes d'administration pour supprimer les utilisateurs vérifiés.
- Support multi-plateforme (x64 et ARM64).

## Prérequis

- [Python 3.11+](https://www.python.org/downloads/)
- Un serveur Discord avec des rôles configurés
- Un compte pour un serveur SMTP pour envoyer les e-mails de vérification (ex. : Gmail, SMTP personnalisé)

## Installation Locale

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/votre-nom-utilisateur/bot-discord-verif-mail-role.git
   cd bot-discord-verif-mail-role
   ```

2. Installez les dépendances Python :
   ```bash
   pip install -r requirements.txt
   ```

3. Créez un fichier `.env` pour stocker les variables d'environnement :
   ```bash
   DISCORD_TOKEN=VotreTokenDiscord
   SMTP_SERVER=smtp.domain.tldr
   SMTP_PORT=587
   SMTP_EMAIL=VotreEmail@domain.tldr
   SMTP_PASSWORD=VotreMotDePasse
   CSV_FILE=./verified_emails.csv
   ```

4. Lancez le bot :
   ```bash
   python bot.py
   ```

## Utilisation

### Commandes Principales

- **`!verif`** : L'utilisateur lance la procédure de vérification de son adresse e-mail. Le bot envoie un code de vérification à l'adresse fournie par l'utilisateur.
- **`!help`** : Affiche la liste des commandes disponibles.
- **`!delete [email]`** *(Administrateurs uniquement)* : Supprime un utilisateur de la liste des e-mails vérifiés.

## Utilisation avec Docker

Vous pouvez également exécuter ce bot en utilisant Docker et Docker Compose.

1. ** Docker Compose** :
   Créez un fichier `docker-compose.yml` avec la configuration suivante :

   ```yaml
   services:
     discord-bot:
       image: ghcr.io/charlesflc/bot-discord-verif-mail-role:latest 
       container_name: discord-bot
       environment:
         DISCORD_TOKEN: "VotreTokenDiscord"
         SMTP_SERVER: "smtp.domain.tldr"
         SMTP_PORT: "587"
         SMTP_EMAIL: "VotreEmail@domain.tldr"
         SMTP_PASSWORD: "VotreMotDePasse"
         CSV_FILE: "/data/verified_emails.csv"
       volumes:
         - ./data:/data
       restart: unless-stopped
   ```

2. **Lancez le conteneur Docker** :
   ```bash
   docker-compose up -d
   ```


## To-Do

- Utiliser un système de base de données à la place du .CSV qui peut être lourd à charger tout le temps. (.csv utilisé car permet d'obtenir rapidement la liste de mails)


## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request si vous souhaitez ajouter des fonctionnalités ou corriger des bugs.

1. Forkez le dépôt.
2. Créez une branche pour vos modifications.
3. Envoyez une pull request une fois vos modifications terminées.

## Licence

Ce projet est sous licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus d'informations.
