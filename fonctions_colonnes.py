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
