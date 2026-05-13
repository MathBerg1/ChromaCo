import numpy as np
import matplotlib.pyplot as plt



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

def calculate_resolution_from_dict(peaks_data : dict[int,list[float,float]], index_n : int) -> float:
    """
    Calculates the resolution (Rs) between two consecutive peaks (n and n+1)
    based on a dictionary of chromatographic data.
    
    Parameters:
    peaks_data (dict): A dictionary where:
                       - Keys are integers representing the peak index (1 to N).
                       - Values are lists [retention_time, peak_width].
    index_n (int): The index of the first peak (n) to compare with the next one (n+1).
    
    Returns:
    float: The resolution value (Rs) between peak n and peak n+1.
    
    Raises:
    ValueError: If the index is invalid, data is missing, or dimensions are incorrect.
    KeyError: If the specified index or the next index does not exist in the dictionary.
    """
    
    # 1. Validate that index_n exists
    if index_n not in peaks_data:
        raise KeyError(f"Index {index_n} not found in the dictionary.")
    
    # 2. Validate that the next peak (n+1) exists
    next_index = index_n + 1
    if next_index not in peaks_data:
        raise KeyError(f"Next peak index ({next_index}) not found. Cannot calculate resolution for the last peak.")
    
    # 3. Extract data for peak 1 (n)
    data_1 = peaks_data[index_n]
    if not isinstance(data_1, list) or len(data_1) != 2:
        raise ValueError(f"Data for peak {index_n} must be a list of two elements [t_R, w].")
    t_r1, w1 = data_1
    
    # 4. Extract data for peak 2 (n+1)
    data_2 = peaks_data[next_index]
    if not isinstance(data_2, list) or len(data_2) != 2:
        raise ValueError(f"Data for peak {next_index} must be a list of two elements [t_R, w].")
    t_r2, w2 = data_2
    
    # 5. Validate numerical constraints
    if w1 <= 0 or w2 <= 0:
        raise ValueError("Peak widths must be strictly positive numbers.")
    if t_r1 <= 0 or t_r2 <= 0:
        raise ValueError("Retention time must be strictly possitive number.")
    if t_r2 < t_r1:
        # In chromatography, peak n+1 should elute after peak n.
        raise ValueError("The first peak sould elute before the second.")

    # 6. Calculate Resolution
    # Formula: Rs = 2 * (t_R2 - t_R1) / (w1 + w2)
    delta_tr = t_r2 - t_r1
    sum_widths = w1 + w2
    
    resolution = (2 * delta_tr) / sum_widths
    
    return resolution

def calculate_dead_time_kovats(retention_times: dict[int, float]) -> float:
    """
    Calculates the dead time (t_M) of a chromatographic column using the Kovats method.
    
    This method uses the retention times of three consecutive n-alkanes to solve for t_M.
    It iterates through all possible consecutive triplets in the provided dictionary,
    calculates a t_M for each triplet, and returns the average of these values.
    
    Formula used for a triplet (t1, t2, t3):
    t_M = (t2^2 - t1 * t3) / (2 * t2 - (t1 + t3))
    
    Parameters:
    retention_times (dict[int, float]): A dictionary where:
                                        - Keys are integers representing the carbon number or index (1 to N).
                                        - Values are the gross retention times (t_R) of the n-alkanes.
                                        Keys must be consecutive integers for the triplets to be valid.
    
    Returns:
    float: The average calculated dead time (t_M).
    
    Raises:
    ValueError: If fewer than 3 data points are provided, or if no valid t_M can be calculated
                (e.g., denominator is zero in all cases).
    """
    if len(retention_times) < 3:
        raise ValueError("At least 3 retention times are required to calculate dead time using Kovats method.")

    # Sort keys to ensure we process them in order (1, 2, 3, ...)
    sorted_indices = sorted(retention_times.keys())
    
    calculated_tm_values = []

    # Iterate through the sorted keys to form triplets (i, i+1, i+2)
    # We stop at len - 2 because we need a group of 3
    for i in range(len(sorted_indices) - 2):
        idx1 = sorted_indices[i]
        idx2 = sorted_indices[i+1]
        idx3 = sorted_indices[i+2]

        # Check if keys are actually consecutive integers (e.g., 1, 2, 3 or 5, 6, 7)
        # If the user provides {1:..., 3:..., 4:...}, the triplet (1,3,4) is not valid for Kovats
        if not (idx2 == idx1 + 1 and idx3 == idx2 + 1):
            continue

        t1 = retention_times[idx1]
        t2 = retention_times[idx2]
        t3 = retention_times[idx3]

        # Validate retention times order (t3 > t2 > t1)
        if not (t3 > t2 > t1):
            raise ValueError("The retention times should be in order")

        # Calculate denominator: 2*t2 - (t1 + t3)
        denominator = 2 * t2 - (t1 + t3)

        # Avoid division by zero (which happens if t2 is exactly the arithmetic mean of t1 and t3)
        if denominator == 0:
            continue

        # Calculate t_M for this triplet
        # Formula: (t2^2 - t1*t3) / (2*t2 - t1 - t3)
        numerator = (t2 ** 2) - (t1 * t3)
        tm_triplet = numerator / denominator

        # Physical check: Dead time must be positive and less than the first retention time
        if 0 < tm_triplet < t1:
            calculated_tm_values.append(tm_triplet)

    if not calculated_tm_values:
        raise ValueError("Could not calculate any valid dead time. Check data consistency (consecutive indices, increasing times).")

    # Return the average of all valid calculated dead times
    return sum(calculated_tm_values) / len(calculated_tm_values)


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
    Load the dipole moment database from a CSV file.
    Indexed by SMILES only. Only SMILES and Dipole columns are required.

    Parameters
    ----------
    path : str
        Path to the CSV file (must contain at least SMILES and Dipole columns).

    Returns
    -------
    dict
        Dictionary indexed by SMILES (lowercase).
        Each value is a dict {"molecule": str, "dipole": float}.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the given path.
    ValueError
        If the file is missing required columns or is empty.
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

    required = {"SMILES", "Dipole"}
    missing  = required - set(fieldnames)
    if missing:
        raise ValueError(
            f"Missing columns in '{path}': {missing}\n"
            f"Columns found: {fieldnames}"
        )

    reader = csv.DictReader(lines[1:], fieldnames=fieldnames, delimiter=delimiter)

    best = {}

    for i, row in enumerate(reader, start=2):
        smiles = (row.get("SMILES")   or "").strip()
        dip_s  = (row.get("Dipole")   or "").strip()
        mol    = (row.get("Molecule") or smiles).strip()  # optional, fallback to SMILES

        # Skip rows without SMILES
        if not smiles:
            continue

        # Skip comment rows (e.g. "μ0 = 1.85498")
        if mol and not mol[0].isalnum():
            continue

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

        key = smiles.lower()
        if key not in best or dip > best[key]["dipole"]:
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


