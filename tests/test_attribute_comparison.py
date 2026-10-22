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

import subprocess
import sys

import h5py
import netCDF4
import numpy as np
import pytest

from ncompare.Comparison import Comparison
from ncompare.getters import value_to_comparable_str
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
    assert value_to_comparable_str(values) == expected


@pytest.mark.parametrize(
    "file_type, scope",
    [
        ("netcdf", "root"),
        ("netcdf", "variable"),
        ("hdf5", "root"),
        ("hdf5", "variable"),
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
                target = (
                    dataset
                    if scope == "root"
                    else dataset.create_dataset("data", shape=(1,), dtype="f4")
                )
                target.attrs["samples"] = values
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
    assert value_to_comparable_str(values, max_items=None) != value_to_comparable_str(
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
    assert value_to_comparable_str(value) == value_to_comparable_str(value, max_items=None)


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


def test_hdf5_variable_attribute_tail_after_numpy_abbreviation_is_detected(tmp_path):
    """A change far beyond NumPy's default abbreviated array display must count."""
    paths = [tmp_path / name for name in ("a.h5", "b.h5")]
    values = np.arange(1600)
    for index, path in enumerate(paths):
        data = values.copy()
        if index:
            data[1500] = -123
        with h5py.File(path, "w") as dataset:
            variable = dataset.create_dataset("data", shape=(1,), dtype="f4")
            variable.attrs["samples"] = data

    with Outputter(no_color=True, keep_only_diffs=True, keep_print_history=True) as out:
        comparison = Comparison(
            *(FileToCompare(p, type="hdf5") for p in paths),
            out,
            show_chunks=False,
            show_attributes=True,
        )
        assert comparison.run_through_comparisons() > 0
        assert comparison.num_attribute_diffs["both"] == 1
        rows = [row for row in out._line_history if row[0] == "samples:"]
        assert len(rows) == 1
        assert rows[0][1:3] == ["[0, 1, 2, 3, 4, ...]"] * 2
        assert rows[0][3]


def test_hdf5_root_and_variable_string_array_display_match(tmp_path):
    """Fixed-length HDF5 strings should render alike at both attribute scopes."""
    path = tmp_path / "sample.h5"
    sources = np.array([b"NASA", b"GSFC", b"JPL"])
    with h5py.File(path, "w") as dataset:
        dataset.attrs["sources"] = sources
        variable = dataset.create_dataset("data", shape=(1,), dtype="f4")
        variable.attrs["sources"] = sources

    with Outputter(no_color=True, keep_print_history=True) as out:
        comparison = Comparison(
            FileToCompare(path, type="hdf5"),
            FileToCompare(path, type="hdf5"),
            out,
            show_chunks=False,
            show_attributes=True,
        )
        assert comparison.run_through_comparisons() == 0
        rows = [row for row in out._line_history if row[0] == "sources:"]
        assert len(rows) == 2
        for row in rows:
            assert row[1:3] == ["[NASA, GSFC, JPL]"] * 2


def test_hdf5_variable_tail_difference_sets_cli_exit_code(tmp_path):
    """--only-diffs and --exit-code must catch a change after element 1500."""
    paths = [tmp_path / name for name in ("before.h5", "after.h5")]
    for index, path in enumerate(paths):
        values = np.arange(1600)
        if index:
            values[1500] = -123
        with h5py.File(path, "w") as dataset:
            dataset.create_dataset("data", shape=(1,), dtype="f4").attrs["samples"] = values

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from ncompare.console import main; main()",
            str(paths[0]),
            str(paths[1]),
            "--show-attributes",
            "--only-diffs",
            "--exit-code",
            "--no-color",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1, result.stderr
    assert "samples:" in result.stdout
    assert "[0, 1, 2, 3, 4, ...]" in result.stdout


def test_hdf5_variable_object_reference_names_are_preserved(tmp_path):
    """Raw non-reference arrays must not change HDF5 reference display."""
    path = tmp_path / "references.h5"
    with h5py.File(path, "w") as dataset:
        target = dataset.create_dataset("target", data=np.arange(2))
        variable = dataset.create_dataset("data", shape=(1,), dtype="f4")
        references = np.empty((1, 1), dtype=h5py.ref_dtype)
        references[0, 0] = target.ref
        variable.attrs.create("linked", references, dtype=h5py.ref_dtype)

    with Outputter(no_color=True, keep_print_history=True) as out:
        comparison = Comparison(
            FileToCompare(path, type="hdf5"),
            FileToCompare(path, type="hdf5"),
            out,
            show_chunks=False,
            show_attributes=True,
        )
        assert comparison.run_through_comparisons() == 0
        rows = [row for row in out._line_history if row[0] == "linked:"]
        assert len(rows) == 1
        assert rows[0][1:3] == ["/target", "/target"]
