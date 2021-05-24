"""Functions for scoring Tests within a Project.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tkinter.scrolledtext import ScrolledText
    from typing import List

    from scalewiz.models.project import Project


def score(project: Project, log_widget: ScrolledText, *args) -> None:
    """Updates the result for every Test in the Project.

    Accepts event args passed from the tkVar trace.
    """
    # extra unused args are passed in by tkinter
    log: List[str] = []
    # scoring props
    limit_minutes = project.limit_minutes.get()
    interval_seconds = project.interval_seconds.get()
    max_readings = round(limit_minutes * 60 / interval_seconds)
    log.append("Max readings: limitMin * 60 / reading interval")
    log.append(f"Max readings: {max_readings}")
    baseline_area = round(project.baseline.get() * max_readings)
    log.append("Baseline area: baseline PSI * max readings")
    log.append(f"Baseline area: {project.baseline.get()} * {max_readings}")
    log.append(f"Baseline area: {baseline_area}")
    log.append("-" * 80)
    log.append("")

    # select the blanks
    blanks = []
    for test in project.tests:
        if test.is_blank.get() and test.include_on_report.get():
            blanks.append(test)
    if len(blanks) < 1:
        return

    areas_over_blanks = []
    for blank in blanks:
        log.append(f"Evaluating {blank.name.get()}")
        log.append(f"Considering data: {blank.pump_to_score.get()}")
        readings = blank.get_readings()
        log.append(f"Total readings: {len(readings)}")
        log.append(f"Observed baseline: {blank.observed_baseline.get()} psi")
        int_psi = sum(readings)
        log.append("Integral PSI: sum of all pressure readings")
        log.append(f"Integral PSI: {int_psi}")
        area = project.limit_psi.get() * len(readings) - int_psi
        log.append("Area over blank: limit_psi * # of readings - integral PSI")
        log.append(
            f"Area over blank: {project.limit_psi.get()} "
            f"* {len(readings)} - {int_psi}"
        )
        log.append(f"Area over blank: {area}")
        log.append("")
        areas_over_blanks.append(area)

    # get protectable area
    avg_blank_area = round(sum(areas_over_blanks) / len(areas_over_blanks))
    log.append(f"Avg. area over blanks: {avg_blank_area}")
    avg_protectable_area = project.limit_psi.get() * max_readings - avg_blank_area
    log.append(
        "Avg. protectable area: limit_psi * max_readings - avg. area over blanks"
    )
    log.append(
        f"Avg. protectable area: {project.limit_psi.get()} "
        f"* {max_readings} - {avg_blank_area}"
    )
    log.append(f"Avg. protectable area: {avg_protectable_area}")
    log.append("-" * 80)
    log.append("")

    # select trials
    trials = []
    for test in project.tests:
        if not test.is_blank.get():
            trials.append(test)

    # get readings
    for trial in trials:
        log.append(f"Evaluating {trial.name.get()}")
        log.append(f"Considering data: {trial.pump_to_score.get()}")
        readings = trial.get_readings()
        log.append(f"Total readings: {len(readings)}")
        log.append(f"Observed baseline: {trial.observed_baseline.get()} psi")
        int_psi = sum(readings) + (
            (max_readings - len(readings)) * project.limit_psi.get()
        )
        log.append("Integral PSI: sum of all pressure readings")
        log.append(f"Integral PSI: {int_psi}")
        result = round(1 - (int_psi - baseline_area) / avg_protectable_area, 3)
        log.append("Result: 1 - (integral PSI - baseline area) / avg protectable area")
        log.append(
            f"Result: 1 - ({int_psi} - {baseline_area}) / {avg_protectable_area}"
        )
        log.append(f"Result: {result} \n")
        trial.result.set(f"{result:.2f}")

    log.insert(0, f"Evaluating results for {project.name.get()}...")
    to_log(log, log_widget)


def to_log(log: list[str], log_widget: ScrolledText) -> None:
    """Adds the passed log message to the Text widget in the Calculations frame."""
    if log_widget.winfo_exists():
        log_widget.configure(state="normal")
        log_widget.delete(1.0, "end")
        for msg in log:
            log_widget.insert("end", "".join((msg, "\n")))
        log_widget.configure(state="disabled")
