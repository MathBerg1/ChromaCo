import tkinter as tk

def action_bouton():
    label.config(text="Bonjour depuis l'interface !")

fenetre = tk.Tk()
fenetre.title("Mon Application")

label = tk.Label(fenetre, text="Bienvenue")
label.pack()

bouton = tk.Button(fenetre, text="Cliquez-moi", command=action_bouton)
bouton.pack()

fenetre.mainloop()
