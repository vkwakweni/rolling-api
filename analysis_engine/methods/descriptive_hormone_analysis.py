from analysis_engine.contracts import HormoneAnalysisInput, HormoneAnalysisResult, HormoneObservation
from analysis_engine.exceptions import AnalysisInputError, AnalysisDataError
from analysis_engine.group_keys import GroupKey
from analysis_engine.utils.statistics_calculator import StatisticsCalculator
from analysis_engine.utils.grouping_engine import GroupingEngine
from analysis_engine.utils.conclusion_mapper import ConclusionMapper

from datetime import datetime, timezone


class DescriptiveHormoneAnalysis:
    def __init__(self):
        self.calculator = StatisticsCalculator()
        self.grouper = GroupingEngine()
        self.conclusion_mapper = ConclusionMapper()

    def run(self, payload: HormoneAnalysisInput) -> HormoneAnalysisResult:
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
        
        # Check that the statistics were actually computed
        if not hormone_dysmenorrhea_performance_statistics:
            raise AnalysisDataError("No descriptive group statistics could be computed.")
        
        statistics = {"hormone_statistics": hormone_statistics,
                      "hormone_performance_statistics": hormone_performance_statistics,
                      "hormone_dysmenorrhea_statistics": hormone_dysmenorrhea_statistics,
                      "hormone_dysmenorrhea_performance_statistics": hormone_dysmenorrhea_performance_statistics}
        
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

    def validate_input(self, payload: HormoneAnalysisInput):
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
    
    # HELPER METHODS FOR BUILDING RESULT COMPONENTS
    def build_summary(self, statistics: dict[str, list[dict]]):
        return {
        "hormone_row_count": len(statistics["hormone_statistics"]),
        "hormone_performance_row_count": len(statistics["hormone_performance_statistics"]),
        "hormone_dysmenorrhea_row_count": len(statistics["hormone_dysmenorrhea_statistics"]),
        "hormone_dysmenorrhea_performance_row_count": len(
            statistics["hormone_dysmenorrhea_performance_statistics"]
        ),
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
            dys_label = "dysmenorrhea present" if row["dysmenorrhea_present"] else "dysmenorrhea absent"
            conclusions.append(
                f"[Hormone + Dysmenorrhea] {row['hormone_name']} with {dys_label}: "
                f"n={row['observation_count']}, mean={row['mean']}, median={row['median']}."
            )

        for row in statistics["hormone_dysmenorrhea_performance_statistics"]:
            dys_label = "dysmenorrhea present" if row["dysmenorrhea_present"] else "dysmenorrhea absent"
            conclusions.append(
                f"[Hormone + Dysmenorrhea + Performance] "
                f"{row['hormone_name']} in '{row['performance_type']}' with {dys_label}: "
                f"n={row['observation_count']}, mean={row['mean']}, median={row['median']}."
            )

        return conclusions

