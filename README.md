**README – Module BI — Projet Zorro**  
**CY Tech – Ingénieur BI & Analytics — PFE 2025**

Ce projet constitue la contribution Business Intelligence du chatbot **Zorro**, une solution numérique visant à prévenir et accompagner les cas de harcèlement chez les adolescents via un agent conversationnel intelligent.

Ce document fournit aux futurs développeurs, analystes ou équipes projet toutes les informations nécessaires pour :

- Comprendre l'architecture BI mise en place  
- Reprendre et faire évoluer le système  
- Connecter les futures données réelles en environnement de production  

---

**Contenu du dossier**

- `Dashboard_Zorro.pbix` → fichier Power BI prêt à l’emploi  
- `Données\Recommandations\catalogue_recommandations.xlsx` → base des recommandations (créée manuellement)  
- `Données\Utilisateurs\profils_utilisateurs.json` → données utilisateurs simulées (à remplacer)  
- `Données\Scoring_Globale\scoring_recommendations_global.xlsx` → résultats du moteur de scoring Python 
- `rapport_BI_Zorro.pdf` → rapport scientifique des travaux réalisés 
- `Presentation.pptx` → support de notre presentation orale
- `InsertionTablePowerBI.py` → code Python servant a générer les tables et la table de scoring globale
- `Template_PowerBI` → ce dossier contient la template ayant servi a la création des pages du Dashboard
- `README.md` → vous êtes ici  

---

**1. Modèle de données BI**

Le modèle Power BI repose sur une architecture en constellation avec les tables suivantes :

**Dimensions**

- `Dim_Utilisateurs` : liste des utilisateurs avec leurs attributs (âge, type de harcèlement, émotions, timestamp)  
- `Dim_Utilisateurs_Harceles` : vue filtrée avec uniquement les cas où `is_harcelement = 1`  
- `Dim_Recommandations` : catalogue complet des recommandations (type, émotion, gravité, âge cible, contact, lien, lieu)  
- `Dim_Calendrier` : table de dates générée dynamiquement via DAX  

**Faits**

- `Fact_Scoring_Globale` : score de pertinence attribué à chaque couple (utilisateur × recommandation)  
- `scoring_recommendations` : vue filtrée sur `Fact_Scoring_Globale` avec score ≥ 6, utilisée dans les visuels  

---

**2. Génération du scoring**

Le moteur de recommandations est implémenté dans le script Python `InsertionTablePowerBI.py`, qui :

- Charge les fichiers `profils_utilisateurs.json` et `catalogue_recommandations.xlsx`  
- Croise les données utilisateurs avec les recommandations  
- Attribue un score entre 0 et 10  
- Génère une table de scoring exportée en `scoring_recommendations_global.xlsx`  

**Note** : seules les émotions avec une intensité > 0.5 sont prises en compte.

---

**3. Mise à jour du modèle**

**A. Remplacement par des fichiers logs**

- Utiliser les fichiers issus du chatbot au format `.csv`, `.json` ou `.xlsx`  
- Adapter les fichiers pour conserver la structure (colonnes, formats) des données simulées  
- Cliquer sur "Actualiser" dans Power BI pour mettre à jour les visuels automatiquement  

**B. Connexion à une base cloud (SQL, BigQuery, etc.)**

- Créer des vues/exportations serveur vers des tables nommées comme `dim_utilisateurs`, `dim_recommandations`, `fact_scoring`  
- Dans Power BI, modifier la source de données et reconnecter les relations entre les tables  
- Les KPIs et mesures DAX sont déjà prêtes à l’emploi  

---

**4. Mesures DAX intégrées**

- `Nb_cas_total`  
- `Nb_cas_detectes`  
- `Nb_recommandations_utilisées`  
- `Nb_recommandations_fournies`  
- `Nb_cas_gravite_elevee`  
- `Nb_cas_par_type`, `Nb_par_age`, etc.  

Ces mesures sont utilisées dans les 4 pages du dashboard :

- Vue d’ensemble  
- Profils à risque  
- Performance des recommandations  
- Focus par élève  

---

**5. Limitations et pistes d’amélioration**

- Pas de détection automatique des émotions (ajout manuel dans les données simulées)  
  → Intégration possible d’un module IA d’analyse émotionnelle à partir de texte  

- Aucun feedback utilisateur encore pris en compte  
  → Idée : créer une table `feedback_reco` pour enregistrer clics et évaluations  

- Intégration API/logs automatisés absente  
  → Prévoir une base connectée pour la production  

---

**6. Conseils pour la prise en main**

- En cas de modification de structure (ajout de colonnes, renommage), penser à mettre à jour les relations et mesures DAX  
- Utiliser le fichier `.pbix` fourni comme base de référence stable  
- Conserver une version des données simulées pour effectuer des tests sans impact  

---

**7. Pour aller plus loin**

- Ajouter des règles métier plus avancées dans le moteur de scoring  
- Intégrer un module de NLP émotionnel  
- Créer une version mobile ou publique anonymisée du dashboard  
- Standardiser les exports IA pour compatibilité directe avec Power BI  

---

**Réalisé par**  
Kenza Abdellaoui Maane  
Mélissa Noupeuhou  
Thomas Deshayes  
CY Tech – Promo ING3 BI & Analytics – Juin 2025
