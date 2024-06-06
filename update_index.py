# Updates index.json, which contains an index of all the submissions

import json
import glob

all_submissions = glob.glob("processed/*/submission.json")
index = {}
for submission in all_submissions:
    with open(submission) as f:
        submission_dict = json.load(f)

    index[submission.split("/")[-2]] = submission_dict["kit"]

with open("index.json", "w") as f:
    json.dump(index, f, indent=2)
