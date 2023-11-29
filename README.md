# Projet-7-backend

Ce répertoire regroupe les fichiers nécessaires au backend du projet OpenClassrooms numéro 7, du parcous Data Scientist, "Implémentez un modèle de scoring".
<br>Il y a en premier lieu le notebook qui contient les différents modèles de classification et qui permet l'export d'un pipeline de prédiction.
On trouve ensuite l'API qui permet, via des appels depuis le frontend (situé dans un autre répertoire GitHub), d'effectuer notamment des prédictions ainsi que diverses opérations d'affichage.
<br>Les fichiers restants sont des données csv allégées pour ne pas alourdir le déploiement cloud ainsi que des fichiers de commande pour le déploiement.

## Fonctionnement général de l'API

L'API est montée sur un serveur Heroku et permet de traiter les informations saisies dans la partie front-end. Elle permet entre autres :
* La communication avec la base de données.
* La calcul d'une prédiction "à la volée" lorsque l'utilisateur de l'application ne fait initialement pas partie de la base de données grâce à un pipeline préalablement réalisé.
* Une construction de données en vue de différents affichages graphiques.

Cette dernière est développé en Python et fonctionne grâce au framework **Flask**.

## Concernant l'environnement de travail

### Dépendances

* Flask
* Numpy
* Pandas
* Joblib
* Gunicorn
* Scikit-learn
* Lightgbm
* werkzeug (pour spécifier une version compatible)

### Installation dans un environnement Linux

Le fichier *requirements.txt* contient toutes les librairies utilisées pour l'éxecution et le fonctionnement de l'API ainsi que les versions nécessaires.

Pour préparer simplement et rapidement un environnement requis au fonctionnement de l'API sous Linux, commencer par créer l'environnement en question :
```sh
python3 -m venv name_environment
```

Activer ensuite l'environnement tout juste créé :
```sh
source name_environment/bin/activate
```

Installer les librairies nécessaires à l'application depuis le fichier *requirements.txt* que l'on aura pris soin de copier dans le dossier de travail au préalable :
```sh
pip install -r requirements.txt
```

S'assurer du bon déroulé du processus en vérifiant les libraires installées :
```sh
pip list
```

## La plateforme Heroku

Heroku est une plateforme en ligne proposant aux entreprises et aux développeurs un moyen rapide et efficace de déployer leurs applications en mettant à leur disposition des serveurs configurables à distances.

[Heroku](https://www.heroku.com/)

Quelques fichiers sont cependants nécessaires au déploiement sur Heroku (en plus des fichiers critiques au fonctionnement intrinsèque de l'API).
<br> Liste des fichiers spécifiques au déploiement sur Heroku :
* Procfile
* requirements.txt
* runtime.txt

## Quelques notes concernant le projet

Le projet est un prototype d'application de *"scoring crédit"*  pour calculer la probabilité qu'un client rembourse son crédit. Le notebook présenté ici renvoie un pipeline de prédiction **qui n'est pas celui utilisé dans l'API**.

Il est à noter qu'il y a des incohérences dans les prédictions. Par exemple dans certaines situations, faire augmenter le salaire en gardant les autres paramètres fixes peut faire baisser le score ce qui est contre-intuitif voire illogique dans notre situation. Le pipeline utilisé dans l'API (appelé *pipeline_backend.joblib*) a été développé de la même manière que celui en sortie du notebook appelé *pipeline_p7.joblib* à la différence que seules les 10 variables utilisées dans le front-end ont servi à son entraînement. 

Cela faisait simplement peu de sens de servir du pipeline_p7 construit dans le notebook quand celui-ci prend en entrée un vecteur (795,) alors que n'utilisons dans les faits que 4 ou 10 variables pour effectuer des prédictions à la volée.

Le prix à payer est que le pipeline construit spécifiquement pour l'API obtient un score [AUC](https://machine-learning.paperspace.com/wiki/auc-area-under-the-roc-curve) plus faible que son "grand-frère" car entraîné sur une quantité bien plus faible de données et souffre en plus d'over-fitting :
* <u>Score AUC pipeline_p7</u>
<br> Jeu d'entraînement : 0.75
<br> Jeu de test : 0.71

* <u>Score AUC pipeline_backend</u>
<br> Jeu d'entraînement : 0.77
<br> Jeu de test : 0.62

Cela n'a finalement pas vraiment d'importance car l'application n'est qu'un début de POC (*Proof of Concept*) mais c'est un point important à noter dans la manière de son fonctionnement et surtout dans le regard critique à adopter vis-à-vis des scores retournés par l'API.

Un autre point important à noter est la contrainte sur la fourchette de valeurs que peut prendre le salaire lors d'une prédiction à la volée. Le salaire que l'on renseigne doit être compris entre les valeurs minimum et maximum que la base de données contient. Cette contrainte a été rajoutée pour éviter des erreurs qui apparaissent lorsque l'utilisateur souhaite comparer sa situation à celle de la base de données.

Si le salaire renseigné est trop bas ou trop haut comparé aux valeurs de la base de données, alors l'API ne sera pas en mesure de renvoyer une réponse ayant du sens. D'autres mesures auraient pû être mises en place pour éviter cela, comme renvoyer une réponse pré-construite dans le cas ou le salaire est vu comme une valeur extrême haute ou basse.

Une fois de plus, la solution de la constriction du salaire a été mise en place simplement pour éviter des scripts d'erreur et permet de prouver la faisabilité du projet.