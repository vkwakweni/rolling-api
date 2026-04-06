from datetime import date, datetime
from typing import Optional
from abc import ABC, abstractmethod
from uuid import UUID

from app.repositories.athletes import create_athlete_batch, get_athlete_by_external_code
from app.repositories.performances import create_performance_batch, get_performance_by_name, get_metric_by_name
from app.repositories.symptoms import create_symptom_record_batch, get_symptom_by_name
from app.repositories.cycle_phases import create_cycle_phase_record_batch, get_cycle_phase_type_by_name
from app.repositories.hormone_measurements import create_hormone_measurement_batch, get_hormone_by_name

from psycopg2.errors import IntegrityError


class BaseContentMapper(ABC):
    """
    TODO doctrings
    TODO rename database tables to match codebase; prefer these ones:
        - research.athletes, research.performance_reocrds,
            research.menstrual_symptom_records, research.menstrual_phase_records
    * What's a better name: row or payload
    """

    filename: str

    def map_rows(self, filename: str, rows: list[dict[str, str]], dataset_id: UUID) -> dict:
        
        try:
            self.validate_filename(filename)
            self.validate_rows_present(rows)
        except ValueError as e:
            return {"file_name": self.filename,
                    "import_successful": False,
                    "row_count": 0,
                    "imported_count": 0,
                    "errors": [str(e)]
                    }
        try:
            payloads = self.build_payloads(rows, dataset_id)
            records = self.persist_payloads(payloads)
        except (IntegrityError, ValueError, RecordNotFoundException) as e:
            return {"file_name": self.filename,
                    "import_successful": False,
                    "row_count": len(rows),
                    "imported_count": 0,
                    "errors": [str(e)]
                    }
        return {"file_name": self.filename,
                "import_successful": True,
                "row_count": len(rows),
                "imported_count": len(records),
                "errors": []
                }

    @abstractmethod
    def build_payloads(self,
                       rows: list[dict[str, str]],
                       dataset_id: UUID,
                       ) -> list[dict]:
        ...

    @abstractmethod
    def persist_payloads(self,
                         payloads: list[dict]) -> list[dict]:
        ...

    def validate_filename(self, file_name: str):
        if file_name != self.filename:
            raise ValueError(f"Expected '{self.filename}', got '{file_name}'")
        
    def validate_rows_present(self, rows: list[dict[str, str]]) -> None:
        if not rows:
            raise ValueError("CSV contains no data rows.")

    # LOOKUP HELPERS
    def get_athlete_id_from_athlete_code(self, athlete_code: str) -> UUID:
        athlete_id = get_athlete_by_external_code(athlete_code)
        if athlete_id:
            return UUID(str(athlete_id["athlete_id"]))
        raise RecordNotFoundException(athlete_code, self.filename)

    def get_performance_type_from_label(self, name: str) -> UUID:
        performance_type = get_performance_by_name(name)
        if performance_type:
            return UUID(str(performance_type["performance_type_id"]))
        raise RecordNotFoundException(name, self.filename)

    def get_metric_type_id(self, name: str) -> int:
        metric_type = get_metric_by_name(name)
        if metric_type:
            return int(metric_type["metric_type_id"])
        raise RecordNotFoundException(name, self.filename)

    def get_hormone_id_by_name(self, name: str) -> int:
        hormone = get_hormone_by_name(name)
        if hormone:
            return int(hormone["hormone_id"])
        raise RecordNotFoundException(name, self.filename)

    def get_cycle_phase_type_id(self, name: str) -> int:
        cycle_phase = get_cycle_phase_type_by_name(name)
        if cycle_phase:
            return int(cycle_phase["cycle_phase_type_id"])
        raise RecordNotFoundException(name, self.filename)

    def get_symptom_id(self, name: str) -> int:
        symptom = get_symptom_by_name(name)
        if symptom:
            return int(symptom["menstrual_symptom_id"])
        raise RecordNotFoundException(name, self.filename)

    # DATE PARSER HELPER
    def parse_date(self, value: str) -> Optional[date]:
        valid_patterns = ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S")
        for pattern in valid_patterns:
            try:
                if value is None or value.strip() == "":
                    return None # TODO should raise an error
                return datetime.strptime(value, pattern).date()
            except ValueError:
                continue

        raise ValueError(f"Unsupported date value '{value}'")
    

class AthleteContentMapper(BaseContentMapper):
    filename = "athletes.csv"

    def build_payloads(self, rows: list[dict[str, str]], dataset_id: UUID) -> list[dict]:
        payloads = []
        for row in rows:
            payload = {
                "external_code": row["athlete_code"],
                "dataset_id": dataset_id,
                "birth_date": (self.parse_date(row["birth_date"]) if row.get("birth_date") else None),
                "birth_year": (int(row["birth_year"]) if row.get("birth_year") else None),
                "age_at_observation": (int(row["age_at_observation"]) if row.get("age_at_observation") else None),
                "age_logged_at": (self.parse_date(row["age_logged_at"]) if row.get("age_logged_at") else None),
                "notes": row.get("notes")
            }
            payloads.append(payload)
        return payloads

    def persist_payloads(self, payloads: list[dict]) -> list[dict]:
        return create_athlete_batch(payloads)

    
