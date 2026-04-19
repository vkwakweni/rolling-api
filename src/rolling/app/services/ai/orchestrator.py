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
    """
    This class is used to orchestrate the AI service.

    It functions as an interface between the different components of the AI service. It produces an AI-generated analysis report.

    The main steps of the AI service include:
    1. Validating that the analyst can access the analysis run.
    2. Validating that the analysis results exist.
    3. Validating that the analysis report exists.
    4. Building the AI service's input.
    5. Building the prompt for the AI service.
    6. Generating the AI analysis report using the model client.
    7. Validating the generated AI analysis report.
    8. Building the metadata for generation of the AI analysis report.
    9. Persists the agent trace that marks using the AI service.
    10. Persists the generated AI analysis report.

    Attributes
    ----------
    input_builder : AIInputBuilder
        An instance of the AIInputBuilder class used to build the input for the AI service.
    prompt_builder : AIPromptBuilder
        An instance of the AIPromptBuilder class used to build the prompt for the AI service.
    model_client : AIModelClient
        An instance of the AIModelClient class used to communicate with the AI service.
    validator : AIValidator
        An instance of the AIReportValidator class used to validate the generated AI analysis report.
    """

    def __init__(self, model_name: str, provider: AIProvider):
        """initialises the AIReportOrchestrator class by creating instances of AIInputBuilder, AIPromptBuilder, AIModelClient, and AIValidator."""
        self.input_builder = input_builder.AIInputBuilder()
        self.prompt_builder = prompt_builder.AIReportPromptBuilder()
        self.model_client = model_client.AIModelClient(model_name=model_name, provider=provider)
        self.validator = validator.AIReportValidator()

    def generate_ai_report_for_analysis_run(self,
                                            analyst_id: UUID,
                                            analysis_run_id: UUID,
                                            ) -> GenerateAIAnalysisReportResponse:
        """
        Executes the generation of the AI Analysis report based on an analysis run.

        Args:
            analyst_id (UUID): The ID of the analyst requesting the AI-generated analysis report.
            analysis_run_id (UUID): The ID of the analysis run on which to base the AI-generated report.

        Returns:
            GenerateAIAnalysisReportResponse: A structured object for the generated AI analysis report.
        """
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
