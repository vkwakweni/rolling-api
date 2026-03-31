from typing import Optional

class ConclusionMapper:
    """
    Responsibilities:
    - interpretation rules
    - maps stats into conclusions
    """
    def map_mean_differences(self, group_a_mean, group_b_mean):
        if group_a_mean > group_b_mean:
            return f"Group A's mean is greater than Group B's: {group_a_mean} > {group_b_mean}"
        if group_a_mean < group_b_mean:
            return f"Group A's mean is less than Group B's: {group_a_mean} < {group_b_mean}"    
        return f"Group A's mean is equivalent to Group B's: {group_a_mean} = {group_b_mean}"


    def map_effect_size_conclusion(self, effect_size: Optional[float | int]):
        """
        Hedge's g and Cohen's d are interpreted in the same way
        """
    
        if effect_size is None:
            return "effect size could not be computed."
        effect_size = abs(effect_size) # TODO later handle negative number interpretations
        if effect_size >= 0.8:
            return "a large effect"
        if effect_size >= 0.5:
            return "a medium effect"
        if effect_size >= 0.2:
            return "a small effect"
        return "no meaningful effect"

    def map_difference_conclusion(self, t_value):
        # TODO implement independent t-test
        return None

    def map_sample_size_conclusion(self, sample_size: int):
        if sample_size < 6:
            return "This is a very small sample; interpret cautiously."
        if sample_size <= 20:
            return "This is small, but sufficient sample; interpret cautiously."
        return "This is a sufficient sample."

    def build_group_conclusion(self, stats_summary) -> str:
        """
        Within group descriptive summaries.
        Answers questions like:
        - Sampel size
        - Particular hormone represented in a subgroup
        - Variability and distribution within a group (eventually)
        stats_summary = {
                        "dysmenorrhea_present": False,
                        "training_group": "TRAINING_LOAD",
                        "hormone_name": "ESTRADIOL",
                        "mean_hormone_value": 142.3,
                        "median_hormone_value": 118.7,
                        "standard_deviation": 12,
                        }
        """
        descriptive_notes = []
        sample_size = stats_summary.get("observation_count", 0)
        descriptive_notes.append(self.map_sample_size_conclusion(sample_size))

        hormone_name = stats_summary.get("hormone_name", "Hormone")
        dysmenorrhea_present = stats_summary.get("dysmenorrhea_present")
        performance_type = stats_summary.get("performance_type", "UNSPECIFIED")
        mean_value = stats_summary.get("mean_hormone_value")

        dysmenorrhea_label = ("with dysmenorrhea present"
                              if dysmenorrhea_present
                              else "without dysmenorrhea present")
        
        if mean_value is not None:
            descriptive_notes.append(f"{hormone_name} has an average value of {mean_value} "
                                     f"in the '{performance_type}' group {dysmenorrhea_label}.")
            
        return " ".join(descriptive_notes)


    def build_comparison_conclusion(self, stats_summary):
        descriptive_notes = []

        sample_size_a = stats_summary.get("sample_size_a", 0)
        sample_size_b = stats_summary.get("sample_size_b", 0)
        descriptive_notes.append(
            f"Group A: {self.map_sample_size_conclusion(sample_size_a)}"
        )
        descriptive_notes.append(
            f"Group B: {self.map_sample_size_conclusion(sample_size_b)}"
        )

        group_a_mean = stats_summary.get("group_a_mean")
        group_b_mean = stats_summary.get("group_b_mean")
        

        descriptive_notes.append(
            self.map_effect_size_conclusion(stats_summary.get("effect_size"))
        )

        if group_a_mean is not None and group_b_mean is not None:
            difference_note = self.map_mean_differences(group_a_mean, group_b_mean)
            if difference_note is not None:
                descriptive_notes.append(difference_note)

        return " ".join(descriptive_notes)

    def build_overall_conclusions(self, analysis_rows):
        if not analysis_rows:
            return ["No comparative conclusions could be generated."]

        conclusions = []

        for row in analysis_rows:
            hormone_name = row.get("hormone_name", "Hormone")
            training_group = row.get("training_group", "UNSPECIFIED")
            conclusion = row.get("conclusion")

            if conclusion:
                conclusions.append(
                    f"{hormone_name} in '{training_group}': {conclusion}"
                )

        if not conclusions:
            return ["No comparative conclusions could be generated."]

        return conclusions

    def build_overall_conclusions2(self, analysis_rows):
        if not analysis_rows:
            return ["No comparative conclusions could be generated."]

        conclusions = []

        for row in analysis_rows:
            hormone_name = row.get("hormone_name", "Hormone")
            conclusion = row.get("conclusion")

            if not conclusion:
                continue

            performance_type = row.get("performance_type")
            comparison_scope = row.get("comparison_scope")

            if performance_type is not None:
                conclusions.append(f"{hormone_name} in '{performance_type}': {conclusion}")
            elif comparison_scope == "all_performance_types":
                conclusions.append(f"{hormone_name} across all performance types: {conclusion}")
            else:
                conclusions.append(f"{hormone_name}: {conclusion}")


        if not conclusions:
            return ["No comparative conclusions could be generated."]

        return conclusions