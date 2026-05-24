
import csv
import math
import os
import textwrap

import matplotlib.pyplot as plt
import numpy as np


# ══════════════════════════════════════════════════════════════════════════════
# Column efficiency
# ══════════════════════════════════════════════════════════════════════════════

def theorical_plates_one(raw_retention_time: float, peak_width: float) -> float:
    """
    Calculate the number of theoretical plates (N) for a chromatography column.

    Parameters
    ----------
    brut_retention_time : float
        Retention time of the peak (t_R), in any time unit.
    peak_width : float
        Width of the peak at the base (w), in the same unit as retention_time.

    Returns
    -------
    float
        Number of theoretical plates (N).

    Raises
    ------
    ValueError
        If peak_width is zero or negative, or if brut_retention_time is negative.
    """
    if peak_width <= 0:
        raise ValueError("Peak width must be a strictly positive number.")
    if raw_retention_time < 0:
        raise ValueError("Retention time cannot be negative.")

    return 16 * (raw_retention_time / peak_width) ** 2


def equivalent_high_one(
    column_length: float,
    raw_rentention_time: float,
    peak_width: float,
) -> float:
    """
    Calculate the Height Equivalent to a Theoretical Plate (HETP) directly from
    chromatographic data.

    Parameters
    ----------
    column_length : float
        Total length of the chromatography column (L), in any length unit.
    brut_rentention_time : float
        Retention time of the peak (t_R), in any time unit.
    peak_width : float
        Width of the peak at the base (w), in the same unit as brut_rentention_time.

    Returns
    -------
    float
        HETP (H), in the same unit as column_length.

    Raises
    ------
    ValueError
        If peak_width is zero or negative, or if any time/length value is negative.
    """
    if peak_width <= 0:
        raise ValueError("Peak width must be a strictly positive number.")
    if raw_rentention_time < 0:
        raise ValueError("Retention time cannot be negative.")
    if column_length < 0:
        raise ValueError("Column length cannot be negative.")

    N = theorical_plates_one(raw_rentention_time, peak_width)
    return round(column_length / N, 7)


# ══════════════════════════════════════════════════════════════════════════════
# Resolution
# ══════════════════════════════════════════════════════════════════════════════

def resolution_between_two_peaks(
    raw_retention_time_1: float,
    raw_retention_time_2: float,
    peak_width_1: float,
    peak_width_2: float,
) -> float:
    """
    Calculate the resolution (Rs) between two consecutive chromatographic peaks.

    Parameters
    ----------
    brut_retention_time_1 : float
        Retention time of the first peak (t_R1), in any time unit.
    brut_retention_time_2 : float
        Retention time of the second peak (t_R2), in the same unit as t_R1.
    peak_width_1 : float
        Width at the base of the first peak (w1), in the same unit as t_R1.
    peak_width_2 : float
        Width at the base of the second peak (w2), in the same unit as t_R1.

    Returns
    -------
    float
        Resolution value (Rs).

    Raises
    ------
    ValueError
        If any width or retention time is non-positive, or if the second peak
        elutes before the first.
    """
    if peak_width_1 <= 0 or peak_width_2 <= 0:
        raise ValueError("Peak widths must be strictly positive numbers.")
    if raw_retention_time_1 <= 0 or raw_retention_time_2 <= 0:
        raise ValueError("Retention time must be strictly positive numbers.")
    if raw_retention_time_2 < raw_retention_time_1:
        raise ValueError("The second peak must elute after the first peak (t_R2 >= t_R1).")

    return (raw_retention_time_2 - raw_retention_time_1) / (0.5 * (peak_width_1 + peak_width_2))


