# Updates index.json, which contains an index of all the submissions

import json
import glob

all_submissions = glob.glob("processed/*/submission.json")
index = {}
for submission in all_submissions:
    with open(submission) as f:
        submission_dict = json.load(f)

    submission_folder = submission.split("/")[-2]
    index[submission_folder] = dict()
    index[submission_folder]["kit"] = submission_dict["kit"]
    index[submission_folder]["assemblies"] = submission_dict["assemblies"]

with open("index.json", "w") as f:
    json.dump(index, f, indent=2)
