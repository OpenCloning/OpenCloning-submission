import sys
from submission_reader import load_submission_folder
import json
import os

if __name__ == "__main__":
    # Get first argument, else give error
    if len(sys.argv) != 2:
        print("Usage python process_submission.py <submission_folder>")
        sys.exit(0)

    submission_folder = sys.argv[1]
    submission = load_submission_folder(submission_folder)

    # Get the last part of the submission folder
    submission_name = os.path.basename(submission_folder)
    output_folder = os.path.join("processed", submission_name)

    if os.path.exists(output_folder):
        raise Exception("Output folder already exists")
    os.mkdir(output_folder)

    template_dir = os.path.join(output_folder, "templates")
    os.mkdir(template_dir)

    for i, template in enumerate(submission.to_template_list()):
        # Format i as 001, etc.
        ii = str(i + 1).zfill(3)
        assembly_file_name = f"assembly_template_{ii}.json"
        with open(
            os.path.join(output_folder, "templates", assembly_file_name), "w"
        ) as f:
            json.dump(template, f, indent=2)
        submission.assemblies[i].template_file = assembly_file_name

    with open(os.path.join(output_folder, "submission.json"), "w") as f:
        json.dump(submission.model_dump(), f, indent=2)
