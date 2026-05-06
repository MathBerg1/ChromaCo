import tkinter as tk
# Importation des classes depuis les fichiers séparés (sans l'extension .py)
from interface_hauteur_equivalente import InterfaceHauteur
from interface_nb_de_plateau import InterfacePlateau
from interface_resolution_two_peaks import InterfaceResolution
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
root.geometry("500x400")

tk.Label(root, text="What do you want to calculate ?", font=("Arial", 16, "bold")).pack(pady=30)

# Bouton 1 -> Lance interface_a.py
btn_a = tk.Button(root, text="Calculate equivalent height", command=ouvrir_hauteur, width=25, height=2, bg="#e3f2fd")
btn_a.pack(pady=10)

# Bouton 2 -> Lance interface_b.py
btn_b = tk.Button(root, text="Calculate number of plates", command=ouvrir_plateau, width=25, height=2, bg="#f5e8f4")
btn_b.pack(pady=10)

# Bouton 3 -> Lance interface_c.py
btn_c = tk.Button(root, text="Calculate resolution between two peaks", command=ouvrir_resolution, width=25, height=2, bg="#e8f5e9")
btn_c.pack(pady=10)


from interface_elut_ord import InterfaceElution

def ouvrir_elution():
    InterfaceElution(root)

btn_d = tk.Button(root, text="Order of elution", command=ouvrir_elution, width=25, height=2, bg="#fff9c4")
btn_d.pack(pady=10)

tk.Button(root, text="Quitter l'application", command=root.quit, bg="#ffebee").pack(pady=40)

root.mainloop()