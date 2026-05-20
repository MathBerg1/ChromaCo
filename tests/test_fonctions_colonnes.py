"""
test/test.py
------------
Unit tests for functions in src/chromaco/interfaces/fonctions_colonnes.py

Run with:
    python test/test.py
"""

import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "chromaco", "interfaces"))

from chromaco.interfaces.fonctions_colonnes import (
    theorical_plates_one,
    equivalent_high_one,
    resolution_between_two_peaks,
    calculate_resolution_from_dict,
    calculate_dead_time_kovats,
    calculate_net_retention_times,
    calculate_selectivity_factor,
    plot_standard_addition,
)


# ══════════════════════════════════════════════════════════════════════════════
# theorical_plates_one
# ══════════════════════════════════════════════════════════════════════════════

class TestTheoreticalPlates(unittest.TestCase):

    def test_basic_calculation(self):
        result = theorical_plates_one(10.0, 2.0)
        self.assertAlmostEqual(result, 16 * (10 / 2) ** 2, places=2)

    def test_exact_value(self):
        """tR=4, w=1 → N = 16 * 16 = 256."""
        self.assertAlmostEqual(theorical_plates_one(4.0, 1.0), 256.0, places=2)

    def test_high_efficiency_column(self):
        result = theorical_plates_one(100.0, 0.5)
        self.assertGreater(result, 100_000)

    def test_zero_peak_width_raises(self):
        with self.assertRaises(ValueError):
            theorical_plates_one(10.0, 0.0)

    def test_negative_peak_width_raises(self):
        with self.assertRaises(ValueError):
            theorical_plates_one(10.0, -1.0)

    def test_negative_retention_time_raises(self):
        with self.assertRaises(ValueError):
            theorical_plates_one(-5.0, 1.0)

    def test_zero_retention_time(self):
        result = theorical_plates_one(0.0, 1.0)
        self.assertAlmostEqual(result, 0.0, places=5)


# ══════════════════════════════════════════════════════════════════════════════
# equivalent_high_one
# ══════════════════════════════════════════════════════════════════════════════

class TestEquivalentHigh(unittest.TestCase):

    def test_basic_calculation(self):
        N = theorical_plates_one(10.0, 2.0)
        expected = round(0.25 / N, 7)
        self.assertAlmostEqual(equivalent_high_one(0.25, 10.0, 2.0), expected, places=7)

    def test_longer_column_gives_larger_H(self):
        h1 = equivalent_high_one(0.25, 10.0, 2.0)
        h2 = equivalent_high_one(0.50, 10.0, 2.0)
        self.assertAlmostEqual(h2, 2 * h1, places=6)

    def test_zero_peak_width_raises(self):
        with self.assertRaises(ValueError):
            equivalent_high_one(0.25, 10.0, 0.0)

    def test_negative_column_length_raises(self):
        with self.assertRaises(ValueError):
            equivalent_high_one(-0.25, 10.0, 1.0)

    def test_negative_retention_time_raises(self):
        with self.assertRaises(ValueError):
            equivalent_high_one(0.25, -10.0, 1.0)

    def test_result_rounded_to_7_decimals(self):
        result = equivalent_high_one(0.3, 8.0, 1.5)
        N = theorical_plates_one(8.0, 1.5)
        self.assertEqual(result, round(0.3 / N, 7))


# ══════════════════════════════════════════════════════════════════════════════
# resolution_between_two_peaks
# ══════════════════════════════════════════════════════════════════════════════

