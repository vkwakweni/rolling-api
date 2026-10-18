import ast
import pathlib
import unittest

import rolling
from rolling.analysis_engine.utils.statistics_calculator import StatisticsCalculator
from rolling.demo import run_demo, synthetic_observations

ENGINE_DIR = pathlib.Path(rolling.__file__).parent / "analysis_engine"


class TestPublicFrontDoor(unittest.TestCase):
    def test_main_names_are_exported(self):
        for name in ("DescriptiveHormoneAnalysis", "HormoneObservation", "HormoneAnalysisInput",
                     "HormoneAnalysisResult", "AnalysisTable", "build_descriptive_hormone_report",
                     "__version__"):
            self.assertTrue(hasattr(rolling, name), name)

    def test_engine_does_not_import_the_app(self):
        for path in ENGINE_DIR.rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text())):
                modules = []
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    modules = [node.module]
                for module in modules:
                    self.assertFalse(module.startswith("rolling.app"), f"{path} imports {module}")


class TestSmallGroups(unittest.TestCase):
    def test_single_value_group_gives_no_effect_size_or_t(self):
        calculator = StatisticsCalculator()
        self.assertIsNone(calculator.hedges_g([1.0], [2.0, 3.0]))
        self.assertIsNone(calculator.welch_test([1.0], [2.0, 3.0]))

    def test_identical_values_give_no_effect_size(self):
        self.assertIsNone(StatisticsCalculator().hedges_g([2.0, 2.0], [2.0, 2.0]))


class TestSeededDemo(unittest.TestCase):
    def test_same_seed_gives_same_data(self):
        self.assertEqual(synthetic_observations(7), synthetic_observations(7))
        self.assertNotEqual(synthetic_observations(7), synthetic_observations(8))

    def test_demo_runs_and_reports(self):
        result, report = run_demo(2026)
        self.assertGreater(result.summary["total_grouped_row_count"], 0)
        self.assertIn("OESTRADIOL", report["report_text"])
