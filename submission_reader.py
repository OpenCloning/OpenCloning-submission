from pandas import read_excel, NA
from models import Submission
import os


def sheet_reader(file, sheet_name):
    return (
        read_excel(file, sheet_name=sheet_name, dtype=str)
        .fillna(NA)
        .replace([NA], [None])
    )


def read_submission(file) -> Submission:
    plasmids = sheet_reader(file, "Sequence")
    plasmids["type"] = "AddGenePlasmid"
    categories = sheet_reader(file, "Category")
    kits = sheet_reader(file, "Kit")
    oligos = sheet_reader(file, "Oligo")
    oligo_pairs = sheet_reader(file, "OligoPair")
    oligo_pairs["type"] = "OligoPair"

    if len(kits) != 1:
        raise ValueError("There should be only one kit")

    submitters = sheet_reader(file, "Submitter")
    assemblies = sheet_reader(file, "Assembly")
    assemblies["fragment_order"] = assemblies["fragment_order"].apply(
        lambda x: x.split("|")
    )

    return Submission.model_validate(
        {
            "sequences": plasmids.to_dict("records") + oligo_pairs.to_dict("records"),
            "categories": categories.to_dict("records"),
            "kit": kits.to_dict("records")[0],
            "submitters": submitters.to_dict("records"),
            "assemblies": assemblies.to_dict("records"),
            "oligos": oligos.to_dict("records"),
        }
    )


def load_submission_folder(submission_folder):

    if not os.path.exists(submission_folder):
        raise Exception("Submission folder does not exist")
    if not os.path.exists(os.path.join(submission_folder, "submission.xlsx")):
        raise Exception("Submission folder does not contain submission.xlsx")

    files_in_folder = [
        entry.name for entry in os.scandir(submission_folder) if entry.is_file()
    ]

    # Exclude .DS_Store and temp ~$ files
    files_in_folder = [
        file
        for file in files_in_folder
        if (not file.startswith("~$") and file != ".DS_Store")
    ]

    file_extensions = [os.path.splitext(file)[-1] for file in files_in_folder]

    if file_extensions.count(".xlsx") != 1:
        raise Exception("There should be one xlsx file")

    image_files = list()
    for ext, image_file in zip(file_extensions, files_in_folder):
        if ext.lower() not in [".jpeg", ".png", ".svg", ".xlsx"]:
            raise Exception(
                f"Error with {image_file}, only jpeg, png and svg images are allowed"
            )
        if ext.lower() in [".jpeg", ".png", ".svg"]:
            image_files.append(image_file)
    try:
        submission = read_submission(os.path.join(submission_folder, "submission.xlsx"))
    except Exception as e:
        raise e

    submission.validate_images(image_files)
    return submission