class TestResolution(unittest.TestCase):

    def test_basic_calculation(self):
        rs = resolution_between_two_peaks(5.0, 7.0, 1.0, 1.0)
        self.assertAlmostEqual(rs, 2 * (7 - 5) / (1 + 1), places=5)

    def test_baseline_resolved_peaks(self):
        rs = resolution_between_two_peaks(5.0, 8.0, 1.0, 1.0)
        self.assertGreaterEqual(rs, 1.5)

    def test_identical_retention_times(self):
        rs = resolution_between_two_peaks(5.0, 5.0, 1.0, 1.0)
        self.assertAlmostEqual(rs, 0.0, places=9)

    def test_second_peak_before_first_raises(self):
        with self.assertRaises(ValueError):
            resolution_between_two_peaks(7.0, 5.0, 1.0, 1.0)

    def test_zero_width_raises(self):
        with self.assertRaises(ValueError):
            resolution_between_two_peaks(5.0, 7.0, 0.0, 1.0)

    def test_negative_retention_time_raises(self):
        with self.assertRaises(ValueError):
            resolution_between_two_peaks(-1.0, 5.0, 1.0, 1.0)

    def test_different_widths(self):
        rs = resolution_between_two_peaks(5.0, 7.0, 1.0, 2.0)
        self.assertAlmostEqual(rs, 2 * (7 - 5) / (1 + 2), places=5)


# ══════════════════════════════════════════════════════════════════════════════
# calculate_resolution_from_dict
# ══════════════════════════════════════════════════════════════════════════════

class TestResolutionFromDict(unittest.TestCase):

    def test_basic(self):
        peaks = {1: [5.0, 1.0], 2: [7.0, 1.0]}
        rs = calculate_resolution_from_dict(peaks, 1)
        self.assertAlmostEqual(rs, 2 * (7 - 5) / (1 + 1), places=5)

    def test_missing_index_raises(self):
        peaks = {1: [5.0, 1.0], 2: [7.0, 1.0]}
        with self.assertRaises(KeyError):
            calculate_resolution_from_dict(peaks, 5)

    def test_last_peak_raises(self):
        peaks = {1: [5.0, 1.0], 2: [7.0, 1.0]}
        with self.assertRaises(KeyError):
            calculate_resolution_from_dict(peaks, 2)

    def test_invalid_data_format_raises(self):
        peaks = {1: [5.0], 2: [7.0, 1.0]}
        with self.assertRaises(ValueError):
            calculate_resolution_from_dict(peaks, 1)

    def test_three_peaks(self):
        peaks = {1: [5.0, 1.0], 2: [7.0, 1.0], 3: [10.0, 1.5]}
        rs12 = calculate_resolution_from_dict(peaks, 1)
        rs23 = calculate_resolution_from_dict(peaks, 2)
        self.assertAlmostEqual(rs12, 2 * (7 - 5) / (1 + 1), places=5)
        self.assertAlmostEqual(rs23, 2 * (10 - 7) / (1 + 1.5), places=5)


# ══════════════════════════════════════════════════════════════════════════════
# calculate_dead_time_kovats
# ══════════════════════════════════════════════════════════════════════════════

class TestDeadTimeKovats(unittest.TestCase):

    def test_basic_triplet(self):
        # t1=3, t2=5, t3=9 → tM = (25-27)/(10-12) = (-2)/(-2) = 1.0
        rt = {1: 3.0, 2: 5.0, 3: 9.0}
        tm = calculate_dead_time_kovats(rt)
        self.assertAlmostEqual(tm, 1.0, places=5)

    def test_fewer_than_3_raises(self):
        with self.assertRaises(ValueError):
            calculate_dead_time_kovats({1: 2.0, 2: 4.0})

    def test_non_consecutive_keys_raises(self):
        rt = {1: 3.0, 3: 5.0, 5: 9.0}
        with self.assertRaises(ValueError):
            calculate_dead_time_kovats(rt)

    def test_non_increasing_times_raises(self):
        with self.assertRaises(ValueError):
            calculate_dead_time_kovats({1: 9.0, 2: 5.0, 3: 3.0})

    def test_four_alkanes_returns_float(self):
        rt = {1: 3.0, 2: 5.0, 3: 9.0, 4: 17.0}
        tm = calculate_dead_time_kovats(rt)
        self.assertIsInstance(tm, float)
        self.assertGreater(tm, 0)


# ══════════════════════════════════════════════════════════════════════════════
# calculate_net_retention_times
# ══════════════════════════════════════════════════════════════════════════════

