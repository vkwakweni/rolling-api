class AnalysisEngineError(Exception):
    """Base exception for analysis engine failures."""
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(message)


class AnalysisInputError(AnalysisEngineError):
    """Raised when analysis input is invalid or incomplete."""
    def __init__(self, message):
        super().__init__(message)


class AnalysisDataError(AnalysisEngineError):
    """Raised when required source data is missing or unusable."""
    def __init__(self, message):
        super().__init__(message)


class AnalysisExecutionError(AnalysisEngineError):
    """Raised when analysis execution fails unexpectedly."""
    def __init__(self, message):
        super().__init__(message)
