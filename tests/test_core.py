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

"""
Tests for the core module.

Note that full comparison tests are performed in both directions, i.e., A -> B and B -> A.
"""

from contextlib import nullcontext as does_not_raise

import pytest

from ncompare.core import compare

from . import data_for_tests_dir


def compare_ab(a, b):
    with does_not_raise():
        compare(a, b)


def compare_ba(a, b):
    with does_not_raise():
        compare(b, a)


def test_no_error_compare(ds_3dims_2vars_4coords, ds_4dims_3vars_5coords):
    compare_ab(ds_3dims_2vars_4coords, ds_4dims_3vars_5coords)
    compare_ba(ds_3dims_2vars_4coords, ds_4dims_3vars_5coords)


def test_no_error_compare_0to1group(ds_3dims_2vars_4coords, ds_3dims_3vars_4coords_1group):
    compare_ab(ds_3dims_2vars_4coords, ds_3dims_3vars_4coords_1group)
    compare_ba(ds_3dims_2vars_4coords, ds_3dims_3vars_4coords_1group)


def test_no_error_compare_1to2groups(ds_3dims_3vars_4coords_1group, ds_3dims_3vars_4coords_2groups):
    compare_ab(ds_3dims_3vars_4coords_1group, ds_3dims_3vars_4coords_2groups)
    compare_ba(ds_3dims_3vars_4coords_1group, ds_3dims_3vars_4coords_2groups)


def test_no_error_compare_2groupsTo1Subgroup(
    ds_3dims_3vars_4coords_2groups, ds_3dims_3vars_4coords_1subgroup
):
    compare_ab(ds_3dims_3vars_4coords_2groups, ds_3dims_3vars_4coords_1subgroup)
    compare_ba(ds_3dims_3vars_4coords_2groups, ds_3dims_3vars_4coords_1subgroup)


def test_zero_for_comparison_with_no_differences(ds_3dims_3vars_4coords_1subgroup):
    assert compare(ds_3dims_3vars_4coords_1subgroup, ds_3dims_3vars_4coords_1subgroup) == 0


def test_icesat(temp_data_dir):
    # Compare the `ncompare` output when testing ICESat
    out_path = temp_data_dir / "output_file_icesat-2-atl06.txt"

    num_differences = compare(
        data_for_tests_dir / "icesat-2-ATL06" / "ATL06_20230816161508_08782002_006_02.h5",
        data_for_tests_dir / "icesat-2-ATL06" / "ATL06_20230816234629_08822013_006_01.h5",
        show_chunks=True,
        show_attributes=True,
        file_text=str(out_path),
    )

    assert num_differences == 5280


def test_error_on_different_file_types(temp_data_dir):
    file1 = data_for_tests_dir / "icesat-2-ATL06" / "ATL06_20230816161508_08782002_006_02.h5"
    file2 = data_for_tests_dir / "test_a.nc"

    with pytest.raises(TypeError):
        compare(file1, file2)
