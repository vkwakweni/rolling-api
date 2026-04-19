import csv
import io
import re
from datetime import datetime

class BaseCSVValidator:
    """
    A base class for validating CSV files.

    For each kind of file, there must a class that inherits this base class. The child classes must have attributes
    describing the file name, the allowed columns, and the allowed types and values.

    Only columns that are exactly contain required_columns and appear in optional_columns may be in the file.

    For columns listed in the type columns (e.g. numeric_columns, date_columns), all values in those columns must be of
    the correct type.

    For columns indexing the dictionary allowed_values, only the values in their keys may appear in the column.

    Attributes:
        filename (str): The name of the file to validate.
        required_columns (set): The set of columns required to be in the file.
        optional_columns (set): The set of columns that are not required to be in the file.
        date_columns (set): The set of columns that must be datetime columns.
        numeric_columns (set): The set of columns that must be of type numeric (float).
        integer_columns (set): The set of columns that must be of type integer (int).
        allowed_values (dict): A dictionary of the allowed values for particular columns in the file.
    """
    filename = ""
    required_columns = set()
    optional_columns = set()
    date_columns = set() # TODO differentiate between date and datetime
    numeric_columns = set()
    integer_columns = set()
    allowed_values = {} # TODO change dict() or defaultdict()

    def validate(self, file_name: str, file_bytes: bytes) -> dict:
        """
        The main function for validation. It ensures that the file contains valid columns and values.

        The main steps of validation include:
        1. Validating that the file name matches the validator class.
        2. Parsing the file bytes.
        3. Validating the columns.
        4. Validating that the columns contain values of the correct type.

        Args:
            file_name (str): The name of the file to validate.
            file_bytes (bytes): The bytes of the file to validate.

        Returns:
            dict: A dictionary of the validation results.
                - "file_name" (str): The name of the file validated.
                - "is_valid" (bool): True if the file contents are valid. False otherwise.
                - "row_count" (int): The number of rows in a valid file. If a file is invalid, 0.
                - "errors" (list[str]): A list of errors generated during validation.
                - "warnings" (list[str]): A list of warnings generated during validation.
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

        Args:
            file_bytes (bytes): Bytes of the file to decode.

        Returns:
            str: The bytes converted to a string.
        """
        return file_bytes.decode("utf-8")

    def parse_csv(self, csv_text: str) -> list[dict]:
        """
        Parses CSV file into a list of dictionary, reading the first row as a header.

        Args:
            csv_text (str): A CSV file as a string.

        Returns:
            list[dict]: The CSV file's rows as a list of dictionaries, with the first row treated as a header and the dictionary keys.
        """
        reader = csv.DictReader(io.StringIO(csv_text))
        return [dict(row) for row in reader]

    def validate_filename(self, file_name: str):
        """
        Checks that the chosen child class matches the file it received.

        If validation is successful, nothing is returned or raised.

        Args:
            file_name: The file name to validate.

        Raises:
            ValueError: If the file name does not match the child class.
        """
        if file_name != self.filename:
            raise ValueError(f"Expected file '{self.filename}', got '{file_name}'")

    def validate_headers(self, headers: set[str]) -> dict[str, list[str]]: # TODO set type to iterable of strings
        """
        Validates that the headers contain the required columns exactly and if any forbidden columns were found.

        Args:
            headers (set[str]): A set of headers to validate.

        Returns:
            dict[str, list[str]]: A dictionary of the validation result.
                - "Required columns missing" (list[str]): A list of required columns missing.
                - "Forbidden columns" (list[str]): A list of forbidden columns.
        """
        missing_required_columns = self.validate_required_columns(headers)
        forbidden_columns = self.validate_allowed_columns(headers)
        return {"Required columns missing": missing_required_columns,
                "Forbidden columns": forbidden_columns}        

    def validate_required_columns(self, headers) -> list[str]: # TODO add type to headers
        """
        Returns a list of required columns missing in the headers.

        Args:
            headers (set[str]): A set of headers to validate.

        Returns:
            list[str]: A list of required columns missing in the header.
        """
        return list(self.required_columns - headers)

    def validate_allowed_columns(self, headers) -> list[str]:
        """
        Returns a list of columns that are forbidden.

        Args:
            headers (set[str]): A set of headers to validate.

        Returns:
            list[str]: A list of columns that are forbidden found in the header.
        """
        allowed_columns = self.required_columns.union(self.optional_columns)
        return list(headers - allowed_columns)

    def validate_rows(self, rows): # TODO add types to rows
        """
        Iteratively validates each row in rows.

        Args:
            rows (list[dict]): A list of rows to validate.

        Returns:
            list[dict]: A list of errors generated during row generation.
        """
        errors = []
        for i, row in enumerate(rows, start=1):
            errors.extend(self.validate_row(row, i))
        return errors

    def validate_row(self, row: dict[str, str], row_number: int): # TODO add return type
        """
        Validates that each row is of the correct type and/or not None.

        For required columns, every row in the column must contain a value. For specifically type columns, every row in
        the column must be of the correct type. For columns with specifically allowed values, every row in the column
        must match the allowed values.

        Args:
            row (dict[str, str]): The row to validate.
            row_number (int): The row number of the row (for error reporting).

        Returns:
            list: A list of errors generated during row generation. If there are no errors, an empty list is returned.
        """
        errors = []
        errors.extend(self.validate_required_values(row, row_number))
        errors.extend(self.validate_date_columns(row, row_number))
        errors.extend(self.validate_numeric_columns(row, row_number))
        errors.extend(self.validate_integer_columns(row, row_number))
        errors.extend(self.validate_allowed_value_columns(row, row_number))
        return errors

    def validate_date_columns(self, row: dict[str, str], row_number: int) -> list[str]:
        """
        Validates columns that expected to be of time datetime.

        Following are the accepted datetime patterns and examples:
            - "%Y-%m-%d": "2000-01-31"
            - "%Y": "2000"
            - "%Y-%m-%d %H:%M:%S": "2000-01-31 10:26:50"
            - "%Y-%m-%d %H:%M": "2000-01-31 10:26"

        Args:
            row (dict[str, str]): The row to validate.
            row_number (int): The row number of the row (for error reporting).

        Returns:
            list: A list of errors generated during row generation. If there are no errors, an empty list is returned.
        """
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
        """
        Validate columns that expected to be of numeric (float) value.

        Args:
            row (dict[str, str]): The row to validate.
            row_number (int): The row number of the row (for error reporting).

        Returns:
            list: A list of errors generated during row generation. If there are no errors, an empty list is returned.
        """
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
        """
        Validate columns that expected to be of integer (int) value.

        Args:
            row (dict[str, str]): The row to validate.
            row_number (int): The row number of the row (for error reporting).

        Returns:
            list: A list of errors generated during row generation. If there are no errors, an empty list is returned.
        """
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
        """
        Validate that required columns contain no null values.

        Args:
            row (dict[str, str]): The row to validate.
            row_number (int): The row number of the row (for error reporting).

        Returns:
            list: A list of errors generated during row generation. If there are no errors, an empty list is returned.
        """
        errors = []
        for column in self.required_columns:
            value = row.get(column)
            if value is None or value.strip() == "":
                errors.append(str(RequiredBlankException(row_number, column)))
        return errors

    def validate_allowed_value_columns(self, row: dict[str, str], row_number: int) -> list[str]:
        """
        Validate columns that only allow specific values only contain those values.

        Args:
            row (dict[str, str]): The row to validate.
            row_number (int): The row number of the row (for error reporting).

        Returns:
            list: A list of errors generated during row generation. If there are no errors, an empty list is returned.
        """
        errors = []

        for column, allowed_values in self.allowed_values.items():
            value = row.get(column)

            if value is None or value.strip() == "":
                continue

            if value not in allowed_values:
                errors.append(str(UnexpectedValueException(row_number, column, allowed_values)))

        return errors


