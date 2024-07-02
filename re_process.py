from process_submission import main as process_submission
import glob
import os
import json
from copy import deepcopy

submission_folders = [d for d in glob.glob("submissions/*") if os.path.isdir(d)]

for submission_folder in submission_folders:
    # Delete the old processed folder
    processed_folder = os.path.join("processed", os.path.basename(submission_folder))
    if os.path.exists(processed_folder):
        print(f"Deleting old processed folder: {processed_folder}")
        os.system(f"rm -rf {processed_folder}")
    process_submission(submission_folder)

# Extra stuff, such as merging kits that are extensions
# merge cidar assembly_template_001.json with cidar extension assembly_template_001.json

base_path = "processed/kits-densmore-cidar-moclo/templates/assembly_template_001.json"
extension_path = (
    "processed/kits-murray-cidar-moclo-v1/templates/assembly_template_001.json"
)

with open(base_path, "r") as f:
    template_base = json.load(f)
with open(extension_path, "r") as f:
    template_extension = json.load(f)

mappings = (
    ("promoter_AB", "promoter"),
    ("RBS_BC", "five_utr"),
    ("CDS_CD", "cds"),
    ("terminator_DE", "terminator"),
)


for old_category, new_category in mappings:
    source_old = next(
        s for s in template_base["sources"] if s["category_id"] == old_category
    )
    source_new = next(
        s for s in template_extension["sources"] if s["category_id"] == new_category
    )
    old_options = deepcopy(source_old["options"])
    for option in old_options:
        option["info"]["well"] = "Base CIDAR Kit " + option["info"]["well"]
    source_new["options"].extend(old_options)

with open(extension_path, "w") as f:
    json.dump(template_extension, f, indent=2)
