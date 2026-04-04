# builds approved AI input payloads.
from typing import Any

from app.models.analyses import AnalysisResultResponse, AnalysisReportResponse
from app.models.ai import AIReportInput


class AIInputBuilder:
    ALLOWED_TABLE_NAMES = {"hormone_statistics",
                           "hormone_performance_statistics",
                           "hormone_dysmenorrhea_statistics",
                           "hormone_dysmenorrhea_performance_statistics"}
    
    def build_allowed_ai_input(self,
                               analysis_results: list[AnalysisResultResponse],
                               analysis_report: AnalysisReportResponse,
                               ) -> AIReportInput:
        """
        Main boundary builder.
        This is for policy enforcement.
        """
        combined_summaries = []
        combined_tables = []

        for analysis_result in analysis_results:
            result_payload = analysis_result.result_payload

            summary = result_payload.get("summary", {})
            tables = result_payload.get("tables", [])
            approved_tables = self.extract_approved_tables(tables=tables,
                                                           analysis_result=analysis_result)
            redacted_tables = self.remove_measured_values_from_tables(approved_tables)

            combined_summaries.append({"analysis_result_id": str(analysis_result.analysis_result_id),
                                       "analysis_run_id": str(analysis_result.analysis_run_id),
                                       "result_type": analysis_result.result_type,
                                       "summary": summary})
            
            combined_tables = [*combined_tables, *redacted_tables]
            
        metadata = {"analysis_run_id": str(analysis_report.analysis_run_id),
                    "source_result_ids": [str(result.analysis_result_id) for result in analysis_results],
                    "result_types": [result.result_type for result in analysis_results],
                    "table_names": [table["name"] for table in combined_tables]}
    
        return AIReportInput(summary={"results": combined_summaries},
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
    
    def remove_measured_values_from_tables(self, tables: list[dict[str, Any]]) -> list[dict[str, Any]]:
        redacted_tables = []
        for table in tables:
            table_name = table.get("name")
            table_rows = table.get("rows", [])

            redacted_rows = []
            for row in table_rows:
                row = row.copy()
                row.pop("measured_values", None)
                redacted_rows.append(row)

            redacted_tables.append({"name": table_name,
                                    "rows": redacted_rows})
        return redacted_tables
