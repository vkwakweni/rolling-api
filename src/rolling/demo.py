"""A seeded demonstration of the hormone analysis engine on invented data.

Rolling is built for one study: hormone levels, menstrual cycle phase, dysmenorrhea and cycling performance.
The demonstration therefore covers all of it: six hormones, four cycle phases, five performance types and the menstrual symptoms.

Every value here is generated from a fixed random seed. No real participant data is used or needed.

Run it with `python -m rolling.demo`.
"""
import json
import random
import sys
from datetime import date, timedelta
from uuid import UUID

from rolling.analysis_engine import (
    DescriptiveHormoneAnalysis,
    HormoneAnalysisInput,
    HormoneObservation,
    build_descriptive_hormone_report,
)

SYNTHETIC_NOTICE = "SYNTHETIC DATA: invented from a fixed random seed. Not real participants."

PHASES = ("MENSTRUAL", "FOLLICULAR", "OVULATION", "LUTEAL")
PERFORMANCE_TYPES = ("TRAINING-RECOVERY", "TRAINING-TAPERING", "TRAINING-PREPARATION", "RACE", "OFF SEASON")
SYMPTOMS = ("BREAST TENDERNESS", "ACHES", "HEADACHES", "BLOATING", "SLEEP CHANGES", "MOOD CHANGES")

# The hormones of the study, as in the app's lookup table: name -> (unit, invented mean level per phase).
# The levels are invented for the demonstration and only loosely follow the textbook cycle shape.
HORMONES = {
    "OESTROGEN": ("pg/mL", {"MENSTRUAL": 40.0, "FOLLICULAR": 90.0, "OVULATION": 180.0, "LUTEAL": 120.0}),
    "PROGESTERONE": ("ng/mL", {"MENSTRUAL": 0.6, "FOLLICULAR": 0.8, "OVULATION": 2.0, "LUTEAL": 12.0}),
    "LH": ("IU/L", {"MENSTRUAL": 5.0, "FOLLICULAR": 6.0, "OVULATION": 30.0, "LUTEAL": 5.0}),
    "FSH": ("IU/L", {"MENSTRUAL": 7.0, "FOLLICULAR": 6.0, "OVULATION": 12.0, "LUTEAL": 4.0}),
    "TESTOSTERONE": ("ng/dL", {"MENSTRUAL": 28.0, "FOLLICULAR": 30.0, "OVULATION": 38.0, "LUTEAL": 32.0}),
    "CORTISOL": ("ug/dL", {"MENSTRUAL": 14.0, "FOLLICULAR": 13.0, "OVULATION": 13.5, "LUTEAL": 15.0}),
}
# invented performance metrics: name -> (unit, mean, spread); they ride along with each observation
METRICS = {"AVG POWER": ("W", 210.0, 25.0), "AVG HR": ("BPM", 148.0, 9.0), "DISTANCE": ("KM", 62.0, 18.0)}


def synthetic_observations(seed: int = 2026, participants: int = 8, cycles: int = 3) -> list[HormoneObservation]:
    """Builds invented observations: every hormone in every phase of every cycle for every participant.

    Each observation also carries a performance type and metric, and a menstrual symptom (dysmenorrhea
    is made likelier in the menstrual phase).
    """
    rng = random.Random(seed)
    observations = []
    start = date(2025, 1, 6)
    for p in range(participants):
        participant_id = UUID(int=rng.getrandbits(128), version=4)
        baseline = rng.uniform(0.85, 1.15)
        for c in range(cycles):
            for i, phase in enumerate(PHASES):
                observed_on = start + timedelta(days=28 * c + 7 * i + p)
                performance_type = rng.choice(PERFORMANCE_TYPES)
                metric_name = rng.choice(tuple(METRICS))
                metric_unit, metric_mean, metric_spread = METRICS[metric_name]
                symptom = ("DYSMENORRHEA" if rng.random() < (0.5 if phase == "MENSTRUAL" else 0.1)
                           else rng.choice(SYMPTOMS + (None, None, None)))
                for hormone_name, (unit, means) in HORMONES.items():
                    value = rng.gauss(means[phase] * baseline, means[phase] * 0.15)
                    observations.append(HormoneObservation(
                        athlete_id=participant_id,
                        observed_on=observed_on,
                        hormone_name=hormone_name,
                        measured_value=round(max(value, 0.1), 2),
                        measurement_unit=unit,
                        symptom_name=symptom,
                        cycle_phase=phase,
                        performance_type=performance_type,
                        metric_name=metric_name,
                        metric_value=round(max(rng.gauss(metric_mean, metric_spread), 0.0), 1),
                        metric_unit=metric_unit,
                    ))
    return observations


def run_demo(seed: int = 2026):
    """Runs the descriptive analysis on the synthetic observations. Returns the result and the report."""
    payload = HormoneAnalysisInput(project_id=UUID(int=seed),
                                   observations=synthetic_observations(seed))
    result = DescriptiveHormoneAnalysis().run(payload)
    return result, build_descriptive_hormone_report(result)


def main(argv: list[str]) -> int:
    seed = int(argv[1]) if len(argv) > 1 else 2026
    result, report = run_demo(seed)
    print(SYNTHETIC_NOTICE)
    print(report["report_text"])
    if len(argv) > 2:
        with open(argv[2], "w") as handle:
            json.dump({"notice": SYNTHETIC_NOTICE, "seed": seed, "tables": result.tables}, handle, indent=2, default=str)
        print(f"Tables written to {argv[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
