"""Functions for scoring Tests within a Project.
"""
from __future__ import annotations

import tkinter as tk
from importlib.metadata import version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tkinter.scrolledtext import ScrolledText
    from typing import List

    from scalewiz.models.project import Project
    from scalewiz.models.test import Test

ALT_LIMIT: int = 1000

# flake8: noqa
def score(project: Project, log_widget: ScrolledText = None, *args) -> None:
    """Updates the result for every Test in the Project.

    Accepts event args passed from the tkVar trace.
    """
    # extra unused args may be passed in by tkinter
    log: List[str] = []
    # sort
    blanks: List[Test] = []
    trials: List[Test] = []
    for test in project.tests:
        if test.include_on_report.get():
            if test.is_blank.get():
                blanks.append(test)
            else:
                trials.append(test)
        else:
            if not test.is_blank.get():
                test.result.set(0)
    if len(blanks) < 1:
        log.append("Insufficient data on report to score.")
        log.append(
            "You must select at least one blank and one trial to generate scores."
        )
        to_log(log, log_widget)
        return

    log.append(f"Evaluating results for {project.name.get()}")
    log.append(f"ScaleWiz {version('scalewiz')} DEVELOPMENT\n")
    # time limit
    limit_minutes = project.limit_minutes.get()
    log.append(f"Time limit: {limit_minutes} min")
    # reading interval
    interval_seconds = project.interval_seconds.get()
    log.append(f"Reading interval: {interval_seconds} s")
    # max psi
    limit_psi = project.limit_psi.get()
    log.append(f"Max PSI: {limit_psi:,}")
    log.append(f"ALT PSI: {ALT_LIMIT:,}")
    # max readings
    log.append("Max readings: time limit minutes * 60 s / reading interval s")
    log.append(
        f"Max readings: round({limit_minutes} min * 60 s / {interval_seconds} s)"
    )
    max_readings = round(limit_minutes * 60 / interval_seconds)
    log.append(f"Max readings: {max_readings:,}")
    # baseline area
    log.append("Baseline area: baseline PSI * max readings")
    baseline = project.baseline.get()
    log.append(f"Baseline area: {baseline:,} * {max_readings:,}")
    baseline_area = baseline * max_readings
    log.append(f"Baseline area: {baseline_area:,}")
    # ---
    log.append("-" * 80)
    log.append("")

    # for each blank, find the area over the curve
    areas_over_blanks: List[int] = []
    ALT_AREAS_BLANKS: List[int] = []
    for blank in blanks:
        log.append(f"Evaluating {blank.name.get()}")
        log.append(f"Considering pump data: {blank.pump_to_score.get()}")
        readings = blank.get_readings()
        ALT_READINGS = blank.get_readings(ALT_LIMIT)
        log.append(f"Total readings: {len(readings):,}")
        log.append(f"ALT readings: {len(ALT_READINGS):,}")
        log.append(f"Observed baseline: {blank.observed_baseline.get():,} PSI")
        log.append(f"Project baseline: {baseline} PSI")
        log.append("Integral PSI: sum of all pressure readings")
        int_psi = sum(readings)
        ALT_INT_PSI = sum(ALT_READINGS)
        log.append(f"Integral PSI: {int_psi:,}")
        log.append(f"ALT Integral PSI: {ALT_INT_PSI:,}")
        log.append("Area over blank: limit PSI * # of readings - integral PSI")
        area = limit_psi * len(readings) - int_psi
        ALT_AREA = ALT_LIMIT * len(ALT_READINGS) - ALT_INT_PSI
        log.append(
            f"Area over blank: {limit_psi:,} " f"* {len(readings):,} - {int_psi:,}"
        )
        log.append(f"Area over blank: {area:,}")
        log.append(
            f"ALT Area over blank: {ALT_LIMIT:,} "
            f"* {len(ALT_READINGS):,} - {ALT_INT_PSI:,}"
        )
        log.append(f"ALT Area over blank: {ALT_AREA:,}")
        areas_over_blanks.append(area)
        ALT_AREAS_BLANKS.append(ALT_AREA)
        log.append("-" * 40)
        log.append("")

    # get protectable area
    avg_blank_area = round(sum(areas_over_blanks) / len(areas_over_blanks))
    ALT_AVG_BLANK_AREA = round(sum(ALT_AREAS_BLANKS) / len(ALT_AREAS_BLANKS))
    log.append(f"Average area over blanks: {avg_blank_area:,}")
    log.append(f"ALT Average area over blanks: {ALT_AVG_BLANK_AREA:,}")
    avg_protectable_area = limit_psi * max_readings - avg_blank_area
    ALT_AVG_PROTECT_AREA = ALT_LIMIT * max_readings - avg_blank_area
    log.append(
        "Average protectable area: limit_psi * max_readings - average area over blanks"
    )
    log.append(
        f"Average protectable area: {limit_psi:,} "
        f"* {max_readings:,} - {avg_blank_area:,}"
    )
    log.append(f"Average protectable area: {avg_protectable_area:,}")
    log.append(
        f"ALT Average protectable area: {ALT_LIMIT:,} "
        f"* {max_readings:,} - {ALT_AVG_BLANK_AREA:,}"
    )
    log.append(f"Average protectable area: {ALT_AVG_PROTECT_AREA:,}")
    log.append("-" * 80)
    log.append("")

    # get readings
    for trial in trials:
        log.append(f"Evaluating {trial.name.get()}")
        log.append(f"Considering data: {trial.pump_to_score.get()}")
        readings = trial.get_readings()
        ALT_READINGS = trial.get_readings(ALT_LIMIT)
        log.append(f"Total readings: {len(readings):,} / {max_readings}")
        log.append(f"ALT Total readings: {len(ALT_READINGS):,} / {max_readings}")
        log.append(f"Observed baseline: {trial.observed_baseline.get():,} PSI")
        log.append(f"Project baseline: {baseline} PSI")
        # int psi
        log.append("Integral PSI: sum of all pressure readings")
        int_psi = sum(readings)
        ALT_INT_PSI = sum(ALT_READINGS)
        log.append(f"Integral PSI: {int_psi:,}")
        log.append(f"ALT Integral PSI: {ALT_INT_PSI:,}")
        # failure region
        fail_psi = (max_readings - len(readings)) * limit_psi
        ALT_FAIL_PSI = (max_readings - len(ALT_READINGS)) * ALT_LIMIT
        log.append(f"Failure PSI: (# max readings - # readings) * max PSI")
        log.append(
            f"Failure PSI: ({max_readings:,} - {len(readings):,}) * {limit_psi:,}"
        )
        log.append(f"Failure PSI: {fail_psi:,}")
        log.append(
            f"ALT Failure PSI: ({max_readings:,} - {len(ALT_READINGS):,}) * {ALT_LIMIT:,}"
        )
        log.append(f"ALT Failure PSI: {ALT_FAIL_PSI:,}")

        log.append("")
        log.append(
            "Result: 1 - (integral area + failure area - baseline area) / (avg protectable area - baseline area)"
        )

        result = round(
            1
            - (int_psi + fail_psi - baseline_area)
            / (avg_protectable_area - baseline_area),
            3,
        )
        ALT_RESULT = round(
            1
            - (ALT_INT_PSI + ALT_FAIL_PSI - baseline_area)
            / (ALT_AVG_PROTECT_AREA - baseline_area),
            3,
        )
        log.append(
            f"Result: 1 - ({int_psi:,} + {fail_psi:,} - {baseline_area:,}) / ({avg_protectable_area:,} - {baseline_area:,})"
        )
        log.append(
            f"ALT Result: 1 - ({ALT_INT_PSI:,} + {ALT_FAIL_PSI:,} - {baseline_area:,}) / ({ALT_AVG_PROTECT_AREA:,} - {baseline_area:,})"
        )

        # ---
        log.append("")
        log.append(f"Result: {result:.3f}")
        log.append(f"ALT Result: {ALT_RESULT:.3f}")
        trial.result.set(result)
        trial.result2.set(ALT_RESULT)
        log.append("-" * 40)
        log.append("")

    to_log(log, log_widget)


def to_log(log: list[str], log_widget: ScrolledText) -> None:
    """Adds the passed log messages to the passed Text widget."""
    if isinstance(log_widget, tk.Text) and log_widget.winfo_exists():
        log_widget.configure(state="normal")
        log_widget.delete(1.0, "end")
        for msg in log:
            log_widget.insert("end", "".join((msg, "\n")))
        log_widget.configure(state="disabled")
