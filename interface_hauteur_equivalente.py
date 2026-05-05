import tkinter as tk

class InterfaceHauteur:
    def __init__(self, parent):
        
        def calculer():
            try:
            # 1. Récupérer les valeurs des champs de saisie 
                Temps_de_retention_brut = float(entree1.get())
                Largueur_base_pic = float(entree2.get())
                Longueur_de_la_column = float(entree3.get())
        
            # 2. Exécuter le calcul (logique Python pure)
                resultat = Temps_de_retention_brut + Largueur_base_pic + Longueur_de_la_column
        
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
        fenetre.geometry("300x250")

    # Éléments de l'interface
        tk.Label(fenetre, text="Brut retention time [min] :").pack(pady=5)
        entree1 = tk.Entry(fenetre)
        entree1.pack()

        tk.Label(fenetre, text="Width of the base of the pic [min] :").pack(pady=5)
        entree2 = tk.Entry(fenetre)
        entree2.pack()

        tk.Label(fenetre, text="lenght of the column [m] :").pack(pady=5)
        entree3 = tk.Entry(fenetre)
        entree3.pack()

    # Bouton déclencheur lié à la fonction 'calculer'
        btn_calculer = tk.Button(fenetre, text="Calculate the theoretical number of plates", command=calculer)
        btn_calculer.pack(pady=10)

    # Zone d'affichage du résultat
        label_resultat = tk.Label(fenetre, text="Résultat : ", font=("Arial", 12, "bold"))
        label_resultat.pack(pady=5)

        label_erreur = tk.Label(fenetre, text="", fg="red")
        label_erreur.pack()

    # Lancement de la boucle principale
        fenetre.mainloop()
