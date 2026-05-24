"""
test/test.py
------------
Unit tests for functions in src/chromaco/interfaces/fonctions_colonnes.py

Run with:
    python test/test.py
"""

import os
import sys
import csv
import math
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "chromaco", "interfaces"))

from chromaco.interfaces.fonctions_colonnes import (
    theorical_plates_one,
    equivalent_high_one,
    resolution_between_two_peaks,
    calculate_resolution_from_dict,
    calculate_dead_time_kovats,
    calculate_net_retention_times,
    calculate_selectivity_factor,
    calculate_retention_factor,
    calculate_kovats_index,
    plot_standard_addition,
    compare_two_columns_advanced,
    load_logp_db,
    load_dipole_db,
    sort_by_logp,
    sort_by_dipole,
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
        alpha = calculate_selectivity_factor(11.0, 6.0, 1.0)
        self.assertGreaterEqual(alpha, 1.0)

    def test_missing_index_raises(self):
        with self.assertRaises(ValueError):
            calculate_selectivity_factor(1.0, 5.0, 1.0)

    def test_last_index_raises(self):
        with self.assertRaises(ValueError):
            calculate_selectivity_factor(5.0, 1.0, 1.0)

    def test_fewer_than_2_raises(self):
        with self.assertRaises(ValueError):
            calculate_selectivity_factor(5.0, None, 1.0)

    def test_order_invariant(self):
        """alpha must be the same regardless of which peak is passed first."""
        a1 = calculate_selectivity_factor(6.0, 11.0, 1.0)
        a2 = calculate_selectivity_factor(11.0, 6.0, 1.0)
        self.assertAlmostEqual(a1, a2, places=10)

    def test_always_gte_1(self):
        for t1, t2 in [(3.0, 8.0), (5.0, 12.0), (10.0, 15.0)]:
            with self.subTest(t1=t1, t2=t2):
                alpha = calculate_selectivity_factor(t1, t2, 1.0)
                self.assertGreaterEqual(alpha, 1.0)

    def test_equal_retention_times_gives_1(self):
        """Two peaks with identical retention time → alpha = 1."""
        self.assertAlmostEqual(
            calculate_selectivity_factor(5.0, 5.0, 1.0), 1.0, places=10
        )

    def test_known_value(self):
        # k1 = (4-1)/1 = 3, k2 = (7-1)/1 = 6 → alpha = 6/3 = 2
        self.assertAlmostEqual(
            calculate_selectivity_factor(4.0, 7.0, 1.0), 2.0, places=10
        )

    def test_invalid_t0_propagates(self):
        with self.assertRaises(ValueError):
            calculate_selectivity_factor(5.0, 8.0, 0.0)

    def test_t_r_equal_t0_propagates(self):
        with self.assertRaises(ValueError):
            calculate_selectivity_factor(1.0, 5.0, 1.0)


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
# calculate_retention_factor
# ══════════════════════════════════════════════════════════════════════════════

class TestRetentionFactor(unittest.TestCase):

    def test_basic_calculation(self):
        # k = (t_r - t_0) / t_0 = (5 - 1) / 1 = 4
        self.assertAlmostEqual(calculate_retention_factor(5.0, 1.0), 4.0, places=10)

    def test_large_retention_factor(self):
        # k = (100 - 1) / 1 = 99
        self.assertAlmostEqual(calculate_retention_factor(100.0, 1.0), 99.0, places=10)

    def test_fractional_times(self):
        # k = (2.5 - 0.5) / 0.5 = 4
        self.assertAlmostEqual(calculate_retention_factor(2.5, 0.5), 4.0, places=10)

    def test_t_r_none_raises(self):
        with self.assertRaises(ValueError):
            calculate_retention_factor(None, 1.0)

    def test_t_0_none_raises(self):
        with self.assertRaises(ValueError):
            calculate_retention_factor(5.0, None)

    def test_t_r_non_numeric_raises(self):
        with self.assertRaises(ValueError):
            calculate_retention_factor("five", 1.0)

    def test_t_0_non_numeric_raises(self):
        with self.assertRaises(ValueError):
            calculate_retention_factor(5.0, "one")

    def test_t_r_zero_raises(self):
        with self.assertRaises(ValueError):
            calculate_retention_factor(0.0, 1.0)

    def test_t_r_negative_raises(self):
        with self.assertRaises(ValueError):
            calculate_retention_factor(-3.0, 1.0)

    def test_t_0_zero_raises(self):
        with self.assertRaises(ValueError):
            calculate_retention_factor(5.0, 0.0)

    def test_t_0_negative_raises(self):
        with self.assertRaises(ValueError):
            calculate_retention_factor(5.0, -1.0)

    def test_t_r_equal_to_t_0_raises(self):
        with self.assertRaises(ValueError):
            calculate_retention_factor(2.0, 2.0)

    def test_t_r_less_than_t_0_raises(self):
        with self.assertRaises(ValueError):
            calculate_retention_factor(1.0, 3.0)


# ══════════════════════════════════════════════════════════════════════════════
# calculate_kovats_index
# ══════════════════════════════════════════════════════════════════════════════

class TestKovatsIndex(unittest.TestCase):
    """
    Reference alkanes: C10 @ 10.0 min, C11 @ 12.0 min, C12 @ 15.0 min.
    Dead time (Kovats triplet): tM = (12²-10·15)/(2·12-(10+15))
                                   = (144-150)/(24-25) = (-6)/(-1) = 6 min.

    Net times: t'(C10)=4, t'(C11)=6, t'(C12)=9.
    Unknown @ 10.8 min → t'_x = 4.8.

    I = 100·[10 + (log10(4.8)-log10(4))/(log10(6)-log10(4))]
    """

    ALKANES   = {10: 10.0, 11: 12.0, 12: 15.0}
    ALL_TIMES = [10.0, 10.8, 12.0, 15.0]
    UNKNOWN   = 10.8

    def _expected_index(self) -> float:
        tM      = 6.0
        t_net_x = self.UNKNOWN      - tM
        t_net_n = self.ALKANES[10]  - tM
        t_net_N = self.ALKANES[11]  - tM
        factor  = (math.log10(t_net_x) - math.log10(t_net_n)) / (
                   math.log10(t_net_N) - math.log10(t_net_n))
        return 100 * (10 + factor)

    def test_index_between_1000_and_1100(self):
        idx = calculate_kovats_index(
            self.UNKNOWN, self.ALL_TIMES, self.ALKANES, 10, 11
        )
        self.assertGreater(idx, 1000)
        self.assertLess(idx, 1100)

    def test_known_value(self):
        idx = calculate_kovats_index(
            self.UNKNOWN, self.ALL_TIMES, self.ALKANES, 10, 11
        )
        self.assertAlmostEqual(idx, self._expected_index(), places=4)

    def test_missing_carbon_before_raises(self):
        with self.assertRaises(ValueError):
            calculate_kovats_index(
                self.UNKNOWN, self.ALL_TIMES, self.ALKANES, 9, 11
            )

    def test_missing_carbon_after_raises(self):
        with self.assertRaises(ValueError):
            calculate_kovats_index(
                self.UNKNOWN, self.ALL_TIMES, self.ALKANES, 10, 13
            )

    def test_wrong_elution_order_raises(self):
        """Unknown eluting after C11 but bracketed as C10–C11 → ValueError."""
        all_times = [10.0, 12.5, 12.0, 15.0]
        with self.assertRaises(ValueError):
            calculate_kovats_index(12.5, all_times, self.ALKANES, 10, 11)

    def test_insufficient_alkanes_raises(self):
        """Only two alkanes → dead time cannot be computed."""
        with self.assertRaises(ValueError):
            calculate_kovats_index(
                self.UNKNOWN, self.ALL_TIMES, {10: 10.0, 11: 12.0}, 10, 11
            )

# ══════════════════════════════════════════════════════════════════════════════
# compare_two_columns_advanced
# ══════════════════════════════════════════════════════════════════════════════

class TestCompareTwoColumnsAdvanced(unittest.TestCase):

    # Column A: better resolved, slower
    COL_A = {
        1: [5.0,  0.5],
        2: [10.0, 0.5],
        3: [16.0, 0.5],
    }
    # Column B: faster but worse resolved
    COL_B = {
        1: [4.0,  1.5],
        2: [7.0,  1.5],
        3: [11.0, 1.5],
    }
    LENGTH = 0.25  # metres

    def _run(self, **kwargs):
        return compare_two_columns_advanced(
            self.COL_A, self.COL_B, self.LENGTH, **kwargs
        )

    # ── Return structure ─────────────────────────────────────────────────────

    def test_returns_required_keys(self):
        result = self._run()
        for key in ("verdict", "A", "B", "elimination", "pairs_used", "warnings"):
            with self.subTest(key=key):
                self.assertIn(key, result)

    def test_verdict_keys_present(self):
        verdict = self._run()["verdict"]
        for key in (
            "Best_resolution", "Best_efficiency_N",
            "Best_HETP", "Best_peak_width", "Fastest",
        ):
            self.assertIn(key, verdict)

    def test_verdict_values_are_a_or_b(self):
        verdict = self._run()["verdict"]
        for key, val in verdict.items():
            with self.subTest(key=key):
                self.assertIn(val, ("A", "B"))

    def test_pairs_are_consecutive(self):
        pairs = self._run()["pairs_used"]
        for i1, i2 in pairs:
            self.assertEqual(i2, i1 + 1)

    def test_no_duplicate_pairs(self):
        pairs = self._run()["pairs_used"]
        self.assertEqual(len(pairs), len(set(pairs)))

    # ── Metric correctness ───────────────────────────────────────────────────

    def test_column_a_has_better_resolution(self):
        result = self._run()
        self.assertGreater(result["A"]["Rs"], result["B"]["Rs"])
        self.assertEqual(result["verdict"]["Best_resolution"], "A")

    def test_column_b_is_faster(self):
        result = self._run()
        self.assertLess(result["B"]["time"], result["A"]["time"])
        self.assertEqual(result["verdict"]["Fastest"], "B")

    def test_column_a_has_better_N(self):
        result = self._run()
        self.assertGreater(result["A"]["N"], result["B"]["N"])
        self.assertEqual(result["verdict"]["Best_efficiency_N"], "A")

    def test_column_a_has_better_hetp(self):
        result = self._run()
        self.assertLess(result["A"]["H"], result["B"]["H"])
        self.assertEqual(result["verdict"]["Best_HETP"], "A")

    # ── Elimination and warning ─────────────────────────────────────────────

    def test_good_resolution_not_eliminated(self):
        result = self._run()
        self.assertFalse(result["elimination"]["A"])

    # ── Subset mode ──────────────────────────────────────────────────────────

    def test_global_mode_uses_all_peaks(self):
        result_global  = self._run(mode="global")
        result_subset  = compare_two_columns_advanced(
            self.COL_A, self.COL_B, self.LENGTH,
            selected_peaks=[1, 2, 3],
            mode="subset",
        )
        self.assertEqual(result_global["pairs_used"], result_subset["pairs_used"])


# ══════════════════════════════════════════════════════════════════════════════
# load_logp_db
# ══════════════════════════════════════════════════════════════════════════════

class TestLoadLogpDb(unittest.TestCase):

    def _make_csv(self, rows: list[str]) -> str:
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        )
        tmp.write("\n".join(rows))
        tmp.close()
        return tmp.name

    def tearDown(self):
        path = getattr(self, "_tmpfile", None)
        if path and os.path.exists(path):
            os.unlink(path)

    def test_basic_load(self):
        self._tmpfile = self._make_csv([
            "CAS,SMILES,logP",
            "60-34-4,CNN,1.34",
            "64-19-7,CC(O)=O,-0.17",
        ])
        db = load_logp_db(self._tmpfile)
        self.assertIn("60-34-4", db)
        self.assertIn("cnn", db)
        self.assertAlmostEqual(db["60-34-4"]["logp"], 1.34)

    def test_smiles_indexed(self):
        self._tmpfile = self._make_csv([
            "CAS,SMILES,logP",
            "60-34-4,CNN,1.34",
        ])
        db = load_logp_db(self._tmpfile)
        self.assertIn("cnn", db)

    def test_negative_logp(self):
        self._tmpfile = self._make_csv([
            "CAS,SMILES,logP",
            "64-19-7,CC(O)=O,-0.17",
        ])
        db = load_logp_db(self._tmpfile)
        self.assertAlmostEqual(db["64-19-7"]["logp"], -0.17)

    def test_file_not_found_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_logp_db("nonexistent_path/logp.csv")

    def test_missing_column_raises(self):
        self._tmpfile = self._make_csv([
            "CAS,SMILES",
            "60-34-4,CNN",
        ])
        with self.assertRaises(ValueError):
            load_logp_db(self._tmpfile)

    def test_invalid_logp_value_raises(self):
        self._tmpfile = self._make_csv([
            "CAS,SMILES,logP",
            "60-34-4,CNN,NOT_A_NUMBER",
        ])
        with self.assertRaises(ValueError):
            load_logp_db(self._tmpfile)

    def test_empty_file_raises(self):
        self._tmpfile = self._make_csv(["CAS,SMILES,logP"])
        with self.assertRaises(ValueError):
            load_logp_db(self._tmpfile)

    def test_rows_without_logp_skipped(self):
        self._tmpfile = self._make_csv([
            "CAS,SMILES,logP",
            "60-34-4,CNN,",
            "64-19-7,CC(O)=O,1.22",
        ])
        db = load_logp_db(self._tmpfile)
        self.assertNotIn("60-34-4", db)
        self.assertIn("64-19-7", db)


