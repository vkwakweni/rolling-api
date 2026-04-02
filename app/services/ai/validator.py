from typing import Any

from app.models.ai import AIModelOutput

class AIReportValidator:

    def __init__(self):
        ...

    def validate_generated_report(self,
                                  generated_output: dict[str, Any]
                                  ) -> AIModelOutput:
        ...
