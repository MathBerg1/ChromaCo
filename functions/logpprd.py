import csv
import numpy as np
import matplotlib.pyplot as plt
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors

# --- 1) logP RDKit ---
def logp_rdkit(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"SMILES invalide : {smiles}")
    logp, mr = rdMolDescriptors.CalcCrippenDescriptors(mol)
    return logp

# --- 2) Chargement de data/data.csv ---
calib = []
with open("data/data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["SMILES"] and row["logS"]:
            calib.append((row["SMILES"], float(row["logP"])))

X = np.array([logp_rdkit(smi) for smi, _ in calib])
Y = np.array([logp_real for _, logp_real in calib])

a = np.cov(X, Y, bias=True)[0,1] / np.var(X)
b = np.mean(Y) - a * np.mean(X)

print(f"Formule : logP_corrigé = {a:.3f} * logP_RDKit + {b:.3f}")

x_line = np.linspace(min(X)-0.5, max(X)+0.5, 100)
y_line = a * x_line + b

plt.scatter(X, Y, color="blue", label="Calibration")
plt.plot(x_line, y_line, color="red", label="Regression")
plt.xlabel("logP RDKit")
plt.ylabel("logP real")
plt.title("Correction of RDKit logP")
plt.grid(True)
plt.legend()
plt.show()

# --- 5) Fonction finale ---
def logp_corrige(smiles):
    lp = logp_rdkit(smiles)
    return a * lp + b