class AthletesCSVValidator(BaseCSVValidator):
    """
    A child class of BaseCSVValidator that validates athlete data files.

    The athlete validator, in addition to need to validate the required columns, column types, and allowed values, it
    also needs to validate:
    - that the athlete codes have the correct format
    - that the birth dates and age columns are submitted in sufficient groups.
    """
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
        """
        Validates that each row is of the correct type and/or not None.

        For required columns, every row in the column must contain a value. For specifically type columns, every row in
        the column must be of the correct type. For columns with specifically allowed values, every row in the column
        must match the allowed values.

        Args:
            row (dict[str, str]): The row to validate.
            row_number (int): The row number of the row (for error reporting).

        Returns:
            list: A list of errors generated during row generation. If there are no errors, an empty list is returned.
        """
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
        """
        Validates that the athlete codes have the correct format.

        The following is the valid pattern for an athlete code and an example:
        - r'^R[A-Z0-9]{{4}}$': R12AB
        
        Args:
            row (dict[str, str]): The row to validate.
            row_number (int): The row number of the row (for error reporting).
            
        Returns:
            list[str]: A list of errors generated during row generation. If there are no errors, an empty list
        """
        errors = []
        value = row.get("athlete_code")

        if value is None or value.strip() == "":
            errors.append(str(RequiredBlankException(row_number, "athlete_code")))
            return errors
        
        if not self.athlete_code_pattern.match(value.strip()):
            errors.append(f"Row {row_number}: column 'athlete_code' must match r'^R[A-Z0-9]{{4}}$', e.g. R12AB")

        return errors
    
    def validate_birth_info_group(self, row: dict[str, str], row_number: int) -> list[str]:
        """
        Validates the birth date and age columns exist in the appropriate groups in the row.

        The following are the valid groups; at least one of these must be satisfied:
            - birth_date is not None and not empty
            - birth_year is not None and not empty
            - age_at_observation and age_logged_at is not None and not empty
        """
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
    """A child class of BaseCSVValidator that validates performance data files."""
    filename = "performances.csv"
    required_columns = {"athlete_code", "date", "session_label", "metric_name", "metric_value"}
    optional_columns = {"metric_unit"}
    numeric_columns = {"metric_value"}
    date_columns = {"date"}
    