def calculate_resolution_from_dict(
    peaks_data: dict[int, list[float, float]],
    index_n: int,
) -> float:
    """
    Calculate the resolution (Rs) between two consecutive peaks (n and n+1)
    from a dictionary of chromatographic data.

    Parameters
    ----------
    peaks_data : dict[int, list[float, float]]
        Dictionary where keys are peak indices (1 to N) and values are
        lists ``[retention_time, peak_width]``.
    index_n : int
        Index of the first peak (n) to compare with the next one (n+1).

    Returns
    -------
    float
        Resolution value (Rs) between peak n and peak n+1.

    Raises
    ------
    KeyError
        If index_n or index_n+1 does not exist in peaks_data.
    ValueError
        If data format is incorrect, widths are non-positive, retention times
        are non-positive, or elution order is violated.
    """
    if index_n not in peaks_data:
        raise KeyError(f"Index {index_n} not found in the dictionary.")

    next_index = index_n + 1
    if next_index not in peaks_data:
        raise KeyError(
            f"Next peak index ({next_index}) not found. "
            "Cannot calculate resolution for the last peak."
        )

    data_1 = peaks_data[index_n]
    if not isinstance(data_1, list) or len(data_1) != 2:
        raise ValueError(f"Data for peak {index_n} must be a list of two elements [t_R, w].")
    t_r1, w1 = data_1

    data_2 = peaks_data[next_index]
    if not isinstance(data_2, list) or len(data_2) != 2:
        raise ValueError(f"Data for peak {next_index} must be a list of two elements [t_R, w].")
    t_r2, w2 = data_2

    if w1 <= 0 or w2 <= 0:
        raise ValueError("Peak widths must be strictly positive numbers.")
    if t_r1 <= 0 or t_r2 <= 0:
        raise ValueError("Retention time must be strictly possitive number.")
    if t_r2 < t_r1:
        raise ValueError("The first peak sould elute before the second.")

    delta_tr = t_r2 - t_r1
    sum_widths = w1 + w2
    return (2 * delta_tr) / sum_widths


# ══════════════════════════════════════════════════════════════════════════════
# Dead time and retention factor
# ══════════════════════════════════════════════════════════════════════════════

def calculate_dead_time_kovats(retention_times: dict[int, float]) -> float:
    """
    Calculate the dead time (t_M) of a chromatographic column using the Kovats
    method.

    Iterates through all consecutive triplets of n-alkane retention times,
    computes t_M for each, and returns the average of physically valid results.

    Formula for a triplet (t1, t2, t3)::

        t_M = (t2² - t1·t3) / (2·t2 - (t1 + t3))

    Parameters
    ----------
    retention_times : dict[int, float]
        Dictionary where keys are consecutive carbon numbers (or indices) and
        values are gross retention times (t_R) of the corresponding n-alkanes.
        At least three consecutive entries are required.

    Returns
    -------
    float
        Average dead time (t_M) across all valid triplets.

    Raises
    ------
    ValueError
        If fewer than 3 data points are provided, or if no valid t_M can be
        derived (e.g., denominator is zero in all cases, or times are not
        strictly increasing).
    """
    if len(retention_times) < 3:
        raise ValueError(
            "At least 3 retention times are required to calculate dead time "
            "using the Kovats method."
        )

    sorted_indices = sorted(retention_times.keys())
    calculated_tm_values = []

    for i in range(len(sorted_indices) - 2):
        idx1 = sorted_indices[i]
        idx2 = sorted_indices[i + 1]
        idx3 = sorted_indices[i + 2]

        if not (idx2 == idx1 + 1 and idx3 == idx2 + 1):
            continue

        t1 = retention_times[idx1]
        t2 = retention_times[idx2]
        t3 = retention_times[idx3]

        if not (t3 > t2 > t1):
            raise ValueError("The retention times should be in order")

        denominator = 2 * t2 - (t1 + t3)
        if denominator == 0:
            continue

        numerator = (t2 ** 2) - (t1 * t3)
        tm_triplet = numerator / denominator

        if 0 < tm_triplet < t1:
            calculated_tm_values.append(tm_triplet)

    if not calculated_tm_values:
        raise ValueError(
            "Could not calculate any valid dead time. "
            "Check data consistency (consecutive indices, increasing times)."
        )

    return sum(calculated_tm_values) / len(calculated_tm_values)


