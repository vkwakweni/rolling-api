import csv
import io
import re
from datetime import datetime

class BaseCSVValidator:
    """
    TODO docstrings
    """
    filename = ""
    required_columns = set()
    optional_columns = set()
    date_columns = set() # TODO differentiate between date and datetime
    numeric_columns = set()
    integer_columns = set()
    allowed_values = {}

    def validate(self, file_name: str, file_bytes: bytes) -> dict:
        """
        An orchestrator
        """
        errors = []
        warnings = []

        try:
            self.validate_filename(file_name)
            csv_text = self.decode_file(file_bytes)
            rows = self.parse_csv(csv_text)

            if not rows:
                return {"file_name": file_name,
                        "is_valid": False,
                        "row_count": 0,
                        "errors": ["CSV contains no data rows."],
                        "warnings": warnings}
            
            headers = set(rows[0].keys())
            header_result = self.validate_headers(headers)

            if header_result["Required columns missing"]:
                errors.append(
                    f"Missing required columns: {sorted(header_result['Required columns missing'])}"
                )

            if header_result["Forbidden columns"]:
                errors.append(
                    f"Unexpected columns: {sorted(header_result['Forbidden columns'])}"
                )

            if not errors:
                errors.extend(self.validate_rows(rows))

            return {"file_name": file_name,
                    "is_valid": len(errors) == 0,
                    "row_count": len(rows),
                    "errors": errors,
                    "warnings": warnings,}
            
        except Exception as e:
            return {"file_name": file_name,
                    "is_valid": False,
                    "row_count": 0,
                    "errors": [str(e)],
                    "warnings": warnings}

    def decode_file(self, file_bytes: bytes) -> str:
        """
        Decodes uploaded file from API
        :returns str: The text of the file that was uploaded
        """
        return file_bytes.decode("utf-8")

    def parse_csv(self, csv_text: str) -> list[dict]:
        """
        Parses csv_text into a list of dictionary, reading the first row as a header.
        TODO testing
        """
        reader = csv.DictReader(io.StringIO(csv_text))
        return [dict(row) for row in reader]

    def validate_filename(self, file_name: str):
        """
        Checks that the chosen subclass matches the file it received
        TODO check if this actually makes sense; I can't imagine a use case
        """
        if file_name != self.filename:
            raise ValueError(f"Expected file '{self.filename}', got '{file_name}'")

    def validate_headers(self, headers: set[str]) -> dict[str, list[str]]: # TODO set type to iterable of strings
        """
        """
        missing_required_columns = self.validate_required_columns(headers)
        forbidden_columns = self.validate_allowed_columns(headers)
        return {"Required columns missing": missing_required_columns,
                "Forbidden columns": forbidden_columns}        

    def validate_required_columns(self, headers) -> list[str]:
        return list(self.required_columns - headers)

    def validate_allowed_columns(self, headers) -> list[str]:
        allowed_columns = self.required_columns.union(self.optional_columns)
        return list(headers - allowed_columns)

    def validate_rows(self, rows):
        errors = []
        for i, row in enumerate(rows, start=1):
            errors.extend(self.validate_row(row, i))
        return errors

    def validate_row(self, row: dict[str, str], row_number: int):
        errors = []
        errors.extend(self.validate_required_values(row, row_number))
        errors.extend(self.validate_date_columns(row, row_number))
        errors.extend(self.validate_numeric_columns(row, row_number))
        errors.extend(self.validate_integer_columns(row, row_number))
        errors.extend(self.validate_allowed_value_columns(row, row_number))
        return errors

    def validate_date_columns(self, row: dict[str, str], row_number: int) -> list[str]:
        """
        Accepted formats:
        - YYYY-MM-DD
        - YYYY
        - YYYY-MM-DD HH:MM
        - YYYY-MM-DD HH:MM:SS
        """
        # pattern checks that they're existing dates too
        # TODO remove year from this check; year should be an integer
        valid_patterns = {"%Y-%m-%d", "%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"}
        errors = [] 

        for column in self.date_columns:
            value = row.get(column)

            if value is None or value.strip() == "":
                continue # TODO make blanks in required columns errors
            
            matched = False
            for pattern in valid_patterns:
                try:
                    datetime.strptime(value, pattern)
                    matched = True
                    break
                except ValueError:
                    continue
            
            if not matched:
                errors.append(str(InvalidDateException(row_number, column)))

        return errors

    def validate_numeric_columns(self, row: dict[str, str], row_number: int) -> list[str]:
        errors = []
        for column in self.numeric_columns:
            value = row.get(column)

            if value is None or value.strip() == "":
                continue

            try:
                float(value)
            except ValueError:
                errors.append(str(InvalidTypeException(row_number, column, "numeric")))

        return errors

    def validate_integer_columns(self, row: dict[str, str], row_number: int) -> list[str]:
        errors = []
        for column in self.integer_columns:
            value = row.get(column)

            if value is None or value.strip() == "":
                continue

            try:
                int(value)
            except ValueError:
                errors.append(str(InvalidTypeException(row_number, column, "integer")))
        return errors
    
    def validate_required_values(self, row: dict[str, str], row_number: int) -> list[str]:
        errors = []
        for column in self.required_columns:
            value = row.get(column)
            if value is None or value.strip() == "":
                errors.append(str(RequiredBlankException(row_number, column)))
        return errors

    def validate_allowed_value_columns(self, row: dict[str, str], row_number: int) -> list[str]:
        errors = []

        for column, allowed_values in self.allowed_values.items():
            value = row.get(column)

            if value is None or value.strip() == "":
                continue

            if value not in allowed_values:
                errors.append(str(UnexpectedValueException(row_number, column, allowed_values)))

        return errors


