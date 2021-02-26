import json
import logging
import os
import time

from pandas import DataFrame

from pct_scalewiz.models.project import Project

logger = logging.getLogger("scalewiz")


def export_csv(project: Project) -> None:
    """Generates a report for the passed Project in a flattened CSV format (or ugly JSON)."""
    start_time = time.time()
    logger.info(f"Beginning export of {project.name.get()}")

    output_dict = {
        "customer": project.customer.get(),
        "submitted by": project.submitted_by.get(),
        "prod. co": project.productionCo.get(),
        "field": project.field.get(),
        "sample point": project.sample.get(),
        "analysis nos.": project.numbers.get(),
        "date sampled": project.sample_date.get(),
        "date received": project.recDate.get(),
        "date completed": project.compDate.get(),
        "test temp F": project.temperature.get(),
        "baseline psi": project.baseline.get(),
        "bicarbs": project.bicarbs.get(),
        "bicarbs increase": project.bicarbsIncreased.get(),
        "chlorides": project.chlorides.get(),
        "time limit min": project.limitMin.get(),
        "limit psi": project.limitPSI.get(),
        "name": [],
        "isBlank": [],
        "chemical": [],
        "rate": [],
        "duration": [],
        "max psi": [],
        "result": [],
        "clarity": [],
        "plot_path": project.plot.get(),
    }

    blanks = [
        test for test in project.tests if test.includeOnRep.get() and test.isBlank.get()
    ]
    trials = [
        test
        for test in project.tests
        if test.includeOnRep.get() and not test.isBlank.get()
    ]
    tests = blanks + trials

    output_dict["name"] = [test.name.get() for test in tests]
    output_dict["isBlank"] = [test.isBlank.get() for test in tests]
    output_dict["chemical"] = [test.chemical.get() for test in tests]
    output_dict["rate"] = [test.rate.get() for test in tests]
    output_dict["duration"] = [
        round(len(test.readings) * project.interval.get() / 60, 2) for test in tests
    ]
    output_dict["max psi"] = [test.maxPSI.get() for test in tests]
    output_dict["result"] = [test.result.get() for test in tests]
    output_dict["clarity"] = [test.clarity.get() for test in tests]

    pre = f"{project.numbers.get().replace(' ', '')} {project.name.get()}"
    out = f"{pre} - CaCO3 Scale Block Analysis.{project.output_format.get()}"
    out = os.path.join(os.path.dirname(project.path.get()), out)

    with open(out, "w") as output:
        if project.output_format.get() == "CSV":
            df = DataFrame.from_dict(output_dict)
            df.to_csv(out, encoding="utf-8")
        elif project.output_format.get() == "JSON":
            json.dump(output_dict, output, indent=4)

    logger.info(
        f"Finished export of {project.name.get()} as {project.output_format.get()} in {round(time.time() - start_time, 3)} s"
    )
