from typing import Optional, Any

class ConclusionMapper:
    """
    This class maps the conclusion based on statistical values.

    It functions as an interface between the analysis results and the human-readable conclusions.

    Methods
    -------
    - map_mean_differences: Returns a conclusion for the difference between group A's mean and group B's mean.
    - map_effect_size_conclusion: Returns a conclusion for the effect size value.
    - map_t_statistic_conclusion: Returns a conclusion for the t-statistic from Welch's Test.
    - map_sample_size_conclusion: Returns a possible warning based on the sample size.
    - build_group_conclusion: Builds conclusions based on a grouped statistics.
    - build_comparison_conclusion: Builds conclusions based on a grouped statistics.
    - build_overall_conclusions: Builds summarising conclusion from an analysis result.
    - build_overall_detailed_conclusions: Builds a summarising conclusion from an analysis result with comparative groups.
    
    """
    def map_mean_differences(self, group_a_mean, group_b_mean) -> str:
        """
        Returns a conclusion for the difference between group A's mean and group B's mean.
        
        Args:
            group_a_mean (float | int): The mean value for group A.
            group_b_mean (float | int): The mean value for group B.

        Returns:
            str: A conclusion string describing the relationship between group A's mean and group B's mean.
        """
        if group_a_mean > group_b_mean:
            return f"Group A's mean is greater than Group B's: {group_a_mean} > {group_b_mean}"
        if group_a_mean < group_b_mean:
            return f"Group A's mean is less than Group B's: {group_a_mean} < {group_b_mean}"    
        return f"Group A's mean is equivalent to Group B's: {group_a_mean} = {group_b_mean}"


    def map_effect_size_conclusion(self, effect_size: Optional[float | int]) -> str:
        """
        Returns a conclusion for the effect size value.

        Args:
            effect_size (float | int | None): The effect size value.

        Returns:
            str: A conclusion string describing the effect size.
        """
        if effect_size is None:
            return "effect size could not be computed"
        effect_size = abs(effect_size) # TODO later handle negative number interpretations
        if effect_size >= 0.8:
            return "a large effect"
        if effect_size >= 0.5:
            return "a medium effect"
        if effect_size >= 0.2:
            return "a small effect"
        return "no meaningful effect"

    def map_t_statistic_conclusion(self, t_statistic: Optional[float | int]) -> str:
        """
        Returns a conclusion for the t-statistic from Welch's Test.

        Args:
            t_statistic (float | int | None): The t-statistic from Welch's Test.

        Returns:
            str: A conclusion string describing the t-statistic.
        """
        # TODO implement independent t-test
        return "t-statistic could not be computed"

    def map_sample_size_conclusion(self, sample_size: int) -> str:
        """
        Returns a possible warning based on the sample size.

        Args:
            sample_size (int): The number of observations in the sample.

        Returns:
            str: A warning string based on the sample size.
        """
        if sample_size < 6:
            return "This is a very small sample; interpret cautiously."
        if sample_size <= 20:
            return "This is small, but sufficient sample; interpret cautiously."
        return "This is a sufficient sample."

    def build_group_conclusion(self, stats_summary: dict[str, Any]) -> str:
        """
        DEPRECATED: Builds conclusions based on a grouped statistics.

        It takes the group labels from stats_summary and builds a sentence to summarise the statistical values.
        """
        descriptive_notes = []
        sample_size = stats_summary.get("observation_count", 0)
        descriptive_notes.append(self.map_sample_size_conclusion(sample_size))

        hormone_name = stats_summary.get("hormone_name", "UNKNOWN_HORMONE")
        dysmenorrhea_present = stats_summary.get("dysmenorrhea_present")
        performance_type = stats_summary.get("performance_type", "UNSPECIFIED")
        mean_value = stats_summary.get("mean")

        dysmenorrhea_label = ("with dysmenorrhea present"
                              if dysmenorrhea_present
                              else "without dysmenorrhea present")
        
        if mean_value is not None:
            descriptive_notes.append(f"{hormone_name} has an average value of {mean_value} "
                                     f"in the '{performance_type}' group {dysmenorrhea_label}.")
            
        return " ".join(descriptive_notes)


    def build_comparison_conclusion(self, stats_summary):
        """
        DEPRECATED: Builds conclusions based on a grouped statistics.

        It takes the group labels from stats_summary and builds a sentence to summarise the statistical values.
        """
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
            self.map_effect_size_conclusion(stats_summary.get("hedges_g"))
        )

        if group_a_mean is not None and group_b_mean is not None:
            difference_note = self.map_mean_differences(group_a_mean, group_b_mean)
            if difference_note is not None:
                descriptive_notes.append(difference_note)

        return " ".join(descriptive_notes)

    def build_overall_conclusions(self, analysis_rows):
        """DEPRECATED: Builds summarising conclusion from an analysis result."""
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

    def build_overall_detailed_conclusions(self, analysis_rows):
        """DEPRECATED: Builds a summarising conclusion from an analysis result with comparative groups."""
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