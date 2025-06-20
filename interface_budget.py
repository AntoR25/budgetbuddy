"""
__author__ = "REMACLE Antoine"
__version__ = 1.6

"""
from PIL import Image, ImageTk
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
import pandas as pd # pour le graphique
import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path # pour l'export excel 
from moteur_budget import (
    ajouter_operation,
    calculer_solde,
    charger_donnees,
    supprimer_operation,
    calculer_totaux_par_categorie,
    filtrer_operations_par_date
)
from ttkbootstrap import Style

# Fichiers de configuration
FICHIER_OBJECTIFS = Path("data/objectifs.json")

# Initialisation de l'application
fenetre = tk.Tk()
fenetre.title("budget_buddy")  
fenetre.geometry("670x740+0+0")
style = Style(theme='flatly')

# Données de l'application
categories_depense = ["Loyer", "Courses", "Transport", "Santé", "Loisirs", "Autre dépense"]
categories_revenu = ["Salaire", "Prime", "Autre salaire", "Autre revenu"]
filtres_disponibles = {
    "type": ["Tous", "Dépense", "Revenu"],
    "categorie": ["Toutes"] + categories_depense + categories_revenu,
    "date": ["Toutes", "Aujourd'hui", "Cette semaine", "Ce mois", "Cette année"]
}

# Variables globales
page_courante = 0
operations_completes = []
NB_OPERATIONS_PAR_PAGE = 6
objectifs_depenses_defaut = {
    "Vetements": 350,       # Trop cher le tissu de nos jours 
    "Transport": 69,        # J'prend le bus donc belek
    "Santé": 120,           # On est jamais sûr de rien 
    "Loisirs": 500,         # bowling, figurines pop inutiles
    "Abonnements": 60,      # Netflix, Disney+, VPN roumain
    "Don streamers": 30,    # “Merci pour le sub bro”
    "Cadeaux": 150,         # Un conseil est un cadeau 
    "NFT": 10,              # L'espoir fait vivre
    "Jeux Steam": 88,       # Jamais lancés
}

# Fonctions de gestion des objectifs de dépense 

