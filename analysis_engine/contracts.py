from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

# TODO doctring for all classes and fields
@dataclass(frozen=True) # makes them immutable
class HormoneObservation:
    # app layer is responsible for building these rows
    # an easy way of processing raw rows
    # Some of these can be null
    athlete_id: UUID # TODO verify it matches the desired format
    observed_on: date
    hormone_name: str # hormone data
    measured_value: float | int
    measurement_unit: Optional[str]
    symptom_name: Optional[str] # menstrual data
    symptom_severity: Optional[str]
    relative_day_to_cycle: Optional[int]
    performance_type: Optional[str] # performance data
    metric_name: Optional[str]
    metric_value: Optional[float]
    metric_unit: Optional[str]


@dataclass(frozen=True)
class HormoneAnalysisInput: # input contract
    project_id: UUID
    observations: list[HormoneObservation] = field(default_factory=list)
    include_hormone_names: Optional[list[str]] = None
    include_performance_types: Optional[list[str]] = None
    include_symptom_names: Optional[list[str]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None

@dataclass(frozen=True)
class HormoneAnalysisResult: # for the app to persist
    analysis_kind: str # TODO document somewhere what this means.
    engine_version: str
    generated_at: datetime
    summary: dict[str, Any] = field(default_factory=dict)
    tables: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    conclusions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AnalysisTable: # stable way to return tables
    name: str
    rows: list[dict[str, Any]] = field(default_factory=list)
