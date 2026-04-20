from datetime import date, datetime
from typing import Optional
from abc import ABC, abstractmethod
from uuid import UUID

from rolling.app.repositories.athletes import create_athlete_batch, get_athlete_by_external_code
from rolling.app.repositories.performances import create_performance_batch, get_performance_by_name, get_metric_by_name
from rolling.app.repositories.symptoms import create_symptom_record_batch, get_symptom_by_name
from rolling.app.repositories.cycle_phases import create_cycle_phase_record_batch, get_cycle_phase_type_by_name
from rolling.app.repositories.hormone_measurements import create_hormone_measurement_batch, get_hormone_by_name

from psycopg2.errors import IntegrityError


class BaseContentMapper(ABC):
    """
    A base class for mapping uploaded files to the database object they need to be uploaded to.

    To work with a specific file type, there must be a class that inherits from this base class. The child classes will
    construct the payloads and persist them with the appropriate repository functions.

    There are only five accepted file names. These names are used for mapping to the appropriate mapping class. The
    classes are as follows:
        1. 'athletes.csv'
        2. 'performances.csv'
        3. 'symptoms.csv'
        4. 'cycle_phases.csv'
        5. 'hormones.csv'

    Attributes:
        filename (str): The name of the uploaded file.
    """

    filename: str

    def map_rows(self, filename: str, rows: list[dict[str, str]], dataset_id: UUID) -> dict:
        """
        This is procedure of mapping file contents to the database.

        The main steps for the mapping include:
        1. Validating that the file name matches mapper class used.
        2. Validating that the rows are not empty.
        3. Building the payloads for uploading to the database.
        4. Persisting the payloads.

        Returns:
            dict: A dictionary containing data on the outcome of the file mapping.
                - "file_name" (str): The name of the file that was uploaded.
                - "import_successful" (bool):True if the mapping was successful. False otherwise.
                - "row_count" (int): The number of rows in the file.
                - "imported_count" (int): The number of records that were persisted.
                - "errors" (list[str]): A list of errors that occurred during mapping.
        """
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
        """An abstract method for building the payloads for uploading to the database."""
        ...

    @abstractmethod
    def persist_payloads(self,
                         payloads: list[dict]) -> list[dict]:
        """An abstract method for persisted payloads to the database."""
        ...

    def validate_filename(self, file_name: str):
        """
        Validates that the file name matches the mapper class used.

        If validation is successful, nothing is returned or raised.

        Args:
            file_name (str): The name of the uploaded file.

        Raises:
            ValueError: If the file name does not match the mapper class used.
        """
        if file_name != self.filename:
            raise ValueError(f"Expected '{self.filename}', got '{file_name}'")
        
    def validate_rows_present(self, rows: list[dict[str, str]]) -> None:
        """
        Validates that the list of rows are not empty.

        If validation is successful, nothing is returned or raised.

        Args:
            rows (list[dict[str, str])): A list of rows to be validated.

        Raises:
            ValueError: If rows is an empty list.
        """
        if not rows:
            raise ValueError("CSV contains no data rows.")

    # LOOKUP HELPERS
    def get_athlete_id_from_athlete_code(self, athlete_code: str) -> UUID:
        """
        Returns the athlete id for a given athlete code.

        Athlete codes are unique within a project, so if the athlete code exists, a single record will be returned.
        Uploaded datasets only include athlete codes.

        Args:
            athlete_code (str): The athlete code for which the athlete ID is to be returned.

        Returns:
            UUID: The athlete ID for a given athlete code.

        Raises:
            RecordNotFoundException: If the athlete code does not exist.
        """
        athlete_id = get_athlete_by_external_code(athlete_code)
        if athlete_id:
            return UUID(str(athlete_id["athlete_id"]))
        raise RecordNotFoundException(athlete_code, self.filename)

    def get_performance_type_from_label(self, name: str) -> UUID:
        """
        Returns the ID of the performance type based on the name.

        Args:
            name (str): The name of the performance type.

        Returns:
            UUID: The perfomance type ID for a given performance type name.

        Raises:
            RecordNotFoundException: If the performance type does not exist.
        """
        performance_type = get_performance_by_name(name)
        if performance_type:
            return UUID(str(performance_type["performance_type_id"]))
        raise RecordNotFoundException(name, self.filename)

    def get_metric_type_id(self, name: Optional[str]) -> Optional[int]:
        """
        Returns the ID of the performance metric type based on the name.

        Args:
            name (str): The name of the performance metric type.

        Returns:
            UUID: The performance metric type ID for a given performance metric type.

        Raises:
            RecordNotFoundException: If the performance metric type does not exist.
        """
        if name is None:
            return None
        metric_type = get_metric_by_name(name)
        if metric_type:
            return int(metric_type["metric_type_id"])
        raise RecordNotFoundException(name, self.filename)

    def get_hormone_id_by_name(self, name: str) -> int:
        """
        Returns the ID of the hormone name.

        Args:
            name (str): The name of the hormone.

        Returns:
            int: The ID of the hormone.

        Raises:
            RecordNotFoundException: If the hormone does not exist.
        """
        hormone = get_hormone_by_name(name)
        if hormone:
            return int(hormone["hormone_id"])
        raise RecordNotFoundException(name, self.filename)

    def get_cycle_phase_type_id(self, name: str) -> int:
        """
        Returns the ID of the cycle phase type.

        Args:
            name (str): The name of the cycle phase type.

        Returns:
            int: The ID of the cycle phase type.

        Raises:
            RecordNotFoundException: If the cycle phase type does not exist.
        """
        cycle_phase = get_cycle_phase_type_by_name(name)
        if cycle_phase:
            return int(cycle_phase["cycle_phase_type_id"])
        raise RecordNotFoundException(name, self.filename)

    def get_symptom_id(self, name: str) -> int:
        """
        Returns the ID of the menstrual symptom type.

        Args:
            name (str): The name of the menstrual symptom.

        Returns:
            int: The ID of the menstrual symptom.

        Raises:
            RecordNotFoundException: If the menstrual symptom does not exist.
        """
        symptom = get_symptom_by_name(name)
        if symptom:
            return int(symptom["menstrual_symptom_id"])
        raise RecordNotFoundException(name, self.filename)

    # DATE PARSER HELPER
    def parse_date(self, value: str) -> Optional[date]: # TODO make a static method
        """
        Parses the date from the provided string if it matches a valid patterns.

        The accepted patterns are as follows, with examples:
            - "%Y-%m-%d": "2000-01-31"
            - "%Y-%m-%d %H:%M": "2000-01-31 10:26"
            - "%Y-%m-%d %H:%M:%S": "2000-01-31 10:26:50"

        If an empty string is provided, None is returned.

        Args:
            value (str): The date to parse.

        Returns:
            Optional[date]: The parsed date, if it is a valid pattern. None otherwise.

        Raises:
            ValueError: If the date string does not match any of the patterns.
        """
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
    """
    A child class of BaseContentMapper. This class maps athlete data from a file called 'athletes.csv' to the database.

    Attributes:
        filename (str): The name of the athlete CSV file. The only accepted file name is 'athletes.csv'.
    """
    filename = "athletes.csv"

    def build_payloads(self, rows: list[dict[str, str]], dataset_id: UUID) -> list[dict]:
        """Builds payloads of athlete data from the CSV file."""
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
        """Persists the provided athlete payloads into the database."""
        return create_athlete_batch(payloads)

    
