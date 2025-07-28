from process_submission import main as process_submission
import glob
import os
import json
from copy import deepcopy
from opencloning.pydantic_models import (
    BaseCloningStrategy as CloningStrategy,
    HomologousRecombinationSource,
    GenomeCoordinatesSource,
    SourceInput,
)
from opencloning_linkml.datamodel.models import TemplateSequence

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


## Add Homologous Recombination to K. phaffi kit
files = [
    "processed/kits-gasser-goldenpics/templates/assembly_template_001.json",
    "processed/kits-gasser-goldenpics/templates/assembly_template_003.json",
]

for file in files:
    with open(file, "r") as f:
        template = json.load(f)
    cs = CloningStrategy.model_validate(template)
    restriction_source = next(
        s for s in cs.sources if s.type == "RestrictionAndLigationSource"
    )

    genome_source = GenomeCoordinatesSource(
        id=0,
        assembly_accession="GCA_900235035.2",
        sequence_accession="LT962479.2",
        locus_tag="BQ9382_C4-0695",
        start=1237975,
        end=241966,
        strand=1,
    )

    cs.add_source_and_sequence(genome_source, TemplateSequence(circular=False, id=0))

    hom_rec = HomologousRecombinationSource(
        id=0,
        input=[
            SourceInput(sequence=genome_source.id),
            SourceInput(sequence=restriction_source.id),
        ],
    )
    cs.add_source_and_sequence(hom_rec, TemplateSequence(circular=False, id=0))

    with open(file, "w") as f:
        json.dump(cs.model_dump(), f, indent=2)

with open(extension_path, "w") as f:
    json.dump(template_extension, f, indent=2)
