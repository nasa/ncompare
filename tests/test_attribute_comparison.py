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

"""Regression coverage for complete attribute comparison and bounded display."""

import h5py
import netCDF4
import numpy as np
import pytest

from ncompare.Comparison import Comparison
from ncompare.getters import _value_to_comparable_str
from ncompare.printing import Outputter
from ncompare.utility_types import FileToCompare


@pytest.mark.parametrize(
    "values, expected",
    [
        ([], "[]"),
        ([1, 2, 3], "[1, 2, 3]"),
        ([1, 2, 3, 4, 5], "[1, 2, 3, 4, 5]"),
        ([1, 2, 3, 4, 5, 6], "[1, 2, 3, 4, 5, ...]"),
        (np.array([b"NASA", b"JPL"]), "[NASA, JPL]"),
    ],
)
def test_ellipsis_means_items_were_omitted(values, expected):
    assert _value_to_comparable_str(values) == expected


@pytest.mark.parametrize(
    "file_type, scope",
    [
        ("netcdf", "root"),
        ("netcdf", "variable"),
        ("hdf5", "root"),
    ],
)
@pytest.mark.parametrize("other", [[0, 1, 2, 3, 4, 99], [0, 1, 2, 3, 4]])
@pytest.mark.parametrize("keep_only_diffs", [False, True])
def test_attribute_tail_differences_are_counted(tmp_path, file_type, scope, other, keep_only_diffs):
    paths = [tmp_path / (name + (".nc" if file_type == "netcdf" else ".h5")) for name in ["a", "b"]]
    for path, values in zip(paths, [[0, 1, 2, 3, 4, 5], other]):
        if file_type == "netcdf":
            with netCDF4.Dataset(path, "w") as dataset:
                target = dataset if scope == "root" else dataset.createVariable("data", "f4", ())
                target.setncattr("samples", values)
        else:
            with h5py.File(path, "w") as dataset:
                dataset.attrs["samples"] = values
    with Outputter(no_color=True, keep_only_diffs=keep_only_diffs, keep_print_history=True) as out:
        comparison = Comparison(
            *(FileToCompare(p, type=file_type) for p in paths),
            out,
            show_chunks=False,
            show_attributes=True,
        )
        total = comparison.run_through_comparisons()
        assert total > 0
        assert comparison.num_attribute_diffs["both"] == 1
        rows = [row for row in out._line_history if row[0] == "samples:"]
        assert len(rows) == 1
        assert rows[0][1] == "[0, 1, 2, 3, 4, ...]"
        assert rows[0][2] == ("[0, 1, 2, 3, 4, ...]" if len(other) > 5 else "[0, 1, 2, 3, 4]")
        assert rows[0][3]
        if scope == "variable":
            assert any(row[0] == "-----VARIABLE-----:" for row in out._line_history)


def test_full_comparison_does_not_use_numpy_ellipsis():
    values = np.arange(1200).reshape(1, 1200)
    other = values.copy()
    other[0, 600] = -1
    assert _value_to_comparable_str(values, max_items=None) != _value_to_comparable_str(
        other, max_items=None
    )


def test_display_override_does_not_change_classification():
    with Outputter(no_color=True, keep_only_diffs=True, keep_print_history=True) as out:
        assert (
            out.side_by_side(
                "value",
                "abcdef",
                "abcxyz",
                highlight_diff=True,
                display_values=("abc...", "abc..."),
            )
            == "both"
        )
        assert out._line_history[-1][1:3] == ["abc...", "abc..."]
        assert out._line_history[-1][3]
        assert out.side_by_side("left", "abcdef", "", display_values=("abc...", "")) == "left"
        assert out.side_by_side("right", "", "abcdef", display_values=("", "abc...")) == "right"
        before = len(out._line_history)
        assert out.side_by_side("equal", "abcdef", "abcdef", display_values=("a", "b")) == "shared"
        assert len(out._line_history) == before


@pytest.mark.parametrize("value", ["abcdefghi", b"NASA", np.array(2), 1.25])
def test_scalar_values_are_not_truncated(value):
    assert _value_to_comparable_str(value) == _value_to_comparable_str(value, max_items=None)


def test_equal_long_attributes_are_not_reported_as_different(tmp_path):
    paths = [tmp_path / name for name in ("a.nc", "b.nc")]
    for path in paths:
        with netCDF4.Dataset(path, "w") as dataset:
            dataset.setncattr("samples", np.arange(20))
    with Outputter(no_color=True, keep_only_diffs=True, keep_print_history=True) as out:
        comparison = Comparison(
            *(FileToCompare(p, type="netcdf") for p in paths),
            out,
            show_chunks=False,
            show_attributes=True,
        )
        assert comparison.run_through_comparisons() == 0
        assert not any(row[0] == "samples:" for row in out._line_history)
