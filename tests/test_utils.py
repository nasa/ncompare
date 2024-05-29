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

from pathlib import Path

import pytest

from ncompare.utils import coerce_to_str, ensure_valid_path_exists


def test_make_valid_path_with_simple_invalid_str_path():
    with pytest.raises(FileNotFoundError):
        ensure_valid_path_exists("whereisthatfile")


def test_make_valid_path_with_close_invalid_Path_path():
    with pytest.raises(FileNotFoundError):
        ensure_valid_path_exists(Path(__file__).parents[0].resolve() / "thisdoesntexist.py")


def test_make_valid_path_from_str_in_repo():
    returnval = ensure_valid_path_exists(str(Path(__file__).parents[0].resolve() / "conftest.py"))
    assert isinstance(returnval, Path)


def test_make_valid_path_from_Path_in_repo():
    returnval = ensure_valid_path_exists(Path(__file__).parents[0].resolve() / "conftest.py")
    assert isinstance(returnval, Path)


def test_coerce_int_to_str():
    assert coerce_to_str(5) == "5"


def test_coerce_tuple_to_str():
    assert coerce_to_str(('step', 123)) == "('step', 123)"