class AthletesCSVValidator(BaseCSVValidator):
    filename = "athletes.csv"
    required_columns = {"athlete_code", "sex"}
    optional_columns = {"birth_date", "birth_year", "age_at_observation",
                        "age_logged_at", "notes"}
    date_columns = {"birth_date", "age_logged_at"}
    numeric_columns = set()
    integer_columns = {"birth_year", "age_at_observation"}
    allowed_values = {"sex": ["F", "I", "M"]}
    athlete_code_pattern = re.compile("^R[A-Z0-9]{4}$")

    def validate_row(self, row: dict[str, str], row_number: int) -> list[str]:
        errors = []
        errors.extend(self.validate_required_values(row, row_number))
        errors.extend(self.validate_date_columns(row, row_number))
        errors.extend(self.validate_numeric_columns(row, row_number))
        errors.extend(self.validate_integer_columns(row, row_number))
        errors.extend(self.validate_allowed_value_columns(row, row_number))
        errors.extend(self.validate_athlete_code(row, row_number))
        errors.extend(self.validate_birth_info_group(row, row_number))
        return errors

    def validate_athlete_code(self, row: dict[str, str], row_number: int) -> list[str]:
        errors = []
        value = row.get("athlete_code")

        if value is None or value.strip() == "":
            errors.append(str(RequiredBlankException(row_number, "athlete_code")))
            return errors
        
        if not self.athlete_code_pattern.match(value.strip()):
            errors.append(f"Row {row_number}: column 'athlete_code' must match r'^R[A-Z0-9]{{4}}$")

        return errors
    
    def validate_birth_info_group(self, row: dict[str, str], row_number: int) -> list[str]:
        birth_date = row.get("birth_date")
        birth_year = row.get("birth_year")
        age_at_observation = row.get("age_at_observation")
        age_logged_at = row.get("age_logged_at")

        has_birth_date = birth_date is not None and birth_date.strip() != ""
        has_birth_year = birth_year is not None and birth_year.strip() != ""
        has_age_pair = (
            age_at_observation is not None and age_at_observation.strip() != ""
            and age_logged_at is not None and age_logged_at.strip() != ""
        )

        if has_birth_date or has_birth_year or has_age_pair:
            return []
        
        return [str(InvalidBirthInfoException(row_number))]


class PerformanceCSVValidator(BaseCSVValidator):
    filename = "performances.csv"
    required_columns = {"athlete_code", "date", "session_label", "metric_name", "metric_value"}
    optional_columns = {"metric_unit"}
    numeric_columns = {"metric_value"}
    date_columns = {"date"}
    

class HormonesCSVValidator(BaseCSVValidator):
    filename = "hormones.csv"
    required_columns = {"athlete_code", "date", "hormone_name", "measurement_value"}
    optional_columns = {"measurement_unit"}
    numeric_columns = {"measurement_value"}
    date_columns = {"date"}


class SymptomsCSVValidator(BaseCSVValidator):
    filename = "symptoms.csv"
    required_columns = {"athlete_code", "date", "symptom"}
    optional_columns = {"severity", "relative_day_to_cycle"}
    integer_columns = {"relative_day_to_cycle"}
    allowed_values = {"severity": ["MILD", "MODERATE", "SEVERE"]}
    date_columns = {"date"}


class CyclePhasesCSVValidator(BaseCSVValidator):
    filename = "cycle_phases.csv"
    required_columns = {"athlete_code", "date", "phase"}
    optional_columns = {"relative_day_to_cycle"}
    integer_columns = {"relative_day_to_cycle"}
    allowed_values = {"phase": ["MENSTRUAL", "FOLLICULAR", "OVULATORY", "LUTEAL"]}
    date_columns = {"date"}


class ValidatorDispatcher:
    def validate_files(self, files: list[tuple[str, bytes]]) -> dict:
        results = []

        for file_name, file_bytes in files:
            validator = get_validator_for_file(file_name)
            results.append(validator.validate(file_name, file_bytes))

        return {"is_valid": all(result["is_valid"] for result in results),
                "files": results,}


VALIDATOR_MAP = {
    "athletes.csv": AthletesCSVValidator,
    "performances.csv": PerformanceCSVValidator,
    "hormones.csv": HormonesCSVValidator,
    "symptoms.csv": SymptomsCSVValidator,
    "cycle_phases.csv": CyclePhasesCSVValidator,
}

def get_validator_for_file(file_name: str) -> BaseCSVValidator:
    validator_cls = VALIDATOR_MAP.get(file_name)
    if validator_cls is None:
        raise ValueError(f"Unsupported file: {file_name}")
    return validator_cls()


class ValidatorException(Exception):
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(message)

class InvalidDateException(ValidatorException):
    def __init__(self, row_number: int, column: str):
        super().__init__(f"Row {row_number}: date column '{column}' is not an accepted format")

class InvalidTypeException(ValidatorException):
    def __init__(self, row_number: int, column: str, expected_type: str):
        super().__init__(f"Row {row_number}: column '{column}' must be of type '{expected_type}'")

class RequiredBlankException(ValidatorException):
    def __init__(self, row_number: int, column: str):
        super().__init__(f"Row {row_number}: required column '{column}' must not be blank")

class UnexpectedValueException(ValidatorException):
    def __init__(self, row_number: int, column: str, allowed_values):
        super().__init__(f"Row {row_number}: column '{column}' only allows {allowed_values}")

class InvalidBirthInfoException(ValidatorException):
    def __init__(self, row_number: int):
        super().__init__(f"Row {row_number}: at least one of ['birth_date', 'birth_year',"
                        "('age_at_observation', 'age_logged_at')] must be provided")

