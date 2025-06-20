"""
__author__ = "REMACLE Antoine"
__version__ = 0.1

"""

def afficher_intro_console():
    ascii_art = r"""
█████╗  ███╗   ██╗████████╗ ██████╗ ██╗███╗   ██╗███████╗   
██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗██║████╗  ██║██╔════╝    
███████║██╔██╗ ██║   ██║   ██║   ██║██║██╔██╗ ██║█████╗      
██╔══██║██║╚██╗██║   ██║   ██║   ██║██║██║╚██╗██║██╔══╝      
██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║██║ ╚████║███████╗    
╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝╚═╝  ╚═══╝╚══════╝    
"""
    print(ascii_art)
    print("Bienvenue dans BudgetBuddy 💰")
    print("L'application simple pour suivre ton argent 😎\n")

import time
import sys

def main():
    # Affiche le texte AVANT l'import qui pourrait bloquer
    afficher_intro_console()

    # Import ici, plus tard, pour éviter blocage console
    from interface_budget import InterfaceBudget
    app = InterfaceBudget()
    app.mainloop()

if __name__ == "__main__":
    main()
