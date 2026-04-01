# DTOs for input/output
from pydantic import BaseModel

class AIReportInput(BaseModel):
    summary: dict
    tables: list[dict]
    report_text: str | None = None
    summary_text: str | None = None
    metadata: dict | None = None
