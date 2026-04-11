import unittest

from analysis_engine.utils.statistics_calculator import (StatisticsCalculator,
                                                         EmptySampleError,
                                                         NonNumericError,
                                                         InsufficientSampleSizeError)

class TestStatisticsCalculator(unittest.TestCase):
    calculator = StatisticsCalculator()
    invalid_input = [1, 2, "a", 4, 5]
    empty_input = []

    correct_input_a = [1, 2, 3, 4, 5]
    correct_input_b = [2, 4, 6, 8, 10]
    
    # calculated manually
    mean_a = 3.0
    median_a = 3.0
    stdev_a = 1.58
    stdev_b = 3.16
    pooled_stdev_ab = 2.50
    cohen_pooled_stdev_ab = 2.50
    cohen_pooled_stderror_ab = 1.58
    cohens_d_ab = 1.20
    independent_t_ab = round(-1.89, 1)

    # MAIN METHODS
    def test_mean(self):
        with self.assertRaises(NonNumericError):
            self.calculator.mean(self.invalid_input)

        with self.assertRaises(EmptySampleError):
            self.calculator.mean(self.empty_input)

        self.assertEqual(self.calculator.mean(self.correct_input_a),
                         self.mean_a)

    def test_median(self):
        with self.assertRaises(NonNumericError):
            self.calculator.median(self.invalid_input)

        with self.assertRaises(EmptySampleError):
            self.calculator.median(self.empty_input)

        self.assertEqual(self.calculator.median(self.correct_input_a),
                         self.median_a)

    def test_standard_deviation(self):
        with self.assertRaises(NonNumericError):
            self.calculator.standard_deviation(self.invalid_input)

        with self.assertRaises(EmptySampleError):
            self.calculator.standard_deviation(self.empty_input)

        self.assertEqual(round(self.calculator.standard_deviation(self.correct_input_a), 2),
                         self.stdev_a)
        
    def test_pooled_standard_deviation(self):
        with self.assertRaises(NonNumericError):
            self.calculator.pooled_standard_deviation(self.invalid_input, self.correct_input_a)

        with self.assertRaises(EmptySampleError):
            self.calculator.pooled_standard_deviation(self.empty_input, self.correct_input_a)

        self.assertEqual(self.calculator.pooled_standard_deviation(self.correct_input_a, self.correct_input_b),
                         self.pooled_stdev_ab)
        
    def test_cohen_pooled_standard_deviation(self):
        with self.assertRaises(NonNumericError):
            self.calculator.cohen_pooled_standard_deviation(self.invalid_input, self.correct_input_a)

        with self.assertRaises(EmptySampleError):
            self.calculator.cohen_pooled_standard_deviation(self.empty_input, self.correct_input_a)

        self.assertEqual(round(self.calculator.cohen_pooled_standard_deviation(self.correct_input_a, self.correct_input_b), 2),
                         self.cohen_pooled_stdev_ab)

    def  test_pooled_standard_error(self):
        with self.assertRaises(NonNumericError):
            self.calculator.cohen_pooled_standard_error(self.invalid_input, self.correct_input_a)

        with self.assertRaises(EmptySampleError):
            self.calculator.cohen_pooled_standard_error(self.empty_input, self.correct_input_a)

        self.assertEqual(round(self.calculator.cohen_pooled_standard_error(self.correct_input_a, self.correct_input_b), 2),
                         self.cohen_pooled_stderror_ab)

    def test_cohens_d(self):
        with self.assertRaises(NonNumericError):
            self.calculator.cohens_d(self.invalid_input, self.correct_input_a)

        with self.assertRaises(EmptySampleError):
            self.calculator.cohens_d(self.empty_input, self.correct_input_a)

        self.assertEqual(round(self.calculator.cohens_d(self.correct_input_a, self.correct_input_b), 2),
                         self.cohens_d_ab)

    def test_independent_t_test(self):
        with self.assertRaises(NonNumericError):
            self.calculator.welch_test(self.invalid_input, self.correct_input_a)

        with self.assertRaises(EmptySampleError):
            self.calculator.welch_test(self.empty_input, self.correct_input_a)

        self.assertEqual(round(self.calculator.welch_test(self.correct_input_a, self.correct_input_b), 2),
                         self.independent_t_ab)

    # HELPER / STATIC METHODS
    def test_validate_numeric_sample(self):
        with self.assertRaises(NonNumericError):
            self.calculator.validate_numeric_sample(self.invalid_input)

        with self.assertRaises(EmptySampleError):
            self.calculator.validate_numeric_sample(self.empty_input)

        self.assertIsNone(self.calculator.validate_numeric_sample(self.correct_input_a))
    
    def test_safe_divide(self):
        with self.assertRaises(ZeroDivisionError):
            self.calculator.safe_divide(0)

        self.assertEqual(self.calculator.safe_divide(10), 10)
