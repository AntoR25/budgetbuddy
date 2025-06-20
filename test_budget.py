import pytest
from datetime import date, timedelta, datetime

from moteur_budget import (
    ajouter_operation,
    calculer_solde,
    calculer_totaux_par_categorie,
    filtrer_operations_par_date,
    sauvegarder_donnees,
    charger_donnees,
    supprimer_operation
)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    sauvegarder_donnees([])
    yield
    sauvegarder_donnees([])

def test_ajouter_operation():
    ajouter_operation("revenu", "Salaire", 1000)
    ajouter_operation("depense", "Courses", 200)
    donnees = charger_donnees()
    assert len(donnees) == 2
    assert donnees[0]["categorie"] == "Salaire"
    assert donnees[1]["montant"] == 200

def test_calculer_solde():
    ajouter_operation("revenu", "Bourse", 500)
    ajouter_operation("depense", "Transport", 100)
    solde = calculer_solde()
    assert solde == 400

def test_calculer_totaux_par_categorie():
    sauvegarder_donnees([
        {"date": "2025-06-15T10:00:00", "type": "depense", "categorie": "Nourriture", "montant": 100, "commentaire": ""},
        {"date": "2025-06-16T10:00:00", "type": "depense", "categorie": "Nourriture", "montant": 50, "commentaire": ""},
        {"date": "2025-06-17T10:00:00", "type": "revenu", "categorie": "Salaire", "montant": 1000, "commentaire": ""}
    ])
    totaux = calculer_totaux_par_categorie()
    assert totaux["Nourriture"] == 150
    assert totaux["Salaire"] == -1000

def test_filtrer_operations_par_date():
    aujourd_hui = date.today()
    hier = aujourd_hui - timedelta(days=1)

    op_1 = {"date": hier.isoformat() + "T12:00:00", "type": "depense", "categorie": "Test", "montant": 50, "commentaire": ""}
    op_2 = {"date": aujourd_hui.isoformat() + "T12:00:00", "type": "depense", "categorie": "Test", "montant": 30, "commentaire": ""}
    sauvegarder_donnees([op_1, op_2])

    resultats = filtrer_operations_par_date(hier, aujourd_hui)
    assert len(resultats) == 2

def test_filtrage_date_aucun_resultat():
    op = {"date": "2025-01-01T10:00:00", "type": "depense", "categorie": "Test", "montant": 25, "commentaire": ""}
    sauvegarder_donnees([op])
    resultats = filtrer_operations_par_date(date(2024, 1, 1), date(2024, 1, 2))
    assert len(resultats) == 0

def test_supprimer_operation():
    ajouter_operation("depense", "Loisir", 60)
    donnees = charger_donnees()
    op_a_supprimer = donnees[0]
    
    supprimer_operation(op_a_supprimer)
    donnees_apres = charger_donnees()
    assert op_a_supprimer not in donnees_apres

def test_ajout_operation_invalide():
    with pytest.raises(TypeError):
        ajouter_operation("revenu")  # manque d'arguments

def test_solde_negatif():
    ajouter_operation("depense", "Facture", 300)
    solde = calculer_solde()
    assert solde == -300

def test_sauvegarde_et_chargement():
    operations = [
        {"date": "2025-06-20T12:00:00", "type": "revenu", "categorie": "Prime", "montant": 500, "commentaire": "Bonus"},
        {"date": "2025-06-21T12:00:00", "type": "depense", "categorie": "Jeux", "montant": 60, "commentaire": "Steam"}
    ]
    sauvegarder_donnees(operations)
    donnees = charger_donnees()
    assert donnees == operations

def test_operations_avec_commentaires():
    ajouter_operation("depense", "Cadeau", 40, commentaire="Anniversaire")
    donnees = charger_donnees()
    assert donnees[0]["commentaire"] == "Anniversaire"

