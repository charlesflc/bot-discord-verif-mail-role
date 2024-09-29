# Étape 1 : Construction
FROM python:3.11-alpine AS builder

# Installer les dépendances nécessaires à la compilation
RUN apk add --no-cache gcc musl-dev

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Étape 2 : Image finale
FROM python:3.11-alpine

# Définir le répertoire de travail
WORKDIR /app

# Copier les dépendances depuis l'étape de construction
COPY --from=builder /install /usr/local

# Copier les fichiers de l'application
COPY . .

# Démarrer le bot
CMD ["python", "main.py"]
