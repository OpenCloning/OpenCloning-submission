from _models import (
    Sequence as _Sequence,
    Submission as _Submission,
    Category as _Category,
    Assembly as _Assembly,
    Submitter as _Submitter,
    Kit as _Kit,
)
from pydantic import (
    ConfigDict,
    field_validator,
    model_validator,
    conlist,
    Field,
    BaseModel,
)
import requests
import annotated_types
from typing import Annotated
from github import Github, Auth
import os


# TODO: validation of categories in sequences and assemblies
# TODO: validate images
# TODO: allow specify enzyme and whether it is or not a Golden Gate assembly


class Submitter(_Submitter):
    # Extra validation that ORCID number exists
    @field_validator("orcid")
    def validate_orcid_exists(cls, v):
        if v is not None:
            resp = requests.get(f"https://pub.orcid.org/v3.0/{v}")
            if resp.status_code != 200:
                print(resp.json())
                raise ValueError(f"ORCID {v} does not exist")
        return v

    @field_validator("github_username")
    def validate_github_username_exists(cls, v):
        if v is not None:
            token = os.getenv("GITHUB_TOKEN")
            if token is None:
                raise ValueError(
                    "Backend github authentication not working, contact admin"
                )
            auth = Auth.Token(token)
            g = Github(auth=auth)
            try:
                g.get_user(v)
            except Exception as e:
                print(e)
                raise ValueError(f"Github username {v} does not exist")
        return v


class Sequence(_Sequence):
    """Allow extra fields and custom model dump"""

    model_config = ConfigDict(extra="allow")

    def to_source_option(self):
        info = dict()
        # All fields that are not part of the source
        for k, v in self.model_dump().items():
            # Drop category
            if k == "category":
                continue
            if k not in ["addgene_id"]:
                info[k] = v
        if self.description:
            option_name = f"{self.description} - {self.plasmid_name}"
        else:
            option_name = self.plasmid_name
        return {
            "name": option_name,
            "source": {
                "type": "AddGeneIdSource",
                "repository_name": "addgene",
                "repository_id": self.addgene_id,
            },
            "info": info,
        }


class Category(_Category):
    def to_source(self, source_id: int, options: list[Sequence]):
        return {
            "id": source_id,
            "input": [],
            "output": source_id + 1,
            "type": "CollectionSource",
            "category_id": self.id,
            "title": self.title,
            "description": self.description,
            "image": self.image,
            "options": [s.to_source_option() for s in options if s.category == self.id],
        }


class Assembly(_Assembly):

    def to_template(self, categories: list[Category], sequences: list[Sequence]):
        sources = list()
        dummy_sequences = list()
        source_id = 1
        final_assembly_inputs = list()
        for category_id in self.fragment_order:

            # A category-derived source
            if category_id:
                category = next(c for c in categories if c.id == category_id)
                sources.append(category.to_source(source_id, sequences))
            # An empty slot
            else:
                sources.append(
                    {
                        "id": source_id,
                        "input": [],
                        "output": source_id + 1,
                    }
                )
            final_assembly_inputs.append(source_id + 1)
            dummy_sequences.append({"id": source_id + 1, "type": "TemplateSequence"})
            source_id += 2

        sources.append(
            {
                "id": source_id,
                "input": final_assembly_inputs,
                "output": source_id + 1,
                "type": "RestrictionAndLigationSource",
            }
        )
        dummy_sequences.append(
            {
                "id": source_id + 1,
                "type": "TemplateSequence",
            }
        )

        return {
            "sources": sources,
            "sequences": dummy_sequences,
            "description": f"{self.title}\n\n{self.description}",
        }


class Kit(_Kit):

    @field_validator("addgene_url")
    def validate_addgene_url(cls, v: str):
        resp = requests.get(v)
        if resp.status_code != 200:
            print(resp)
            raise ValueError(f"Addgene URL {v} does not exist")
        return v

    @field_validator("pmid")
    def validate_pmid_exists(cls, v: str):
        if v is None:
            return v
        id_only = v.split(":")[1]
        resp = requests.get(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id={id_only}"
        )
        if len(resp.json()["result"]["uids"]) == 0:
            print(resp.json())
            raise ValueError(f"PMID {v} does not exist")
        return v


# def ref_check(targets, ids, ref, ref_name):
#     for t, id in zip(targets, ids):
#         if t not in ref:
#             raise ValueError(f"error in {id} - {ref_name} {t} not in: {ref}")


class Submission(_Submission):
    """Allow extra fields and custom model dump"""

    submitters: Annotated[list[Submitter], annotated_types.Len(min_length=1)] = Field(
        default_factory=list
    )
    kit: Kit = Field(...)
    sequences: Annotated[list[Sequence], annotated_types.Len(min_length=1)] = Field(
        default_factory=list
    )
    categories: Annotated[list[Category], annotated_types.Len(min_length=1)] = Field(
        default_factory=list
    )
    assemblies: Annotated[list[Assembly], annotated_types.Len(min_length=1)] = Field(
        default_factory=list
    )

    def to_template_list(self):
        return [
            a.to_template(self.categories, self.sequences)
            for i, a in enumerate(self.assemblies)
        ]

    @model_validator(mode="after")
    def validate_referencial_integrity(self):
        category_ids = [c.id for c in self.categories]
        # Check that all categories in assemblies are in categories
        for a in self.assemblies:
            for c in a.fragment_order:
                # c can be empty if it represents an empty lane
                if c and c not in category_ids:
                    raise ValueError(
                        f'Error in assembly "{a.title}", category "{c}" not in categories'
                    )

        for s in self.sequences:
            if s.category not in category_ids:
                raise ValueError(
                    f'Error in plasmid {s.plasmid_name} / {s.addgene_id}, "{s.category}" not in categories'
                )

        return self

    def validate_images(self, image_list):
        for c in self.categories:
            if c.image and c.image not in image_list:
                raise ValueError(
                    f'Error in category "{c.title}", image {c.image} not included in submission'
                )
        for ima in image_list:
            if ima not in [c.image for c in self.categories]:
                raise ValueError(f"Error in image {ima}, not included in any category")


class SuccessResponse(BaseModel):
    pull_request_url: str