# ══════════════════════════════════════════════════════════════════════════════
# load_dipole_db
# ══════════════════════════════════════════════════════════════════════════════

class TestLoadDipoleDb(unittest.TestCase):

    def _make_tsv(self, rows: list[str]) -> str:
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        )
        tmp.write("\n".join(rows))
        tmp.close()
        return tmp.name

    def tearDown(self):
        path = getattr(self, "_tmpfile", None)
        if path and os.path.exists(path):
            os.unlink(path)

    def test_basic_load_tsv(self):
        self._tmpfile = self._make_tsv([
            "SMILES\tDipole\tMolecule",
            "O\t1.85\tWater",
            "CCO\t1.69\tEthanol",
        ])
        db = load_dipole_db(self._tmpfile)
        self.assertIn("o", db)
        self.assertAlmostEqual(db["o"]["dipole"], 1.85)
        self.assertEqual(db["o"]["molecule"], "Water")

    def test_smiles_key_is_lowercase(self):
        self._tmpfile = self._make_tsv([
            "SMILES\tDipole\tMolecule",
            "CCO\t1.69\tEthanol",
        ])
        db = load_dipole_db(self._tmpfile)
        self.assertIn("cco", db)

    def test_file_not_found_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_dipole_db("nonexistent/dipole.csv")

    def test_missing_column_raises(self):
        self._tmpfile = self._make_tsv([
            "SMILES\tMolecule",
            "O\tWater",
        ])
        with self.assertRaises(ValueError):
            load_dipole_db(self._tmpfile)

    def test_invalid_dipole_raises(self):
        self._tmpfile = self._make_tsv([
            "SMILES\tDipole",
            "O\tNOT_A_NUMBER",
        ])
        with self.assertRaises(ValueError):
            load_dipole_db(self._tmpfile)

    def test_empty_file_raises(self):
        self._tmpfile = self._make_tsv(["SMILES\tDipole"])
        with self.assertRaises(ValueError):
            load_dipole_db(self._tmpfile)

    def test_best_dipole_kept(self):
        """When the same SMILES appears twice, keep the higher dipole."""
        self._tmpfile = self._make_tsv([
            "SMILES\tDipole\tMolecule",
            "O\t1.85\tWater_a",
            "O\t2.10\tWater_b",
        ])
        db = load_dipole_db(self._tmpfile)
        self.assertAlmostEqual(db["o"]["dipole"], 2.10)


