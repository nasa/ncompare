from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypedDict, Union

VarProperties = namedtuple(
    "VarProperties", "varname, variable, dtype, dimensions, shape, chunking, attributes"
)

GroupPair = namedtuple(
    "GroupPair",
    "group_a_name group_a group_b_name group_b",
    defaults=("", None, "", None),
)

valid_file_type_ids = Literal["netcdf", "hdf5"]


@dataclass
class FileToCompare:
    path: Union[Path, str]
    type: valid_file_type_ids = "netcdf"

    def __post_init__(self):
        # We'll validate the inputs here.
        if not isinstance(self.path, (str, Path)):
            raise ValueError(f"'path' must be a str or Path, was {type(self.path)}")
        if self.type not in ("netcdf", "hdf5"):
            raise ValueError("'type' must be either 'netcdf' or 'hdf5'")

    def __str__(self):
        return f"path: {self.path} is considered a {self.type} file"


class SummaryDifferencesDict(TypedDict):
    shared: int
    left: int
    right: int
    both: int
    difference_types: set
