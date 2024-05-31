from pandas import read_excel, NA
from models import Submission


def sheet_reader(file, sheet_name):

    return (
        read_excel(file, sheet_name=sheet_name, dtype=str)
        .fillna(NA)
        .replace([NA], [None])
    )


def read_submission(file) -> Submission:
    sequences = sheet_reader(file, "Sequence")
    categories = sheet_reader(file, "Category")
    kits = sheet_reader(file, "Kit")

    if len(kits) != 1:
        raise ValueError("There should be only one kit")

    submitters = sheet_reader(file, "Submitter")
    assemblies = sheet_reader(file, "Assembly")
    assemblies["fragment_order"] = assemblies["fragment_order"].apply(
        lambda x: x.split("|")
    )

    return Submission.model_validate(
        {
            "sequences": sequences.to_dict("records"),
            "categories": categories.to_dict("records"),
            "kit": kits.to_dict("records")[0],
            "submitters": submitters.to_dict("records"),
            "assemblies": assemblies.to_dict("records"),
        }
    )


if __name__ == "__main__":
    submission = read_submission("test_join.xlsx")