# ══════════════════════════════════════════════════════════════════════════════
# sort_by_logp
# ══════════════════════════════════════════════════════════════════════════════

class TestSortByLogp(unittest.TestCase):

    DB = {
        "ccc":   {"smiles": "CCC",   "logp":  1.0},
        "ccco":  {"smiles": "CCCO",  "logp": -0.5},
        "ccccc": {"smiles": "CCCCC", "logp":  2.8},
    }

    def test_apolar_ascending_order(self):
        result = sort_by_logp(["CCC", "CCCO", "CCCCC"], self.DB, "apolar")
        logps = [self.DB[m.lower()]["logp"] for m in result]
        self.assertEqual(logps, sorted(logps))

    def test_polar_descending_order(self):
        result = sort_by_logp(["CCC", "CCCO", "CCCCC"], self.DB, "polar")
        logps = [self.DB[m.lower()]["logp"] for m in result]
        self.assertEqual(logps, sorted(logps, reverse=True))

    def test_empty_list_raises(self):
        with self.assertRaises(ValueError):
            sort_by_logp([], self.DB, "apolar")

    def test_invalid_column_type_raises(self):
        with self.assertRaises(ValueError):
            sort_by_logp(["CCC"], self.DB, "reverse_phase")

    def test_molecule_not_in_db_raises(self):
        with self.assertRaises(ValueError):
            sort_by_logp(["UNKNOWN_MOL"], self.DB, "apolar")

    def test_single_molecule_returned(self):
        result = sort_by_logp(["CCC"], self.DB, "apolar")
        self.assertEqual(result, ["CCC"])

    def test_tiebreak_shorter_smiles_first(self):
        db = {
            "aa":  {"smiles": "AA",  "logp": 1.0},
            "aaa": {"smiles": "AAA", "logp": 1.0},
        }
        result = sort_by_logp(["AA", "AAA"], db, "apolar")
        self.assertEqual(result[0], "AA")


