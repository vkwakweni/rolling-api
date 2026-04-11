import unittest
from typing import Optional
from uuid import uuid4
from datetime import datetime, timedelta
from random import randrange

from analysis_engine.methods.descriptive_hormone_analysis import (DescriptiveHormoneAnalysis,
                                                                  AnalysisInputError)
from analysis_engine.utils.conclusion_mapper import ConclusionMapper
from analysis_engine.utils.grouping_engine import GroupingEngine
from analysis_engine.utils.statistics_calculator import StatisticsCalculator
from analysis_engine.contracts import (HormoneAnalysisInput,
                                       HormoneAnalysisResult,
                                       HormoneObservation)
from analysis_engine.group_keys import (GroupKey,
                                        HormoneGroupKey,
                                        HormoneDysmenorrheaGroupKey,
                                        HormonePerformanceGroupKey,
                                        HormoneDysmenorrheaPerformanceGroupKey)

class TestDescriptiveHormoneAnalysis(unittest.TestCase):
    mapper = ConclusionMapper()
    grouper = GroupingEngine()
    calculator = StatisticsCalculator()
    engine = DescriptiveHormoneAnalysis()

    def test_run(self):
        payload: HormoneAnalysisInput
        ...

    def test_validate_input(self):
        with self.assertRaises(AnalysisInputError) as e:
            self.engine.validate_input(None)
        self.assertIn("must not be None", str(e.exception))

        empty_payload: Optional[HormoneAnalysisInput] = HormoneAnalysisInput(project_id=uuid4().hex,
                                                                             observations=[])
        with self.assertRaises(AnalysisInputError) as e:
            self.engine.validate_input(empty_payload)
        self.assertIn("must include observations", str(e.exception))

        correct_payload = HormoneAnalysisInput(project_id=uuid4().hex,
                                               observations=[HormoneObservation(athlete_id=uuid4(),
                                                                                observed_on=datetime(2026, 3, 5),
                                                                                hormone_name="test_hormone1",
                                                                                measured_value=1),
                                                            HormoneObservation(athlete_id=uuid4(),
                                                                                observed_on=datetime(2026, 3, 5),
                                                                                hormone_name="test_hormone2",
                                                                                measured_value=1),
                                                            HormoneObservation(athlete_id=uuid4(),
                                                                                observed_on=datetime(2026, 3, 5),
                                                                                hormone_name="test_hormone1",
                                                                                measured_value=2)])
        self.assertIsNone(self.engine.validate_input(correct_payload))

    def test_build_group_statistics(self):
        grouped_observation: dict[GroupKey, list[HormoneObservation]]
        date = datetime(2026, 3, 5)
        values = [1, 2]
        count = 2
        mean = 1.5
        median = 1.5
        stdev = 0.7071067811865476

        # hormone observations
        hormone_obs = {
            HormoneGroupKey(hormone_name="test_hormone1"): [HormoneObservation(athlete_id=uuid4().hex,
                                                                               observed_on=date,
                                                                               hormone_name="test_hormone1",
                                                                               measured_value=1),
                                                            HormoneObservation(athlete_id=uuid4().hex,
                                                                               observed_on=date,
                                                                               hormone_name="test_hormone1",
                                                                               measured_value=2)],
            HormoneGroupKey(hormone_name="test_hormone2"): [HormoneObservation(athlete_id=uuid4().hex,
                                                                               observed_on=date,
                                                                               hormone_name="test_hormone2",
                                                                               measured_value=1),
                                                            HormoneObservation(athlete_id=uuid4().hex,
                                                                               observed_on=date,
                                                                               hormone_name="test_hormone2",
                                                                               measured_value=2)]
        }
        hormone_stats = [
            {
                "hormone_name": "test_hormone1",
                "measured_values": values,
                "observation_count": count,
                "mean": mean,
                "median": median,
                "standard_deviation": stdev
            },
            {
                "hormone_name": "test_hormone2",
                "measured_values": values,
                "observation_count": count,
                "mean": mean,
                "median": median,
                "standard_deviation": stdev
            }
        ]
        self.assertEqual(hormone_stats,
                         self.engine.build_group_statistics(hormone_obs))

        # hormone x performance observations
        hormone_performance_obs = {
            HormonePerformanceGroupKey(hormone_name="test_hormone1",
                                       performance_type="OFF SEASON"): [HormoneObservation(athlete_id=uuid4().hex,
                                                                                           observed_on=date,
                                                                                           hormone_name="test_hormone1",
                                                                                           measured_value=1,
                                                                                           performance_type="OFF SEASON"),
                                                                        HormoneObservation(athlete_id=uuid4().hex,
                                                                                           observed_on=date,
                                                                                           hormone_name="test_hormone1",
                                                                                           measured_value=2,
                                                                                           performance_type="OFF SEASON")],
            HormonePerformanceGroupKey(hormone_name="test_hormone1",
                                       performance_type="HIGH INTENSITY"): [HormoneObservation(athlete_id=uuid4().hex,
                                                                                           observed_on=date,
                                                                                           hormone_name="test_hormone1",
                                                                                           measured_value=1,
                                                                                           performance_type="HIGH INTENSITY"),
                                                                        HormoneObservation(athlete_id=uuid4().hex,
                                                                                           observed_on=date,
                                                                                           hormone_name="test_hormone1",
                                                                                           measured_value=2,
                                                                                           performance_type="HIGH INTENSITY")],
            HormonePerformanceGroupKey(hormone_name="test_hormone2",
                                       performance_type="OFF SEASON"): [HormoneObservation(athlete_id=uuid4().hex,
                                                                                           observed_on=date,
                                                                                           hormone_name="test_hormone2",
                                                                                           measured_value=1,
                                                                                           performance_type="OFF SEASON"),
                                                                        HormoneObservation(athlete_id=uuid4().hex,
                                                                                           observed_on=date,
                                                                                           hormone_name="test_hormone2",
                                                                                           measured_value=2,
                                                                                           performance_type="OFF SEASON")]
        }

        hormone_performance_stats = [
            {
                "hormone_name": "test_hormone1",
                "performance_type": "OFF SEASON",
                "measured_values": values,
                "observation_count": count,
                "mean": mean,
                "median": median,
                "standard_deviation": stdev

            },
            {
                "hormone_name": "test_hormone1",
                "performance_type": "HIGH INTENSITY",
                "measured_values": values,
                "observation_count": count,
                "mean": mean,
                "median": median,
                "standard_deviation": stdev

            },
            {
                "hormone_name": "test_hormone2",
                "performance_type": "OFF SEASON",
                "measured_values": values,
                "observation_count": count,
                "mean": mean,
                "median": median,
                "standard_deviation": stdev

            }
        ]

        self.assertEqual(hormone_performance_stats,
                         self.engine.build_group_statistics(hormone_performance_obs))

        # hormone x dysmenorrhea observations
        hormone_dysmenorrhea_obs = {
            HormoneDysmenorrheaGroupKey(hormone_name="test_hormone1",
                                        dysmenorrhea_present=True): [HormoneObservation(athlete_id=uuid4().hex,
                                                                                        observed_on=date,
                                                                                        hormone_name="test_hormone1",
                                                                                        measured_value=1,
                                                                                        symptom_name="DYSMENORRHEA"),
                                                                    HormoneObservation(athlete_id=uuid4().hex,
                                                                                        observed_on=date,
                                                                                        hormone_name="test_hormone1",
                                                                                        measured_value=2,
                                                                                        symptom_name="DYSMENORRHEA"),],
            HormoneDysmenorrheaGroupKey(hormone_name="test_hormone1",
                                        dysmenorrhea_present=False): [HormoneObservation(athlete_id=uuid4().hex,
                                                                                        observed_on=date,
                                                                                        hormone_name="test_hormone1",
                                                                                        measured_value=1),
                                                                    HormoneObservation(athlete_id=uuid4().hex,
                                                                                        observed_on=date,
                                                                                        hormone_name="test_hormone1",
                                                                                        measured_value=2)],
            HormoneDysmenorrheaGroupKey(hormone_name="test_hormone2",
                                        dysmenorrhea_present=True): [HormoneObservation(athlete_id=uuid4().hex,
                                                                                        observed_on=date,
                                                                                        hormone_name="test_hormone2",
                                                                                        measured_value=1,
                                                                                        symptom_name="DYSMENORRHEA"),
                                                                    HormoneObservation(athlete_id=uuid4().hex,
                                                                                        observed_on=date,
                                                                                        hormone_name="test_hormone2",
                                                                                        measured_value=2,
                                                                                        symptom_name="DYSMENORRHEA"),]
        }

        hormone_dysmenorrhea_stats = [
            {
                "hormone_name": "test_hormone1",
                "dysmenorrhea_present": True,
                "measured_values": values,
                "observation_count": count,
                "mean": mean,
                "median": median,
                "standard_deviation": stdev

            },
            {
                "hormone_name": "test_hormone1",
                "dysmenorrhea_present": False,
                "measured_values": values,
                "observation_count": count,
                "mean": mean,
                "median": median,
                "standard_deviation": stdev

            },
            {
                "hormone_name": "test_hormone2",
                "dysmenorrhea_present": True,
                "measured_values": values,
                "observation_count": count,
                "mean": mean,
                "median": median,
                "standard_deviation": stdev

            },
        ]

        self.assertEqual(hormone_dysmenorrhea_stats,
                         self.engine.build_group_statistics(hormone_dysmenorrhea_obs))

        # hormone x dysmenorrhea x performance observations
        hormone_dysmenorrhea_performance_obs = {
            HormoneDysmenorrheaPerformanceGroupKey(hormone_name="test_hormone1",
                                                   dysmenorrhea_present=True,
                                                   performance_type="OFF SEASON"): [HormoneObservation(athlete_id=uuid4().hex,
                                                                                                       observed_on=date,
                                                                                                       hormone_name="test_hormone1",
                                                                                                       measured_value=1,
                                                                                                       symptom_name="DYSMENORRHEA",
                                                                                                       performance_type="OFF SEASON"),
                                                                                    HormoneObservation(athlete_id=uuid4().hex,
                                                                                                        observed_on=date,
                                                                                                        hormone_name="test_hormone1",
                                                                                                        measured_value=2,
                                                                                                        symptom_name="DYSMENORRHEA",
                                                                                                        performance_type="OFF SEASON")],
            HormoneDysmenorrheaPerformanceGroupKey(hormone_name="test_hormone1",
                                                   dysmenorrhea_present=True,
                                                   performance_type="HIGH INTENSITY"): [HormoneObservation(athlete_id=uuid4().hex,
                                                                                                       observed_on=date,
                                                                                                       hormone_name="test_hormone1",
                                                                                                       measured_value=1,
                                                                                                       symptom_name="DYSMENORRHEA",
                                                                                                       performance_type="HIGH INTENSITY"),
                                                                                    HormoneObservation(athlete_id=uuid4().hex,
                                                                                                        observed_on=date,
                                                                                                        hormone_name="test_hormone1",
                                                                                                        measured_value=2,
                                                                                                        symptom_name="DYSMENORRHEA",
                                                                                                        performance_type="HIGH INTENSITY")],
            HormoneDysmenorrheaPerformanceGroupKey(hormone_name="test_hormone2",
                                                   dysmenorrhea_present=False,
                                                   performance_type="OFF SEASON"): [HormoneObservation(athlete_id=uuid4().hex,
                                                                                                       observed_on=date,
                                                                                                       hormone_name="test_hormone2",
                                                                                                       measured_value=1,
                                                                                                       performance_type="OFF SEASON"),
                                                                                    HormoneObservation(athlete_id=uuid4().hex,
                                                                                                        observed_on=date,
                                                                                                        hormone_name="test_hormone2",
                                                                                                        measured_value=2,
                                                                                                        performance_type="OFF SEASON")],
        }
        
        hormone_dysmenorrhea_performance_stats = [
            {
                "hormone_name": "test_hormone1",
                "dysmenorrhea_present": True,
                "performance_type": "OFF SEASON",
                "measured_values": values,
                "observation_count": count,
                "mean": mean,
                "median": median,
                "standard_deviation": stdev
            },
            {
                "hormone_name": "test_hormone1",
                "dysmenorrhea_present": True,
                "performance_type": "HIGH INTENSITY",
                "measured_values": values,
                "observation_count": count,
                "mean": mean,
                "median": median,
                "standard_deviation": stdev
            },
            {
                "hormone_name": "test_hormone2",
                "dysmenorrhea_present": False,
                "performance_type": "OFF SEASON",
                "measured_values": values,
                "observation_count": count,
                "mean": mean,
                "median": median,
                "standard_deviation": stdev
            }
        ]

        self.assertEqual(hormone_dysmenorrhea_performance_stats,
                         self.engine.build_group_statistics(hormone_dysmenorrhea_performance_obs))

    def test_build_hormone_performance_statistics(self):
        values_a = [1, 2, 3, 4, 5, 6]
        values_b = [1, 4, 5, 7, 8, 9]
        count = 6
        mean_a = 3.5
        mean_b = 5.666666666666667
        median_a = 3.5
        median_b = 6
        stdev_a = 1.8708286933869707
        stdev_b = 2.943920288775949
        cohens_d = abs(-0.8784585919193318)
        independent_t = 1.5215349135496976 # TODO actual function is still wrong
        
        hormone_performance_stats = [
            {
                "hormone_name": "test_hormone1",
                "performance_type": "OFF SEASON",
                "measured_values": values_a,
                "observation_count": count,
                "mean": mean_a,
                "median": median_a,
                "standard_deviation": stdev_a

            },
            {
                "hormone_name": "test_hormone1",
                "performance_type": "HIGH INTENSITY",
                "measured_values": values_b,
                "observation_count": count,
                "mean": mean_b,
                "median": median_b,
                "standard_deviation": stdev_b

            },
            {
                "hormone_name": "test_hormone2",
                "performance_type": "OFF SEASON",
                "measured_values": values_a,
                "observation_count": values_a,
                "mean": mean_a,
                "median": median_a,
                "standard_deviation": stdev_a

            }
        ]

        intended_comparative = [
            {
                "hormone_name": "test_hormone1",
                "performance_type_a": "HIGH INTENSITY",
                "performance_type_b": "OFF SEASON",
                "measured_values_a": values_b,
                "measured_values_b": values_a,
                "observation_count_a": count,
                "observation_count_b": count,
                "mean_a": mean_b,
                "mean_b": mean_a,
                "median_a": median_b,
                "median_b": median_a,
                "standard_deviation_a": stdev_b,
                "standard_deviation_b": stdev_a,
                "cohens_d": cohens_d,
                "independent_t": independent_t,
                "observation_count": 2 * count
            }
        ]
        actual_comparative = self.engine.build_hormone_performance_statistics(hormone_performance_stats)
        for i in range(len(intended_comparative)):
            for key in intended_comparative[i].keys(): # TODO format better
                self.assertEqual(intended_comparative[i][key],
                                 actual_comparative[i][key])            

    def test_build_hormone_dysmenorrhea_statistics(self):
        values_a = [1, 2, 3, 4, 5, 6]
        values_b = [1, 4, 5, 7, 8, 9]
        count = 6
        mean_a = 3.5
        mean_b = 5.666666666666667
        median_a = 3.5
        median_b = 6
        stdev_a = 1.8708286933869707
        stdev_b = 2.943920288775949
        cohens_d = abs(-0.8784585919193318)
        independent_t = -1.5215349135496976
        
        hormone_dysmenorrhea_stats = [
            {
                "hormone_name": "test_hormone1",
                "dysmenorrhea_present": True,
                "measured_values": values_a,
                "observation_count": count,
                "mean": mean_a,
                "median": median_a,
                "standard_deviation": stdev_a

            },
            {
                "hormone_name": "test_hormone1",
                "dysmenorrhea_present": False,
                "measured_values": values_b,
                "observation_count": count,
                "mean": mean_b,
                "median": median_b,
                "standard_deviation": stdev_b

            },
            {
                "hormone_name": "test_hormone2",
                "dysmenorrhea_present": True,
                "measured_values": values_a,
                "observation_count": values_a,
                "mean": mean_a,
                "median": median_a,
                "standard_deviation": stdev_a

            }
        ]
        
        intended_comparative = [
            {
                "hormone_name": "test_hormone1",
                "dysmenorrhea_present_a": True,
                "dysmenorrhea_present_b": False,
                "measured_values_a": values_a,
                "measured_values_b": values_b,
                "observation_count_a": count,
                "observation_count_b": count,
                "mean_a": mean_a,
                "mean_b": mean_b,
                "median_a": median_a,
                "median_b": median_b,
                "standard_deviation_a": stdev_a,
                "standard_deviation_b": stdev_b,
                "cohens_d": cohens_d,
                "independent_t": independent_t,
                "observation_count": 2 * count
            }
        ]
        actual_comparative = self.engine.build_hormone_dysmenorrhea_statistics(hormone_dysmenorrhea_stats)
        for i in range(len(intended_comparative)):
            for key in intended_comparative[i].keys(): # TODO format better
                self.assertEqual(intended_comparative[i][key],
                                 actual_comparative[i][key]) 

    def test_build_hormone_dysmenorrhea_performance_statistics(self):
        values_a = [1, 2, 3, 4, 5, 6]
        values_b = [1, 4, 5, 7, 8, 9]
        count = 6
        mean_a = 3.5
        mean_b = 5.666666666666667
        median_a = 3.5
        median_b = 6.0
        stdev_a = 1.8708286933869707
        stdev_b = 2.943920288775949
        cohens_d = abs(-0.8784585919193318)
        independent_t = -1.5215349135496976
        
        hormone_dysmenorrhea_performance_stats = [
            {
                "hormone_name": "test_hormone1",
                "dysmenorrhea_present": True,
                "performance_type": "OFF SEASON",
                "measured_values": values_a,
                "observation_count": count,
                "mean": mean_a,
                "median": median_a,
                "standard_deviation": stdev_a

            },
            {
                "hormone_name": "test_hormone1",
                "dysmenorrhea_present": False,
                "performance_type": "OFF SEASON",
                "measured_values": values_b,
                "observation_count": count,
                "mean": mean_b,
                "median": median_b,
                "standard_deviation": stdev_b

            },
            {
                "hormone_name": "test_hormone1",
                "dysmenorrhea_present": True,
                "performance_type": "HIGH INTENSITY",
                "measured_values": values_a,
                "observation_count": values_a,
                "mean": mean_a,
                "median": median_a,
                "standard_deviation": stdev_a

            }
        ]
        
        intended_comparative = [
            {
                "hormone_name": "test_hormone1",
                "performance_type": "OFF SEASON",
                "dysmenorrhea_present_a": True,
                "dysmenorrhea_present_b": False,
                "measured_values_a": values_a,
                "measured_values_b": values_b,
                "observation_count_a": count,
                "observation_count_b": count,
                "mean_a": mean_a,
                "mean_b": mean_b,
                "median_a": median_a,
                "median_b": median_b,
                "standard_deviation_a": stdev_a,
                "standard_deviation_b": stdev_b,
                "cohens_d": cohens_d,
                "independent_t": independent_t,
                "observation_count": 2 * count
            },
            {
                "hormone_name": "test_hormone1",
                "dysmenorrhea_present": True,
                "performance_type_a": "OFF SEASON",
                "performance_type_b": "HIGH INTENSITY",
                "measured_values_a": values_a,
                "measured_values_b": values_a,
                "observation_count_a": count,
                "observation_count_b": count,
                "mean_a": mean_a,
                "mean_b": mean_a,
                "median_a": median_a,
                "median_b": median_a,
                "standard_deviation_a": stdev_a,
                "standard_deviation_b": stdev_a,
                "cohens_d": 0,
                "independent_t": 0,
                "observation_count": 2 * count
            }
        ]
        self.assertEqual(len(intended_comparative),
                         len(self.engine.build_hormone_dysmenorrhea_performance_statistics(hormone_dysmenorrhea_performance_stats)),
                         msg="Lengths are not equal")
        self.assertEqual(intended_comparative,
                        self.engine.build_hormone_dysmenorrhea_performance_statistics(hormone_dysmenorrhea_performance_stats))

    def test_build_summary(self):
        values = [1, 2]
        count = 2
        mean = 1.5
        median = 1.5
        stdev = 0.7071067811865476
        statistics = {
            "hormone_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev
                },
                {
                    "hormone_name": "test_hormone2",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev
                }
            ],
            "hormone_performance_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "performance_type": "OFF SEASON",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                },
                {
                    "hormone_name": "test_hormone1",
                    "performance_type": "HIGH INTENSITY",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                },
                {
                    "hormone_name": "test_hormone2",
                    "performance_type": "OFF SEASON",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                }
            ],
            "hormone_dysmenorrhea_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "dysmenorrhea_present": True,
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                },
                {
                    "hormone_name": "test_hormone1",
                    "dysmenorrhea_present": False,
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                },
                {
                    "hormone_name": "test_hormone2",
                    "dysmenorrhea_present": True,
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                }
            ],
            "hormone_dysmenorrhea_performance_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "dysmenorrhea_present": True,
                    "performance_type": "OFF SEASON",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                },
                {
                    "hormone_name": "test_hormone1",
                    "dysmenorrhea_present": True,
                    "performance_type": "HIGH INTENSITY",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                },
                {
                    "hormone_name": "test_hormone2",
                    "dysmenorrhea_present": False,
                    "performance_type": "OFF SEASON",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                }
            ],
            "comparative_hormone_performance_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "performance_type_a": "HIGH INTENSITY",
                    "performance_type_b": "OFF SEASON",
                    "measured_values_a": values,
                    "measured_values_b": values,
                    "observation_count_a": count,
                    "observation_count_b": count,
                    "mean_a": mean,
                    "mean_b": mean,
                    "median_a": median,
                    "median_b": median,
                    "standard_deviation_a": stdev,
                    "standard_deviation_b": stdev,
                    "cohens_d": 0,
                    "independent_t": 0,
                    "observation_count": 2 * count
                },
            ],
            "comparative_hormone_dysmenorrhea_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "dysmenorrhea_present_a": True,
                    "dysmenorrhea_present_b": False,
                    "measured_values_a": values,
                    "measured_values_b": values,
                    "observation_count_a": count,
                    "observation_count_b": count,
                    "mean_a": mean,
                    "mean_b": mean,
                    "median_a": median,
                    "median_b": median,
                    "standard_deviation_a": stdev,
                    "standard_deviation_b": stdev,
                    "cohens_d": 0,
                    "independent_t": 0,
                    "observation_count": 2 * count
                },
            ],
            "comparative_hormone_dysmenorrhea_performance_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "performance_type": "OFF SEASON",
                    "dysmenorrhea_present_a": True,
                    "dysmenorrhea_present_b": False,
                    "measured_values_a": values,
                    "measured_values_b": values,
                    "observation_count_a": count,
                    "observation_count_b": count,
                    "mean_a": mean,
                    "mean_b": mean,
                    "median_a": median,
                    "median_b": median,
                    "standard_deviation_a": stdev,
                    "standard_deviation_b": stdev,
                    "cohens_d": 0,
                    "independent_t": 0,
                    "observation_count": 2 * count
                },
                {
                    "hormone_name": "test_hormone1",
                    "dysmenorrhea_present": True,
                    "performance_type_a": "OFF SEASON",
                    "performance_type_b": "HIGH INTENSITY",
                    "measured_values_a": values,
                    "measured_values_b": values,
                    "observation_count_a": count,
                    "observation_count_b": count,
                    "mean_a": mean,
                    "mean_b": mean,
                    "median_a": median,
                    "median_b": median,
                    "standard_deviation_a": stdev,
                    "standard_deviation_b": stdev,
                    "cohens_d": 0,
                    "independent_t": 0,
                    "observation_count": 2 * count
                }
            ]
        }

        intended_summary = {
            "hormone_row_count": 2,
            "hormone_performance_row_count": 3,
            "hormone_dysmenorrhea_row_count": 3,
            "hormone_dysmenorrhea_performance_row_count": 3,
            "comparative_hormone_performance_row_count": 1,
            "comparative_hormone_dysmenorrhea_row_count": 1,
            "comparative_hormone_dysmenorrhea_performance_row_count": 2,
            "total_grouped_row_count": 15
        }
        self.assertEqual(intended_summary,
                         self.engine.build_summary(statistics))

    def test_build_tables(self):
        values = [1, 2]
        count = 2
        mean = 1.5
        median = 1.5
        stdev = 0.7071067811865476
        statistics = {
            "hormone_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev
                },
                {
                    "hormone_name": "test_hormone2",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev
                }
            ],
            "hormone_performance_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "performance_type": "OFF SEASON",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                },
                {
                    "hormone_name": "test_hormone1",
                    "performance_type": "HIGH INTENSITY",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                },
                {
                    "hormone_name": "test_hormone2",
                    "performance_type": "OFF SEASON",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                }
            ],
            "hormone_dysmenorrhea_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "dysmenorrhea_present": True,
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                },
                {
                    "hormone_name": "test_hormone1",
                    "dysmenorrhea_present": False,
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                },
                {
                    "hormone_name": "test_hormone2",
                    "dysmenorrhea_present": True,
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                }
            ],
            "hormone_dysmenorrhea_performance_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "dysmenorrhea_present": True,
                    "performance_type": "OFF SEASON",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                },
                {
                    "hormone_name": "test_hormone1",
                    "dysmenorrhea_present": True,
                    "performance_type": "HIGH INTENSITY",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                },
                {
                    "hormone_name": "test_hormone2",
                    "dysmenorrhea_present": False,
                    "performance_type": "OFF SEASON",
                    "measured_values": values,
                    "observation_count": count,
                    "mean": mean,
                    "median": median,
                    "standard_deviation": stdev,
                }
            ],
            "comparative_hormone_performance_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "performance_type_a": "HIGH INTENSITY",
                    "performance_type_b": "OFF SEASON",
                    "measured_values_a": values,
                    "measured_values_b": values,
                    "observation_count_a": count,
                    "observation_count_b": count,
                    "mean_a": mean,
                    "mean_b": mean,
                    "median_a": median,
                    "median_b": median,
                    "standard_deviation_a": stdev,
                    "standard_deviation_b": stdev,
                    "cohens_d": 0,
                    "independent_t": 0,
                    "observation_count": 2 * count
                },
            ],
            "comparative_hormone_dysmenorrhea_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "dysmenorrhea_present_a": True,
                    "dysmenorrhea_present_b": False,
                    "measured_values_a": values,
                    "measured_values_b": values,
                    "observation_count_a": count,
                    "observation_count_b": count,
                    "mean_a": mean,
                    "mean_b": mean,
                    "median_a": median,
                    "median_b": median,
                    "standard_deviation_a": stdev,
                    "standard_deviation_b": stdev,
                    "cohens_d": 0,
                    "independent_t": 0,
                    "observation_count": 2 * count
                },
            ],
            "comparative_hormone_dysmenorrhea_performance_statistics": [
                {
                    "hormone_name": "test_hormone1",
                    "performance_type": "OFF SEASON",
                    "dysmenorrhea_present_a": True,
                    "dysmenorrhea_present_b": False,
                    "measured_values_a": values,
                    "measured_values_b": values,
                    "observation_count_a": count,
                    "observation_count_b": count,
                    "mean_a": mean,
                    "mean_b": mean,
                    "median_a": median,
                    "median_b": median,
                    "standard_deviation_a": stdev,
                    "standard_deviation_b": stdev,
                    "cohens_d": 0,
                    "independent_t": 0,
                    "observation_count": 2 * count
                },
                {
                    "hormone_name": "test_hormone1",
                    "dysmenorrhea_present": True,
                    "performance_type_a": "OFF SEASON",
                    "performance_type_b": "HIGH INTENSITY",
                    "measured_values_a": values,
                    "measured_values_b": values,
                    "observation_count_a": count,
                    "observation_count_b": count,
                    "mean_a": mean,
                    "mean_b": mean,
                    "median_a": median,
                    "median_b": median,
                    "standard_deviation_a": stdev,
                    "standard_deviation_b": stdev,
                    "cohens_d": 0,
                    "independent_t": 0,
                    "observation_count": 2 * count
                }
            ]
        }

        intended_tables = [
            {
                "name": "hormone_statistics",
                "rows": [
                    {
                        "hormone_name": "test_hormone1",
                        "measured_values": values,
                        "observation_count": count,
                        "mean": mean,
                        "median": median,
                        "standard_deviation": stdev
                    },
                    {
                        "hormone_name": "test_hormone2",
                        "measured_values": values,
                        "observation_count": count,
                        "mean": mean,
                        "median": median,
                        "standard_deviation": stdev
                    }
                ],
            },
            {
                "name": "hormone_performance_statistics",
                "rows": [
                    {
                        "hormone_name": "test_hormone1",
                        "performance_type": "OFF SEASON",
                        "measured_values": values,
                        "observation_count": count,
                        "mean": mean,
                        "median": median,
                        "standard_deviation": stdev,
                    },
                    {
                        "hormone_name": "test_hormone1",
                        "performance_type": "HIGH INTENSITY",
                        "measured_values": values,
                        "observation_count": count,
                        "mean": mean,
                        "median": median,
                        "standard_deviation": stdev,
                    },
                    {
                        "hormone_name": "test_hormone2",
                        "performance_type": "OFF SEASON",
                        "measured_values": values,
                        "observation_count": count,
                        "mean": mean,
                        "median": median,
                        "standard_deviation": stdev,
                    }
                ],
            },
            {
                "name": "hormone_dysmenorrhea_statistics",
                "rows": [
                    {
                        "hormone_name": "test_hormone1",
                        "dysmenorrhea_present": True,
                        "measured_values": values,
                        "observation_count": count,
                        "mean": mean,
                        "median": median,
                        "standard_deviation": stdev,
                    },
                    {
                        "hormone_name": "test_hormone1",
                        "dysmenorrhea_present": False,
                        "measured_values": values,
                        "observation_count": count,
                        "mean": mean,
                        "median": median,
                        "standard_deviation": stdev,
                    },
                    {
                        "hormone_name": "test_hormone2",
                        "dysmenorrhea_present": True,
                        "measured_values": values,
                        "observation_count": count,
                        "mean": mean,
                        "median": median,
                        "standard_deviation": stdev,
                    }
                ],
            },
            {
                "name": "hormone_dysmenorrhea_performance_statistics",
                "rows": [
                    {
                        "hormone_name": "test_hormone1",
                        "dysmenorrhea_present": True,
                        "performance_type": "OFF SEASON",
                        "measured_values": values,
                        "observation_count": count,
                        "mean": mean,
                        "median": median,
                        "standard_deviation": stdev,
                    },
                    {
                        "hormone_name": "test_hormone1",
                        "dysmenorrhea_present": True,
                        "performance_type": "HIGH INTENSITY",
                        "measured_values": values,
                        "observation_count": count,
                        "mean": mean,
                        "median": median,
                        "standard_deviation": stdev,
                    },
                    {
                        "hormone_name": "test_hormone2",
                        "dysmenorrhea_present": False,
                        "performance_type": "OFF SEASON",
                        "measured_values": values,
                        "observation_count": count,
                        "mean": mean,
                        "median": median,
                        "standard_deviation": stdev,
                    }
                ],
            },
            
            {
                "name": "comparative_hormone_performance_statistics",
                "rows": [
                    {
                        "hormone_name": "test_hormone1",
                        "performance_type_a": "HIGH INTENSITY",
                        "performance_type_b": "OFF SEASON",
                        "measured_values_a": values,
                        "measured_values_b": values,
                        "observation_count_a": count,
                        "observation_count_b": count,
                        "mean_a": mean,
                        "mean_b": mean,
                        "median_a": median,
                        "median_b": median,
                        "standard_deviation_a": stdev,
                        "standard_deviation_b": stdev,
                        "cohens_d": 0,
                        "independent_t": 0,
                        "observation_count": 2 * count
                    },
                ],
            },
            {
                "name": "comparative_hormone_dysmenorrhea_statistics",
                "rows": [
                    {
                        "hormone_name": "test_hormone1",
                        "dysmenorrhea_present_a": True,
                        "dysmenorrhea_present_b": False,
                        "measured_values_a": values,
                        "measured_values_b": values,
                        "observation_count_a": count,
                        "observation_count_b": count,
                        "mean_a": mean,
                        "mean_b": mean,
                        "median_a": median,
                        "median_b": median,
                        "standard_deviation_a": stdev,
                        "standard_deviation_b": stdev,
                        "cohens_d": 0,
                        "independent_t": 0,
                        "observation_count": 2 * count
                    },
                ],
            },
            {
                "name": "comparative_hormone_dysmenorrhea_performance_statistics",
                "rows": [
                    {
                        "hormone_name": "test_hormone1",
                        "performance_type": "OFF SEASON",
                        "dysmenorrhea_present_a": True,
                        "dysmenorrhea_present_b": False,
                        "measured_values_a": values,
                        "measured_values_b": values,
                        "observation_count_a": count,
                        "observation_count_b": count,
                        "mean_a": mean,
                        "mean_b": mean,
                        "median_a": median,
                        "median_b": median,
                        "standard_deviation_a": stdev,
                        "standard_deviation_b": stdev,
                        "cohens_d": 0,
                        "independent_t": 0,
                        "observation_count": 2 * count
                    },
                    {
                        "hormone_name": "test_hormone1",
                        "dysmenorrhea_present": True,
                        "performance_type_a": "OFF SEASON",
                        "performance_type_b": "HIGH INTENSITY",
                        "measured_values_a": values,
                        "measured_values_b": values,
                        "observation_count_a": count,
                        "observation_count_b": count,
                        "mean_a": mean,
                        "mean_b": mean,
                        "median_a": median,
                        "median_b": median,
                        "standard_deviation_a": stdev,
                        "standard_deviation_b": stdev,
                        "cohens_d": 0,
                        "independent_t": 0,
                        "observation_count": 2 * count
                    }
                ],
            }
        ]
        self.assertEqual(intended_tables,
                         self.engine.build_tables(statistics))
        

    def test_build_data(self):
        payload: HormoneAnalysisInput
        statistics: dict[str, list[dict]]
        ...

    def test_build_conclusions(self):
        statistics: dict[str, list[dict]]
        ...

    # HELPERS
    def create_observation() -> HormoneObservation:
        STARTING_DATE = datetime(206, 3, 1)
        day_count = randrange(0, 31, 1)
        random_days = timedelta(days=day_count)
        date = STARTING_DATE + random_days

        hormone_suffix = randrange(0, 3, 1)
        hormone = f"test_hormone{hormone_suffix}"
        value = hormone_suffix

        symptoms = ["DYSMENORRHEA"]
        choose = randrange(0, 2, 1)
        if choose:
            symptom = None
        else:
            symptom = symptoms[0]

        performance_types = ["OFF SEASON", "HIGH INTENSITY"]
        choose = randrange(0, 2, 1)
        performance_type = performance_types[choose]

        return HormoneObservation(athlete_id=uuid4().hex,
                                  observed_on=date,
                                  hormone_name=hormone,
                                  measured_value=value,
                                  symptom_name=symptom,
                                  performance_type=performance_type)
    
    def create_hormone_group_obersations(self) -> dict[GroupKey, list[HormoneObservation]]:
        observations = [TestDescriptiveHormoneAnalysis.create_observation() for i in range(10)]
        group = self.grouper.group_hormone_observations(observations)
        return group
    
    def create_hormone_dysmenorrhea_group_obersations(self) -> dict[GroupKey, list[HormoneObservation]]:
        observations = [TestDescriptiveHormoneAnalysis.create_observation() for i in range(10)]
        group = self.grouper.group_hormone_dysmenorrhea_observations(observations)
        return group
    
    def create_hormone_performance_group_obersations(self) -> dict[GroupKey, list[HormoneObservation]]:
        observations = [TestDescriptiveHormoneAnalysis.create_observation() for i in range(10)]
        group = self.grouper.group_hormone_performance_observations(observations)
        return group
    
    def create_hormone_dysmenorrhea_performance_group_obersations(self) -> dict[GroupKey, list[HormoneObservation]]:
        observations = [TestDescriptiveHormoneAnalysis.create_observation() for i in range(10)]
        group = self.grouper.group_hormone_dysmenorrhea_performance_observations(observations)
        return group

