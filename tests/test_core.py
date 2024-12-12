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

import netCDF4 as nc

from ncompare.core import (
    _var_properties,
    compare,
)


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


def test_var_properties(ds_3dims_3vars_4coords_1group):
    with nc.Dataset(ds_3dims_3vars_4coords_1group) as ds:
        result = _var_properties(ds.groups["Group1"], varname="step")
        assert result.varname == "step"
        assert result.dtype == "float32"
        assert result.shape == "(3,)"
        assert result.chunking == "contiguous"
        assert result.attributes == {}
