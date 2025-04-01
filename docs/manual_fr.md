# Manuel du Site Web et du Tableau de Bord Administrateur Apeko

## Table des Matières
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Premiers Pas](#premiers-pas)
4. [Interface Utilisateur](#interface-utilisateur)
5. [Tableau de Bord Administrateur](#tableau-de-bord-administrateur)
6. [Personnalisation du Site Web](#personnalisation-du-site-web)
7. [Agent IA](#agent-ia)
8. [Base de Données RAG](#base-de-données-rag)
9. [Dépannage](#dépannage)
10. [FAQ](#faq)

## Introduction

Apeko est une plateforme complète d'évaluation immobilière qui combine les méthodologies d'évaluation traditionnelles avec une technologie d'IA de pointe. La plateforme se compose d'un site web destiné aux clients et d'un tableau de bord administrateur pour gérer les évaluations, les clients et l'agent IA.

### Fonctionnalités Clés

- **Évaluations Assistées par IA** : Exploitez l'intelligence artificielle pour faciliter les évaluations immobilières
- **Gestion des Clients** : Suivez et gérez les informations et interactions des clients
- **Gestion des Documents** : Stockez et organisez les documents d'évaluation et les fichiers associés
- **Base de Données RAG** : Système de Génération Augmentée par Récupération pour fournir des réponses contextuelles
- **Tableau de Bord Analytique** : Visualisez les indicateurs clés et les performances

## Installation

### Configuration Requise

- Python 3.9 ou supérieur
- Base de données SQLite (par défaut) ou PostgreSQL
- 4 Go de RAM minimum (8 Go recommandés)
- 10 Go d'espace disque libre

### Étapes d'Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votrenomdutilisateur/AppraisalAI.git
   cd AppraisalAI
   ```

2. Créez un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Initialisez la base de données :
   ```bash
   python -m app.database.init_db
   ```

5. Démarrez l'application :
   ```bash
   python -m app.main
   ```

6. Accédez à l'application sur http://localhost:8001

## Premiers Pas

Après l'installation, vous devrez configurer votre compte administrateur initial :

1. Naviguez vers http://localhost:8001/admin/login
2. Utilisez les identifiants par défaut :
   - Nom d'utilisateur : admin
   - Mot de passe : apeko2025
3. Vous serez invité à changer votre mot de passe lors de la première connexion

## Interface Utilisateur

Le site web Apeko comprend plusieurs sections clés :

### Page d'Accueil

La page d'accueil présente les principaux services offerts par Apeko, notamment :
- Évaluations Résidentielles
- Évaluations Commerciales
- Analyse de Marché
- Évaluations Assistées par IA

### Services

Informations détaillées sur chaque service offert, notamment :
- Descriptions des processus
- Informations sur les prix
- Délais d'exécution
- Exemples de rapports

### À Propos

Informations sur l'entreprise, les membres de l'équipe, les qualifications et les certifications.

### Contact

Un formulaire de contact et les informations de l'entreprise pour que les clients puissent nous contacter.

## Tableau de Bord Administrateur

Le tableau de bord administrateur est le centre de contrôle pour gérer tous les aspects de la plateforme Apeko.

### Aperçu du Tableau de Bord

Le tableau de bord principal affiche des métriques clés :
- Total des clients
- Projets actifs
- Demandes en attente
- Activités récentes

### Gestion des Clients

La section clients vous permet de :
- Voir tous les clients
- Ajouter de nouveaux clients
- Modifier les informations des clients
- Archiver les clients inactifs

### Gestion des Évaluations

La section évaluations vous permet de :
- Créer de nouveaux rapports d'évaluation
- Suivre l'état des évaluations
- Assigner des évaluateurs
- Générer des rapports finaux

### Explorateur de Fichiers

L'explorateur de fichiers fournit :
- Organisation des documents par client et par projet
- Fonctionnalité de téléchargement
- Contrôle de version
- Capacités de recherche

### Agent IA

La section Agent IA vous permet de :
- Interagir avec l'assistant IA
- Consulter l'historique des conversations
- Configurer les paramètres de l'IA
- Former l'IA avec de nouvelles données

### Base de Données RAG

La section Base de Données RAG (Génération Augmentée par Récupération) vous permet de :
- Télécharger des documents dans la base de connaissances
- Gérer les catégories de documents
- Consulter l'historique des requêtes
- Surveiller les performances du système

### Analytique

La section analytique fournit :
- Tendances du volume d'évaluations
- Métriques d'acquisition de clients
- Analyse des revenus
- Statistiques d'utilisation de l'IA

### Paramètres

La section paramètres vous permet de :
- Gérer les comptes utilisateurs
- Configurer les paramètres du système
- Personnaliser les modèles d'e-mail
- Configurer des intégrations

## Personnalisation du Site Web

### Modification du Contenu du Site Web

Le contenu du site web peut être modifié en éditant les fichiers de modèles situés dans :
```
app/templates/
```

Les fichiers de modèles clés comprennent :
- `index.html` : Page d'accueil
- `services.html` : Page des services
- `about.html` : Page À propos
- `contact.html` : Page de contact

### Changement des Images

Pour changer les images sur le site web :

1. Préparez vos nouvelles images avec les dimensions appropriées :
   - Bannière principale : 1920x1080px
   - Icônes de service : 512x512px
   - Photos d'équipe : 800x800px

2. Placez vos images dans le répertoire statique :
   ```
   app/static/images/
   ```

3. Mettez à jour les références d'images dans les fichiers de modèles :
   ```html
   <img src="{{ url_for('static', path='/images/votre-nouvelle-image.jpg') }}" alt="Description">
   ```

### Modification des Styles CSS

Pour changer l'apparence du site web :

1. Éditez le fichier CSS principal :
   ```
   app/static/css/apeko.css
   ```

2. Sections de style clés :
   - Variables de schéma de couleurs en haut du fichier
   - Styles de typographie
   - Styles spécifiques aux composants
   - Points de rupture de conception responsive

3. Exemple de changement de la couleur primaire :
   ```css
   :root {
     --apeko-primary: #9d0208;  /* Changez ceci à votre couleur souhaitée */
     --apeko-secondary: #dc2f02;
     --apeko-accent: #f48c06;
   }
   ```

### Ajout de Nouvelles Pages

Pour ajouter une nouvelle page au site web :

1. Créez un nouveau fichier de modèle dans `app/templates/`

2. Ajoutez une nouvelle route dans `app/web/controllers.py` :
   ```python
   @router.get("/votre-nouvelle-page", response_class=HTMLResponse)
   async def votre_nouvelle_page(request: Request, db: Session = Depends(get_db)):
       return templates.TemplateResponse(
           "votre-nouvelle-page.html",
           {"request": request}
       )
   ```

3. Ajoutez un lien vers la nouvelle page dans le menu de navigation dans `app/templates/base.html`

## Agent IA

### Configuration de l'Agent IA

L'agent IA est alimenté par l'API Nebius et peut être configuré dans :
```
app/core/config.py
```

Options de configuration clés :
- `NEBIUS_API_KEY` : Votre clé API Nebius
- `NEBIUS_API_ENDPOINT` : URL du point de terminaison de l'API
- `NEBIUS_MODEL_NAME` : Nom du modèle à utiliser (par défaut : meta-llama/Meta-Llama-3.1-70B-Instruct)

### Formation de l'Agent IA

L'agent IA utilise un système RAG (Génération Augmentée par Récupération) pour fournir des réponses contextuelles :

1. Téléchargez des documents pertinents dans la base de données RAG via le tableau de bord administrateur
2. Catégorisez les documents de manière appropriée
3. L'IA utilisera automatiquement ces documents pour fournir des réponses plus précises

### Utilisation de l'Agent IA

Pour utiliser l'agent IA :

1. Naviguez vers la section Agent IA dans le tableau de bord administrateur
2. Tapez votre question dans l'interface de chat
3. L'IA répondra avec des informations basées sur sa formation et les documents dans la base de données RAG
4. Vous pouvez consulter les sources utilisées par l'IA en cliquant sur "Voir les sources" sous chaque réponse

## Base de Données RAG

### Ajout de Documents

Pour ajouter des documents à la base de données RAG :

1. Naviguez vers la section Base de Données RAG dans le tableau de bord administrateur
2. Cliquez sur "Ajouter un Document"
3. Remplissez les détails du document :
   - Titre
   - Type de document
   - Téléchargez le fichier du document
   - Ajoutez une description optionnelle
4. Cliquez sur "Ajouter un Document" pour traiter et indexer le document

### Types de Documents

Le système prend en charge divers types de documents :
- Rapports d'Évaluation
- Analyses de Marché
- Réglementations
- Données Immobilières
- Autres

### Surveillance des Performances

Le tableau de bord de la Base de Données RAG fournit des métriques sur :
- Total des documents
- Total des fragments
- Volume de requêtes
- Scores de pertinence

## Dépannage

### Problèmes Courants

#### L'Application ne Démarre Pas

**Problème** : L'application ne démarre pas avec un message d'erreur.

**Solution** :
1. Vérifiez si la version correcte de Python est installée
2. Vérifiez que toutes les dépendances sont installées : `pip install -r requirements.txt`
3. Assurez-vous que la base de données est correctement initialisée : `python -m app.database.init_db`
4. Vérifiez les conflits de port et changez le port si nécessaire dans `app/core/config.py`

#### Erreurs de Base de Données

**Problème** : Des messages d'erreur liés à la base de données apparaissent.

**Solution** :
1. Vérifiez les paramètres de connexion à la base de données dans `app/core/config.py`
2. Assurez-vous que le serveur de base de données est en cours d'exécution (si vous utilisez PostgreSQL)
3. Vérifiez les autorisations de la base de données
4. Essayez de réinitialiser la base de données : `python -m app.database.init_db`

#### L'Agent IA ne Répond Pas

**Problème** : L'agent IA ne répond pas aux questions.

**Solution** :
1. Vérifiez votre clé API Nebius dans `app/core/config.py`
2. Vérifiez la connectivité Internet
3. Assurez-vous que le nom du modèle est correct
4. Vérifiez les journaux de l'API pour les messages d'erreur

## FAQ

### Questions Générales

**Q : Puis-je utiliser un système de base de données différent ?**

R : Oui, l'application prend en charge SQLite (par défaut) et PostgreSQL. Pour passer à PostgreSQL, mettez à jour `DATABASE_URL` dans `app/core/config.py`.

**Q : Comment sauvegarder mes données ?**

R : Pour SQLite, copiez le fichier `app.db`. Pour PostgreSQL, utilisez les procédures standard de sauvegarde PostgreSQL.

**Q : Comment ajouter un nouvel utilisateur administrateur ?**

R : Naviguez vers Paramètres > Gestion des Utilisateurs dans le tableau de bord administrateur et cliquez sur "Ajouter un Utilisateur".

### Questions de Personnalisation

**Q : Puis-je changer le logo ?**

R : Oui, remplacez le fichier logo à `app/static/images/APEKOLOGO.png` par votre propre logo (conservez le même nom de fichier ou mettez à jour les références dans les modèles).

**Q : Comment changer le schéma de couleurs ?**

R : Éditez les variables CSS dans `app/static/css/apeko.css` pour changer le schéma de couleurs sur tout le site.

**Q : Puis-je ajouter du JavaScript personnalisé ?**

R : Oui, ajoutez votre JavaScript personnalisé à `app/static/js/` et incluez-le dans les modèles en utilisant :
```html
<script src="{{ url_for('static', path='/js/votre-script.js') }}"></script>
```

### Questions Techniques

**Q : Quel modèle d'IA est utilisé ?**

R : L'application utilise le modèle Meta-Llama-3.1-70B-Instruct via l'API Nebius.

**Q : Comment les embeddings de documents sont-ils générés ?**

R : Les embeddings de documents sont générés en utilisant le même modèle que l'agent IA, avec une dimension de 1536.

**Q : Puis-je déployer ceci sur un serveur de production ?**

R : Oui, pour le déploiement en production, nous recommandons :
1. Utiliser un serveur ASGI de production comme Uvicorn ou Hypercorn
2. Mettre en place une authentification appropriée
3. Utiliser PostgreSQL au lieu de SQLite
4. Configurer HTTPS
5. Définir les variables d'environnement appropriées
