from collections import defaultdict

from rolling.analysis_engine.contracts import HormoneObservation
from rolling.analysis_engine.group_keys import (HormoneDysmenorrheaPerformanceGroupKey,
                                                HormonePerformanceGroupKey,
                                                HormoneDysmenorrheaGroupKey,
                                                HormoneGroupKey)


class GroupingEngine:
    """
    The GroupingEngine class provides methods to filter and group hormone observations based on various criteria such as hormone name, symptom name, performance type, and observation date. It includes methods to build group keys for different grouping strategies and to assign observations to specific groups based on their attributes.

    It functions as a utility class for organizing hormone observations into meaningful categories
    for analysis, allowing for flexible filtering and grouping based on the needs of the analysis 
    being performed.

    Methods
    -------
    filter_observations(observations, hormone_names=None, symptom_names=None, performance_types=None, date_from=None, date_to=None)
        Filters the given observations based on the provided criteria.
    assign_dysmenorrhea_group(observation)
        Determines if the observation is associated with dysmenorrhea based on the symptom name.
    assign_performance_type_group(observation)
        Determines the performance type group for the observation based on the performance type.
    build_hormone_dysmenorrhea_performance_group_key(observation)
        Builds a group key for the observation based on a hormone name, dysmenorrhea presence, and performance type.
    build_hormone_dysmenorrhea_group_key(observation)
        Buiilds a group key for the observation based on a hormone name and dysmenorrhea presence.
    build_hormone_performance_group_key(observation)
        Builds a group key for the observation based on a hormone name and performance type.
    build_hormone_group_key(observation)
        Builds a group key for the observation based on a hormone name.
    group_hormone_dysmenorrhea_performance_observations(observations)
        Groups observations into a dictionary indexed by hormone name, dysmenorrhea presence, and performance type.
    group_hormone_dysmenorrhea_observations(observations)
        Groups observations into a dictionary indexed by hormone name and dysmenorrhea presence.
    group_hormone_performance_observations(observations)
        Groups observations into a dictionary indexed by hormone name and performance type.
    group_hormone_observations(observations)
        Groups observations into a dictionary indexed by hormone name.
    """
    def filter_observations(self, observations: list[HormoneObservation], *,
                            hormone_names=None, symptom_names=None,
                            performance_types=None, date_from=None, date_to=None,
                            ) -> list[HormoneObservation]:
        """
        Filters the given observations based on the provided criteria.
        
        Args:
            observations (list[HormoneObservation]): The list of hormone observations to filter.
            hormone_names (list[str], optional): A list of hormone names to include. If None, all hormone names are included.
            symptom_names (list[str], optional): A list of symptom names to include. If None, all symptom names are included.
            performance_types (list[str], optional): A list of performance types to include. If None, all performance types are included.
            date_from (datetime, optional): The start date to include observations from. If None, there is no lower date limit.
            date_to (datetime, optional): The end date to include observations up to. If None, there is no upper date limit.
        
        Returns:
            list[HormoneObservation]: A list of hormone observations that match the provided filtering criteria.
        """
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
        """
        Determines if the observation is associated with dysmenorrhea based on the symptom name.
        
        Args:
            observation (HormoneObservation): The hormone observation to evaluate.

        Returns:
            bool: True if the observation is associated with dysmenorrhea, False otherwise.
        """
        if observation.symptom_name is None:
            return False
        return observation.symptom_name.strip().upper() == "DYSMENORRHEA"

    def assign_performance_type_group(self, observation: HormoneObservation) -> str:
        """
        Determines the performance type group for the observation based on the performance type.

        Args:
            observation (HormoneObservation): The hormone observation to evaluate.

        Returns:
            str: The performance type group for the observation.
        """
        if observation.performance_type is None:
            return "UNSPECIFIED"
        if observation.performance_type.strip().upper() != "OFF SEASON":
            return "HIGH INTENSITY"
        return observation.performance_type.strip().upper()
    
    # KEY BUILDERS
    def build_hormone_dysmenorrhea_performance_group_key(self,
                                                         observation: HormoneObservation
                                                         ) -> HormoneDysmenorrheaPerformanceGroupKey:
        """
        Builds a group key for the observation based on a hormone name, dysmenorrhea presence, and performance type.

        Args:
            observation (HormoneObservation): The hormone observation to build the group key for.

        Returns:
            HormoneDysmenorrheaPerformanceGroupKey: The group key for the observation.
        """
        return HormoneDysmenorrheaPerformanceGroupKey(hormone_name=observation.hormone_name,
                                                      dysmenorrhea_present=self.assign_dysmenorrhea_group(observation),
                                                      performance_type=self.assign_performance_type_group(observation))
    
    def build_hormone_dysmenorrhea_group_key(self,
                                             observation: HormoneObservation
                                             ) -> HormoneDysmenorrheaGroupKey:
        """
        Buiilds a group key for the observation based on a hormone name and dysmenorrhea presence.

        Args:
            observation (HormoneObservation): The hormone observation to build the group key for.

        Returns:
            HormoneDysmenorrheaGroupKey: The group key for the observation.
        """
        return HormoneDysmenorrheaGroupKey(hormone_name=observation.hormone_name,
                                           dysmenorrhea_present=self.assign_dysmenorrhea_group(observation))
    
    def build_hormone_performance_group_key(self,
                                            observation: HormoneObservation
                                            ) -> HormonePerformanceGroupKey:
        """
        Builds a group key for the observation based on a hormone name and performance type.

        Args:
            observation (HormoneObservation): The hormone observation to build the group key for.

        Returns:
            HormonePerformanceGroupKey: The group key for the observation.
        """
        return HormonePerformanceGroupKey(hormone_name=observation.hormone_name,
                                          performance_type=self.assign_performance_type_group(observation))
    
    def build_hormone_group_key(self,
                                observation: HormoneObservation
                                ) -> HormoneGroupKey:
        """
        Builds a group key for the observation based on a hormone name.

        Args:
            observation (HormoneObservation): The hormone observation to build the group key for.

        Returns:
            HormoneGroupKey: The group key for the observation.
        """
        return HormoneGroupKey(hormone_name=observation.hormone_name)
    
    # GROUP BUILDERS
    def group_hormone_dysmenorrhea_performance_observations(self,
                                                            observations: list[HormoneObservation],
                                                            ) -> dict[HormoneDysmenorrheaPerformanceGroupKey, list]:
        """
        Groups observations into a dictionary indexed by hormone name, dysmenorrhea presence, and performance type.

        Args:
            observation (HormoneObservation): The hormone observation to build the group key for.

        Returns:
            dict[HormoneGroupKey, list]: A dictionary indexed by the group keys with values being matching observation.
        """        
        grouped = defaultdict(list)
        
        for observation in observations:
            key = self.build_hormone_dysmenorrhea_performance_group_key(observation)
            grouped[key].append(observation)

        return dict(grouped)

    def group_hormone_dysmenorrhea_observations(self,
                                                observations: list[HormoneObservation],
                                                ) -> dict[HormoneDysmenorrheaGroupKey, list]:
        """
        Groups observations into a dictionary indexed by hormone name and dysmenorrhea presence.

        Args:
            observation (HormoneObservation): The hormone observation to build the group key for.

        Returns:
            dict[HormoneDysmenorrheaGroupKey, list]: A dictionary indexed by the group keys with values being matching observation.
        """
        grouped = defaultdict(list)
        
        for observation in observations:
            key = self.build_hormone_dysmenorrhea_group_key(observation)
            grouped[key].append(observation)

        return dict(grouped)

    def group_hormone_performance_observations(self,
                                               observations: list[HormoneObservation],
                                               ) -> dict[HormonePerformanceGroupKey, list]:
        """
        Groups observations into a dictionary indexed by hormone name and performance type.

        Args:
            observation (HormoneObservation): The hormone observation to build the group key for.

        Returns:
            dict[HormonePerformanceGroupKey, list]: A dictionary indexed by the group keys with values being matching observation.
        """        
        grouped = defaultdict(list)
        
        for observation in observations:
            key = self.build_hormone_performance_group_key(observation)
            grouped[key].append(observation)

        return dict(grouped)

    def group_hormone_observations(self,
                                   observations: list[HormoneObservation],
                                   ) -> dict[HormoneGroupKey, list]:
        """
        Groups observations into a dictionary indexed by hormone name.
        

        Args:
            observation (HormoneObservation): The hormone observation to build the group key for.

        Returns:
            dict[HormoneGroupKey, list]: A dictionary indexed by the group keys with values being matching observation.
        """        
        grouped = defaultdict(list)
        
        for observation in observations:
            key = self.build_hormone_group_key(observation)
            grouped[key].append(observation)

        return dict(grouped)