def calculate_retention_factor(t_r: float, t_0: float) -> float:
    """
    Calculate the chromatographic retention factor k.

    The retention factor expresses how long an analyte is retained relative to
    an unretained compound::

        k = (t_r - t_0) / t_0

    Parameters
    ----------
    t_r : float
        Retention time of the analyte (same unit as t_0).
    t_0 : float
        Dead time / void time of the column.

    Returns
    -------
    float
        Retention factor k.

    Raises
    ------
    ValueError
        If t_r or t_0 is None, non-numeric, non-positive, or if t_r <= t_0.
    """
    if t_r is None:
        raise ValueError("Retention time t_r cannot be None.")
    if t_0 is None:
        raise ValueError("Dead time t_0 cannot be None.")
    if not isinstance(t_r, (int, float)):
        raise ValueError("Retention time t_r must be a number.")
    if not isinstance(t_0, (int, float)):
        raise ValueError("Dead time t_0 must be a number.")
    if t_r <= 0:
        raise ValueError("Retention time t_r must be strictly positive.")
    if t_0 <= 0:
        raise ValueError("Dead time t_0 must be strictly positive.")
    if t_r <= t_0:
        raise ValueError("Retention time t_r must be greater than dead time t_0.")

    return (t_r - t_0) / t_0


def calculate_selectivity_factor(t_r1: float, t_r2: float, t_0: float) -> float:
    """
    Calculate the selectivity factor (alpha) between two peaks.

    The selectivity factor is defined as::

        alpha = k2 / k1   (always >= 1)

    where k1 and k2 are the retention factors of peak 1 and peak 2.
    By convention, the function always divides the larger k by the smaller one.

    Parameters
    ----------
    t_r1 : float
        Retention time of the first peak.
    t_r2 : float
        Retention time of the second peak.
    t_0 : float
        Dead time / void time of the column.

    Returns
    -------
    float
        Selectivity factor alpha (always >= 1).

    Raises
    ------
    ValueError
        Propagated from calculate_retention_factor() if any time value is
        invalid (None, non-numeric, non-positive, or t_r <= t_0).
    """
    k1 = calculate_retention_factor(t_r1, t_0)
    k2 = calculate_retention_factor(t_r2, t_0)
    return k2 / k1 if k2 >= k1 else k1 / k2


# ══════════════════════════════════════════════════════════════════════════════
# Net retention times and Kovats index
# ══════════════════════════════════════════════════════════════════════════════

def calculate_net_retention_times(
    all_retention_times: list[float],
    alkane_data: dict[int, float],
) -> list[float]:
    """
    Calculate net retention times (tR') for a list of peaks.

    Dead time (tM) is estimated via :func:`calculate_dead_time_kovats` and
    subtracted from every gross retention time.

    Parameters
    ----------
    all_retention_times : list[float]
        Gross retention times for all peaks.
    alkane_data : dict[int, float]
        Dictionary ``{carbon_number: retention_time}`` for n-alkane references.
        Must contain at least 3 consecutive entries.

    Returns
    -------
    list[float]
        Net retention times in the same order as all_retention_times.

    Raises
    ------
    ValueError
        If dead time calculation fails (insufficient or inconsistent alkane data).
    """
    try:
        t_dead = calculate_dead_time_kovats(alkane_data)
    except ValueError as e:
        raise ValueError(f"Failed to calculate dead time: {e}")

    net_times = []
    for t_brut in all_retention_times:
        t_net = t_brut - t_dead
        if t_net < 0:
            print(
                f"Warning: Raw time {t_brut:.4f} is less than the calculated "
                f"dead time ({t_dead:.4f})."
            )
        net_times.append(t_net)

    return net_times


