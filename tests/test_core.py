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
import xarray as xr

from ncompare.core import _get_vars, _match_random_value, _print_sample_values, compare


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


def test_matching_random_values(
    ds_3dims_2vars_4coords,
    ds_4dims_3vars_5coords,
    ds_3dims_3vars_4coords_1group,
    outputter_to_console,
):
    variable_array_1 = xr.open_dataset(ds_3dims_2vars_4coords).variables['z1']
    variable_array_2 = xr.open_dataset(ds_4dims_3vars_5coords).variables['z1']

    assert (
        _match_random_value(
            outputter_to_console,
            variable_array_1,
            variable_array_1,
        )
        is True
    )
    assert (
        _match_random_value(
            outputter_to_console,
            variable_array_1,
            variable_array_2,
        )
        is False
    )


def test_print_values_runs_with_no_error(ds_3dims_3vars_4coords_1group, outputter_to_console):
    with does_not_raise():
        _print_sample_values(
            outputter_to_console, ds_3dims_3vars_4coords_1group, groupname="Group1", varname="step"
        )


def test_print_values_to_text_file_runs_with_no_error(
    ds_3dims_3vars_4coords_1group, outputter_to_text_file, temp_test_text_file_path
):
    _print_sample_values(
        outputter_to_text_file, ds_3dims_3vars_4coords_1group, groupname="Group1", varname="step"
    )
    outputter_to_text_file._text_file_obj.close()

    comparison_variable = xr.open_dataset(
        ds_3dims_3vars_4coords_1group, backend_kwargs={"group": "Group1"}
    )["step"]

    with open(temp_test_text_file_path) as f:
        lines = f.readlines()
        assert lines[0].strip().replace("[", "").replace("]", "").split() == [
            str(round(x, 1)) for x in comparison_variable[:].values
        ]


def test_comparison_group_no_error_for_duplicate_dataset(
    ds_3dims_3vars_4coords_1group, temp_test_text_file_path
):
    compare(
        ds_3dims_3vars_4coords_1group,
        ds_3dims_3vars_4coords_1group,
        comparison_var_group="Group1",
        file_text=temp_test_text_file_path,
    )

    found_expected = False
    with open(temp_test_text_file_path) as f:
        for line in f.readlines():
            if "Variables within specified group <Group1>:" in line:
                found_expected = True

    if found_expected:
        assert True
    else:
        assert False


def test_comparison_var_no_error_for_duplicate_dataset(
    ds_3dims_3vars_4coords_1group, temp_test_text_file_path
):
    compare(
        ds_3dims_3vars_4coords_1group,
        ds_3dims_3vars_4coords_1group,
        comparison_var_group="Group1",
        comparison_var_name="var1",
        file_text=temp_test_text_file_path,
    )

    found_expected = False
    with open(temp_test_text_file_path) as f:
        for line in f.readlines():
            if "Sample values within specified variable <var1>:" in line:
                found_expected = True

    if found_expected:
        assert True
    else:
        assert False


def test_get_vars_with_group(ds_3dims_3vars_4coords_1group):
    result = _get_vars(ds_3dims_3vars_4coords_1group, groupname="Group1")
    assert set(result) == {'step', 'var1', 'var2', 'w'}


def test_get_vars_error_when_no_group(ds_3dims_2vars_4coords):
    with pytest.raises(OSError):
        _get_vars(ds_3dims_2vars_4coords, groupname="nonexistent_group")
