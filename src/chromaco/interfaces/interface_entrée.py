import tkinter as tk
# Importation des classes depuis les fichiers séparés (sans l'extension .py)
from chromaco.interfaces.interface_hauteur_equivalente import InterfaceHauteur
from chromaco.interfaces.interface_nb_de_plateau import InterfacePlateau
from chromaco.interfaces.interface_resolution_two_peaks import InterfaceResolution
from chromaco.interfaces.interface_standard_addition import InterfaceAjoutsDoses
from chromaco.interfaces.interface_elut_ord import InterfaceElution
from chromaco.interfaces.interface_retfac import InterfaceRetentionFactor
from chromaco.interfaces.interface_comparison import InterfaceCompareColumns
# from interface_c import InterfaceGraphique  # Exemple pour un 3ème fichier

def ouvrir_hauteur():
    # Crée une nouvelle instance de l'interface A
    # Chaque clic crée une nouvelle fenêtre indépendante
    InterfaceHauteur(root)

def ouvrir_plateau():
    # Crée une nouvelle instance de l'interface B
    InterfacePlateau(root)

def ouvrir_resolution():
    # Crée une nouvelle instance de l'interface B
    InterfaceResolution(root)

def ouvrir_graphiques():
    # Exemple pour une 3ème interface
    # InterfaceGraphique(root)
    pass

# --- Configuration du Menu Principal ---
root = tk.Tk()
root.title("Your calculator")
root.geometry("500x500")

tk.Label(root, text="What do you want to calculate ?", font=("Arial", 16, "bold")).pack(pady=30)

# Bouton 1 -> Lance interface_a.py
btn_a = tk.Button(root, text="Calculate equivalent height", command=ouvrir_hauteur, width=30, height=2, bg="#e3f2fd")
btn_a.pack(pady=10)

# Bouton 2 -> Lance interface_b.py
btn_b = tk.Button(root, text="Calculate number of plates", command=ouvrir_plateau, width=30, height=2, bg="#f5e8f4")
btn_b.pack(pady=10)

# Bouton 3 -> Lance interface_c.py
btn_c = tk.Button(root, text="Calculate resolution between two peaks", command=ouvrir_resolution, width=30, height=2, bg="#e8f5e9")
btn_c.pack(pady=10)




def ouvrir_elution():
    InterfaceElution(root)

btn_d = tk.Button(root, text="Order of elution", command=ouvrir_elution, width=30, height=2, bg="#fff9c4")
btn_d.pack(pady=10)

def ouvrir_ajouts_doses():
    InterfaceAjoutsDoses(root)

btn_ajouts = tk.Button(
    root,
    text="Standard addition method",
    command=ouvrir_ajouts_doses,
    width=30,
    height=2,
    bg="#ffdec4"
)
btn_ajouts.pack(pady=10)

def ouvrir_retfac():
    InterfaceRetentionFactor(root)

btn_ajouts = tk.Button(
    root,
    text="Calculate retention factor",
    command=ouvrir_retfac,
    width=30,
    height=2,
    bg="#ffd5c4"
)

btn_ajouts.pack(pady=10)

def ouvrir_comparison():
    InterfaceCompareColumns(root)

btn_ajouts = tk.Button(
    root,
    text="Compare two columns",
    command=ouvrir_comparison,
    width=30,
    height=2,
    bg="#ffd5c4"
)

btn_ajouts.pack(pady=10)


tk.Button(root, text="Exit the application", command=root.quit, bg="#ffebee").pack(pady=40)

root.mainloop()