import numpy as np
import matplotlib.pyplot as plt

def plot_standard_addition(concentrations, areas, show_plot=True):
    """
    Performs linear regression for the standard addition method.
    Returns slope, intercept, R², and unknown concentration.
    If show_plot=True, displays the regression plot.
    """

    # --- Validation ---
    if len(concentrations) != len(areas):
        raise ValueError("Lists must have the same length.")
    if len(concentrations) < 2:
        raise ValueError("At least 2 points are required.")

    try:
        X = np.array(concentrations, dtype=float)
        Y = np.array(areas, dtype=float)
    except Exception:
        raise ValueError("All values must be numeric.")

    # --- Regression ---
    a, b = np.polyfit(X, Y, 1)
    if a == 0:
        raise ValueError("Slope is zero, cannot compute intercept.")

    Y_pred = a * X + b

    ss_res = np.sum((Y - Y_pred)**2)
    ss_tot = np.sum((Y - np.mean(Y))**2)
    r2 = 1 - ss_res/ss_tot if ss_tot != 0 else 0

    # Intercept at y = 0
    C_unknown = -b / a

    # If only calculation is needed
    if not show_plot:
        return {
            "a": a,
            "b": b,
            "r2": r2,
            "C_unknown": C_unknown
        }

    # --- Plotting ---
    # Ensure intercept is visible
    xmin = min(min(X), C_unknown) - abs(C_unknown) * 0.1
    xmax = max(max(X), C_unknown) + abs(C_unknown) * 0.1

    plt.figure(figsize=(7, 5))

    # Experimental points
    plt.scatter(X, Y, color="blue", label="Experimental points")

    # Regression line
    x_line = np.linspace(xmin, xmax, 200)
    plt.plot(x_line, a * x_line + b, color="blue", linewidth=2, label="Regression line")

    # Intercept line
    plt.axvline(C_unknown, color="red", linestyle="--",
                linewidth=2, label=f"Intercept = {C_unknown:.4f}")

    # Equation + R²
    sign = "+" if b >= 0 else "-"
    plt.text(0.05, 0.95,
             f"y = {a:.4f}x {sign} {abs(b):.4f}\nR² = {r2:.4f}",
             transform=plt.gca().transAxes,
             fontsize=10, verticalalignment="top",
             bbox=dict(facecolor="white", alpha=0.7))

    plt.xlabel("Added concentration")
    plt.ylabel("Peak area")
    plt.title("Standard Addition Method")
    plt.grid(True)
    plt.legend()
    plt.xlim(xmin, xmax)
    plt.tight_layout()
    plt.show()

    return {
        "a": a,
        "b": b,
        "r2": r2,
        "C_unknown": C_unknown
    }

