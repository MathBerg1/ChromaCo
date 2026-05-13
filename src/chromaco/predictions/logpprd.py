"""
logp_regression.py
------------------
Computes linear regression coefficients (a, b) to correct RDKit logP
against experimental logP values from data/logP.csv.

No plot is shown. Import this module to get logp_corrige().

Dependencies:
    pip install numpy rdkit
"""

import csv
import numpy as np
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors


def logp_rdkit(smiles):
    """
    Compute RDKit Crippen logP for a given SMILES.

    Parameters
    ----------
    smiles : str
        SMILES string of the molecule.

    Returns
    -------
    float
        RDKit Crippen logP value.

    Raises
    ------
    ValueError
        If the SMILES cannot be parsed by RDKit.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    logp, _ = rdMolDescriptors.CalcCrippenDescriptors(mol)
    return logp


def compute_regression(logp_csv_path="data/logP.csv"):
    """
    Load calibration data and compute linear regression coefficients
    to correct RDKit logP values against experimental logP values.

    Regression: logP_corrected = a * logP_RDKit + b

    Parameters
    ----------
    logp_csv_path : str
        Path to the CSV file (columns: CAS, SMILES, logP).

    Returns
    -------
    tuple (float, float)
        Coefficients (a, b) of the linear correction.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist.
    ValueError
        If the CSV has fewer than 2 valid entries.
    """
    calib = []
    with open(logp_csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            smiles = (row.get("SMILES") or "").strip()
            logp_s = (row.get("logP")   or "").strip()
            if smiles and logp_s:
                try:
                    calib.append((smiles, float(logp_s)))
                except ValueError:
                    continue

    if len(calib) < 2:
        raise ValueError(
            f"Not enough valid entries in '{logp_csv_path}' to compute regression "
            f"(need at least 2, got {len(calib)})."
        )

    X = np.array([logp_rdkit(smi) for smi, _ in calib])
    Y = np.array([logp_exp         for _, logp_exp in calib])

    # Linear regression via covariance
    a = np.cov(X, Y, bias=True)[0, 1] / np.var(X)
    b = np.mean(Y) - a * np.mean(X)

    return a, b


# Compute once at import time
_a, _b = compute_regression()


def logp_correction(smiles):
    """
    Return the corrected experimental logP for a given SMILES.

    Parameters
    ----------
    smiles : str
        SMILES string of the molecule.

    Returns
    -------
    float
        Corrected logP value (a * logP_RDKit + b).
    """
    return _a * logp_rdkit(smiles) + _b