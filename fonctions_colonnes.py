def theorical_plates_one(brut_retention_time: float, peak_width : float)-> float:
    """
    Calculates the number of theoretical plates (N) for a chromatography column.
    
    Parameters:
    brut_retention_time (float): The retention time of the peak (t_R), in any time unit.
    peak_width (float): The width of the peak at the base (w), in the same unit as retention_time.
    
    Returns:
    float: The number of theoretical plates (N).
    
    Raises:
    ValueError: If the peak width is zero or negative.
    """
    if peak_width <= 0:
        raise ValueError("Peak width must be a strictly positive number.")
    
    if brut_retention_time < 0:
        raise ValueError("Retention time cannot be negative.")
    
    # Formula: N = 16 * (t_R / w)^2
    theorical_plates = 16*(brut_retention_time/peak_width)**2
    return round(theorical_plates,3)

def equivalent_high_one(column_length : float, brut_rentention_time : float, peak_width : float)-> float:
    """
    Calculates the Height Equivalent to a Theoretical Plate (HETP) directly from 
    chromatographic data: column length, retention time, and peak width.
    
    Parameters:
    column_length (float): The total length of the chromatography column (L), in any length unit.
    brut_retention_time (float): The retention time of the peak (t_R), in any time unit.
    peak_width (float): The width of the peak at the base (w), in the same unit as retention_time.
    
    Returns:
    float: The Height Equivalent to a Theoretical Plate (H), in the same unit as column_lenght.
    
    Raises:
    ValueError: If peak_width is zero/negative or if retention_time/column_length is negative.
    """
    if peak_width <= 0:
        raise ValueError("Peak width must be a strictly positive number.")
    if brut_rentention_time < 0:
        raise ValueError("Retention time cannot be negative.")
    if column_length < 0:
        raise ValueError("Column length cannot be negative.")
    
    # Uses the previous function
    theorical_plates = theorical_plates_one(brut_rentention_time,peak_width)
    # Formula: H = L / N
    equivalent_high = column_length/theorical_plates
    return round(equivalent_high,7)

def resolution_between_two_peaks(brut_retention_time_1 : float, brut_retention_time_2 : float, peak_width_1 : float, peak_width_2 : float)-> float:
    """
    Calculates the resolution (Rs) between two consecutive chromatographic peaks.
    
    Parameters:
    brut_retention_time_1 (float): Retention time of the first peak (t_R1), in any time unit.
    peak_width_1 (float): Width at the base of the first peak (w1), in the same unit as brut_retention_time_1.
    brut_retention_time_2 (float): Retention time of the second peak (t_R2), in the same unit as brut_retention_time_1.
    peak_width_2 (float): Width at the base of the second peak (w2), in the same unit as brut_retention_time_1.
    
    Returns:
    float: The resolution value (Rs).
    
    Raises:
    ValueError: If widths or retention time are non-positive or if the second peak elutes before the first.
    """
    if peak_width_1 <= 0 or peak_width_2 <= 0:
        raise ValueError("Peak widths must be strictly positive numbers.")
    
    if brut_retention_time_1 <= 0 or brut_retention_time_2 <= 0:
        raise ValueError("Retention time must be strictly positive numbers.")
    
    if brut_retention_time_2 < brut_retention_time_1:
        raise ValueError("The second peak must elute after the first peak (t_R2 >= t_R1).")
    # Formula: Rs = 2 * (t_R2 - t_R1) / (w1 + w2)
    resolution = (brut_retention_time_2-brut_retention_time_1)/(0.5*(peak_width_1+peak_width_2))

    return resolution


"""
fonctions_colonnes.py
---------------------
Functions for loading molecule databases and sorting molecules
by LogP or dipole moment to determine elution order.
"""

import csv
import os


# ── Database loading ───────────────────────────────────────────────────────────

