# Copyright 2024 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software calls the following third-party software,
# which is subject to the terms and conditions of its licensor, as applicable.
# Users must license their own copies; the links are provided for convenience only.
#
# dask - https://github.com/dask/dask/blob/main/LICENSE.txt
# netCDF4 - https://github.com/Unidata/netcdf4-python/blob/master/LICENSE
# numpy - https://github.com/numpy/numpy/blob/main/LICENSE.txt
# xarray - https://github.com/pydata/xarray/blob/main/LICENSE
# Python Standard Library - https://docs.python.org/3/license.html#psf-license
#
# The STITCHEE: STITCH by Extending a dimEnsion platform is licensed under the
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
    """Convert input to a pathlib.Path and check that the resulting filepath exists."""
    fails_to_exist_msg = "Expected file does not exist: "
    wrong_type_msg = "Unexpected type for something that should be convertable to a Path: "

    if isinstance(should_be_path, str):
        # Convert to a Path object
        path_obj = Path(should_be_path)
        if path_obj.exists():
            return path_obj
        raise FileNotFoundError(fails_to_exist_msg + str(should_be_path))

    if isinstance(should_be_path, Path):
        if should_be_path.exists():
            return should_be_path
        raise FileNotFoundError(fails_to_exist_msg + str(should_be_path))

    raise TypeError(wrong_type_msg + str(type(should_be_path)))


def ensure_valid_path_with_suffix(should_be_path: Union[str, Path], suffix: str) -> Path:
    """Coerce input to a pathlib.Path with given suffix."""
    wrong_type_msg = "Unexpected type for something that should be convertable to a Path: "

    if isinstance(should_be_path, str):
        path_obj = Path(should_be_path)
    elif isinstance(should_be_path, Path):
        path_obj = should_be_path
    else:
        raise TypeError(wrong_type_msg + str(type(should_be_path)))

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