def charger_objectifs():
    """
    Charge les objectifs de dépenses depuis le fichier JSON `FICHIER_OBJECTIFS`
    - Si le fichier existe, il est lu et transformé en dictionnaire Python
    - Les catégories manquantes (nouvelles ou modifiées dans le code) sont ajoutées avec leur valeur par défaut
    - En cas d'erreur de lecture, on retourne une copie des objectifs par défaut (`objectifs_depenses_defaut`)
    """
    if os.path.exists(FICHIER_OBJECTIFS):
        try:
            with open(FICHIER_OBJECTIFS, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Complète avec les catégories par défaut si manquantes
                for cle in objectifs_depenses_defaut.keys():
                    if cle not in data:
                        data[cle] = objectifs_depenses_defaut[cle]

                return data
        except Exception as e:
            print("Erreur chargement objectifs:", e)

    # Retourne les valeurs par défaut si fichier absent ou erreur
    return objectifs_depenses_defaut.copy()


def sauvegarder_objectifs():
    """
    Sauvegarde les valeurs saisies des objectifs dans le fichier `FICHIER_OBJECTIFS`
    - Lit les valeurs dans `entries_objectifs` (les champs d'entrée Tkinter)
    - Valide que chaque valeur est un nombre positif (float >= 0)
    - Écrit le dictionnaire `objectifs_depenses` dans un fichier JSON
    - Affiche des messages d'erreur ou de succès à l'utilisateur
    """
    global objectifs_depenses

    # Lecture et validation des valeurs saisies
    for cat, entry in entries_objectifs.items():
        try:
            val = float(entry.get())
            if val < 0:
                raise ValueError()
            objectifs_depenses[cat] = val
        except ValueError:
            messagebox.showerror("Erreur", f"Objectif invalide pour '{cat}'. Veuillez saisir un nombre positif.")
            return

    # Sauvegarde dans le fichier JSON
    try:
        with open(FICHIER_OBJECTIFS, "w", encoding="utf-8") as f:
            json.dump(objectifs_depenses, f, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de sauvegarder les objectifs:\n{e}")
        return

    # Confirmation et mise à jour dans l'interface
    messagebox.showinfo("Succès", "Objectifs sauvegardés.")
    maj_objectifs()

# Interface principale
notebook = ttk.Notebook(fenetre)
notebook.pack(fill="both", expand=True, padx=20, pady=(10, 0))

# Onglet Accueil
onglet_accueil = ttk.Frame(notebook)
notebook.add(onglet_accueil, text="🏠 Accueil")

# Section solde
label_solde = tk.Label(
    onglet_accueil,
    text="💼 Solde actuel : 0.00 €",
    font=("Courier New", 15, "bold"),
    bd=4,
    relief="ridge",
    padx=12,
    pady=8
)
label_solde.pack(pady=10, anchor="w", padx=15)

# Formulaire d'ajout
frame_formulaire = ttk.Frame(onglet_accueil)
frame_formulaire.pack(pady=10, anchor="w", padx=30)

var_type = tk.StringVar(value="depense")
ttk.Label(frame_formulaire, text="Type :").pack(anchor="w")
frame_type = ttk.Frame(frame_formulaire)
ttk.Radiobutton(frame_type, text="Dépense", variable=var_type, value="depense", command=lambda: mettre_a_jour_categories()).pack(side="left", padx=4)
ttk.Radiobutton(frame_type, text="Revenu", variable=var_type, value="revenu", command=lambda: mettre_a_jour_categories()).pack(side="left", padx=4)
frame_type.pack(anchor="w")

var_categorie = tk.StringVar()
ttk.Label(frame_formulaire, text="Catégorie :", padding=(0, 6)).pack(anchor="w")
menu_categorie = ttk.Combobox(frame_formulaire, textvariable=var_categorie, state="readonly", width=35)
menu_categorie.pack(anchor="w", fill="x")
menu_categorie.bind("<<ComboboxSelected>>", lambda e: afficher_champ_autre())

entry_montant = ttk.Entry(frame_formulaire, width=35)
ttk.Label(frame_formulaire, text="Montant (€) :").pack(anchor="w", pady=(10, 0))
entry_montant.pack(anchor="w")

entry_commentaire = ttk.Entry(frame_formulaire, width=35)
ttk.Label(frame_formulaire, text="Commentaire :").pack(anchor="w", pady=(10, 0))
entry_commentaire.pack(anchor="w")

# Boutons actions
frame_boutons = ttk.Frame(onglet_accueil)
frame_boutons.pack(pady=10, anchor="w", padx=30)

ttk.Button(frame_boutons, text="Ajouter", command=lambda: ajouter()).pack(side="left", padx=5)
ttk.Button(frame_boutons, text="📊 Voir graphique", command=lambda: afficher_graphique()).pack(side="left", padx=5)
ttk.Button(frame_boutons, text="⬇️ Exporter Excel", command=lambda: exporter_excel()).pack(side="left", padx=5)

# Liste des opérations avec filtres
frame_liste_externe = ttk.LabelFrame(onglet_accueil, text="🧾 Dernières opérations")
frame_liste_externe.pack(fill="both", expand=True, padx=30, pady=10)

frame_filtres = ttk.Frame(frame_liste_externe)
frame_filtres.pack(fill="x", padx=5, pady=5)

# Filtres
ttk.Label(frame_filtres, text="Type:").pack(side="left", padx=2)
var_filtre_type = tk.StringVar(value="Tous")
menu_filtre_type = ttk.Combobox(frame_filtres, textvariable=var_filtre_type, 
                               values=filtres_disponibles["type"], state="readonly", width=10)
menu_filtre_type.pack(side="left", padx=2)

ttk.Label(frame_filtres, text="Catégorie:").pack(side="left", padx=2)
var_filtre_categorie = tk.StringVar(value="Toutes")
menu_filtre_categorie = ttk.Combobox(frame_filtres, textvariable=var_filtre_categorie, 
                                    values=filtres_disponibles["categorie"], state="readonly", width=15)
menu_filtre_categorie.pack(side="left", padx=2)

ttk.Label(frame_filtres, text="Période:").pack(side="left", padx=2)
var_filtre_date = tk.StringVar(value="Toutes")
menu_filtre_date = ttk.Combobox(frame_filtres, textvariable=var_filtre_date, 
                               values=filtres_disponibles["date"], state="readonly", width=15)
menu_filtre_date.pack(side="left", padx=2)

ttk.Button(frame_filtres, text="Filtrer", command=lambda: maj_affichage()).pack(side="left", padx=5)

frame_liste_interior = ttk.Frame(frame_liste_externe)
frame_liste_interior.pack(fill="both", expand=True)

# Pagination
frame_pagination = ttk.Frame(onglet_accueil)
frame_pagination.pack(pady=(0, 10))

btn_prec = ttk.Button(frame_pagination, text="⬅️ Précédent", command=lambda: page_precedente())
btn_prec.pack(side="left", padx=5)
label_page = ttk.Label(frame_pagination, text="Page 1 / 1")
label_page.pack(side="left", padx=10)
btn_suiv = ttk.Button(frame_pagination, text="Suivant ➡️", command=lambda: page_suivante())
btn_suiv.pack(side="left", padx=5)

# Onglet Objectifs
onglet_objectifs = ttk.Frame(notebook)
notebook.add(onglet_objectifs, text="🎯 Objectifs")

frame_objectifs_interior = ttk.Frame(onglet_objectifs)
frame_objectifs_interior.pack(fill="both", expand=True, padx=10, pady=10)

objectifs_depenses = charger_objectifs()
entries_objectifs = {}

# Fonctions principales
def mettre_a_jour_categories():
    if var_type.get() == "revenu":
        menu_categorie['values'] = categories_revenu
    else:
        menu_categorie['values'] = categories_depense
    menu_categorie.set(menu_categorie['values'][0])
    afficher_champ_autre()

def afficher_champ_autre():
    val = var_categorie.get()
    if val.startswith("Autre"):
        menu_categorie.config(state="normal")
        menu_categorie.set(val)
    else:
        menu_categorie.config(state="readonly")

def ajouter():
    try:
        montant = float(entry_montant.get())
    except ValueError:
        messagebox.showerror("Erreur", "Montant invalide.")
        return

    type_op = var_type.get()
    categorie = var_categorie.get().strip()
    commentaire = entry_commentaire.get()

    if not categorie:
        messagebox.showerror("Erreur", "Veuillez spécifier une catégorie.")
        return

    ajouter_operation(type_op, categorie, montant, commentaire)
    maj_affichage()
    messagebox.showinfo("Succès", "Opération enregistrée.")
    entry_montant.delete(0, "end")
    entry_commentaire.delete(0, "end")
    menu_categorie.config(state="readonly")

def supprimer_et_rafraichir(op):
    if messagebox.askyesno("Confirmer", "Supprimer cette opération ?"):
        supprimer_operation(op)
        maj_affichage()

def appliquer_filtres(operations):
    operations_filtrees = operations.copy()
    
    # Filtre par type
    type_filtre = var_filtre_type.get()
    if type_filtre == "Dépense":
        operations_filtrees = [op for op in operations_filtrees if op["type"] == "depense"]
    elif type_filtre == "Revenu":
        operations_filtrees = [op for op in operations_filtrees if op["type"] == "revenu"]
    
    # Filtre par catégorie
    categorie_filtre = var_filtre_categorie.get()
    if categorie_filtre != "Toutes":
        operations_filtrees = [op for op in operations_filtrees if op["categorie"] == categorie_filtre]
    
    # Filtre par date
    date_filtre = var_filtre_date.get()
    aujourdhui = datetime.now().date()
    
    if date_filtre == "Aujourd'hui":
        operations_filtrees = filtrer_operations_par_date(aujourdhui, aujourdhui)
    elif date_filtre == "Cette semaine":
        debut = aujourdhui - timedelta(days=aujourdhui.weekday())
        fin = debut + timedelta(days=6)
        operations_filtrees = filtrer_operations_par_date(debut, fin)
    elif date_filtre == "Ce mois":
        debut = aujourdhui.replace(day=1)
        if aujourdhui.month == 12:
            fin = aujourdhui.replace(year=aujourdhui.year+1, month=1, day=1) - timedelta(days=1)
        else:
            fin = aujourdhui.replace(month=aujourdhui.month+1, day=1) - timedelta(days=1)
        operations_filtrees = filtrer_operations_par_date(debut, fin)
    elif date_filtre == "Cette année":
        debut = aujourdhui.replace(month=1, day=1)
        fin = aujourdhui.replace(month=12, day=31)
        operations_filtrees = filtrer_operations_par_date(debut, fin)
    
    return operations_filtrees

# Réinitialise les filtres à leurs valeurs par défaut et met à jour l'affichage (pas de bouton reset implanté pour le moment)
def reset_filtres():
    var_filtre_type.set("Tous")
    var_filtre_categorie.set("Toutes")
    var_filtre_date.set("Toutes")
    maj_affichage()

# Met à jour l'affichage des opérations, du solde, et des objectifs
def maj_affichage():
    global operations_completes, page_courante
    solde = calculer_solde()
    label_solde.config(text=f"💼 Solde actuel : {solde:.2f} €", foreground="green" if solde >= 0 else "red")
    operations_completes[:] = appliquer_filtres(list(reversed(charger_donnees())))
    page_courante = 0
    afficher_page()
    maj_objectifs()

# Affiche la page courante des opérations avec styles et boutons associés
def afficher_page():
    style = ttk.Style()
    style.configure("danger.TButton", foreground="white", background="#d9534f")
    style.map("danger.TButton", foreground=[('pressed', 'white'), ('active', 'white')],
              background=[('pressed', '#c9302c'), ('active', '#c9302c')])

    for widget in frame_liste_interior.winfo_children():
        widget.destroy()

    nb_par_page = NB_OPERATIONS_PAR_PAGE
    debut = page_courante * nb_par_page
    fin = debut + nb_par_page
    page_ops = operations_completes[debut:fin]

    for op in page_ops:
        ligne = f"{op['date'][:10]} | {op['type']} | {op['categorie']} | {op['montant']} €"
        bordure_couleur = "green" if op['type'] == "revenu" else "orange"

        ligne_frame = tk.Frame(frame_liste_interior, bg="#ffffff", bd=0, relief="flat",
                               highlightbackground=bordure_couleur,
                               highlightcolor=bordure_couleur,
                               highlightthickness=2)
        ligne_frame.pack(fill="x", padx=5, pady=3)

        lbl = ttk.Label(ligne_frame, text=ligne, anchor="w")
        lbl.pack(side="left", padx=5, pady=2, fill="x", expand=True)

        btns_frame = ttk.Frame(ligne_frame)
        btns_frame.pack(side="right")

        btn_commentaire = ttk.Button(btns_frame, text="💬", width=2,
                                     command=lambda commentaire=op['commentaire']:
                                     messagebox.showinfo("Commentaire", commentaire or "Aucun commentaire."))
        btn_commentaire.pack(side="left", padx=(0, 2))

        btn_supprimer = ttk.Button(btns_frame, text="🗑️", width=2, style="danger.TButton",
                                   command=lambda op=op: supprimer_et_rafraichir(op))
        btn_supprimer.pack(side="left", padx=(2, 0))

    total = len(operations_completes)
    total_pages = max((total - 1) // nb_par_page + 1, 1)
    label_page.config(text=f"Page {page_courante + 1} / {total_pages}")
    btn_prec.config(state="normal" if page_courante > 0 else "disabled")
    btn_suiv.config(state="normal" if (page_courante + 1) * nb_par_page < total else "disabled")

# Passe à la page précédente si possible et met à jour l'affichage
def page_precedente():
    global page_courante
    if page_courante > 0:
        page_courante -= 1
        afficher_page()

# Passe à la page suivante si possible et met à jour l'affichage
def page_suivante():
    global page_courante
    nb_par_page = NB_OPERATIONS_PAR_PAGE
    if (page_courante + 1) * nb_par_page < len(operations_completes):
        page_courante += 1
        afficher_page()

# Affiche un graphique camembert des dépenses par catégorie
def afficher_graphique():
    totaux = calculer_totaux_par_categorie()
    depenses = {k: v for k, v in totaux.items() if v > 0}

    if not depenses:
        messagebox.showinfo("Aucune dépense", "Aucune donnée à afficher.")
        return

    categories = list(depenses.keys())
    valeurs = list(depenses.values())

    plt.figure(figsize=(6, 6))
    plt.pie(valeurs, labels=categories, autopct="%1.1f%%", startangle=90)
    plt.title("Répartition des dépenses")
    plt.axis("equal")
    plt.show()

# Exporte les opérations visibles vers un fichier Excel
def exporter_excel():
    df = pd.DataFrame(operations_completes)
    chemin = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                         filetypes=[("Fichier Excel", "*.xlsx")],
                                         initialfile="budgetbuddy.xlsx")
    if chemin:
        try:
            df.to_excel(chemin, index=False)
            messagebox.showinfo("Succès", f"Exporté dans {chemin}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'exporter :\n{e}")

# Met à jour l'affichage des objectifs avec barres de progression et statuts
def maj_objectifs():
    for widget in frame_objectifs_interior.winfo_children():
        widget.destroy()

    totaux = calculer_totaux_par_categorie()
    total_depenses = 0
    total_objectifs = 0

    for categorie, objectif in objectifs_depenses.items():
        depense = totaux.get(categorie, 0)
        pourcentage = depense / objectif * 100 if objectif else 0
        pourcentage_clamp = min(pourcentage, 100)
        statut = "✅" if depense <= objectif else "🚨"
        couleur_style = "success" if depense <= objectif else "danger"
        restant = max(0, objectif - depense)

        cadre_cat = ttk.Frame(frame_objectifs_interior)
        cadre_cat.pack(fill="x", pady=6, padx=10)

        cadre_cat.grid_columnconfigure(0, minsize=90)
        cadre_cat.grid_columnconfigure(1, minsize=110)
        cadre_cat.grid_columnconfigure(2, minsize=210)

        label_cat = ttk.Label(cadre_cat, text=f"{categorie} :")
        label_cat.grid(row=0, column=0, sticky="w", padx=(0, 2))

        entry_obj = ttk.Entry(cadre_cat, width=10)
        entry_obj.insert(0, str(objectifs_depenses[categorie]))
        entry_obj.grid(row=0, column=1, padx=(2, 5), sticky="w")
        entries_objectifs[categorie] = entry_obj

        prog = ttk.Progressbar(cadre_cat, value=pourcentage_clamp, maximum=100,
                               length=200, style=f"{couleur_style}.Horizontal.TProgressbar")
        prog.grid(row=0, column=2, sticky="w")

        label_depense = ttk.Label(cadre_cat, text=f"Dépensé: {depense:.2f} €")
        label_depense.grid(row=1, column=1, sticky="w", padx=(2, 5))

        label_restant = ttk.Label(cadre_cat, text=f"Reste: {restant:.2f} € {statut}")
        label_restant.grid(row=1, column=2, sticky="w")

        total_depenses += depense
        total_objectifs += objectif


    # Synthèse totale
    label_synthese = ttk.Label(
        frame_objectifs_interior,
        text=f"Total : {total_depenses:.2f} € / {total_objectifs:.2f} €",
        font=("Segoe UI", 12, "bold")
    )
    label_synthese.pack(anchor="w", padx=10, pady=(15, 10))

    # Bouton d'enregistrement
    btn_enregistrer = ttk.Button(
        frame_objectifs_interior,
        text="💾 Enregistrer les objectifs",
        command=sauvegarder_objectifs
    )
    btn_enregistrer.pack(anchor="w", padx=10, pady=(0, 15))


# Styles
style.configure("danger.TButton", foreground="red")
style.configure("success.Horizontal.TProgressbar", troughcolor="#e0f2f1", background="#388e3c")
style.configure("danger.Horizontal.TProgressbar", troughcolor="#fbe9e7", background="#d32f2f")

# Image budget en haut à droite
try:
    image_path = "image/ar.jpg"  
    image = Image.open(image_path)
    image = image.resize((130, 130))  
    photo = ImageTk.PhotoImage(image)

    def rickroll(event=None):
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    image_label = tk.Label(onglet_accueil, image=photo, bg="white", cursor="hand2")
    image_label.image = photo  
    image_label.place(relx=1.0, x=0, y=10, anchor="ne")  # Collé à droite sans marge
    image_label.bind("<Button-1>", rickroll)

except Exception as e:
    print("Erreur lors du chargement de l'image AR :", e)


# Initialisation
mettre_a_jour_categories()
maj_affichage()

fenetre.mainloop()

# Possibilité d'ajouts dans le futur : moyen de paiements, ajouter des factures sous format .png
