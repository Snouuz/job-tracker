# Job Tracker

Application web locale pour suivre ses candidatures, gérer les relances et intégrer Gmail.

## Fonctionnalités

- Ajouter et suivre des candidatures (email, LinkedIn, jobboard)
- Relances automatiques planifiées à J+2 et J+5
- Tableau de bord avec statistiques (total, entretiens, refus, taux de réponse)
- Création de brouillons Gmail pour les relances (sans envoi automatique)
- Statuts : `envoyée`, `relance_1`, `relance_2`, `entretien`, `refus`, `acceptée`

## Installation

```bash
pip install flask google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Copier le fichier de données exemple :

```bash
cp data/candidatures.example.csv data/candidatures.csv
```

## Intégration Gmail (optionnelle)

1. Créer un projet dans la [Google Cloud Console](https://console.cloud.google.com/) et activer l'API Gmail
2. Télécharger les identifiants OAuth 2.0 (type "application de bureau")
3. Renommer le fichier en `credentials.json` et le placer à la racine du projet (voir `credentials.example.json` pour le format attendu)
4. Au premier lancement, un navigateur s'ouvre pour autoriser l'accès — cela génère automatiquement `token.json`

> `credentials.json` et `token.json` sont dans le `.gitignore` et ne seront jamais commités.

## Utilisation

**Windows :**
```bat
run.bat
```

**Linux :**
```bash
./run.sh
```

Les deux scripts démarrent le serveur sur http://localhost:5000 et ouvrent le navigateur automatiquement.

Pour arrêter le serveur, fais `Ctrl+C` dans le terminal (Linux) ou ferme la fenêtre console Flask (Windows).
