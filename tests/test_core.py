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

import netCDF4
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


def test_summary_is_not_produced_by_a_print_side_effect(tmp_path):
    """The returned total must not depend on `_print_summary` mutating the tally."""
    import netCDF4

    from ncompare.Comparison import Comparison
    from ncompare.printing import Outputter
    from ncompare.utility_types import FileToCompare

    # Two files whose shared variable has an attribute that differs in value
    # (a "both"-sided difference).
    for filename, units in (("a.nc", "m"), ("b.nc", "cm")):
        with netCDF4.Dataset(tmp_path / filename, "w") as ds:
            variable = ds.createVariable("x", "f4", ())
            variable.units = units

    file_a = FileToCompare(path=tmp_path / "a.nc", type="netcdf")
    file_b = FileToCompare(path=tmp_path / "b.nc", type="netcdf")

    with Outputter(keep_print_history=True) as out:
        comparison = Comparison(file_a, file_b, out, show_chunks=False, show_attributes=True)
        total = comparison.run_through_comparisons()

        assert comparison.num_attribute_diffs["both"] >= 1  # the differing 'units' attribute
        left_after_run = comparison.num_attribute_diffs["left"]

        # Rendering the summary again must not change the tally or the total.
        comparison._print_summary()
        assert comparison.num_attribute_diffs["left"] == left_after_run
        assert comparison._total_difference_count() == total

    assert total >= 1


def test_root_attributes_included_when_show_attributes(tmp_path):
    """With show_attributes, root-level attributes appear in the report and are counted."""
    path_a = tmp_path / "root_attrs_a.nc"
    with netCDF4.Dataset(path_a, mode="w") as ds:
        ds.setncattr("title", "Dataset A")
        ds.setncattr("shared_attr", "same")

    path_b = tmp_path / "root_attrs_b.nc"
    with netCDF4.Dataset(path_b, mode="w") as ds:
        ds.setncattr("title", "Dataset B")
        ds.setncattr("shared_attr", "same")

    out_path = tmp_path / "output_with_attrs.txt"
    num_differences = compare(path_a, path_b, show_attributes=True, file_text=str(out_path))

    assert num_differences > 0
    contents = out_path.read_text()
    assert "Root-level Attributes:" in contents
    assert "title:" in contents


def test_root_attributes_excluded_when_not_show_attributes(tmp_path):
    """Without show_attributes, the root-level attributes section is not emitted."""
    path_a = tmp_path / "root_attrs_a.nc"
    with netCDF4.Dataset(path_a, mode="w") as ds:
        ds.setncattr("title", "Dataset A")

    path_b = tmp_path / "root_attrs_b.nc"
    with netCDF4.Dataset(path_b, mode="w") as ds:
        ds.setncattr("title", "Dataset B")

    out_path = tmp_path / "output_without_attrs.txt"
    compare(path_a, path_b, show_attributes=False, file_text=str(out_path))

    assert "Root-level Attributes:" not in out_path.read_text()


# Number of differences between the two ATL06 granules, for the pinned version
# (see ATL06_VERSION in conftest.py). The structural fixtures reproduce the real
# granules' count exactly, so the hermetic test below and the opt-in test against
# real granules assert against this one value.
EXPECTED_ATL06_DIFFERENCES = 4978


def test_icesat_structure(temp_data_dir, atl06_structure_granule_1, atl06_structure_granule_2):
    """Compare two real-world-complex ATL06 structures, without touching the network."""
    out_path = temp_data_dir / "output_file_icesat-2-atl06_structure.txt"

    num_differences = compare(
        atl06_structure_granule_1,
        atl06_structure_granule_2,
        show_chunks=True,
        show_attributes=True,
        file_text=str(out_path),
    )

    assert num_differences > 0, "Expected to find differences between granules"
    assert out_path.exists(), "Output file was not created"
    assert num_differences == EXPECTED_ATL06_DIFFERENCES


def test_error_on_different_file_types(atl06_structure_granule_1):
    file2 = data_for_tests_dir / "test_a.nc"

    with pytest.raises(TypeError):
        compare(atl06_structure_granule_1, file2)


@pytest.mark.integration
def test_icesat(temp_data_dir, icesat2_atl06_granule_1, icesat2_atl06_granule_2):
    """Verify the real granules still match the committed structural fixtures.

    This is the one test that reaches live NASA Earthdata, so it is deselected by
    default and never runs in CI -- an outage there says nothing about this
    codebase. Run it deliberately with ``pytest -m integration`` (which needs
    Earthdata credentials, via ``.netrc`` or the EARTHDATA_* environment
    variables) when changing how files are read, or to check whether ATL06 has
    been reprocessed.

    A mismatch does not mean ncompare is broken: it means the real collection has
    moved on from the fixtures.
    """
    out_path = temp_data_dir / "output_file_icesat-2-atl06.txt"

    num_differences = compare(
        icesat2_atl06_granule_1,
        icesat2_atl06_granule_2,
        show_chunks=True,
        show_attributes=True,
        file_text=str(out_path),
    )

    assert num_differences > 0, "Expected to find differences between granules"
    assert out_path.exists(), "Output file was not created"

    # A mismatch here means the real granules have drifted from the fixtures --
    # most likely an ATL06 reprocessing. Regenerate with
    # scripts/make_atl06_structural_fixtures.py.
    assert num_differences == EXPECTED_ATL06_DIFFERENCES, (
        f"Real granules produced {num_differences} differences but the structural "
        f"fixtures expect {EXPECTED_ATL06_DIFFERENCES}. If ATL06 was reprocessed, "
        "regenerate the fixtures with scripts/make_atl06_structural_fixtures.py."
    )
