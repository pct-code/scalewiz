"""A function for exporting a representation of a Project as CSV."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Tuple

from pandas import DataFrame

from scalewiz.models.project import Project

LOGGER = logging.getLogger("scalewiz")


def export_csv(project: Project) -> Tuple[int, Path]:
    """Generates a report for a Project in a flattened CSV format (or ugly JSON)."""
    start_time = time.time()
    LOGGER.info("Beginning export of %s", project.name.get())

    output_dict = {
        "customer": project.customer.get(),
        "submitteBy": project.submitted_by.get(),
        "productionCompany": project.client.get(),
        "field": project.field.get(),
        "samplePoint": project.sample.get(),
        "analysisNumbers": project.numbers.get(),
        "dateSampled": project.sample_date.get(),
        "dateReceived": project.received_date.get(),
        "dateCompleted": project.completed_date.get(),
        "testTempF": project.temperature.get(),
        "baselinePsi": project.baseline.get(),
        "bicarbs": project.bicarbs.get(),
        "bicarbsIncreased": project.bicarbs_increased.get(),
        "chlorides": project.chlorides.get(),
        "timeLimitMin": project.limit_minutes.get(),
        "limitPsi": project.limit_psi.get(),
        "name": [],
        "isBlank": [],
        "chemical": [],
        "rate": [],
        "duration": [],
        "maxPsi": [],
        "result": [],
        "clarity": [],
        "plotPath": project.plot.get(),
    }
    # filter the blanks and trials to sort them
    blanks = {
        test
        for test in project.tests
        if test.include_on_report.get() and test.is_blank.get()
    }
    trials = {
        test
        for test in project.tests
        if test.include_on_report.get() and not test.is_blank.get()
    }
    tests = blanks + trials
    # we use lists here instead of sets since sets aren't JSON serializable
    output_dict["name"] = [test.name.get() for test in tests]
    output_dict["isBlank"] = [test.is_blank.get() for test in tests]
    output_dict["chemical"] = [test.chemical.get() for test in tests]
    output_dict["rate"] = [test.rate.get() for test in tests]
    output_dict["duration"] = [
        round(len(test.readings) * project.interval_seconds.get() / 60, 2)
        for test in tests
    ]
    output_dict["maxPsi"] = [test.max_psi.get() for test in tests]
    output_dict["result"] = [test.result.get() for test in tests]
    output_dict["clarity"] = [test.clarity.get() for test in tests]

    fmt = project.output_format.get()
    out = f"{project.numbers.get().replace(' ', '')} {project.name.get()}"
    out = f"{out} - CaCO3 Scale Block Analysis.{fmt}".strip()
    out = Path(Path(project.path.get()).parent).joinpath(out).resolve()

    with out.open("w") as output:
        if fmt == "CSV":
            data = DataFrame.from_dict(output_dict)
            data.to_csv(out, encoding="utf-8")
        elif fmt == "JSON":
            json.dump(output_dict, output, indent=4)

    LOGGER.info(
        "Finished export of %s as %s in %s s",
        project.name.get(),
        project.output_format.get(),
        round(time.time() - start_time, 3),
    )

    if out.is_file:
        return 0, out
    else:
        return 1, out
