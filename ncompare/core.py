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
# pylint: disable=too-many-arguments
# pylint: disable=consider-using-f-string
# pylint: disable=no-member
# pylint: disable=fixme

"""Compare the structure of two netCDF or HDF files."""

from pathlib import Path

from ncompare.Comparison import Comparison
from ncompare.path_and_string_operations import (
    ensure_valid_path_exists,
    ensure_valid_path_with_suffix,
    validate_file_type,
)
from ncompare.printing import Outputter


def compare(
    path_a: str | Path,
    path_b: str | Path,
    only_diffs: bool = False,
    no_color: bool = False,
    show_chunks: bool = False,
    show_attributes: bool = False,
    file_text: str | Path = "",
    file_csv: str | Path = "",
    file_xlsx: str | Path = "",
    column_widths: tuple[int | str, int | str, int | str] | None = None,
) -> int:
    """Compare the variables contained within two netCDF or HDF files.

    Parameters
    ----------
    path_a
        filepath to the first netCDF or HDF
    path_b
        filepath to the second netCDF or HDF
    only_diffs
        Whether to show only the variables/attributes that are different between the two files
    no_color
        Turns off the use of ANSI escape character sequences for producing colored terminal text
    show_chunks
        Whether to include data chunk sizes in the displayed comparison of variables
    show_attributes
        Whether to include variable attributes in the displayed comparison of variables
    file_text
        filepath destination to save captured text output as a TXT file.
    file_csv
        filepath destination to save comparison output as comma-separated values (CSV).
    file_xlsx
        filepath destination to save comparison output as an Excel workbook.
    column_widths
        the width in number of characters for each column of the comparison table.

    Returns
    -------
    int
        total number of differences found (across variables, groups, and attributes)
    """
    # Check the validity of paths.
    path_a = ensure_valid_path_exists(path_a)
    path_b = ensure_valid_path_exists(path_b)
    if file_text:
        file_text = ensure_valid_path_with_suffix(file_text, ".txt")
    if file_csv:
        file_csv = ensure_valid_path_with_suffix(file_csv, ".csv")
    if file_xlsx:
        file_xlsx = ensure_valid_path_with_suffix(file_xlsx, ".xlsx")

    # Check the validity of file types
    file_a = validate_file_type(path_a)
    file_b = validate_file_type(path_b)
    if file_a.type != file_b.type:
        # I'm not sure if there is a use-case where we'd want to compare a netCDF with an HDF file?
        # This assumption of files being the same type, affects the rest of the comparison logic.
        raise TypeError("Both files must be of the same type (either both netCDF or both HDF).")

    # The Outputter object is initialized to handle stdout and optional writing to a text file.
    with Outputter(
        keep_print_history=True,
        keep_only_diffs=only_diffs,
        no_color=no_color,
        text_file=file_text,
        column_widths=column_widths,
    ) as out:
        out.print(f"File A: {file_a.path}")
        out.print(f"File B: {file_b.path}")

        # Start the comparison process.
        comparison = Comparison(
            file_a, file_b, out, show_chunks=show_chunks, show_attributes=show_attributes
        )
        total_diff_count = comparison.run_through_comparisons()

        # Write to CSV and Excel files.
        if file_csv:
            comparison.out.write_history_to_csv(filename=file_csv)
        if file_xlsx:
            comparison.out.write_history_to_excel(filename=file_xlsx)

        comparison.out.print("\nDone.", colors=False)

        return total_diff_count
