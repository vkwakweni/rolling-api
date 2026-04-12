# builds approved AI input payloads.
from typing import Any

from app.models.analyses import AnalysisResultResponse, AnalysisReportResponse
from app.models.ai import AIAnalysisReportInput


class AIInputBuilder:
    ALLOWED_TABLE_NAMES = {"hormone_statistics",
                           "hormone_performance_statistics",
                           "hormone_dysmenorrhea_statistics",
                           "hormone_dysmenorrhea_performance_statistics",
                           "comparative_hormone_performance_statistics",
                           "comparative_hormone_dysmenorrhea_statistics",
                           "comparative_hormone_dysmenorrhea_performance_statistics"}
    
    ALLOWED_KEYS = {"hormone_name",
                    "dysmenorrhea_present",
                    "performance_type",
                    "dysmenorrhea_present_a",
                    "dysmenorrhea_present_b",
                    "performance_type_a",
                    "performance_type_b",
                    "observation_count",
                    "obervation_count_a",
                    "observation_count_b",
                    "mean",
                    "mean_a",
                    "mean_b",
                    "median",
                    "median_a",
                    "median_b",
                    "standard_deviation",
                    "standard_deviation_a",
                    "standard_deviation_b",
                    "cohens_d",
                    "independent_t"}
    
    def build_allowed_ai_input(self,
                               analysis_results: list[AnalysisResultResponse],
                               analysis_report: AnalysisReportResponse,
                               ) -> AIAnalysisReportInput:
        combined_summaries = []
        combined_tables = []

        for analysis_result in analysis_results:
            result_payload = analysis_result.result_payload

            summary = result_payload.get("summary", {})
            tables = result_payload.get("tables", [])
            approved_tables = self.extract_approved_tables(tables=tables,
                                                           analysis_result=analysis_result)
            redacted_tables = self.get_whitelisted_keys_from_tables(approved_tables)

            combined_summaries.append({"analysis_result_id": str(analysis_result.analysis_result_id),
                                       "analysis_run_id": str(analysis_result.analysis_run_id),
                                       "result_type": analysis_result.result_type,
                                       "summary": summary})
            
            combined_tables = [*combined_tables, *redacted_tables]
            
        metadata = {"analysis_run_id": str(analysis_report.analysis_run_id),
                    "source_result_ids": [str(result.analysis_result_id) for result in analysis_results],
                    "result_types": [result.result_type for result in analysis_results],
                    "table_names": [table["name"] for table in combined_tables]}
    
        return AIAnalysisReportInput(summary={"results": combined_summaries},
                             tables=combined_tables,
                             report_text=analysis_report.report_text,
                             summary_text=analysis_report.summary_text,
                             metadata=metadata)

    # HELPERS
    def extract_approved_tables(self,
                                tables: list[dict[str, Any]],
                                analysis_result: AnalysisResultResponse
                                ) -> list[dict[str, Any]]:
        approved_tables = []
        for table in tables:
            table_name = table.get("name")
            table_rows = table.get("rows", [])

            if table_name not in self.ALLOWED_TABLE_NAMES:
                continue

            approved_tables.append({"name": table_name,
                                    "rows": table_rows,
                                    "source_analysis_result_id": str(analysis_result.analysis_result_id),
                                    "source_result_type": analysis_result.result_type})
            
        return approved_tables
    
    def get_whitelisted_keys_from_tables(self, tables: list[dict[str, Any]]) -> list[dict[str, Any]]:
        redacted_tables = []
        for table in tables:
            table_name = table.get("name")
            table_rows = table.get("rows", [])

            redacted_rows = []
            for row in table_rows:
                row = dict()
                for key, value in row.items():
                    if key in self.ALLOWED_KEYS:
                        row[key] = value
                redacted_rows.append(row)

            redacted_tables.append({"name": table_name,
                                    "rows": redacted_rows})
        return redacted_tables