def calculate_kovats_index(
    gross_retention_unknown: float,
    all_gross_times: list[float],
    alkane_data: dict[int, float],
    n_carbon_before: int,
    n_carbon_after: int,
) -> float:
    """
    Calculate the Kovats Retention Index (I) for a specific compound.

    Uses the Van den Dool and Kratz equation based on net retention times::

        I = 100 · [ n + (log(t'R_x) - log(t'R_n)) / (log(t'R_N) - log(t'R_n)) ]

    Where:
    - n   = carbon number of the n-alkane eluting before the compound.
    - N   = carbon number of the n-alkane eluting after the compound.
    - t'R_x = net retention time of the unknown compound.
    - t'R_n = net retention time of the n-alkane with carbon number n.
    - t'R_N = net retention time of the n-alkane with carbon number N.

    Parameters
    ----------
    gross_retention_unknown : float
        Gross (observed) retention time of the compound to analyse.
    all_gross_times : list[float]
        Gross retention times for all peaks (including the unknown and alkanes).
    alkane_data : dict[int, float]
        Dictionary ``{carbon_number: gross_retention_time}`` for n-alkane
        references, used for dead-time calculation.
    n_carbon_before : int
        Carbon number (z) of the n-alkane eluting immediately before the
        unknown (e.g., 10 if the unknown is between C10 and C11).
    n_carbon_after : int
        Carbon number of the n-alkane eluting immediately after the unknown
        (e.g., 11 if the unknown is between C10 and C11).

    Returns
    -------
    float
        Kovats Retention Index (I).

    Raises
    ------
    ValueError
        If alkane reference times are missing, net times are non-positive, or
        the elution order is inconsistent.
    """
    processing_list = list(all_gross_times)

    if gross_retention_unknown not in processing_list:
        processing_list.append(gross_retention_unknown)

    for t_alk in alkane_data.values():
        if t_alk not in processing_list:
            processing_list.append(t_alk)

    try:
        net_times_list = calculate_net_retention_times(
            all_retention_times=processing_list,
            alkane_data=alkane_data,
        )
    except ValueError as e:
        raise ValueError(f"Failed to calculate net retention times: {e}")

    time_map = dict(zip(processing_list, net_times_list))

    t_net_unknown = time_map.get(gross_retention_unknown)

    if n_carbon_before not in alkane_data:
        raise ValueError(f"Alkane C{n_carbon_before} not found in alkane_data.")
    if n_carbon_after not in alkane_data:
        raise ValueError(f"Alkane C{n_carbon_after} not found in alkane_data.")

    t_net_n = time_map.get(alkane_data[n_carbon_before])
    t_net_N = time_map.get(alkane_data[n_carbon_after])

    if t_net_unknown is None or t_net_n is None or t_net_N is None:
        raise ValueError("Could not map gross times to net times correctly.")
    if t_net_unknown <= 0 or t_net_n <= 0 or t_net_N <= 0:
        raise ValueError("Net retention times must be positive for Kovats index calculation.")
    if not (t_net_n < t_net_unknown < t_net_N):
        raise ValueError(
            f"Elution order mismatch: The unknown (net tR'={t_net_unknown:.4f}) is not between "
            f"C{n_carbon_before} (net tR'={t_net_n:.4f}) and "
            f"C{n_carbon_after} (net tR'={t_net_N:.4f})."
        )

    log_unknown = math.log10(t_net_unknown)
    log_n       = math.log10(t_net_n)
    log_N       = math.log10(t_net_N)

    denominator = log_N - log_n
    if denominator == 0:
        raise ValueError("The net retention times of the two reference alkanes are identical.")

    interpolation_factor = (log_unknown - log_n) / denominator
    return 100 * (n_carbon_before + interpolation_factor)


# ══════════════════════════════════════════════════════════════════════════════
# Standard addition
# ══════════════════════════════════════════════════════════════════════════════

