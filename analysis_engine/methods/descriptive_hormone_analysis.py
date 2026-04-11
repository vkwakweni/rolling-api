from datetime import datetime, timezone
from typing import Optional

from analysis_engine.contracts import HormoneAnalysisInput, HormoneAnalysisResult, HormoneObservation
from analysis_engine.exceptions import AnalysisInputError, AnalysisDataError
from analysis_engine.group_keys import (GroupKey,
                                        HormoneDysmenorrheaPerformanceGroupKey, HormoneGroupKey,
                                        HormonePerformanceGroupKey,
                                        HormoneDysmenorrheaGroupKey)
from analysis_engine.utils.statistics_calculator import StatisticsCalculator
from analysis_engine.utils.grouping_engine import GroupingEngine
from analysis_engine.utils.conclusion_mapper import ConclusionMapper


class DescriptiveHormoneAnalysis:
    def __init__(self):
        self.calculator = StatisticsCalculator()
        self.grouper = GroupingEngine()
        self.conclusion_mapper = ConclusionMapper()

    def run(self, payload: Optional[HormoneAnalysisInput]) -> HormoneAnalysisResult:
        self.validate_input(payload)

        filtered = self.grouper.filter_observations(payload.observations,
                                                    hormone_names=payload.include_hormone_names,
                                                    symptom_names=payload.include_symptom_names,
                                                    performance_types=payload.include_performance_types,
                                                    date_from=payload.date_from,
                                                    date_to=payload.date_to)
        
        if not filtered:
            raise AnalysisDataError("No observation remained after filtering.")
        
        # group by hormone
        hormone_group = self.grouper.group_hormone_observations(filtered)

        # group by hormone-performance
        hormone_performance_group = self.grouper.group_hormone_performance_observations(filtered)

        # group by hormone-dysmenorrhea
        hormone_dysmenorrhea_group = self.grouper.group_hormone_dysmenorrhea_observations(filtered)

        # group by hormone-dysmenorrhea-performance
        comparative_group = self.grouper.group_hormone_dysmenorrhea_performance_observations(filtered)

        # get statistics
        hormone_statistics, hormone_performance_statistics, \
            hormone_dysmenorrhea_statistics, hormone_dysmenorrhea_performance_statistics \
                = [self.build_group_statistics(group)
                   for group in [hormone_group,
                                 hormone_performance_group,
                                 hormone_dysmenorrhea_group,
                                 comparative_group]]
        
        # comparative statistics
        comparative_hormone_performance_statistics = self.build_hormone_performance_statistics(hormone_performance_statistics)
        comparative_hormone_dysmenorrhea_statistics = self.build_hormone_dysmenorrhea_statistics(hormone_dysmenorrhea_statistics)
        comparative_hormone_dysmenorrhea_performance_statistics = self.build_hormone_dysmenorrhea_performance_statistics(hormone_dysmenorrhea_performance_statistics)
        
        statistics = {"hormone_statistics": hormone_statistics,
                      "hormone_performance_statistics": hormone_performance_statistics,
                      "hormone_dysmenorrhea_statistics": hormone_dysmenorrhea_statistics,
                      "hormone_dysmenorrhea_performance_statistics": hormone_dysmenorrhea_performance_statistics,
                      "comparative_hormone_performance_statistics": comparative_hormone_performance_statistics,
                      "comparative_hormone_dysmenorrhea_statistics": comparative_hormone_dysmenorrhea_statistics,
                      "comparative_hormone_dysmenorrhea_performance_statistics": comparative_hormone_dysmenorrhea_performance_statistics
        }
        
        # generate summary
        summary = self.build_summary(statistics)

        # generate table
        tables = self.build_tables(statistics)

        # generate metadata
        metadata = self.build_metadata(payload, statistics)

        # generate conclusions
        conclusions = self.build_conclusions(statistics)

        # return HormoneAnalysisResult
        return HormoneAnalysisResult(analysis_kind="descriptive_hormone_analysis",
                                     engine_version="traditional",
                                     generated_at=datetime.now(timezone.utc),
                                     summary=summary,
                                     tables=tables,
                                     metadata=metadata,
                                     conclusions=conclusions)

    def validate_input(self, payload: Optional[HormoneAnalysisInput]):
        if payload is None:
            raise AnalysisInputError("Analysis input payload must not be None.")
        if not payload.observations:
            raise AnalysisInputError("Analysis input must include observations.")
    
    def build_group_statistics(self, grouped_observations: dict[GroupKey, list[HormoneObservation]]) -> list[dict]:
        group_statistics = []

        for group_key, observations in grouped_observations.items():
            values = [obs.measured_value for obs in observations if obs.measured_value is not None]
            if not values:
                continue
            
            labels = group_key.as_dict()
            stats_summary = {**labels,
                             "measured_values": values,
                             "observation_count": len(values),
                             "mean": self.calculator.mean(values),
                             "median": self.calculator.median(values),
                             "standard_deviation": (self.calculator.standard_deviation(values)
                                                    if len(values) > 1
                                                    else None)}
            
            group_statistics.append(stats_summary)

        return group_statistics
    
    def build_hormone_performance_statistics(self, group_statistics: list[dict]) -> list[dict]:
        comparative_hormone_performance_statistics = []
        for stat1 in group_statistics:
            compared = dict()
            for stat2 in group_statistics:
                if stat1["hormone_name"] == stat2["hormone_name"] and stat1["performance_type"] != stat2["performance_type"]:
                    if stat1["performance_type"] == "HIGH INTENSITY" and stat2["performance_type"] == "OFF SEASON":
                        compared["hormone_name"] = stat1["hormone_name"]
                        values_1 = stat1["measured_values"]
                        values_2 = stat2["measured_values"]
                        compared["performance_type_a"] = stat1["performance_type"]
                        compared["performance_type_b"] = stat2["performance_type"]
                        compared["measured_values_a"] = values_1
                        compared["measured_values_b"] = values_2
                        compared["observation_count_a"] = len(values_1)
                        compared["observation_count_b"] = len(values_2)
                        compared["mean_a"] = self.calculator.mean(values_1)
                        compared["mean_b"] = self.calculator.mean(values_2)
                        compared["median_a"] = self.calculator.median(values_1)
                        compared["median_b"] = self.calculator.median(values_2)
                        compared["standard_deviation_a"] = (self.calculator.standard_deviation(values_1)
                                                        if len(values_1) > 1
                                                        else None)
                        compared["standard_deviation_b"] = (self.calculator.standard_deviation(values_2)
                                                        if len(values_2) > 1
                                                        else None)
                        compared["cohens_d"] = self.calculator.cohens_d(values_1, values_2)
                        compared["independent_t"] = self.calculator.welch_test(values_1, values_2)
                        compared["observation_count"] = len(values_1) + len(values_2)
                    if compared not in comparative_hormone_performance_statistics and compared:
                            comparative_hormone_performance_statistics.append(compared)
        return comparative_hormone_performance_statistics

    def build_hormone_dysmenorrhea_statistics(self, group_statistics: list[dict]) -> list[dict]:
        comparative_hormone_dysmenorrhea_statistics = []
        for stat1 in group_statistics:
            compared = dict()
            for stat2 in group_statistics:
                if stat1["hormone_name"] == stat2["hormone_name"] and (stat1["dysmenorrhea_present"] != stat2["dysmenorrhea_present"]):
                    compared["hormone_name"] = stat1["hormone_name"]
                    values_1 = stat1["measured_values"]
                    values_2 = stat2["measured_values"]
                    compared["dysmenorrhea_present_a"] = stat1["dysmenorrhea_present"]
                    compared["dysmenorrhea_present_b"] = stat2["dysmenorrhea_present"]
                    compared["measured_values_a"] = values_1
                    compared["measured_values_b"] = values_2
                    compared["observation_count_a"] = len(values_1)
                    compared["observation_count_b"] = len(values_2)
                    compared["mean_a"] = self.calculator.mean(values_1)
                    compared["mean_b"] = self.calculator.mean(values_2)
                    compared["median_a"] = self.calculator.median(values_1)
                    compared["median_b"] = self.calculator.median(values_2)
                    compared["standard_deviation_a"] = (self.calculator.standard_deviation(values_1)
                                                    if len(values_1) > 1
                                                    else None)
                    compared["standard_deviation_b"] = (self.calculator.standard_deviation(values_2)
                                                    if len(values_2) > 1
                                                    else None)
                    compared["cohens_d"] = self.calculator.cohens_d(values_1, values_2)
                    compared["independent_t"] = self.calculator.welch_test(values_1, values_2)
                    compared["observation_count"] = len(values_1) + len(values_2)
                    if compared not in comparative_hormone_dysmenorrhea_statistics and compared:
                            comparative_hormone_dysmenorrhea_statistics.append(compared)
                    break
        return comparative_hormone_dysmenorrhea_statistics

    def build_hormone_dysmenorrhea_performance_statistics(self, group_statistics: list[dict]) -> list[dict]:
        comparative_hormone_dysmenorrhea_performance_statistics = []
        for stat1 in group_statistics:
            compared = dict()
            for stat2 in group_statistics:
                if (stat1["hormone_name"] == stat2["hormone_name"]) and (stat1["dysmenorrhea_present"] == stat2["dysmenorrhea_present"]) and (stat1["performance_type"] != stat2["performance_type"]):
                    compared["hormone_name"] = stat1["hormone_name"]
                    compared["dysmenorrhea_present"] = stat1["dysmenorrhea_present"]
                    values_1 = stat1["measured_values"]
                    values_2 = stat2["measured_values"]
                    compared["performance_type_a"] = stat1["performance_type"]
                    compared["performance_type_b"] = stat2["performance_type"]
                    compared["measured_values_a"] = values_1
                    compared["measured_values_b"] = values_2
                    compared["observation_count_a"] = len(values_1)
                    compared["observation_count_b"] = len(values_2)
                    compared["mean_a"] = self.calculator.mean(values_1)
                    compared["mean_b"] = self.calculator.mean(values_2)
                    compared["median_a"] = self.calculator.median(values_1)
                    compared["median_b"] = self.calculator.median(values_2)
                    compared["standard_deviation_a"] = (self.calculator.standard_deviation(values_1)
                                                    if len(values_1) > 1
                                                    else None)
                    compared["standard_deviation_b"] = (self.calculator.standard_deviation(values_2)
                                                    if len(values_2) > 1
                                                    else None)
                    compared["cohens_d"] = self.calculator.cohens_d(values_1, values_2)
                    compared["independent_t"] = self.calculator.welch_test(values_1, values_2)
                    compared["observation_count"] = len(values_1) + len(values_2)
                    if compared not in comparative_hormone_dysmenorrhea_performance_statistics and compared:
                            comparative_hormone_dysmenorrhea_performance_statistics.append(compared)
                    continue
                if (stat1["hormone_name"] == stat2["hormone_name"]) and (stat1["dysmenorrhea_present"] != stat2["dysmenorrhea_present"]) and (stat1["performance_type"] == stat2["performance_type"]):
                    compared["hormone_name"] = stat1["hormone_name"]
                    compared["performance_type"] = stat1["performance_type"]
                    values_1 = stat1["measured_values"]
                    values_2 = stat2["measured_values"]
                    compared["dysmenorrhea_present_a"] = stat1["dysmenorrhea_present"]
                    compared["dysmenorrhea_present_b"] = stat2["dysmenorrhea_present"]
                    compared["measured_values_a"] = values_1
                    compared["measured_values_b"] = values_2
                    compared["observation_count_a"] = len(values_1)
                    compared["observation_count_b"] = len(values_2)
                    compared["mean_a"] = self.calculator.mean(values_1)
                    compared["mean_b"] = self.calculator.mean(values_2)
                    compared["median_a"] = self.calculator.median(values_1)
                    compared["median_b"] = self.calculator.median(values_2)
                    compared["standard_deviation_a"] = (self.calculator.standard_deviation(values_1)
                                                    if len(values_1) > 1
                                                    else None)
                    compared["standard_deviation_b"] = (self.calculator.standard_deviation(values_2)
                                                    if len(values_2) > 1
                                                    else None)
                    compared["cohens_d"] = self.calculator.cohens_d(values_1, values_2)
                    compared["independent_t"] = self.calculator.welch_test(values_1, values_2)
                    compared["observation_count"] = len(values_1) + len(values_2)
                    if compared not in comparative_hormone_dysmenorrhea_performance_statistics and compared:
                            comparative_hormone_dysmenorrhea_performance_statistics.append(compared)
                    continue
        return comparative_hormone_dysmenorrhea_performance_statistics
    
    # HELPER METHODS FOR BUILDING RESULT COMPONENTS
    def build_summary(self, statistics: dict[str, list[dict]]):
        return {
        "hormone_row_count": len(statistics["hormone_statistics"]),
        "hormone_performance_row_count": len(statistics["hormone_performance_statistics"]),
        "hormone_dysmenorrhea_row_count": len(statistics["hormone_dysmenorrhea_statistics"]),
        "hormone_dysmenorrhea_performance_row_count": len(
            statistics["hormone_dysmenorrhea_performance_statistics"]
        ),
        "comparative_hormone_performance_row_count": len(statistics["comparative_hormone_performance_statistics"]),
        "comparative_hormone_dysmenorrhea_row_count": len(statistics["comparative_hormone_dysmenorrhea_statistics"]),
        "comparative_hormone_dysmenorrhea_performance_row_count": len(statistics["comparative_hormone_dysmenorrhea_performance_statistics"]),
        "total_grouped_row_count": sum(len(rows) for rows in statistics.values()),
    }

    def build_tables(self, statistics: dict[str, list[dict]]):
        return [{"name": name, "rows": rows} for name, rows in statistics.items()]

    def build_metadata(self, payload: HormoneAnalysisInput, statistics: dict[str, list[dict]]):
        return {
        "project_id": str(payload.project_id),
        "input_observation_count": len(payload.observations),
        "hormone_row_count": len(statistics["hormone_statistics"]),
        "hormone_performance_row_count": len(statistics["hormone_performance_statistics"]),
        "hormone_dysmenorrhea_row_count": len(statistics["hormone_dysmenorrhea_statistics"]),
        "hormone_dysmenorrhea_performance_row_count": len(
            statistics["hormone_dysmenorrhea_performance_statistics"]
        ),
        "comparative_hormone_performance_row_count": len(statistics["comparative_hormone_performance_statistics"]),
        "comparative_hormone_dysmenorrhea_row_count": len(statistics["comparative_hormone_dysmenorrhea_statistics"]),
        "comparative_hormone_dysmenorrhea_performance_row_count": len(statistics["comparative_hormone_dysmenorrhea_performance_statistics"]),
        "included_hormone_names": payload.include_hormone_names,
        "included_performance_types": payload.include_performance_types,
        "included_symptom_names": payload.include_symptom_names,
        "date_from": payload.date_from.isoformat() if payload.date_from else None,
        "date_to": payload.date_to.isoformat() if payload.date_to else None,
    }

    def build_conclusions(self, statistics: dict[str, list[dict]]) -> list[str]:
        conclusions = []

        for row in statistics["hormone_statistics"]:
            conclusions.append(
                f"[Hormone] {row['hormone_name']}: "
                f"n={row['observation_count']}, mean={row['mean']}, median={row['median']}."
            )

        for row in statistics["hormone_performance_statistics"]:
            conclusions.append(
                f"[Hormone + Performance] {row['hormone_name']} in '{row['performance_type']}': "
                f"n={row['observation_count']}, mean={row['mean']}, median={row['median']}."
            )

        for row in statistics["hormone_dysmenorrhea_statistics"]:
            dys_label = "dysmenorrhea present" if str(row["dysmenorrhea_present"]).lower() == "true" else "dysmenorrhea absent"
            conclusions.append(
                f"[Hormone + Dysmenorrhea] {row['hormone_name']} with {dys_label}: "
                f"n={row['observation_count']}, mean={row['mean']}, median={row['median']}."
            )

        for row in statistics["hormone_dysmenorrhea_performance_statistics"]:
            dys_label = "dysmenorrhea present" if str(row["dysmenorrhea_present"]).lower() == "true" else "dysmenorrhea absent"
            conclusions.append(
                f"[Hormone + Dysmenorrhea + Performance] "
                f"{row['hormone_name']} in '{row['performance_type']}' with {dys_label}: "
                f"n={row['observation_count']}, mean={row['mean']}, median={row['median']}."
            )

        for row in statistics["comparative_hormone_performance_statistics"]:
            performance_type_a = row.get("performance_type_a", "unknown")
            performance_type_b = row.get("performance_type_b", "unknown")
            conclusions.append(
                f"Comparative [Hormone + Performance] "
                f"{row['hormone_name']} in ['{performance_type_a}' and '{performance_type_b}']: "
                f"{row['observation_count']}, cohen's d={row['cohens_d']}, independent t={row['independent_t']}."
            )

        for row in statistics["comparative_hormone_dysmenorrhea_statistics"]:
            dys_label_a = "dysmenorrhea present" if str(row["dysmenorrhea_present_a"]).lower() == "true" else "dysmenorrhea absent"
            dys_label_b = "dysmenorrhea present" if str(row["dysmenorrhea_present_b"]).lower() == "true" else "dysmenorrhea absent"
            conclusions.append(
                f"Comparative [Hormone + Dysmenorrhea] {row['hormone_name']} with {dys_label_a} and {dys_label_b}: "
                f"{row['observation_count']}, cohen's d={row['cohens_d']}, independent t={row['independent_t']}."
            )
        
        for row in statistics["comparative_hormone_dysmenorrhea_performance_statistics"]:
            if "performance_type" in row.keys():
                dys_label_a = "dysmenorrhea present" if str(row["dysmenorrhea_present_a"]).lower() == "true" else "dysmenorrhea absent"
                dys_label_b = "dysmenorrhea present" if str(row["dysmenorrhea_present_b"]).lower() == "true" else "dysmenorrhea absent"
                conclusions.append(
                    f"Comparative [Hormone + Dysmenorrhea + Performance] "
                    f"{row['hormone_name']} in '{row['performance_type']}' with {dys_label_a} and {dys_label_b}: "
                    f"{row['observation_count']}, cohen's d={row['cohens_d']}, independent t={row['independent_t']}."
                )
            else:
                dys_label = "dysmenorrhea present" if str(row["dysmenorrhea_present"]).lower() == "true" else "dysmenorrhea absent"
                performance_type_a = row.get("performance_type_a", "unknown")
                performance_type_b = row.get("performance_type_b", "unknown")
                conclusions.append(
                    f"Comparative [Hormone + Dysmenorrhea + Performance] "
                    f"{row['hormone_name']} with {dys_label} for performance types {performance_type_a} and {performance_type_b}: "
                    f"{row['observation_count']}, cohen's d={row['cohens_d']}, independent t={row['independent_t']}."
                )

        return conclusions