# ══════════════════════════════════════════════════════════════════════════════
# sort_by_dipole
# ══════════════════════════════════════════════════════════════════════════════

class TestSortByDipole(unittest.TestCase):

    DB = {
        "o":   {"molecule": "Water",   "dipole": 1.85},
        "cco": {"molecule": "Ethanol", "dipole": 1.69},
        "c":   {"molecule": "Methane", "dipole": 0.00},
    }

    def test_apolar_ascending_order(self):
        result = sort_by_dipole(["O", "CCO", "C"], self.DB, "apolar")
        dipoles = [self.DB[m.lower()]["dipole"] for m in result]
        self.assertEqual(dipoles, sorted(dipoles))

    def test_polar_descending_order(self):
        result = sort_by_dipole(["O", "CCO", "C"], self.DB, "polar")
        dipoles = [self.DB[m.lower()]["dipole"] for m in result]
        self.assertEqual(dipoles, sorted(dipoles, reverse=True))

    def test_empty_list_raises(self):
        with self.assertRaises(ValueError):
            sort_by_dipole([], self.DB, "apolar")

    def test_invalid_column_type_raises(self):
        with self.assertRaises(ValueError):
            sort_by_dipole(["O"], self.DB, "nonpolar")

    def test_molecule_not_in_db_raises(self):
        with self.assertRaises(ValueError):
            sort_by_dipole(["BENZENE"], self.DB, "apolar")

    def test_single_molecule_returned(self):
        result = sort_by_dipole(["O"], self.DB, "apolar")
        self.assertEqual(result, ["O"])

    def test_tiebreak_shorter_name_first(self):
        db = {
            "ab":  {"molecule": "AB",    "dipole": 1.0},
            "abc": {"molecule": "ABCDE", "dipole": 1.0},
        }
        result = sort_by_dipole(["AB", "ABC"], db, "apolar")
        self.assertEqual(result[0], "AB")


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)