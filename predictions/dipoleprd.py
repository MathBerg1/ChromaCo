"""
dipoleprd.py
------------
Estimates the molecular dipole moment from SMILES using RDKit 3D geometry
and Pauling electronegativity differences.

Physics model:
    For each bond A-B:
        contribution = |EN_A - EN_B| * dist(bond_midpoint, center_of_mass)
    Raw dipole = sum of contributions / molecular_length (normalization)

Dependencies:
    pip install rdkit numpy
"""

import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem


# ── Pauling electronegativity table ───────────────────────────────────────────

ELECTRONEGATIVITY = {
    "H":  2.20, "He": 0.00,
    "Li": 0.98, "Be": 1.57, "B":  2.04, "C":  2.55, "N":  3.04,
    "O":  3.44, "F":  3.98,
    "Na": 0.93, "Mg": 1.31, "Al": 1.61, "Si": 1.90, "P":  2.19,
    "S":  2.58, "Cl": 3.16,
    "K":  0.82, "Ca": 1.00, "Sc": 1.36, "Ti": 1.54, "V":  1.63,
    "Cr": 1.66, "Mn": 1.55, "Fe": 1.83, "Co": 1.88, "Ni": 1.91,
    "Cu": 1.90, "Zn": 1.65, "Ga": 1.81, "Ge": 2.01, "As": 2.18,
    "Se": 2.55, "Br": 2.96,
    "Rb": 0.82, "Sr": 0.95, "Y":  1.22, "Zr": 1.33, "Nb": 1.60,
    "Mo": 2.16, "Tc": 1.90, "Ru": 2.20, "Rh": 2.28, "Pd": 2.20,
    "Ag": 1.93, "Cd": 1.69, "In": 1.78, "Sn": 1.96, "Sb": 2.05,
    "Te": 2.10, "I":  2.66,
    "Cs": 0.79, "Ba": 0.89, "La": 1.10,
    "Hf": 1.30, "Ta": 1.50, "W":  2.36, "Re": 1.90, "Os": 2.20,
    "Ir": 2.20, "Pt": 2.28, "Au": 2.54, "Hg": 2.00, "Tl": 1.62,
    "Pb": 2.33, "Bi": 2.02,
}


# ── 3D conformer generation ────────────────────────────────────────────────────

def _get_3d_mol(smiles):
    """
    Generate a 3D conformer for a molecule from its SMILES.

    Parameters
    ----------
    smiles : str
        SMILES string of the molecule.

    Returns
    -------
    rdkit.Chem.Mol
        RDKit molecule with 3D coordinates and explicit hydrogens.

    Raises
    ------
    ValueError
        If the SMILES is invalid or 3D embedding fails.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: '{smiles}'")

    mol = Chem.AddHs(mol)

    result = AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
    if result == -1:
        result = AllChem.EmbedMolecule(mol, randomSeed=42)
    if result == -1:
        raise ValueError(f"3D embedding failed for SMILES: '{smiles}'")

    AllChem.MMFFOptimizeMolecule(mol)
    return mol


# ── Dipole estimator ───────────────────────────────────────────────────────────

def dipole_rdkit(smiles):
    """
    Estimate the molecular dipole moment from 3D geometry and
    Pauling electronegativity differences.

    For each bond A-B:
        partial_dipole = |EN_A - EN_B| * dist(bond_midpoint, center_of_mass)

    Total raw dipole = sum of bond contributions / molecular_length

    Parameters
    ----------
    smiles : str
        SMILES string of the molecule.

    Returns
    -------
    float
        Estimated normalized dipole moment (arbitrary units).

    Raises
    ------
    ValueError
        If the SMILES is invalid, 3D embedding fails, or an atom's
        electronegativity is not in the ELECTRONEGATIVITY table.
    """
    mol = _get_3d_mol(smiles)
    conf = mol.GetConformer()
    n_atoms = mol.GetNumAtoms()

    # Atomic positions as numpy array
    positions = np.array([conf.GetAtomPosition(i) for i in range(n_atoms)])

    # Atomic masses for center-of-mass calculation
    masses = np.array([mol.GetAtomWithIdx(i).GetMass() for i in range(n_atoms)])

    # Center of mass
    total_mass = masses.sum()
    if total_mass == 0:
        raise ValueError("Total molecular mass is zero.")
    center_of_mass = (masses[:, None] * positions).sum(axis=0) / total_mass

    # Molecular length: max interatomic distance (normalization factor)
    dists = np.linalg.norm(positions[:, None] - positions[None, :], axis=-1)
    mol_length = dists.max()
    if mol_length == 0:
        mol_length = 1.0  # single-atom molecule

    # Sum bond dipole contributions
    raw_dipole = 0.0
    for bond in mol.GetBonds():
        i = bond.GetBeginAtomIdx()
        j = bond.GetEndAtomIdx()

        sym_i = mol.GetAtomWithIdx(i).GetSymbol()
        sym_j = mol.GetAtomWithIdx(j).GetSymbol()

        en_i = ELECTRONEGATIVITY.get(sym_i)
        en_j = ELECTRONEGATIVITY.get(sym_j)

        if en_i is None:
            raise ValueError(f"Electronegativity not found for element '{sym_i}'.")
        if en_j is None:
            raise ValueError(f"Electronegativity not found for element '{sym_j}'.")

        delta_en    = abs(en_i - en_j)
        midpoint    = (positions[i] + positions[j]) / 2.0
        dist_to_com = np.linalg.norm(midpoint - center_of_mass)

        raw_dipole += delta_en * dist_to_com

    return raw_dipole / mol_length