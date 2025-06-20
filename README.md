Application de Gestion de Budget
===============================

Cette application permet de gérer un budget personnel via une interface graphique simple et moderne.

Fonctionnalités
---------------
- Ajout et suppression d'opérations (dépenses, revenus, objectifs).
- Calcul automatique du solde actuel.
- Filtrage des opérations par date et catégorie.
- Visualisation graphique des totaux par catégorie avec matplotlib.
- Objectifs de dépenses par mois avec barème.

Installation
------------
1. Cloner le dépôt :
   git clone https://ton_depot.git
   cd ton_depot

2. Installer les dépendances :
   pip install -r requirements.txt

Remarque :
Tkinter est inclus dans la plupart des distributions Python.
Sous Linux, il est parfois nécessaire d'installer le paquet python3-tk via le gestionnaire de paquets.

Usage
-----
Lancer l’application avec la commande :
python main.py

Structure du projet
-------------------
- main.py : point d’entrée de l’application, interface utilisateur.
- moteur_budget.py : logique métier (gestion des opérations, calculs).
- requirements.txt : liste des dépendances Python.
- interface_budget.py : gère tout l'interface + page des objectifs
- test_budget.py : tests effectué via pytest pour vérifier que les opérations fonctionne correctement 

Contribution
------------
Les contributions sont les bienvenues !
Merci de créer une issue ou une pull request.

Licence
-------
Projet sous licence AR (moi) 

Image de l'application
----------------------
![budgetbuddy](https://github.com/user-attachments/assets/3a528562-29a0-4297-921d-d5bb932e5922)