def load_logp_db(path="data/logP.csv"):
    """
    Load the LogP database from a CSV file.

    Expected file format:
        CAS,SMILES,logP
        60-34-4,CNN,1.34
        64-19-7,CC(O)=O,1.22

    Parameters
    ----------
    path : str
        Path to the CSV file containing LogP data.

    Returns
    -------
    dict
        Dictionary indexed by CAS (lowercase) and SMILES (lowercase).
        Each value is a dict {"smiles": str, "logp": float}.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the given path.
    ValueError
        If the file is missing required columns CAS, SMILES or logP,
        if a logP value cannot be converted to float,
        or if the database is empty after parsing.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"LogP database not found: '{path}'\n"
            f"Make sure the file exists in the 'data/' folder."
        )

    db = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = [col.strip() for col in (reader.fieldnames or [])]

        required = {"CAS", "SMILES", "logP"}
        missing = required - set(fieldnames)
        if missing:
            raise ValueError(
                f"Missing columns in '{path}': {missing}\n"
                f"Columns found: {fieldnames}"
            )

        for i, row in enumerate(reader, start=2):
            cas    = (row.get("CAS")    or "").strip()
            smiles = (row.get("SMILES") or "").strip()
            logp_s = (row.get("logP")   or "").strip()

            if not logp_s:
                continue  # row without logP value: skip

            try:
                logp = float(logp_s)
            except ValueError:
                raise ValueError(
                    f"Invalid logP value at line {i} of '{path}': '{logp_s}'"
                )

            entry = {"smiles": smiles, "logp": logp}

            if cas:
                db[cas.lower()] = entry
            if smiles:
                db[smiles.lower()] = entry

    if not db:
        raise ValueError(
            f"The LogP database '{path}' is empty or contains no valid entries."
        )

    return db


def load_dipole_db(path="data/dipole.csv"):
    """
    Load the dipole moment database from a CSV or TSV file.

    Expected file format (tab or comma separated):
        Molecule    Name                Dipole
        H2          Hydrogen diatomic   0.000
        H2O         Water               1.857

    When a molecule appears more than once, only the row with the
    highest dipole value is kept.

    Parameters
    ----------
    path : str
        Path to the CSV/TSV file containing dipole moment data.

    Returns
    -------
    dict
        Dictionary indexed by molecular formula (Molecule, lowercase)
        and by name (Name, lowercase).
        Each value is a dict {"molecule": str, "dipole": float}.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the given path.
    ValueError
        If the file is missing required columns Molecule, Name or Dipole,
        if a Dipole value cannot be converted to float,
        or if the database is empty after parsing.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dipole database not found: '{path}'\n"
            f"Make sure the file exists in the 'data/' folder."
        )

    with open(path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    if not lines:
        raise ValueError(f"The file '{path}' is empty.")

    delimiter  = "\t" if "\t" in lines[0] else ","
    fieldnames = [col.strip() for col in lines[0].split(delimiter)]

    required = {"Molecule", "Name", "Dipole"}
    missing  = required - set(fieldnames)
    if missing:
        raise ValueError(
            f"Missing columns in '{path}': {missing}\n"
            f"Columns found: {fieldnames}"
        )

    reader = csv.DictReader(lines[1:], fieldnames=fieldnames, delimiter=delimiter)

    # Keep the highest dipole value per key (formula or name)
    best = {}

    for i, row in enumerate(reader, start=2):
        mol   = (row.get("Molecule") or "").strip()
        name  = (row.get("Name")     or "").strip()
        dip_s = (row.get("Dipole")   or "").strip()

        if not mol:
            continue  # empty row: skip

        if not dip_s:
            dip = 0.0
        else:
            try:
                dip = float(dip_s)
            except ValueError:
                raise ValueError(
                    f"Invalid Dipole value at line {i} of '{path}': '{dip_s}'"
                )

        entry = {"molecule": mol, "dipole": dip}

        for key in [mol.lower(), name.lower()]:
            if key and (key not in best or dip > best[key]["dipole"]):
                best[key] = entry

    if not best:
        raise ValueError(
            f"The dipole database '{path}' is empty or contains no valid entries."
        )

    return best


# ── Sorting functions ──────────────────────────────────────────────────────────

def sort_by_logp(molecules, db, column_type):
    """
    Sort a list of molecules by LogP according to the column type.

    Sorting rules:
      - Apolar column : ascending LogP  (least polar elutes first)
      - Polar column  : descending LogP (most polar elutes first)
      - Tie-break     : shorter SMILES string comes first

    Parameters
    ----------
    molecules : list[str]
        List of molecule identifiers (CAS or SMILES) entered by the user.
    db : dict
        Database returned by load_logp_db().
    column_type : str
        Column type: "apolar" or "polar".

    Returns
    -------
    list[str]
        List of molecule identifiers sorted in elution order (first to last).

    Raises
    ------
    ValueError
        If column_type is neither "apolar" nor "polar".
        If the molecule list is empty.
        If one or more molecules are not found in the database.
    """
    if not molecules:
        raise ValueError("The molecule list is empty.")

    if column_type not in ("apolar", "polar"):
        raise ValueError(
            f"Invalid column type: '{column_type}'. "
            f"Accepted values: 'apolar' or 'polar'."
        )

    not_found = [m for m in molecules if m.lower() not in db]
    if not_found:
        raise ValueError(
            "Molecule(s) not found in the LogP database:\n"
            + "\n".join(f"  - {m}" for m in not_found)
        )

    # reverse=True  → descending LogP (polar column)
    # reverse=False → ascending LogP  (apolar column)
    reverse = (column_type == "polar")

    def sort_key(mol):
        entry      = db[mol.lower()]
        logp       = entry["logp"]
        smiles_len = len(entry["smiles"])
        # Negate logp for descending sort without using reverse=True
        # so that the tie-break (smiles_len) always sorts ascending
        return (logp * (-1 if reverse else 1), smiles_len)

    return sorted(molecules, key=sort_key)


def sort_by_dipole(molecules, db, column_type):
    """
    Sort a list of molecules by dipole moment according to the column type.

    Sorting rules:
      - Apolar column : ascending dipole  (least polar elutes first)
      - Polar column  : descending dipole (most polar elutes first)
      - Tie-break     : shorter molecular formula string comes first

    Parameters
    ----------
    molecules : list[str]
        List of molecular formulas entered by the user.
    db : dict
        Database returned by load_dipole_db().
    column_type : str
        Column type: "apolar" or "polar".

    Returns
    -------
    list[str]
        List of molecule identifiers sorted in elution order (first to last).

    Raises
    ------
    ValueError
        If column_type is neither "apolar" nor "polar".
        If the molecule list is empty.
        If one or more molecules are not found in the database.
    """
    if not molecules:
        raise ValueError("The molecule list is empty.")

    if column_type not in ("apolar", "polar"):
        raise ValueError(
            f"Invalid column type: '{column_type}'. "
            f"Accepted values: 'apolar' or 'polar'."
        )

    not_found = [m for m in molecules if m.lower() not in db]
    if not_found:
        raise ValueError(
            "Molecule(s) not found in the dipole database:\n"
            + "\n".join(f"  - {m}" for m in not_found)
        )

    reverse = (column_type == "polar")

    def sort_key(mol):
        entry   = db[mol.lower()]
        dipole  = entry["dipole"]
        mol_len = len(entry["molecule"])
        return (dipole * (-1 if reverse else 1), mol_len)

    return sorted(molecules, key=sort_key)
