from uuid import UUID

from rolling.app.models.ai import GenerateAIAnalysisReportResponse
from rolling.app.models.analyses import AnalysisReportResponse, AnalysisResultResponse
from rolling.app.services.ai import (validator)
from rolling.app.services.ai.provider import AIProvider
from rolling.app.repositories.ai import (create_agent_trace,
                                 create_ai_analysis_report)
from rolling.app.repositories.analyses import (list_analysis_results_by_analysis_run,
                                       get_analysis_report_by_analysis_run,
                                       analyst_can_access_analysis_run)
from rolling.app.services.ai import input_builder, model_client, prompt_builder

class AIReportOrchestrator:

    def __init__(self, model_name: str, provider: AIProvider):
        self.input_builder = input_builder.AIInputBuilder()
        self.prompt_builder = prompt_builder.AIReportPromptBuilder()
        self.model_client = model_client.AIModelClient(model_name=model_name, provider=provider)
        self.validator = validator.AIReportValidator()

    def generate_ai_report_for_analysis_run(self,
                                            analyst_id: UUID,
                                            analysis_run_id: UUID,
                                            ) -> GenerateAIAnalysisReportResponse:
        if not analyst_can_access_analysis_run(analyst_id=analyst_id, analysis_run_id=analysis_run_id):
            raise PermissionError("Analayst cannot access this analysis run")
        
        analysis_results = list_analysis_results_by_analysis_run(analysis_run_id)
        if not analysis_results:
            raise ValueError("AI report cannot be generated from an empty result set")
        
        analysis_results = [AnalysisResultResponse(**result) for result in analysis_results]
        
        analysis_report = get_analysis_report_by_analysis_run(analysis_run_id)
        if not analysis_report:
            raise ValueError("AI report cannot be generated from an empty traditional analysis report")
        analysis_report = AnalysisReportResponse(**analysis_report)

        ai_input = self.input_builder.build_allowed_ai_input(analysis_results=analysis_results,
                                                             analysis_report=analysis_report)

        prompt = self.prompt_builder.build_prompt(ai_input=ai_input)

        model_output = self.model_client.generate_ai_analyis_report(prompt_payload=prompt)

        validated_output = self.validator.validate_generated_report(model_output)

        metadata = {"status": "completed",
                    "operation": "ai_report_generation",
                    "notes": None}

        trace_record = create_agent_trace(analyst_id=analyst_id,
                                          analysis_run_id=analysis_run_id,
                                          step_name="ai_report_generation",
                                          model_name=self.model_client.model_name,
                                          metadata=metadata)
        
        report_record = create_ai_analysis_report(analyst_id=analyst_id,
                                                  analysis_run_id=analysis_run_id,
                                                  agent_trace_id=trace_record.get("agent_trace_id"),
                                                  model_name=self.model_client.model_name,
                                                  report_text=validated_output.report_text,
                                                  summary_text=validated_output.summary_text,
                                                  comparison_notes=None)

        return GenerateAIAnalysisReportResponse(agent_trace=trace_record,
                                        ai_report=report_record)
