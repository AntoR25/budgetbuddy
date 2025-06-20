"""
__author__ = "REMACLE Antoine"
__version__ = 0.5

"""

import json
from datetime import datetime
from pathlib import Path

FICHIER_DONNEES = Path("data/budget_2025_06.json")


def charger_donnees():
    """Charge les opérations depuis le fichier JSON."""
    if not FICHIER_DONNEES.exists():
        return []
    try:
        with open(FICHIER_DONNEES, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        print("Erreur lors du chargement des données.")
        return []


def sauvegarder_donnees(donnees):
    """Sauvegarde les opérations dans un fichier JSON."""
    try:
        with open(FICHIER_DONNEES, "w", encoding="utf-8") as f:
            json.dump(donnees, f, indent=4, ensure_ascii=False)
    except IOError:
        print("Erreur lors de la sauvegarde des données.")


def ajouter_operation(type_op, categorie, montant, commentaire=""):
    """Ajoute une opération de revenu ou dépense."""
    donnees = charger_donnees()
    operation = {
        "date": datetime.now().isoformat(),
        "type": type_op,
        "categorie": categorie,
        "montant": montant,
        "commentaire": commentaire,
    }
    donnees.append(operation)
    sauvegarder_donnees(donnees)


def calculer_solde():
    """Calcule le solde actuel (revenus - dépenses)."""
    donnees = charger_donnees()
    solde = 0
    for op in donnees:
        if op["type"] == "revenu":
            solde += op["montant"]
        elif op["type"] == "depense":
            solde -= op["montant"]
    return solde


def calculer_totaux_par_categorie():
    """Retourne un dictionnaire avec les totaux par catégorie."""
    donnees = charger_donnees()
    totaux = {}
    for op in donnees:
        cat = op["categorie"]
        montant = op["montant"] if op["type"] == "depense" else -op["montant"]
        totaux[cat] = totaux.get(cat, 0) + montant
    return totaux


def filtrer_operations_par_date(date_debut, date_fin):
    """Filtre les opérations entre deux dates ISO (YYYY-MM-DD)."""
    donnees = charger_donnees()
    resultat = []
    for op in donnees:
        date_op = datetime.fromisoformat(op["date"]).date()
        if date_debut <= date_op <= date_fin:
            resultat.append(op)
    return resultat


def supprimer_operation(op_a_supprimer):
    """Supprime une opération exacte à partir de ses champs."""
    data = charger_donnees()
    for i, op in enumerate(data):
        if (op["date"] == op_a_supprimer["date"] and
            op["type"] == op_a_supprimer["type"] and
            op["categorie"] == op_a_supprimer["categorie"] and
            op["montant"] == op_a_supprimer["montant"] and
            op.get("commentaire", "") == op_a_supprimer.get("commentaire", "")):
            del data[i]
            break
    sauvegarder_donnees(data)


def modifier_operation(index, nouvelle_op):
    """Modifie une opération existante à l'index donné."""
    donnees = charger_donnees()
    if 0 <= index < len(donnees):
        donnees[index] = nouvelle_op
        sauvegarder_donnees(donnees)