class PerformanceContentMapper(BaseContentMapper):
    """
    A child class of BaseContentMapper. This class maps athlete data from a file called 'performance.csv' to the database.

    Attributes:
        filename (str): The name of the athlete CSV file. The only accepted file name is 'performances.csv'.
    """
    filename = "performances.csv"

    def build_payloads(self, rows: list[dict[str, str]], dataset_id: UUID) -> list[dict]:
        """Builds payloads of performance data from the CSV file."""
        payloads = []
        for row in rows:
            payload = {
                "athlete_id": self.get_athlete_id_from_athlete_code(row["athlete_code"]),
                "dataset_id": dataset_id,
                "performance_type": self.get_performance_type_from_label(row["session_label"]),
                "metric_type": self.get_metric_type_id(row.get("metric_name")),
                "metric_value": float(row.get("metric_value")) if row.get("metric_value") else None,
                "metric_unit": row.get("metric_unit"),
                "observed_on": self.parse_date(row["date"])
            }
            payloads.append(payload)
        return payloads

    def persist_payloads(self, payloads: list[dict]) -> list[dict]:
        """Persists the provided performance payloads into the database."""
        return create_performance_batch(payloads)

class SymptomsContentMapper(BaseContentMapper):
    """
    A child class of BaseContentMapper. This class maps athlete data from a file called 'symptoms.csv' to the database.

    Attributes:
        filename (str): The name of the athlete CSV file. The only accepted file name is 'symptoms.csv'.
    """
    filename = "symptoms.csv"

    def build_payloads(self, rows: list[dict[str, str]], dataset_id: UUID) -> list[dict]:
        """Builds payloads of symptom data from the CSV file."""
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
        """Persists the provided symptom payloads into the database."""
        return create_symptom_record_batch(payloads)

