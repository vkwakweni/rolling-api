import unittest

from app.services.upload_validation import (PerformanceCSVValidator,
                                            HormonesCSVValidator,
                                            MenstruationSymptomsCSVValidator,
                                            MenstruationPhaseCSVValidator)

# Helper builders
def make_csv_text(headers: list[str], rows: list[list[str]]) -> str:
    lines = [",".join(headers)]
    lines.extend(",".join(row) for row in rows)
    return "\n".join(lines)

# happy-path test TODO check this name
class TestCSVValid(unittest.TestCase): # highest level ones
    def test_performance_csv_valid(self):
        pass

    def test_hormones_csv_valid(self):
        pass

    def test_menstruation_symptom_csv_valid(self):
        pass

    def test_menstruation_phase_csv_valid(self):
        pass

# header validation tests
class TestHeaderValidation(unittest.TestCase):
    def test_missing_required_column_fails(self):
        pass

    def test_unexpected_column_fails(self):
        pass

# type validation tests
class TestTypeValidation(unittest.TestCase):
    def test_invalid_date_fails(self):
        pass

    def test_invalid_numeric_fails(self):
        pass

    def test_invalid_integer_fails(self):
        pass

# allowed values tests
class TestAllowedValues(unittest.TestCase):
    def test_invalid_severity_fails(self):
        pass

    def test_invalid_phase_fails(self):
        pass

# blank handling test
class TestBlankHandling(unittest.TestCase):
    def test_blank_required_value_fails(self):
        pass

