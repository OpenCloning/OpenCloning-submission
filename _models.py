from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
from typing import Any, List, Literal, Dict, Optional, Union
from pydantic.version import VERSION as PYDANTIC_VERSION
from pydantic import conlist
from pydantic import conlist

if int(PYDANTIC_VERSION[0]) >= 2:
    from pydantic import BaseModel, ConfigDict, Field, field_validator
else:
    from pydantic import BaseModel, Field, validator

from pydantic import conlist

metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )
    pass


class Category(ConfiguredBaseModel):
    id: str = Field(..., description="""The identifier for the object""")
    title: str = Field(
        ..., description="""A title for the representation of the object"""
    )
    description: Optional[str] = Field(
        None, description="""A description of the object"""
    )
    image: Optional[str] = Field(
        None, description="""File name of an image for the object"""
    )

    @field_validator("image")
    def pattern_image(cls, v):
        pattern = re.compile(r"^[a-zA-Z0-9_\-\.]+\.(png|jpg|jpeg|gif|svg)$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid image format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid image format: {v}")
        return v


class Kit(ConfiguredBaseModel):
    pmid: Optional[str] = Field(None, description="""The PubMed ID for the object""")
    addgene_url: str = Field(..., description="""The Addgene URL for the kit""")
    title: str = Field(
        ..., description="""A title for the representation of the object"""
    )
    description: str = Field(..., description="""A description of the object""")

    @field_validator("pmid")
    def pattern_pmid(cls, v):
        pattern = re.compile(r"^PMID:\d+$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid pmid format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid pmid format: {v}")
        return v

    @field_validator("addgene_url")
    def pattern_addgene_url(cls, v):
        pattern = re.compile(r"^https://www.addgene.org/.+$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid addgene_url format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid addgene_url format: {v}")
        return v


class Sequence(ConfiguredBaseModel):
    name: str = Field(..., description="""The name of a thing""")
    category: str = Field(...)
    description: Optional[str] = Field(
        None, description="""A description of the object"""
    )
    type: Literal["Sequence"] = Field(
        "Sequence", description="""The type of sequence"""
    )


class AddGenePlasmid(Sequence):
    addgene_id: str = Field(..., description="""The Addgene ID for the plasmid""")
    resistance: Optional[str] = Field(None)
    well: Optional[str] = Field(
        None, description="""The well where a plasmid is located in a plate"""
    )
    description: Optional[str] = Field(
        None, description="""A description of the object"""
    )
    name: str = Field(..., description="""The name of a thing""")
    category: str = Field(...)
    type: Literal["AddGenePlasmid"] = Field(
        "AddGenePlasmid", description="""The type of sequence"""
    )

    @field_validator("addgene_id")
    def pattern_addgene_id(cls, v):
        pattern = re.compile(r"^\d+$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid addgene_id format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid addgene_id format: {v}")
        return v


class Submitter(ConfiguredBaseModel):
    full_name: str = Field(
        ...,
        description="""The full name of the submitter, will be ignored if the name can be taken from ORCID""",
    )
    orcid: Optional[str] = Field(None, description="""The ORCID of the submitter""")
    github_username: Optional[str] = Field(
        None, description="""The GitHub username of the submitter"""
    )

    @field_validator("orcid")
    def pattern_orcid(cls, v):
        pattern = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid orcid format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid orcid format: {v}")
        return v

    @field_validator("github_username")
    def pattern_github_username(cls, v):
        pattern = re.compile(r"^[a-zA-Z0-9-]+$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid github_username format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid github_username format: {v}")
        return v


class Oligo(ConfiguredBaseModel):
    name: str = Field(..., description="""The name of a thing""")
    id: Optional[int] = Field(None)
    sequence: str = Field(...)


class OligoPair(Sequence):
    forward_oligo: str = Field(...)
    reverse_oligo: str = Field(...)
    name: str = Field(..., description="""The name of a thing""")
    category: str = Field(...)
    description: Optional[str] = Field(
        None, description="""A description of the object"""
    )
    type: Literal["OligoPair"] = Field(
        "OligoPair", description="""The type of sequence"""
    )


class Assembly(ConfiguredBaseModel):
    title: str = Field(
        ..., description="""A title for the representation of the object"""
    )
    description: Optional[str] = Field(
        None, description="""A description of the object"""
    )
    fragment_order: Optional[List[str]] = Field(default_factory=list)
    template_file: Optional[str] = Field(None)

    @field_validator("template_file")
    def pattern_template_file(cls, v):
        pattern = re.compile(r"^.*.json$")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid template_file format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid template_file format: {v}")
        return v


class Submission(ConfiguredBaseModel):
    submitters: conlist(min_length=1, item_type=Submitter) = Field(default_factory=list)
    kit: Kit = Field(...)
    sequences: conlist(
        min_length=1, item_type=Union[Sequence, AddGenePlasmid, OligoPair]
    ) = Field(default_factory=list)
    categories: conlist(min_length=1, item_type=Category) = Field(default_factory=list)
    assemblies: conlist(min_length=1, item_type=Assembly) = Field(default_factory=list)
    oligos: Optional[List[Oligo]] = Field(default_factory=list)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Category.model_rebuild()
Kit.model_rebuild()
Sequence.model_rebuild()
AddGenePlasmid.model_rebuild()
Submitter.model_rebuild()
Oligo.model_rebuild()
OligoPair.model_rebuild()
Assembly.model_rebuild()
Submission.model_rebuild()
