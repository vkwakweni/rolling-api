from collections import defaultdict

from rolling.analysis_engine.contracts import HormoneObservation
from rolling.analysis_engine.group_keys import (HormoneDysmenorrheaPerformanceGroupKey,
                                        HormonePerformanceGroupKey,
                                        HormoneDysmenorrheaGroupKey,
                                        HormoneGroupKey)


class GroupingEngine:
    def filter_observations(self, observations: list[HormoneObservation], *,
                            hormone_names=None, symptom_names=None,
                            performance_types=None, date_from=None, date_to=None,
                            ) -> list[HormoneObservation]:
        filtered = observations

        if hormone_names is not None:
            allowed_hormones = set(hormone_names)
            filtered = [obs for obs in filtered
                       if obs.hormone_name in allowed_hormones]
            
        if symptom_names is not None:
            allowed_symptoms = set(symptom_names)
            filtered = [obs for obs in filtered
                        if obs.symptom_name in allowed_symptoms]
            
        if performance_types is not None:
            performance_types = set(performance_types)
            filtered = [obs for obs in filtered
                        if obs.performance_type in performance_types]
            
        if date_from is not None:
            filtered = [obs for obs in filtered
                        if obs.observed_on >= date_from]
            
        if date_to is not None:
            filtered = [obs for obs in filtered
                        if obs.observed_on <= date_to]
            
        return filtered
            
    def assign_dysmenorrhea_group(self, observation: HormoneObservation) -> bool:
        if observation.symptom_name is None:
            return False
        return observation.symptom_name.strip().upper() == "DYSMENORRHEA"

    def assign_performance_type_group(self, observation: HormoneObservation) -> str:
        if observation.performance_type is None:
            return "UNSPECIFIED"
        if observation.performance_type.strip().upper() != "OFF SEASON":
            return "HIGH INTENSITY"
        return observation.performance_type.strip().upper()
    
    # KEY BUILDERS
    def build_hormone_dysmenorrhea_performance_group_key(self,
                                                         observation: HormoneObservation
                                                         ) -> HormoneDysmenorrheaPerformanceGroupKey:
        return HormoneDysmenorrheaPerformanceGroupKey(hormone_name=observation.hormone_name,
                                                      dysmenorrhea_present=self.assign_dysmenorrhea_group(observation),
                                                      performance_type=self.assign_performance_type_group(observation))
    
    def build_hormone_dysmenorrhea_group_key(self,
                                             observation: HormoneObservation
                                             ) -> HormoneDysmenorrheaPerformanceGroupKey:
        return HormoneDysmenorrheaGroupKey(hormone_name=observation.hormone_name,
                                           dysmenorrhea_present=self.assign_dysmenorrhea_group(observation))
    
    def build_hormone_performance_group_key(self,
                                            observation: HormoneObservation
                                            ) -> HormoneDysmenorrheaPerformanceGroupKey:
        return HormonePerformanceGroupKey(hormone_name=observation.hormone_name,
                                          performance_type=self.assign_performance_type_group(observation))
    
    def build_hormone_group_key(self,
                                observation: HormoneObservation
                                ) -> HormoneDysmenorrheaPerformanceGroupKey:
        return HormoneGroupKey(hormone_name=observation.hormone_name)
    
    # GROUP BUILDERS
    def group_hormone_dysmenorrhea_performance_observations(self,
                                                            observations: list[HormoneObservation],
                                                            ) -> dict[HormoneDysmenorrheaPerformanceGroupKey, list]:
        
        grouped = defaultdict(list)
        
        for observation in observations:
            key = self.build_hormone_dysmenorrhea_performance_group_key(observation)
            grouped[key].append(observation)

        return dict(grouped)

    def group_hormone_dysmenorrhea_observations(self,
                                                observations: list[HormoneObservation],
                                                ) -> dict[HormoneDysmenorrheaPerformanceGroupKey, list]:
        
        grouped = defaultdict(list)
        
        for observation in observations:
            key = self.build_hormone_dysmenorrhea_group_key(observation)
            grouped[key].append(observation)

        return dict(grouped)

    def group_hormone_performance_observations(self,
                                               observations: list[HormoneObservation],
                                               ) -> dict[HormoneDysmenorrheaPerformanceGroupKey, list]:
        
        grouped = defaultdict(list)
        
        for observation in observations:
            key = self.build_hormone_performance_group_key(observation)
            grouped[key].append(observation)

        return dict(grouped)

    def group_hormone_observations(self,
                                   observations: list[HormoneObservation],
                                   ) -> dict[HormoneDysmenorrheaPerformanceGroupKey, list]:
        
        grouped = defaultdict(list)
        
        for observation in observations:
            key = self.build_hormone_group_key(observation)
            grouped[key].append(observation)

        return dict(grouped)
