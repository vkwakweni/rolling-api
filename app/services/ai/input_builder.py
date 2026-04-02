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
                               analysis_result: AnalysisResultResponse,
                               analysis_report: AnalysisReportResponse,
                               ) -> AIReportInput:
        """
        Main boundary builder.
        This is for policy enforcement.
        """
        result_payload = analysis_result.result_payload

        summary = result_payload.get("summary", {})
        tables = result_payload.get("tables", [])
        approved_tables = self.extract_approved_tables(tables)

        metadata = {"analysis_run_id": str(analysis_result.analysis_run_id),
                    "result_type": analysis_result.result_type,
                    "table_names": [table["name"] for table in approved_tables]}
        
        return AIReportInput(summary=summary,
                             tables=approved_tables,
                             report_text=analysis_report.report_text,
                             summary_text=analysis_report.summary_text,
                             metadata=metadata)


    # HELPERS
    def extract_approved_tables(self,
                                tables: list[dict[str, Any]]
                                ) -> list[dict[str, Any]]:
        approved_tables = []
        for table in tables:
            table_name = table.get("name")
            table_rows = table.get("rows", [])

            if table_name not in self.ALLOWED_TABLE_NAMES:
                continue

            approved_tables.append({"name": table_name,
                                    "rows": table_rows})
            
        return approved_tables
