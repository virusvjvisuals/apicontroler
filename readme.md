# API Controller

Une application Gradio permettant de contrôler plusieurs applications via des commandes API préenregistrées, avec un système de suivi des exécutions et de débogage.

## Fonctionnalités

- **Enregistrement d'API** : Enregistrez facilement vos configurations d'API (URL, méthode, headers, paramètres, body)
- **Exécution d'API** : Lancez vos API enregistrées en un clic
- **Retour visuel** : Visualisez le succès ou l'échec de chaque exécution
- **Débogage** : En cas d'échec, un outil de débogage analyse l'erreur et propose des solutions

## Installation et démarrage

### Via Pinokio

1. Recherchez "API Controller" dans le navigateur de scripts Pinokio
2. Installez l'application
3. Cliquez sur "API Controller" dans le menu de navigation pour lancer l'application

### Installation manuelle

```bash
# Clonez ce dépôt
git clone https://github.com/votre-nom/api-controller.git
cd api-controller

# Installez les dépendances
pip install -r requirements.txt

# Lancez l'application
python app.py
```

## Utilisation

### Enregistrer une API

1. Accédez à l'onglet "Enregistrer une API"
2. Remplissez les informations requises :
   - Nom de l'API (pour la référencer facilement)
   - URL de l'API
   - Méthode HTTP (GET, POST, PUT, etc.)
   - Headers (au format JSON)
   - Paramètres (au format JSON)
   - Corps de la requête (au format JSON)
3. Cliquez sur "Enregistrer l'API"

### Exécuter une API

1. Accédez à l'onglet "Exécuter des API"
2. Sélectionnez l'API à exécuter dans la liste déroulante
3. Cliquez sur "Exécuter l'API"
4. Le statut de l'exécution et la réponse seront affichés

### Déboguer une API

Si une API échoue lors de son exécution :
1. Cliquez sur le bouton "Déboguer" qui apparaît
2. Les informations de débogage vous aideront à identifier et résoudre le problème

## Fichiers et structure

- `app.py` : Application principale Gradio
- `pinokio.js` : Script d'intégration pour Pinokio
- `api_configs/` : Dossier contenant les configurations d'API enregistrées
- `api_controller.log` : Journal des exécutions d'API

## Personnalisation

Pour personnaliser l'application, vous pouvez modifier directement les fichiers source. N'hésitez pas à ajouter des fonctionnalités selon vos besoins.
