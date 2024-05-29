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

import pandas as pd

from ncompare.core import compare

from . import data_for_tests_dir


def test_full_run_to_text_output(temp_data_dir):
    # Compare the `ncompare` output (of test_a.nc vs. test_b.nc) against a pre-computed 'golden' file
    out_path = temp_data_dir / "output_file.txt"

    compare(
        data_for_tests_dir / "test_a.nc",
        data_for_tests_dir / "test_b.nc",
        show_chunks=True,
        show_attributes=True,
        file_text=str(out_path),
    )

    with open(data_for_tests_dir / "a-b_test_golden_file.txt") as f1, open(str(out_path)) as f2:
        exclude_n_lines = 3

        for _ in range(exclude_n_lines):
            next(f1)
            next(f2)

        for line1, line2 in zip(f1, f2):
            assert line1 in line2


def test_full_run_to_csv_output(temp_data_dir):
    # Compare the `ncompare` output (of test_a.nc vs. test_b.nc) against a pre-computed 'golden' file
    out_path = temp_data_dir / "output_file.csv"

    compare(
        data_for_tests_dir / "test_a.nc",
        data_for_tests_dir / "test_b.nc",
        show_chunks=True,
        show_attributes=True,
        file_csv=str(out_path),
    )

    with open(data_for_tests_dir / "a-b_test_golden_file.csv") as f1, open(str(out_path)) as f2:
        exclude_n_lines = 3

        for _ in range(exclude_n_lines):
            next(f1)
            next(f2)

        for line1, line2 in zip(f1, f2):
            assert line1 in line2


def test_full_run_to_xlsx_output(temp_data_dir):
    # Compare the `ncompare` output (of test_a.nc vs. test_b.nc) against a pre-computed 'golden' file
    out_path = temp_data_dir / "output_file.xlsx"

    compare(
        data_for_tests_dir / "test_a.nc",
        data_for_tests_dir / "test_b.nc",
        show_chunks=True,
        show_attributes=True,
        file_xlsx=str(out_path),
    )

    df1 = pd.read_excel(data_for_tests_dir / "a-b_test_golden_file.xlsx")
    df2 = pd.read_excel(out_path)

    difference = df1[df1 != df2]
    rows_with_differences = [(idx, row) for idx, row in difference.notnull().iterrows() if any(row)]

    if len(rows_with_differences) != 0:
        print(
            f"Test will fail because of differences in <{len(rows_with_differences)}> rows. "
            f"Differences identified (Row index ----> row contents):"
        )
        for idx, row in rows_with_differences:
            diff = difference.loc[idx]
            print(f"  {idx} ----> {diff}")

    assert len(rows_with_differences) == 0