class HormonesCSVValidator(BaseCSVValidator):
    """A child class of BaseCSVValidator that validates hormone measurement data files."""
    filename = "hormones.csv"
    required_columns = {"athlete_code", "date", "hormone_name", "measurement_value"}
    optional_columns = {"measurement_unit"}
    numeric_columns = {"measurement_value"}
    date_columns = {"date"}


class SymptomsCSVValidator(BaseCSVValidator):
    """A child class of BaseCSVValidator that validates menstrual symptom data files."""
    filename = "symptoms.csv"
    required_columns = {"athlete_code", "date", "symptom"}
    optional_columns = {"severity", "relative_day_to_cycle"}
    integer_columns = {"relative_day_to_cycle"}
    allowed_values = {"severity": ["MILD", "MODERATE", "SEVERE"]}
    date_columns = {"date"}


class CyclePhasesCSVValidator(BaseCSVValidator):
    """A child class of BaseCSVValidator that validates menstrual cycle phase data files."""
    filename = "cycle_phases.csv"
    required_columns = {"athlete_code", "date", "phase"}
    optional_columns = {"relative_day_to_cycle"}
    integer_columns = {"relative_day_to_cycle"}
    allowed_values = {"phase": ["MENSTRUAL", "FOLLICULAR", "OVULATORY", "LUTEAL"]}
    date_columns = {"date"}


class ValidatorDispatcher:
    """A dispatcher class that takes a file and matches to the appropriate validator subclass."""
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
    """Gets the validator subclass for a given file name."""
    validator_cls = VALIDATOR_MAP.get(file_name)
    if validator_cls is None:
        raise ValueError(f"Unsupported file: {file_name}")
    return validator_cls()


class ValidatorException(Exception):
    """A base exception class for all validators."""
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(message)

class InvalidDateException(ValidatorException):
    """Raised when a date is invalid."""
    def __init__(self, row_number: int, column: str):
        super().__init__(f"Row {row_number}: date column '{column}' is not an accepted format")

class InvalidTypeException(ValidatorException):
    """Raised when a value in a particular column has the wrong type."""
    def __init__(self, row_number: int, column: str, expected_type: str):
        super().__init__(f"Row {row_number}: column '{column}' must be of type '{expected_type}'")

class RequiredBlankException(ValidatorException):
    """Raised when a row in a required column is blank."""
    def __init__(self, row_number: int, column: str):
        super().__init__(f"Row {row_number}: required column '{column}' must not be blank")

class UnexpectedValueException(ValidatorException):
    """Raised when a value in a column that requires specific values is not allowed."""
    def __init__(self, row_number: int, column: str, allowed_values):
        super().__init__(f"Row {row_number}: column '{column}' only allows {allowed_values}")

class InvalidBirthInfoException(ValidatorException):
    """Raised when a birth date or age information is invalid."""
    def __init__(self, row_number: int):
        super().__init__(f"Row {row_number}: at least one of ['birth_date', 'birth_year',"
                        "('age_at_observation', 'age_logged_at')] must be provided")

