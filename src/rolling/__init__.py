"""Rolling: analysis of small, domain-specific datasets (first case: hormones and the menstrual cycle)."""
from importlib.metadata import PackageNotFoundError, version

from rolling.analysis_engine import (
    AnalysisTable,
    DescriptiveHormoneAnalysis,
    HormoneAnalysisInput,
    HormoneAnalysisResult,
    HormoneObservation,
    build_descriptive_hormone_report,
)

try:
    __version__ = version("rolling")
except PackageNotFoundError:  # running from a source tree that is not installed
    __version__ = "0.1.0"

__all__ = [
    "AnalysisTable",
    "DescriptiveHormoneAnalysis",
    "HormoneAnalysisInput",
    "HormoneAnalysisResult",
    "HormoneObservation",
    "__version__",
    "build_descriptive_hormone_report",
]
