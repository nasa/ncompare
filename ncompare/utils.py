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
from typing import Union


def ensure_valid_path_exists(should_be_path: Union[str, Path]) -> Path:
    """Coerce input to a pathlib.Path and check that the resulting filepath exists."""
    path_obj = _coerce_str_or_path_to_path(should_be_path)
    if path_obj.exists():
        return path_obj
    raise FileNotFoundError("Expected file does not exist: " + str(should_be_path))


def ensure_valid_path_with_suffix(should_be_path: Union[str, Path], suffix: str) -> Path:
    """Coerce input to a pathlib.Path with given suffix."""
    path_obj = _coerce_str_or_path_to_path(should_be_path)
    return path_obj.with_suffix(suffix)


def coerce_to_str(some_object: Union[str, int, tuple]):
    """Ensure the type is a string."""
    if isinstance(some_object, str):
        return some_object
    if isinstance(some_object, int):
        return str(some_object)
    if isinstance(some_object, tuple):
        return str(some_object)

    raise TypeError(f"Unable to coerce value to str. Unexpected type <{type(some_object)}>.")


def _coerce_str_or_path_to_path(should_be_path: Union[Path, str]) -> Path:
    wrong_type_msg = "Unexpected type for something that should be convertable to a Path: "
    if isinstance(should_be_path, str):
        return Path(should_be_path)
    elif isinstance(should_be_path, Path):
        return should_be_path
    else:
        raise TypeError(wrong_type_msg + str(type(should_be_path)))