def calculate_net_retention_times(all_retention_times: list[float], alkane_data: dict[int, float]) -> list[float]:
    """
    Calculates the net retention times (tR') for a list of peaks.
    
    1. Calculates the dead time (tM) using the 'calculate_dead_time_kovats' function.
    2. Subtracts tM from each gross retention time in the provided list.
    
    Args:
        all_retention_times (list[float]): List of brut retention times for all peaks.
        alkane_data (dict[int, float]): Dictionary {carbon_number: retention_time} for n-alkane references.
                                        Must contain at least 3 consecutive alkanes.
        
    Returns:
        list[float]: List of corresponding net retention times.
        
    Raises:
        ValueError: If the dead time calculation fails (insufficient or inconsistent alkane data).
    """
    # 1. Calculate dead time using the calculate_dead_time_kovats function
    # We delegate the entire dead time logic to calculate_dead_time_kovats
    try:
        t_dead = calculate_dead_time_kovats(alkane_data)
    except ValueError as e:
        # Propagate the error if alkanes do not allow calculation (e.g., not enough points, non-consecutive)
        raise ValueError(f"Failed to calculate dead time: {e}")

    # 2. Calculate net times (tR' = tR - tM)
    net_times = []
    for t_brut in all_retention_times:
        t_net = t_brut - t_dead
        
        # Optional: Warning if the peak elutes before the dead time (unretained peak or artifact)
        if t_net < 0:
            print(f"Warning: Brut time {t_brut:.4f} is less than the calculated dead time ({t_dead:.4f}).")
            
        net_times.append(t_net)
        
    return net_times

def calculate_selectivity_factor(brut_retention_times: dict[int, float], index: int) -> float:
    """
    Calculates the selectivity factor (alpha) between peak 'n' and peak 'n+1'.
    
    Logic:
    1. Identifies consecutive integer keys in the dictionary to treat them as n-alkanes for dead time calculation.
    2. Calculates net retention times for all peaks.
    3. Locates the specific pair (index, index+1) in the sorted list.
    4. Returns the single alpha value for this pair.
    
    Args:
        brut_retention_times (dict[int, float]): Dictionary {peak_index: brut_retention_time}.
                                                  Must contain at least 3 consecutive integer keys 
                                                  (to serve as alkanes for tM calculation).
        index (int): The index 'n' of the first peak in the pair. 
                     The function will calculate alpha between peak 'n' and peak 'n+1'.
        
    Returns:
        float: The selectivity factor (alpha) between peak 'n' and 'n+1'.
        
    Raises:
        ValueError: If the index is not found, if 'index+1' is not found, 
                    if insufficient data exists for dead time, or if net times are invalid.
    """
    if len(brut_retention_times) < 2:
        raise ValueError("At least 2 peaks are required in the dictionary.")

    if index not in brut_retention_times:
        raise ValueError(f"Peak index {index} not found in the dictionary.")
    
    # We need to find the successor in the elution order, not just index+1 numerically,
    # UNLESS the user implies the keys represent the elution order directly.
    # Based on previous context, keys are sorted to determine elution order.
    # So we find where 'index' sits in the sorted list, and take the next one.
    
    sorted_indices = sorted(brut_retention_times.keys())
    
    try:
        pos_n = sorted_indices.index(index)
    except ValueError:
        # Should be caught by the check above, but double safety
        raise ValueError(f"Peak index {index} not found in sorted list.")

    if pos_n + 1 >= len(sorted_indices):
        raise ValueError(f"No peak found after index {index}. Cannot calculate selectivity for the last peak.")

    index_next = sorted_indices[pos_n + 1]

    # 1. Identify Alkanes for Dead Time Calculation (Same logic as before)
    alkane_data = {}
    consecutive_sequences = []
    current_seq = []
    
    for i, idx in enumerate(sorted_indices):
        if not current_seq:
            current_seq = [idx]
        else:
            if idx == current_seq[-1] + 1:
                current_seq.append(idx)
            else:
                if len(current_seq) >= 3:
                    consecutive_sequences.append(current_seq)
                current_seq = [idx]
        if i == len(sorted_indices) - 1 and len(current_seq) >= 3:
            consecutive_sequences.append(current_seq)

    if not consecutive_sequences:
        raise ValueError(
            "Could not find at least 3 consecutive integer keys to calculate dead time. "
            "Ensure the dictionary contains n-alkanes labeled with consecutive integers."
        )
    
    alkane_indices = consecutive_sequences[0]
    alkane_data = {idx: brut_retention_times[idx] for idx in alkane_indices}

    # 2. Calculate Net Retention Times for ALL peaks
    all_brut_times = [brut_retention_times[i] for i in sorted_indices]
    
    try:
        net_times = calculate_net_retention_times(
            all_retention_times=all_brut_times,
            alkane_data=alkane_data
        )
    except ValueError as e:
        raise ValueError(f"Failed to calculate net retention times: {e}")

    # 3. Extract specific pair and calculate alpha
    t_net_1 = net_times[pos_n]       # Net time for peak 'n'
    t_net_2 = net_times[pos_n + 1]   # Net time for peak 'n+1' (in elution order)

    if t_net_1 <= 0 or t_net_2 <= 0:
        raise ValueError(
            f"Cannot calculate alpha for indices ({index}, {index_next}): "
            f"Net retention times must be positive (t1={t_net_1:.4f}, t2={t_net_2:.4f})."
        )

    # alpha = tR'(2) / tR'(1). Ensure alpha >= 1.
    if t_net_2 >= t_net_1:
        alpha = t_net_2 / t_net_1
    else:
        alpha = t_net_1 / t_net_2
        
    return alpha

