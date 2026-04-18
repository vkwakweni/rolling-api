from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

# TODO doctring for all classes and fields
@dataclass(frozen=True) # makes them immutable
class HormoneObservation:
    """Represents a single observation of hormone levels, symptoms, or performance metrics for an athlete on a specific day.
    
    This is the raw data format that the analysis engine will process. The app layer is responsible
    for transforming raw data into this format before passing it to the analysis engine.

    Attributes:
        athlete_id (UUID): Unique identifier for an athlete.
        observed_on (date): The date on which the observation was performed.
        hormone_name (str): The name of the hormone that was measured.
        measured_value (float | int): The value of the hormone measurement.
        measurement_unit (Optional[str]): The unit of measurement for the hormone measurement.
        symptom_name (Optional[str]): The name of a menstrual symptom observed.
        symptom_severity (Optional[str]): The severity of the menstrual symptom observed.
        relative_day_to_cycle: (Optional[int]): The number of days since the first menstrual bleeding (the beginning of a new menstrual cycle).
        performance_type (Optional[str]): The type of performance performed on the observed day, which represents the intensity of the performance.
        metric_name (Optional[str]): A name of a performance metric (e.g. 'BPM' for heart rate)
        metric_value (Optional[str]): The value of the performance metric.
        metric_unit (Optional[str]): The unit of measurement for the performance metric.
    
    """
    athlete_id: UUID
    observed_on: date
    hormone_name: str # hormone data
    measured_value: float | int
    measurement_unit: Optional[str] = None
    symptom_name: Optional[str] = None # menstrual data
    symptom_severity: Optional[str] = None
    relative_day_to_cycle: Optional[int] = None
    performance_type: Optional[str] = None # performance data
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    metric_unit: Optional[str] = None


@dataclass(frozen=True)
class HormoneAnalysisInput:
    """
    Represents the input data required for hormone analysis, including hormone observations and optional filters for hormone names, performance types, symptom names, and date range.

    This is the input format that the analysis engine expects. The app layer is responsible for transforming raw data into this format before passing it to the analysis engine.

    Attributes:
        project_id (UUID): Unique identifier for a project.
        observations (list[HormoneObservation]): A collection of hormone observations.
        include_hormone_names (Optional[list[str]]): An optional collection of hormone names to inclusively filter for in `observations`.
        include_performance_types (Optional[list[str]]): An optional collection of hormone names to inclusively filter for in `observations`.
        include_symptom_names (Optional[list[str]]): An optional collection of symptom names to inclusively filter for in `observations`.
        date_from (Optional[date]): Used to filter for observations from this date inclusviely.
        date_to (Optional[date]): Used to filter for observations until this date inclusively.
    """
    project_id: UUID
    observations: list[HormoneObservation] = field(default_factory=list)
    include_hormone_names: Optional[list[str]] = None
    include_performance_types: Optional[list[str]] = None
    include_symptom_names: Optional[list[str]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None

@dataclass(frozen=True)
class HormoneAnalysisResult:
    """
    Represents the result of a hormone analysis, including the summary of the analysis results, any tables generated during the analysis, additional metadata about the analysis, and conclusions drawn from the analysis.
    
    This is the output format that the analysis engine will produce. The app layer is responsible for
    persisting this data and using it to generate insights for the user.

    Attributes:
        analysis_kind (str): The kind of analysis that was executed. Version 1 only supports `'descriptive_hormone_analysis'`.
        engine_version (str): Describes whether the analysis was run using traditional methods or with AI-assistance. Version 1 only supports `'traditional'`.
        generated_at (datetime): A timestamp of when the analysis was executed.
        summary (dict[str, Any]): A dictionary of statistics for grouped and compared observations.
        tables (list[dict[str, Any]]): A list of the `summary` statistics structured as tables with an identifying table name.
        metadata (dict[str, Any]): A dictionary of the metadata of the analysis run, including the project ID, the observation counts and filters.
        conclusions (list[str]): Human-readable conclusions from the `summary` statistics.
    """
    analysis_kind: str 
    engine_version: str
    generated_at: datetime
    summary: dict[str, Any] = field(default_factory=dict)
    tables: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    conclusions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AnalysisTable: # stable way to return tables
    """DEPRECATED: Represents a table generated during hormone analysis, including the name of the table and the rows of data contained in the table."""
    name: str
    rows: list[dict[str, Any]] = field(default_factory=list)