class PerformanceContentMapper(BaseContentMapper):
    filename = "performances.csv"

    def build_payloads(self, rows: list[dict[str, str]], dataset_id: UUID) -> list[dict]:
        payloads = []
        for row in rows:
            payload = {
                "athlete_id": self.get_athlete_id_from_athlete_code(row["athlete_code"]),
                "dataset_id": dataset_id,
                "performance_type": self.get_performance_type_from_label(row["session_label"]),
                "metric_type": self.get_metric_type_id(row["metric_name"]),
                "metric_value": float(row["metric_value"]),
                "metric_unit": row.get("metric_unit"),
                "observed_on": self.parse_date(row["date"])
            }
            payloads.append(payload)
        return payloads

    def persist_payloads(self, payloads: list[dict]) -> list[dict]:
        return create_performance_batch(payloads)

class SymptomsContentMapper(BaseContentMapper):
    filename = "symptoms.csv"

    def build_payloads(self, rows: list[dict[str, str]], dataset_id: UUID) -> list[dict]:
        payloads = []
        for row in rows:
            payload = {
                "athlete_id": self.get_athlete_id_from_athlete_code(row["athlete_code"]),
                "dataset_id": dataset_id,
                "symptom_id": int(self.get_symptom_id(row["symptom"])),
                "observed_on": self.parse_date(row["date"]),
                "symptom_severity": row.get("severity"),
                "notes": row.get("notes"),
                "relative_day_to_cycle": (int(row["relative_day_to_cycle"]) if row.get("relative_day_to_cycle") else None)
            }
            payloads.append(payload)
        return payloads


    def persist_payloads(self, payloads: list[dict]) -> list[dict]:
        return create_symptom_record_batch(payloads)

class CyclePhasesContentMapper(BaseContentMapper):
    filename = "cycle_phases.csv"

    def build_payloads(self, rows: list[dict[str, str]], dataset_id: UUID) -> list[dict]:
        payloads = []
        for row in rows:
            payload = {
                "athlete_id": self.get_athlete_id_from_athlete_code(row["athlete_code"]),
                "dataset_id": dataset_id,
                "observed_on": self.parse_date(row["date"]),
                "cycle_phase_type": int(self.get_cycle_phase_type_id(row["phase"])),
                "cycle_day": (int(row["relative_day_to_cycle"]) if row.get("relative_day_to_cycle") else None)
            }
            payloads.append(payload)
        return payloads
    def persist_payloads(self, payloads: list[dict]) -> list[dict]:
        return create_cycle_phase_record_batch(payloads)
        
class HormonesContentMapper(BaseContentMapper):
    filename = "hormones.csv"

    def build_payloads(self, rows: list[dict[str, str]], dataset_id: UUID) -> list[dict]:
        payloads = []
        for row in rows:
            payload = {
                "athlete_id": self.get_athlete_id_from_athlete_code(row["athlete_code"]),
                "dataset_id": dataset_id,
                "hormone_id": self.get_hormone_id_by_name(row["hormone_name"]),
                "measured_value": float(row["measurement_value"]),
                "unit": row.get("measurement_unit"),
                "observed_on": self.parse_date(row["date"])
            }
            payloads.append(payload)
        return payloads

    def persist_payloads(self, payloads: list[dict]) -> list[dict]:
        return create_hormone_measurement_batch(payloads)
    

class MapperDispatcher():

    def map_files(self,
                  files: list[tuple[str, list[dict[str, str]], UUID]],
                  ) -> list[dict]:
        results = []
        for file_name, rows, dataset_id in files:
            results.append(self.map_file(file_name, rows, dataset_id))
        return results

    def map_file(self,
                 file_name: str,
                 rows: list[dict[str, str]],
                 dataset_id: UUID,
                 ) -> dict:
        mapper = get_mapper_for_file(file_name)
        return mapper.map_rows(file_name, rows, dataset_id)

MAPPER_MAP = {
    "athletes.csv": AthleteContentMapper,
    "performances.csv": PerformanceContentMapper,
    "hormones.csv": HormonesContentMapper,
    "symptoms.csv": SymptomsContentMapper,
    "cycle_phases.csv": CyclePhasesContentMapper,
}

def get_mapper_for_file(file_name: str) -> BaseContentMapper:
    mapper_cls = MAPPER_MAP.get(file_name)
    if mapper_cls is None:
        raise ValueError(f"Unsupported file: {file_name}")
    return mapper_cls()

# EXCEPTIONS
class MappingException(Exception):
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(message)

class RecordNotFoundException(MappingException):
    def __init__(self, value: int, filename: str):
        super().__init__(f"Record  '{value}' from '{filename}' not found in database.")
