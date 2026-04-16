import unittest
from uuid import uuid4
from datetime import datetime

from rolling.analysis_engine.utils.grouping_engine import GroupingEngine
from rolling.analysis_engine.contracts import HormoneObservation
from rolling.analysis_engine.group_keys import (HormoneGroupKey,
                                        HormonePerformanceGroupKey,
                                        HormoneDysmenorrheaGroupKey,
                                        HormoneDysmenorrheaPerformanceGroupKey)


class TestGroupingEngine(unittest.TestCase):
    grouper = GroupingEngine()
    
    def test_assign_dysmenorrhea_group(self):
        dys_observation = HormoneObservation(athlete_id = uuid4().hex,
                                             observed_on = datetime(2026, 3, 5),
                                             hormone_name = "test_hormone",
                                             measured_value = 1,
                                             symptom_name = "DYSMENORRHEA")
        nondys_observation = HormoneObservation(athlete_id = uuid4().hex,
                                                observed_on = datetime(2026, 3, 5),
                                                hormone_name = "test_hormone",
                                                measured_value = 1,
                                                symptom_name = "NAUSEA")
        no_symptom_observation = HormoneObservation(athlete_id = uuid4().hex,
                                                    observed_on = datetime(2026, 3, 5),
                                                    hormone_name = "test_hormone",
                                                    measured_value = 1)
        
        self.assertTrue(self.grouper.assign_dysmenorrhea_group(dys_observation))
        self.assertFalse(self.grouper.assign_dysmenorrhea_group(nondys_observation))
        self.assertFalse(self.grouper.assign_dysmenorrhea_group(no_symptom_observation))
        

    def test_assign_performance_type_group(self):
        off_observation = HormoneObservation(athlete_id = uuid4().hex,
                                             observed_on = datetime(2026, 3, 5),
                                             hormone_name = "test_hormone",
                                             measured_value = 1,
                                             performance_type="OFF SEASON")
        other_observation = HormoneObservation(athlete_id = uuid4().hex,
                                               observed_on = datetime(2026, 3, 5),
                                               hormone_name = "test_hormone",
                                               measured_value = 1,
                                               performance_type="RUN")
        no_performance_observation = HormoneObservation(athlete_id = uuid4().hex,
                                                        observed_on = datetime(2026, 3, 5),
                                                        hormone_name = "test_hormone",
                                                        measured_value = 1)
        
        self.assertEqual(self.grouper.assign_performance_type_group(off_observation), "OFF SEASON")
        self.assertEqual(self.grouper.assign_performance_type_group(other_observation), "HIGH INTENSITY")
        self.assertEqual(self.grouper.assign_performance_type_group(no_performance_observation), "UNSPECIFIED")
        
    # KEY BUILDER TESTS
    def test_build_hormone_dysmenorrhea_performance_group_key(self):
        correct_observation = HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA",
                                  performance_type="OFF SEASON")
        correct_key = HormoneDysmenorrheaPerformanceGroupKey(hormone_name="test_hormone",
                                                             dysmenorrhea_present=True,
                                                             performance_type="OFF SEASON")
        

        self.assertEqual(correct_key,
                         self.grouper.build_hormone_dysmenorrhea_performance_group_key(correct_observation))
        
        invalid_performance_observation = HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA")
        invalid_performance_key = HormoneDysmenorrheaPerformanceGroupKey(hormone_name="test_hormone",
                                                             dysmenorrhea_present=True,
                                                             performance_type="UNSPECIFIED")
        
        self.assertEqual(invalid_performance_key,
                         self.grouper.build_hormone_dysmenorrhea_performance_group_key(invalid_performance_observation))
        
        invalid_dysmenorrhea_observation = HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone",
                                  measured_value = 1,
                                  performance_type="OFF SEASON")
        invalid_dysmenorrhea_key = HormoneDysmenorrheaPerformanceGroupKey(hormone_name="test_hormone",
                                                             dysmenorrhea_present=False,
                                                             performance_type="OFF SEASON")
        
        self.assertEqual(invalid_dysmenorrhea_key,
                         self.grouper.build_hormone_dysmenorrhea_performance_group_key(invalid_dysmenorrhea_observation))

    def test_build_hormone_dysmenorrhea_group_key(self):
        correct_observation = HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA")
        correct_key = HormoneDysmenorrheaGroupKey(hormone_name="test_hormone",
                                                             dysmenorrhea_present=True)
        
        invalid_observation = HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone",
                                  measured_value = 1)
        invalid_key = HormoneDysmenorrheaGroupKey(hormone_name="test_hormone",
                                                             dysmenorrhea_present=False)
        
        self.assertEqual(correct_key,
                         self.grouper.build_hormone_dysmenorrhea_performance_group_key(correct_observation))
        self.assertEqual(invalid_key,
                         self.grouper.build_hormone_dysmenorrhea_performance_group_key(invalid_observation))

    def test_build_hormone_performance_group_key(self):
        correct_observation = HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone",
                                  measured_value = 1,
                                  performance_type="OFF SEASON")
        correct_key = HormonePerformanceGroupKey(hormone_name="test_hormone",
                                                             performance_type="OFF SEASON")
        

        self.assertEqual(correct_key,
                         self.grouper.build_hormone_dysmenorrhea_performance_group_key(correct_observation))
        
        invalid_performance_observation = HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA")
        invalid_performance_key = HormonePerformanceGroupKey(hormone_name="test_hormone",
                                                             performance_type="UNSPECIFIED")
        
        self.assertEqual(invalid_performance_key,
                         self.grouper.build_hormone_dysmenorrhea_performance_group_key(invalid_performance_observation))

    def test_hormone_group_key(self):
        correct_observation = HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone",
                                  measured_value = 1,
                                  performance_type="OFF SEASON")
        correct_key = HormoneGroupKey(hormone_name="test_hormone")
        

        self.assertEqual(correct_key,
                         self.grouper.build_hormone_dysmenorrhea_performance_group_key(correct_observation))
        
        with self.assertRaises(TypeError) as e: # TODO this should be for testing group_keys
            HormoneGroupKey().hormone_name
        

    # GROUP BUILDER TESTS
    def test_group_hormone_dysmenorrhea_performance(self):
        correct_observation = [HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone1",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA",
                                  performance_type="OFF SEASON"),
                                HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone2",
                                  measured_value = 1,
                                  performance_type="OFF SEASON"),
                                HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone1",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA",
                                  performance_type="OFF SEASON"),]

        grouped = dict()
        grouped[HormoneDysmenorrheaPerformanceGroupKey(hormone_name="test_hormone1",
                                                       dysmenorrhea_present=True,
                                                       performance_type="OFF SEASON")] = [correct_observation[0],
                                                                                          correct_observation[2]]
        grouped[HormoneDysmenorrheaPerformanceGroupKey(hormone_name="test_hormone2",
                                                       dysmenorrhea_present=False,
                                                       performance_type="OFF SEASON")] = [correct_observation[1]]
        
        self.assertEqual(grouped,
                         self.grouper.group_hormone_dysmenorrhea_performance_observations(correct_observation))

    def test_group_hormone_dysmenorrhea_observation(self):
        correct_observation = [HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone1",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA"),
                                HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone2",
                                  measured_value = 1,
                                  performance_type="OFF SEASON"),
                                HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone1",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA",
                                  performance_type="OFF SEASON"),]
        
        grouped = dict()
        grouped[HormoneDysmenorrheaGroupKey(hormone_name="test_hormone1",
                                            dysmenorrhea_present=True)] = [correct_observation[0], correct_observation[2]]
        grouped[HormoneDysmenorrheaGroupKey(hormone_name="test_hormone2",
                                            dysmenorrhea_present=False)] = [correct_observation[1]]
        
        self.assertEqual(grouped,
                         self.grouper.group_hormone_dysmenorrhea_observations(correct_observation))

    def test_group_hormone_performance_observation(self):
        correct_observation = [HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone1",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA",
                                  performance_type="OFF SEASON"),
                                HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone2",
                                  measured_value = 1,
                                  performance_type="OFF SEASON"),
                                HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone1",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA",
                                  performance_type="RACE"),]

        grouped = dict()
        grouped[HormonePerformanceGroupKey(hormone_name="test_hormone1",
                                           performance_type="OFF SEASON")] = [correct_observation[0]]
        grouped[HormonePerformanceGroupKey(hormone_name="test_hormone2",
                                           performance_type="OFF SEASON")] = [correct_observation[1]]
        grouped[HormonePerformanceGroupKey(hormone_name="test_hormone1",
                                           performance_type="HIGH INTENSITY")] = [correct_observation[2]]
        
        self.assertEqual(grouped,
                         self.grouper.group_hormone_performance_observations(correct_observation))
        
        missing_performance_observation = [HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone1",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA",
                                  performance_type="OFF SEASON"),
                                HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone2",
                                  measured_value = 1),
                                HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone1",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA",
                                  performance_type="RACE"),]
        
        grouped = dict()
        grouped[HormonePerformanceGroupKey(hormone_name="test_hormone1",
                                           performance_type="OFF SEASON")] = [missing_performance_observation[0]]
        grouped[HormonePerformanceGroupKey(hormone_name="test_hormone2",
                                         performance_type="UNSPECIFIED")] = [missing_performance_observation[1]]
        grouped[HormonePerformanceGroupKey(hormone_name="test_hormone1",
                                           performance_type="HIGH INTENSITY")] = [missing_performance_observation[2]]
        
        self.assertEqual(grouped,
                         self.grouper.group_hormone_performance_observations(missing_performance_observation))
    
    def test_group_hormone_observations(self):
        correct_observation = [HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone1",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA",
                                  performance_type="OFF SEASON"),
                                HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone2",
                                  measured_value = 1,
                                  performance_type="OFF SEASON"),
                                HormoneObservation(athlete_id = uuid4().hex,
                                  observed_on = datetime(2026, 3, 5),
                                  hormone_name = "test_hormone1",
                                  measured_value = 1,
                                  symptom_name = "DYSMENORRHEA",
                                  performance_type="RACE"),]
        
        grouped = dict()
        grouped[HormoneGroupKey(hormone_name="test_hormone1")] = [correct_observation[0], correct_observation[2]]
        grouped[HormoneGroupKey(hormone_name="test_hormone2")] = [correct_observation[1]]

        self.assertEqual(grouped,
                         self.grouper.group_hormone_observations(correct_observation))