class TestNetRetentionTimes(unittest.TestCase):

    def setUp(self):
        self.alkanes = {1: 3.0, 2: 5.0, 3: 9.0}  # tM = 1.0

    def test_basic(self):
        net = calculate_net_retention_times([3.0, 5.0, 9.0, 12.0], self.alkanes)
        for got, exp in zip(net, [2.0, 4.0, 8.0, 11.0]):
            self.assertAlmostEqual(got, exp, places=5)

    def test_length_preserved(self):
        net = calculate_net_retention_times([4.0, 6.0, 10.0], self.alkanes)
        self.assertEqual(len(net), 3)

    def test_invalid_alkanes_raises(self):
        with self.assertRaises(ValueError):
            calculate_net_retention_times([5.0], {1: 3.0, 2: 5.0})


# ══════════════════════════════════════════════════════════════════════════════
# calculate_selectivity_factor
# ══════════════════════════════════════════════════════════════════════════════


class TestSelectivityFactor(unittest.TestCase):

    def test_basic(self):
        # t0 = 1
        # t_r1 = 6 → k1 = (6-1)/1 = 5
        # t_r2 = 11 → k2 = (11-1)/1 = 10
        # alpha = 10 / 5 = 2
        alpha = calculate_selectivity_factor(6.0, 11.0, 1.0)
        self.assertAlmostEqual(alpha, 2.0, places=2)

    def test_alpha_always_gte_1(self):
        # Inversion should still give alpha >= 1
        alpha = calculate_selectivity_factor(11.0, 6.0, 1.0)
        self.assertGreaterEqual(alpha, 1.0)

    def test_missing_index_raises(self):
        # Equivalent: invalid retention time (t_r <= t_0)
        with self.assertRaises(ValueError):
            calculate_selectivity_factor(1.0, 5.0, 1.0)

    def test_last_index_raises(self):
        # Same logic: invalid retention time
        with self.assertRaises(ValueError):
            calculate_selectivity_factor(5.0, 1.0, 1.0)

    def test_fewer_than_2_raises(self):
        # Not meaningful anymore → replaced by invalid input test
        with self.assertRaises(ValueError):
            calculate_selectivity_factor(5.0, None, 1.0)



# ══════════════════════════════════════════════════════════════════════════════
# plot_standard_addition
# ══════════════════════════════════════════════════════════════════════════════

class TestPlotStandardAddition(unittest.TestCase):

    def test_basic_result(self):
        # slope=2, intercept=4 → C_unknown = -4/2 = -2
        conc  = [0.0, 1.0, 2.0, 3.0]
        areas = [4.0, 6.0, 8.0, 10.0]
        result = plot_standard_addition(conc, areas, show_plot=False)
        self.assertAlmostEqual(result["C_unknown"], -2.0,  places=4)
        self.assertAlmostEqual(result["a"],          2.0,  places=4)
        self.assertAlmostEqual(result["b"],          4.0,  places=4)
        self.assertAlmostEqual(result["r2"],         1.0,  places=4)

    def test_r2_perfect_linear(self):
        conc  = [0.0, 1.0, 2.0]
        areas = [10.0, 20.0, 30.0]
        result = plot_standard_addition(conc, areas, show_plot=False)
        self.assertAlmostEqual(result["r2"], 1.0, places=5)

    def test_unequal_lengths_raises(self):
        with self.assertRaises(ValueError):
            plot_standard_addition([0, 1, 2], [10, 20], show_plot=False)

    def test_fewer_than_2_raises(self):
        with self.assertRaises(ValueError):
            plot_standard_addition([0], [10], show_plot=False)

    def test_zero_slope_raises(self):
        with self.assertRaises(ValueError):
            plot_standard_addition([0, 1, 2], [5.0, 5.0, 5.0], show_plot=False)

    def test_non_numeric_raises(self):
        with self.assertRaises((ValueError, TypeError)):
            plot_standard_addition(["a", "b"], [1, 2], show_plot=False)

    def test_c_unknown_value(self):
        # slope=2, intercept=8 → C_unknown = -8/2 = -4
        conc  = [0.0, 2.0, 4.0]
        areas = [8.0, 12.0, 16.0]
        result = plot_standard_addition(conc, areas, show_plot=False)
        self.assertAlmostEqual(result["C_unknown"], -4.0, places=4)


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)