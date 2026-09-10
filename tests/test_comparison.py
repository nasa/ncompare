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

"""Tests for the Comparison class."""

import h5py
import netCDF4
import numpy as np
import pytest

from ncompare.Comparison import Comparison
from ncompare.printing import Outputter
from ncompare.utility_types import FileToCompare, VarProperties


def test_mismatched_file_types_raises(tmp_path):
    """Comparing files of different types is rejected with a TypeError (not an assert)."""
    netcdf_file = FileToCompare(path=tmp_path / "x.nc", type="netcdf")
    hdf5_file = FileToCompare(path=tmp_path / "y.h5", type="hdf5")

    with Outputter() as out:
        with pytest.raises(TypeError):
            Comparison(netcdf_file, hdf5_file, out, show_chunks=False, show_attributes=False)


def test_attributes_read_only_when_requested(tmp_path):
    """Variable attributes are read only when `show_attributes` is set."""
    path = tmp_path / "with_attrs.nc"
    with netCDF4.Dataset(path, "w") as ds:
        variable = ds.createVariable("temperature", "f4", ())
        variable.units = "kelvin"

    file = FileToCompare(path=path, type="netcdf")

    with Outputter() as out:
        comparison_off = Comparison(file, file, out, show_chunks=False, show_attributes=False)
        with netCDF4.Dataset(path) as ds:
            props_off = comparison_off._create_var_properties(
                ds, "temperature", original_dataset=ds
            )
        assert props_off.attributes == {}

        comparison_on = Comparison(file, file, out, show_chunks=False, show_attributes=True)
        with netCDF4.Dataset(path) as ds:
            props_on = comparison_on._create_var_properties(ds, "temperature", original_dataset=ds)
        assert props_on.attributes["units"] == "kelvin"


def test_hdf5_attributes_read_only_when_requested(tmp_path):
    """The HDF5 read path is gated on `show_attributes` too, not just the netCDF one."""
    path = tmp_path / "with_attrs.h5"
    with h5py.File(path, "w") as f:
        dataset = f.create_dataset("temperature", data=np.arange(4))
        dataset.attrs["units"] = "kelvin"

    file = FileToCompare(path=path, type="hdf5")

    with Outputter() as out:
        comparison_off = Comparison(file, file, out, show_chunks=False, show_attributes=False)
        with h5py.File(path, "r") as f:
            props_off = comparison_off._create_var_properties(f, "temperature", original_dataset=f)
        assert props_off.attributes == {}

        comparison_on = Comparison(file, file, out, show_chunks=False, show_attributes=True)
        with h5py.File(path, "r") as f:
            props_on = comparison_on._create_var_properties(f, "temperature", original_dataset=f)
        assert props_on.attributes["units"] == "kelvin"


def test_variable_name_truncated_to_configured_column_width(tmp_path):
    """Variable names are truncated to the configured column widths, not a hardcoded 47."""
    long_name = "x" * 80
    file = FileToCompare(path=tmp_path / "x.nc", type="netcdf")

    def _props():
        return VarProperties(long_name, None, "f4", "()", "()", "", {})

    with Outputter(keep_print_history=True, column_widths=(33, 12, 12)) as out:
        comparison = Comparison(file, file, out, show_chunks=False, show_attributes=False)
        comparison._print_var_properties_side_by_side(_props(), _props())

    variable_rows = [row for row in out._line_history if row and "VARIABLE" in row[0]]
    assert variable_rows, "expected a variable header row to be recorded"
    # The name is truncated to the configured width (12), never the full 80 characters.
    assert variable_rows[0][1] == long_name[:12]
    assert all(long_name not in cell for row in out._line_history for cell in row)


def test_summary_tally_difference_types_are_independent(tmp_path):
    """Each summary tally keeps its own difference_types set."""
    file = FileToCompare(path=tmp_path / "a.nc", type="netcdf")
    with Outputter() as out:
        comparison = Comparison(file, file, out, show_chunks=False, show_attributes=False)

    comparison.num_attribute_diffs["difference_types"].add("units")
    assert comparison.num_var_diffs["difference_types"] == set()
    assert comparison.num_group_diffs["difference_types"] == set()
