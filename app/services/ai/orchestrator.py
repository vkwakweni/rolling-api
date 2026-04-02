from typing import UUID

from app.models.ai import GenerateAIReportResponse

class AIReportOrchestrator:

    def __init__(self):
        """
        Possible dependencies:
        - AI repo
        - analysis repository/service
        - input builder
        - prompt builder
        - model client
        - validator
        """

    def generate_for_analysis_run(self,
                                  analysis_id: UUID,
                                  analysis_run_id: UUID,
                                  ) -> GenerateAIReportResponse:
        ...