class CyclePhasesContentMapper(BaseContentMapper):
    """
    A child class of BaseContentMapper. This class maps athlete data from a file called 'cycle_phases.csv' to the database.

    Attributes:
        filename (str): The name of the athlete CSV file. The only accepted file name is 'cycle_phases.csv'.
    """
    filename = "cycle_phases.csv"

    def build_payloads(self, rows: list[dict[str, str]], dataset_id: UUID) -> list[dict]:
        """Builds payloads of cycle phase data from the CSV file."""
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
        """Persists the provided cycle phase payloads into the database."""
        return create_cycle_phase_record_batch(payloads)
        
class HormonesContentMapper(BaseContentMapper):
    """
    A child class of BaseContentMapper. This class maps athlete data from a file called 'hormones.csv' to the database.

    Attributes:
        filename (str): The name of the athlete CSV file. The only accepted file name is 'hormones.csv'.
    """
    filename = "hormones.csv"

    def build_payloads(self, rows: list[dict[str, str]], dataset_id: UUID) -> list[dict]:
        """Builds payloads of hormone data from the CSV file."""
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
        """Persists the provided hormone measurement payloads into the database."""
        return create_hormone_measurement_batch(payloads)
    

class MapperDispatcher(): # TODO remove parentheses
    """
    This class acts a dispatcher. It takes the uploaded files and matches them to the appropriate mapper class.
    """
    def map_files(self,
                  files: list[tuple[str, list[dict[str, str]], UUID]],
                  ) -> list[dict]:
        """
        Iteratively maps each file in files to the database.

        Args:
            files: list[tuple[str, list[dict[str, str]], UUID]]: The files to be mapped.

        Returns:
            list[dict]: A list of dictionaries containing data on the outcome of the file mapping.
        """
        results = []
        for file_name, rows, dataset_id in files:
            results.append(self.map_file(file_name, rows, dataset_id))
        return results

    def map_file(self, # TODO make a static method
                 file_name: str,
                 rows: list[dict[str, str]],
                 dataset_id: UUID,
                 ) -> dict:
        """
        Uploads the rows from a file_name to the database.

        Args:
            file_name (str): The name of the file uploaded.
            rows (list[dict[str, str]]): The rows for the file uploaded.
            dataset_id (UUID): The id of the dataset record (of the file uploaded).

        Returns:
            dict: A dictionary containing data on the outcome of the file mapping.
                - "file_name" (str): The name of the file that was uploaded.
                - "import_successful" (bool):True if the mapping was successful. False otherwise.
                - "row_count" (int): The number of rows in the file.
                - "imported_count" (int): The number of records that were persisted.
                - "errors" (list[str]): A list of errors that occurred during mapping.
        """
        mapper = get_mapper_for_file(file_name)
        return mapper.map_rows(file_name, rows, dataset_id)

MAPPER_MAP = { # TODO make an attribute of the class
    "athletes.csv": AthleteContentMapper,
    "performances.csv": PerformanceContentMapper,
    "hormones.csv": HormonesContentMapper,
    "symptoms.csv": SymptomsContentMapper,
    "cycle_phases.csv": CyclePhasesContentMapper,
}

def get_mapper_for_file(file_name: str) -> BaseContentMapper:
    """
    Maps a file name to the appropriate content mapper.

    Args:
        file_name (str): The name of the file uploaded.

    Returns:
        BaseContentMapper: The relevant child class of BaseContentMapper.

    Raises:
        ValueError: If the file name is invalid.
    """
    mapper_cls = MAPPER_MAP.get(file_name)
    if mapper_cls is None:
        raise ValueError(f"Unsupported file: {file_name}")
    return mapper_cls()

# EXCEPTIONS
class MappingException(Exception): # TODO rename to error
    """Base exception for mapping failures."""
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(message)

class RecordNotFoundException(MappingException): # TODO rename to error
    """Raised when a record is not found in the database."""
    def __init__(self, value: int, filename: str):
        super().__init__(f"Record  '{value}' from '{filename}' not found in database.")
