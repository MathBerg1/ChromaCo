import tkinter as tk
from fonctions_colonnes import resolution_between_two_peaks

class InterfaceResolution:
    def __init__(self, parent):
        
        def calculer():
            try:
            # 1. Récupérer les valeurs des champs de saisie 
                Temps_de_retention_brut_1 = float(entree1.get())
                Largueur_base_pic_1 = float(entree2.get())
                Temps_de_retention_brut_2 = float(entree3.get())
                Largueur_base_pic_2 = float(entree4.get())

        
            # 2. Exécuter le calcul (logique Python pure)
                resultat = resolution_between_two_peaks (Temps_de_retention_brut_1 , Temps_de_retention_brut_2 , Largueur_base_pic_1 , Largueur_base_pic_2)
            # 3. Afficher le résultat dans l'interface
                label_resultat.config(text=f"Résultat : {resultat}")
                label_erreur.config(text="") # Effacer les erreurs précédentes
        
            except ValueError:
            # Gestion des erreurs si l'utilisateur entre du texte non numérique
                label_erreur.config(text="Please enter valide numbers.")
                label_resultat.config(text="")

    # Création de la fenêtre principale
        fenetre = tk.Tk()
        fenetre.title("Calculateur of the equivalent high")
        fenetre.geometry("500x350")

    # Éléments de l'interface
        tk.Label(fenetre, text="Brut retention time nb 1 [min] :").pack(pady=5)
        entree1 = tk.Entry(fenetre)
        entree1.pack()

        tk.Label(fenetre, text="Width of the base of the pic nb 1 [min] :").pack(pady=5)
        entree2 = tk.Entry(fenetre)
        entree2.pack()

        tk.Label(fenetre, text="Brut retention time nb 2 [min] :").pack(pady=5)
        entree3 = tk.Entry(fenetre)
        entree3.pack()

        tk.Label(fenetre, text="Width of the base of the pic nb 1 [min] :").pack(pady=5)
        entree4 = tk.Entry(fenetre)
        entree4.pack()

    # Bouton déclencheur lié à la fonction 'calculer'
        btn_calculer = tk.Button(fenetre, text="Calculate the resolution between two peaks", command=calculer)
        btn_calculer.pack(pady=10)

    # Zone d'affichage du résultat
        label_resultat = tk.Label(fenetre, text="Résultat : ", font=("Arial", 12, "bold"))
        label_resultat.pack(pady=5)

        label_erreur = tk.Label(fenetre, text="", fg="red")
        label_erreur.pack()

    # Lancement de la boucle principale
        fenetre.mainloop()
