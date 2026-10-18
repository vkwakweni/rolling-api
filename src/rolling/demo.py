"""A seeded demonstration of the analysis engine on invented data.

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
PERFORMANCE_TYPES = ("TRAINING-PREPARATION", "RACE", "OFF SEASON")
# invented mean level per phase (pg/mL) for the demonstration only
PHASE_MEANS = {"MENSTRUAL": 40.0, "FOLLICULAR": 90.0, "OVULATION": 180.0, "LUTEAL": 120.0}


def synthetic_observations(seed: int = 2026, participants: int = 8, cycles: int = 3) -> list[HormoneObservation]:
    """Builds invented oestradiol observations, one per phase per cycle per participant."""
    rng = random.Random(seed)
    observations = []
    start = date(2025, 1, 6)
    for p in range(participants):
        participant_id = UUID(int=rng.getrandbits(128), version=4)
        baseline = rng.uniform(0.85, 1.15)
        for c in range(cycles):
            for i, phase in enumerate(PHASES):
                observed_on = start + timedelta(days=28 * c + 7 * i + p)
                value = rng.gauss(PHASE_MEANS[phase] * baseline, 15.0)
                observations.append(HormoneObservation(
                    athlete_id=participant_id,
                    observed_on=observed_on,
                    hormone_name="OESTRADIOL",
                    measured_value=round(max(value, 1.0), 1),
                    measurement_unit="pg/mL",
                    symptom_name="DYSMENORRHEA" if rng.random() < (0.5 if phase == "MENSTRUAL" else 0.1) else None,
                    cycle_phase=phase,
                    performance_type=rng.choice(PERFORMANCE_TYPES),
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
