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

"""Tests for HDF5-specific handling, e.g., object-reference attributes."""

import h5py
import numpy as np
import pytest

from ncompare.Comparison import Comparison
from ncompare.core import compare
from ncompare.printing import Outputter
from ncompare.utility_types import FileToCompare


def _build_hdf5_with_reference(path, target_name: str) -> None:
    """Create an HDF5 file whose `data` variable has an object-reference attribute.

    The `my_ref` attribute points to a target dataset named `target_name`, mimicking
    reference attributes (such as `DIMENSION_LIST`) that netCDF/HDF5 writers produce.
    """
    with h5py.File(path, "w") as f:
        target = f.create_dataset(target_name, data=np.arange(3))
        variable = f.create_dataset("data", data=np.arange(4))
        ref_array = np.empty((1, 1), dtype=h5py.ref_dtype)
        ref_array[0, 0] = target.ref
        variable.attrs.create("my_ref", data=ref_array)


@pytest.fixture(scope="function")
def hdf5_reference_pair(tmp_path):
    """A pair of HDF5 files whose `data` variable references differently-named targets."""
    path_a = tmp_path / "ref_a.h5"
    path_b = tmp_path / "ref_b.h5"
    _build_hdf5_with_reference(path_a, target_name="target_alpha")
    _build_hdf5_with_reference(path_b, target_name="target_beta")
    return path_a, path_b


def test_hdf5_reference_attribute_resolves_against_its_own_file(hdf5_reference_pair):
    """File B's object references must be resolved against File B, not File A.

    Regression test for a bug where both variables' reference attributes were
    dereferenced against File A's open handle. With that bug, File B's `my_ref`
    resolved to File A's target name, so the differing references were reported as
    identical and `my_ref` never appeared among the differing attributes.
    """
    path_a, path_b = hdf5_reference_pair
    file_a = FileToCompare(path=path_a, type="hdf5")
    file_b = FileToCompare(path=path_b, type="hdf5")

    with Outputter(keep_print_history=True) as out:
        comparison = Comparison(file_a, file_b, out, show_chunks=False, show_attributes=True)
        comparison.run_through_comparisons()

    # Because the references point to differently-named targets, correctly resolving
    # each against its own file yields "/target_alpha" vs "/target_beta" -- a difference.
    assert "my_ref" in comparison.num_attribute_diffs["difference_types"]


@pytest.mark.parametrize("text", ["NASA", "café", "", "b'NASA'"])
def test_variable_string_storage_types_compare_equal(tmp_path, text):
    """Fixed-width bytes and variable-width UTF-8 denote the same attribute text."""
    paths = [tmp_path / "fixed.h5", tmp_path / "variable.h5"]
    values = [np.bytes_(text.encode("utf-8")), text]
    for path, value in zip(paths, values, strict=True):
        with h5py.File(path, "w") as dataset:
            dataset.create_dataset("data", data=np.arange(3)).attrs["source"] = value

    report = tmp_path / "report.txt"
    assert compare(*paths, show_attributes=True, file_text=str(report)) == 0
    assert text in report.read_text()


@pytest.mark.parametrize("shape", [(2,), (1, 2), (2, 1), (1, 1, 2), (0,)])
def test_variable_string_array_storage_types_compare_equal(tmp_path, shape):
    """String arrays must not be interpreted as HDF5 object references."""
    paths = [tmp_path / "fixed.h5", tmp_path / "variable.h5"]
    count = int(np.prod(shape))
    values = ["NASA", "café"][:count]
    fixed = np.array([value.encode("utf-8") for value in values], dtype="S8").reshape(shape)
    variable = np.array(values, dtype=h5py.string_dtype()).reshape(shape)
    for path, value in zip(paths, [fixed, variable], strict=True):
        with h5py.File(path, "w") as dataset:
            dataset.create_dataset("data", data=np.arange(3)).attrs["source"] = value

    assert compare(*paths, show_attributes=True) == 0


def test_invalid_variable_string_bytes_use_replacement_decoding(tmp_path):
    """Use the same invalid-UTF-8 policy as the root attribute normalizer."""
    path = tmp_path / "invalid.h5"
    with h5py.File(path, "w") as dataset:
        variable = dataset.create_dataset("data", data=np.arange(3))
        variable.attrs["source"] = np.bytes_(b"NASA\xff")
        variable.attrs["sources"] = np.array([b"NASA\xff"], dtype="S5")

    report = tmp_path / "report.txt"
    assert compare(path, path, show_attributes=True, file_text=str(report)) == 0
    assert "NASA�" in report.read_text()
    assert "\\xff" not in report.read_text()


def test_hdf5_numeric_attribute_array_format_is_unchanged(tmp_path):
    """Text decoding must not change the existing numeric array representation."""
    path = tmp_path / "numeric.h5"
    value = np.array([1, 2, 3, 4])
    with h5py.File(path, "w") as dataset:
        dataset.create_dataset("data", data=np.arange(3)).attrs["matrix"] = value
    file = FileToCompare(path=path, type="hdf5")
    with Outputter() as out, h5py.File(path) as dataset:
        comparison = Comparison(file, file, out, show_chunks=False, show_attributes=True)
        props = comparison._create_var_properties(dataset, "data", dataset)
        assert props.attributes["matrix"] == str(value)


@pytest.mark.parametrize("array", [False, True])
def test_different_variable_strings_are_still_reported(tmp_path, array):
    """Decoding storage types must preserve genuine text differences."""
    paths = [tmp_path / "a.h5", tmp_path / "b.h5"]
    for path, value in zip(paths, ["NASA", "GSFC"], strict=True):
        stored = np.bytes_(value.encode("utf-8"))
        if array:
            stored = np.array([stored])
        with h5py.File(path, "w") as dataset:
            dataset.create_dataset("data", data=np.arange(3)).attrs["source"] = stored
    assert compare(*paths, show_attributes=True) > 0
