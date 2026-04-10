import unittest

from analysis_engine.utils.conclusion_mapper import ConclusionMapper
from analysis_engine.utils.statistics_calculator import StatisticsCalculator

# this may be more of an integration test than a unit test, but it is important to
# ensure that the mapper produces the expected conclusions given certain inputs.
# We can also use this as a starting point for testing the individual mapping
# functions (e.g. map_effect_size_conclusion) in isolation.
class TestConclusionMapper(unittest.TestCase):
    mapper = ConclusionMapper()

    def test_mean_differences(self):
        mean_a = 8
        mean_b = 4
        greater_str = "Group A's mean is greater than Group B's: {group_a_mean} > {group_b_mean}"
        lesser_str = "Group A's mean is less than Group B's: {group_a_mean} < {group_b_mean}"
        equal_Str ="Group A's mean is equivalent to Group B's: {group_a_mean} = {group_b_mean}"

        self.assertEqual(greater_str.format(group_a_mean=mean_a, group_b_mean=mean_b),
                         self.mapper.map_mean_differences(mean_a, mean_b))
        self.assertEqual(lesser_str.format(group_a_mean=mean_b, group_b_mean=mean_a),
                         self.mapper.map_mean_differences(mean_b, mean_a))
        self.assertEqual(equal_Str.format(group_a_mean=mean_a, group_b_mean=mean_a),
                         self.mapper.map_mean_differences(mean_a, mean_a))

    def test_map_effect_size_conclusion(self):
        large_size = 1
        medium_size = 0.7
        small_size = 0.4
        no_size = 0.1
        invalid_input = "1"

        large_str = "a large effect"
        medium_str = "a medium effect"
        small_str = "a small effect"
        no_effect_str = "no meaningful effect"
        none_str = "effect size could not be computed"

        self.assertEqual(large_str,
                         self.mapper.map_effect_size_conclusion(large_size))
        self.assertEqual(medium_str,
                         self.mapper.map_effect_size_conclusion(medium_size))
        self.assertEqual(small_str,
                         self.mapper.map_effect_size_conclusion(small_size))
        self.assertEqual(no_effect_str,
                         self.mapper.map_effect_size_conclusion(no_size))
        self.assertEqual(none_str,
                         self.mapper.map_effect_size_conclusion(None))
        with self.assertRaises(TypeError):
            self.mapper.map_effect_size_conclusion(invalid_input)

    def test_map_difference_conclusion(self):
        ... # TODO still need to implement map_different

    def test_sample_size_conclusion(self):
        small_size = 5
        sufficient_size = 19
        large_size = 21

        small_str = "This is a very small sample; interpret cautiously."
        small_sufficient_str = "This is small, but sufficient sample; interpret cautiously."
        sufficient_str = "This is a sufficient sample."

        self.assertEqual(small_str,
                         self.mapper.map_sample_size_conclusion(small_size))
        self.assertEqual(small_sufficient_str,
                         self.mapper.map_sample_size_conclusion(sufficient_size))
        self.assertEqual(sufficient_str,
                         self.mapper.map_sample_size_conclusion(large_size))

    def test_build_group_conclusion(self):
        calculator = StatisticsCalculator()

        group_labels = {"hormone_name": "test_hormone1",
                        "dysmenorrhea_present": True,
                        "performance_type": "OFF SEASON"}
        values = [1, 2, 3, 4, 5, 6]

        correct_group_summary = {**group_labels,
                                 "measured_values": values,
                                 "observation_count": len(values),
                                 "mean": calculator.mean(values),
                                 "median": calculator.median(values),
                                 "standard_deviation": (calculator.standard_deviation(values)
                                                        if len(values) > 1
                                                        else None)}
        
        group_conclusions = "This is small, but sufficient sample; interpret cautiously. " + \
                             f"{correct_group_summary['hormone_name']} has an average value of {correct_group_summary['mean']} " + \
                             f"in the '{correct_group_summary['performance_type']}' group with dysmenorrhea present."
                            
        
        self.assertEqual(group_conclusions,
                         self.mapper.build_group_conclusion(correct_group_summary))

    def test_build_comparison_conclusion(self):
        
        # hormone x performance stats

        # hormone x dysmenorrhea stats

        # hormone x dysmenorrhea x performance stats
        ...

    def test_build_overall_conclusions(self):
        # TODO I don't think this is necessary
        ...

    def test_build_overall_detailed_conclusions(self):
        # TODO I don't think this is necessary
        ...