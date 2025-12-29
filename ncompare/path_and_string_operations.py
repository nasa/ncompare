# Copyright 2024 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software calls the following third-party software,
# which is subject to the terms and conditions of its licensor, as applicable.
# Users must license their own copies; the links are provided for convenience only.
#
# colorama - BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause
# netCDF4 - MIT License - https://opensource.org/licenses/MIT
# numpy - BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause
# openpyxl - MIT License - https://opensource.org/licenses/MIT
# xarray - Apache License, version 2.0 - https://www.apache.org/licenses/LICENSE-2.0
# Python Standard Library - Python Software Foundation (PSF) License Agreement-
#   https://docs.python.org/3/license.html#psf-license
#
# The ncompare: NetCDF structural comparison tool platform is licensed under the
# Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Helper utilities."""

from pathlib import Path

from ncompare.utility_types import FileToCompare, valid_file_type_ids


def ensure_valid_path_exists(should_be_path: str | Path) -> Path:
    """Coerce input to a pathlib.Path and check that the resulting filepath exists."""
    path_obj = Path(should_be_path)
    if path_obj.exists():
        return path_obj
    raise FileNotFoundError(f"Expected file does not exist: {should_be_path}")


def ensure_valid_path_with_suffix(should_be_path: str | Path, suffix: str) -> Path:
    """Coerce input to a pathlib.Path with given suffix."""
    if not suffix.startswith("."):
        raise ValueError(f"Invalid suffix: {suffix}. It must start with '.'")
    return Path(should_be_path).with_suffix(suffix)


def coerce_to_str(some_object: str | int | tuple) -> str:
    """Ensure the type is a string."""
    if isinstance(some_object, (str, int, tuple)):
        return str(some_object)
    raise TypeError(f"Unable to coerce value to str. Unexpected type <{type(some_object)}>.")


def validate_file_type(file_path: Path) -> FileToCompare:
    """Validate a file type and return a FileToCompare instance."""
    if file_path.suffix.lower() in (".h5", ".hdf5", ".he5"):
        file_type: valid_file_type_ids = "hdf5"
    elif file_path.suffix.lower() in (".nc", ".nc4", ".nc3"):
        file_type = "netcdf"
    else:
        raise TypeError(
            f"{file_path.suffix} is not a valid file type. "
            f"Expected a netcdf ('.nc', '.nc4', '.nc3') or "
            f"hdf5 ('.h5', '.hdf5', '.he5)."
        )

    return FileToCompare(path=file_path, type=file_type)
