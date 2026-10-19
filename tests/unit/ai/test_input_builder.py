import unittest

from rolling.app.services.ai.input_builder import AIInputBuilder

class TestInputBuilder(unittest.TestCase):
    input_builder = AIInputBuilder()

    def test_whitelisted_keys_are_kept_and_other_keys_dropped(self):
        tables = [{"name": "hormone_phase_statistics",
                   "rows": [{"hormone_name": "OESTROGEN",
                             "cycle_phase": "LUTEAL",
                             "measured_values": [1.0, 2.0, 3.0],
                             "observation_count": 3,
                             "mean": 2.0,
                             "standard_deviation": 1.0}]}]

        redacted = self.input_builder.get_whitelisted_keys_from_tables(tables)

        self.assertEqual(redacted[0]["name"], "hormone_phase_statistics")
        self.assertEqual(redacted[0]["rows"],
                         [{"hormone_name": "OESTROGEN",
                           "observation_count": 3,
                           "mean": 2.0,
                           "standard_deviation": 1.0}])

    def test_raw_measured_values_never_reach_the_output(self):
        tables = [{"name": "hormone_statistics",
                   "rows": [{"hormone_name": "CORTISOL", "measured_values": [9.9], "mean": 9.9}]}]

        redacted = self.input_builder.get_whitelisted_keys_from_tables(tables)

        self.assertNotIn("measured_values", redacted[0]["rows"][0])
        self.assertNotIn([9.9], redacted[0]["rows"][0].values())

    def test_every_row_is_kept(self):
        tables = [{"name": "hormone_statistics",
                   "rows": [{"hormone_name": "LH", "mean": 1.0},
                            {"hormone_name": "FSH", "mean": 2.0}]}]

        redacted = self.input_builder.get_whitelisted_keys_from_tables(tables)

        self.assertEqual([row["hormone_name"] for row in redacted[0]["rows"]], ["LH", "FSH"])