def plot_standard_addition(
    concentrations: list[float],
    areas: list[float],
    show_plot: bool = True,
) -> dict:
    """
    Perform linear regression for the standard addition method.

    Parameters
    ----------
    concentrations : list[float]
        Added standard concentrations (including zero for the original sample).
    areas : list[float]
        Corresponding peak areas.
    show_plot : bool, optional
        If True (default), display the regression plot.

    Returns
    -------
    dict
        ``{"a": slope, "b": intercept, "r2": R², "C_unknown": unknown_concentration}``

    Raises
    ------
    ValueError
        If the lists differ in length, contain fewer than 2 points, contain
        non-numeric values, or the slope is effectively zero.
    """
    if len(concentrations) != len(areas):
        raise ValueError("Lists must have the same length.")
    if len(concentrations) < 2:
        raise ValueError("At least 2 points are required.")

    try:
        X = np.array(concentrations, dtype=float)
        Y = np.array(areas, dtype=float)
    except Exception:
        raise ValueError("All values must be numeric.")

    a, b = np.polyfit(X, Y, 1)
    if abs(a) < 1e-12:
        raise ValueError("Slope is zero, cannot compute intercept.")

    Y_pred = a * X + b
    ss_res = np.sum((Y - Y_pred) ** 2)
    ss_tot = np.sum((Y - np.mean(Y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0

    C_unknown = -b / a

    if not show_plot:
        return {"a": a, "b": b, "r2": r2, "C_unknown": C_unknown}

    xmin = min(min(X), C_unknown) - abs(C_unknown) * 0.1
    xmax = max(max(X), C_unknown) + abs(C_unknown) * 0.1

    plt.figure(figsize=(7, 5))
    plt.scatter(X, Y, color="blue", label="Experimental points")

    x_line = np.linspace(xmin, xmax, 200)
    plt.plot(x_line, a * x_line + b, color="blue", linewidth=2, label="Regression line")
    plt.axvline(
        C_unknown, color="red", linestyle="--", linewidth=2,
        label=f"Intercept = {C_unknown:.4f}",
    )

    sign = "+" if b >= 0 else "-"
    plt.text(
        0.05, 0.95,
        f"y = {a:.4f}x {sign} {abs(b):.4f}\nR² = {r2:.4f}",
        transform=plt.gca().transAxes,
        fontsize=10, verticalalignment="top",
        bbox=dict(facecolor="white", alpha=0.7),
    )

    plt.xlabel("Added concentration")
    plt.ylabel("Peak area")
    plt.title("Standard Addition Method")
    plt.grid(True)
    plt.legend()
    plt.xlim(xmin, xmax)
    plt.tight_layout()
    plt.show()

    return {"a": a, "b": b, "r2": r2, "C_unknown": C_unknown}


# ══════════════════════════════════════════════════════════════════════════════
# Column comparison
# ══════════════════════════════════════════════════════════════════════════════

def compare_two_columns_advanced(
    columnA: dict,
    columnB: dict,
    column_length: float,
    selected_peaks: list[int] | None = None,
    mode: str = "global",
) -> dict:
    """
    Compare two chromatographic columns using peak-based performance metrics.

    Evaluates both columns on:

    - Resolution between consecutive peaks (Rs)
    - Theoretical plates (N)
    - Height Equivalent to a Theoretical Plate (HETP, H)
    - Peak widths
    - Total analysis time

    Only **consecutive peak pairs (i, i+1)** are considered. Each pair is
    counted exactly once. If any individual resolution value is below 1.5 for
    an included pair, a warning is added to the output under ``"warnings"``.

    Parameters
    ----------
    columnA : dict[int, list[float, float]]
        Peaks for column A. Format: ``{peak_index: [tR, w]}``.
    columnB : dict[int, list[float, float]]
        Same structure as columnA, for column B.
    column_length : float
        Column length in metres, used for HETP calculation.
    selected_peaks : list[int] or None, optional
        Peak indices to include. If None, all peaks in the dataset are used.
    mode : {"global", "subset"}, optional
        ``"global"`` uses all peaks; ``"subset"`` restricts to selected_peaks.

    Returns
    -------
    dict
        ``{
            "verdict":    {criterion: "A" or "B"},
            "A":          {metric: value},
            "B":          {metric: value},
            "elimination": {"A": bool, "B": bool},
            "pairs_used": [(i, i+1), ...],
            "warnings":   {"A": [str, ...], "B": [str, ...]},
        }``
    """

    def safe_theoretical_plates(tR, w):
        try:
            if tR <= 0 or w <= 0:
                return 0
            N = theorical_plates_one(tR, w)
            return N if N > 0 else 0
        except Exception:
            return 0

    def compute_metrics(peaks):
        indices = sorted(peaks.keys())
        if not indices:
            return {"N": {}, "H": {}, "widths": {}, "Rs": {}, "time": 0}

        N      = {i: safe_theoretical_plates(peaks[i][0], peaks[i][1]) for i in indices}
        H      = {i: equivalent_high_one(column_length, peaks[i][0], peaks[i][1]) for i in indices}
        widths = {i: peaks[i][1] for i in indices}

        Rs = {}
        for i1, i2 in zip(indices[:-1], indices[1:]):
            Rs[(i1, i2)] = resolution_between_two_peaks(
                peaks[i1][0], peaks[i2][0],
                peaks[i1][1], peaks[i2][1],
            )

        total_time = max(peaks[i][0] for i in indices)
        return {"N": N, "H": H, "widths": widths, "Rs": Rs, "time": total_time}

    A = compute_metrics(columnA)
    B = compute_metrics(columnB)

    if mode == "subset" and selected_peaks:
        selected_peaks = sorted(selected_peaks)
    else:
        selected_peaks = sorted(columnA.keys())

    def build_consecutive_pairs(peaks):
        return [(p, p + 1) for p in peaks if (p, p + 1) in A["Rs"]]

    valid_pairs = build_consecutive_pairs(selected_peaks)

    def check_elimination_and_warnings(metrics, pairs, label):
        eliminated = False
        warnings   = []
        for (i1, i2) in pairs:
            if (i1, i2) in metrics["Rs"]:
                Rs_val = metrics["Rs"][(i1, i2)]
                if Rs_val < 1.5:
                    eliminated = True
                    warnings.append(
                        f"Column {label}: Peak pair ({i1}, {i2}) has Rs = {Rs_val:.3f} < 1.5"
                    )
        return eliminated, warnings

    elimA, warnA = check_elimination_and_warnings(A, valid_pairs, "A")
    elimB, warnB = check_elimination_and_warnings(B, valid_pairs, "B")

    def sum_resolutions(Rs_dict, pairs):
        return sum(Rs_dict[p] for p in pairs if p in Rs_dict)

    scoreA = {
        "Rs":     sum_resolutions(A["Rs"], valid_pairs),
        "N":      sum(A["N"].get(i, 0) for pair in valid_pairs for i in pair),
        "H":      sum(A["H"].get(i, 0) for pair in valid_pairs for i in pair),
        "widths": sum(A["widths"].get(i, 0) for pair in valid_pairs for i in pair),
        "time":   A["time"],
    }

    scoreB = {
        "Rs":     sum_resolutions(B["Rs"], valid_pairs),
        "N":      sum(B["N"].get(i, 0) for pair in valid_pairs for i in pair),
        "H":      sum(B["H"].get(i, 0) for pair in valid_pairs for i in pair),
        "widths": sum(B["widths"].get(i, 0) for pair in valid_pairs for i in pair),
        "time":   B["time"],
    }

    verdict = {
        "Best_resolution":   "A" if scoreA["Rs"]     > scoreB["Rs"]     else "B",
        "Best_efficiency_N": "A" if scoreA["N"]       > scoreB["N"]      else "B",
        "Best_HETP":         "A" if scoreA["H"]       < scoreB["H"]      else "B",
        "Best_peak_width":   "A" if scoreA["widths"]  < scoreB["widths"] else "B",
        "Fastest":           "A" if scoreA["time"]    < scoreB["time"]   else "B",
    }

    return {
        "verdict":     verdict,
        "A":           scoreA,
        "B":           scoreB,
        "elimination": {"A": elimA, "B": elimB},
        "pairs_used":  valid_pairs,
        "warnings":    {"A": warnA, "B": warnB},
    }


# ══════════════════════════════════════════════════════════════════════════════
# Molecule databases
# ══════════════════════════════════════════════════════════════════════════════

def load_logp_db(path: str = "data/logP.csv") -> dict:
    """
    Load the LogP database from a CSV file.

    Expected file format::

        CAS,SMILES,logP
        60-34-4,CNN,1.34
        64-19-7,CC(O)=O,1.22

    Parameters
    ----------
    path : str, optional
        Path to the CSV file. Default is ``"data/logP.csv"``.

    Returns
    -------
    dict
        Dictionary indexed by CAS (lowercase) and SMILES (lowercase).
        Each value is ``{"smiles": str, "logp": float}``.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the given path.
    ValueError
        If required columns (CAS, SMILES, logP) are missing, a logP value
        cannot be converted to float, or the database is empty after parsing.
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
        missing  = required - set(fieldnames)
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
                continue

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


def load_dipole_db(path: str = "data/dipole.csv") -> dict:
    """
    Load the dipole moment database from a CSV file.

    Indexed by SMILES only. Only the SMILES and Dipole columns are required;
    the optional Molecule column is used as a display name when present.

    Parameters
    ----------
    path : str, optional
        Path to the CSV file. Default is ``"data/dipole.csv"``.

    Returns
    -------
    dict
        Dictionary indexed by SMILES (lowercase).
        Each value is ``{"molecule": str, "dipole": float}``.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the given path.
    ValueError
        If required columns (SMILES, Dipole) are missing or the database is
        empty after parsing.
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
    best   = {}

    for i, row in enumerate(reader, start=2):
        smiles = (row.get("SMILES")   or "").strip()
        dip_s  = (row.get("Dipole")   or "").strip()
        mol    = (row.get("Molecule") or smiles).strip()

        if not smiles:
            continue
        if mol and not mol[0].isalnum():
            continue

        dip = 0.0 if not dip_s else float.__new__(float)
        if dip_s:
            try:
                dip = float(dip_s)
            except ValueError:
                raise ValueError(
                    f"Invalid Dipole value at line {i} of '{path}': '{dip_s}'"
                )

        entry = {"molecule": mol, "dipole": dip}
        key   = smiles.lower()
        if key not in best or dip > best[key]["dipole"]:
            best[key] = entry

    if not best:
        raise ValueError(
            f"The dipole database '{path}' is empty or contains no valid entries."
        )

    return best


# ══════════════════════════════════════════════════════════════════════════════
# Elution-order sorting
# ══════════════════════════════════════════════════════════════════════════════

def sort_by_logp(molecules: list[str], db: dict, column_type: str) -> list[str]:
    """
    Sort a list of molecules by LogP according to the column type.

    Sorting rules:

    - Apolar column : ascending LogP  (least polar elutes first)
    - Polar column  : descending LogP (most polar elutes first)
    - Tie-break     : shorter SMILES string comes first

    Parameters
    ----------
    molecules : list[str]
        Molecule identifiers (CAS or SMILES) entered by the user.
    db : dict
        Database returned by :func:`load_logp_db`.
    column_type : str
        ``"apolar"`` or ``"polar"``.

    Returns
    -------
    list[str]
        Molecule identifiers sorted in elution order (first to last).

    Raises
    ------
    ValueError
        If column_type is invalid, the molecule list is empty, or any molecule
        is absent from the database.
    """
    if not molecules:
        raise ValueError("The molecule list is empty.")
    if column_type not in ("apolar", "polar"):
        raise ValueError(
            f"Invalid column type: '{column_type}'. "
            "Accepted values: 'apolar' or 'polar'."
        )

    not_found = [m for m in molecules if m.lower() not in db]
    if not_found:
        raise ValueError(
            "Molecule(s) not found in the LogP database:\n"
            + "\n".join(f"  - {m}" for m in not_found)
        )

    reverse = (column_type == "polar")

    def sort_key(mol):
        entry      = db[mol.lower()]
        logp       = entry["logp"]
        smiles_len = len(entry["smiles"])
        return (logp * (-1 if reverse else 1), smiles_len)

    return sorted(molecules, key=sort_key)


def sort_by_dipole(molecules: list[str], db: dict, column_type: str) -> list[str]:
    """
    Sort a list of molecules by dipole moment according to the column type.

    Sorting rules:

    - Apolar column : ascending dipole  (least polar elutes first)
    - Polar column  : descending dipole (most polar elutes first)
    - Tie-break     : shorter molecular formula string comes first

    Parameters
    ----------
    molecules : list[str]
        Molecular formulas entered by the user.
    db : dict
        Database returned by :func:`load_dipole_db`.
    column_type : str
        ``"apolar"`` or ``"polar"``.

    Returns
    -------
    list[str]
        Molecule identifiers sorted in elution order (first to last).

    Raises
    ------
    ValueError
        If column_type is invalid, the molecule list is empty, or any molecule
        is absent from the database.
    """
    if not molecules:
        raise ValueError("The molecule list is empty.")
    if column_type not in ("apolar", "polar"):
        raise ValueError(
            f"Invalid column type: '{column_type}'. "
            "Accepted values: 'apolar' or 'polar'."
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
