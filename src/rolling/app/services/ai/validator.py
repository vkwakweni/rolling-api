from rolling.app.models.ai import AIModelOutput

class AIReportValidator:
    """
    A class that validates the AI-generated analysis report.

    The main steps of validation include:
    1. Checking that the model exists and is non-empty.
    2. Checking that the report text is valid and non-empty.
    3. Returns the AI-generated analysis report as a structured object.
    """

    def validate_generated_report(self,
                                  generated_output: AIModelOutput
                                  ) -> AIModelOutput:
        """
        Validates the generated AI-generated report.

        Args:
            generated_output (AIModelOutput): The generated AI-generated analysis report.

        Returns:
            AIModelOutput: If validated, the AI-generated analysis report.

        Raises:
            ValueError: If the model name is empty; if the report text is empty.
        """
        model_name = generated_output.model_name.strip() if generated_output.model_name is not None else None
        report_text = generated_output.report_text.strip() if generated_output.report_text is not None else None
        summary_text = generated_output.summary_text.strip() if generated_output.summary_text is not None else None

        if not model_name:
            raise ValueError("AI output must include a model_name.")
        
        if not report_text:
            raise ValueError("AI output must include non-empty report_text")
        
        return AIModelOutput(model_name=model_name,
                             report_text=report_text,
                             summary_text=summary_text)
