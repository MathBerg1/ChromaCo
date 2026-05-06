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
alkanes_data = {
    10: 5.50,  # t_R1
    11: 7.80,  # t_R2
    12: 8.40,  # t_R3
    13: 10.30, # t_R4
    14: 12.50  # t_R5
}
print(calculate_dead_time_kovats(alkanes_data))