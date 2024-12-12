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

"""Compare the structure of two NetCDF files."""

import warnings
from collections import namedtuple
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Optional, TypedDict, Union

import netCDF4
import xarray as xr
from colorama import Fore

from ncompare.printing import Outputter, SummaryDifferenceKeys
from ncompare.sequence_operations import common_elements, count_diffs
from ncompare.utils import ensure_valid_path_exists, ensure_valid_path_with_suffix

VarProperties = namedtuple(
    "VarProperties", "varname, variable, dtype, dimensions, shape, chunking, attributes"
)

GroupPair = namedtuple(
    "GroupPair",
    "group_a_name group_a group_b_name group_b",
    defaults=("", None, "", None),
)


class SummaryDifferencesDict(TypedDict):
    shared: int
    left: int
    right: int
    both: int
    difference_types: set


def compare(
    nc_a: Union[str, Path],
    nc_b: Union[str, Path],
    only_diffs: bool = False,
    no_color: bool = False,
    show_chunks: bool = False,
    show_attributes: bool = False,
    file_text: Union[str, Path] = "",
    file_csv: Union[str, Path] = "",
    file_xlsx: Union[str, Path] = "",
    column_widths: Optional[tuple[Union[int, str], Union[int, str], Union[int, str]]] = None,
) -> None:
    """Compare the variables contained within two different netCDF datasets.

    Parameters
    ----------
    nc_a
        filepath to the first netCDF
    nc_b
        filepath to the second netCDF
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
    None
    """
    # Check the validity of paths.
    nc_a = ensure_valid_path_exists(nc_a)
    nc_b = ensure_valid_path_exists(nc_b)
    if file_text:
        file_text = ensure_valid_path_with_suffix(file_text, ".txt")
    if file_csv:
        file_csv = ensure_valid_path_with_suffix(file_csv, ".csv")
    if file_xlsx:
        file_xlsx = ensure_valid_path_with_suffix(file_xlsx, ".xlsx")

    # The Outputter object is initialized to handle stdout and optional writing to a text file.
    with Outputter(
        keep_print_history=True,
        keep_only_diffs=only_diffs,
        no_color=no_color,
        text_file=file_text,
        column_widths=column_widths,
    ) as out:
        out.print(f"File A: {nc_a}")
        out.print(f"File B: {nc_b}")

        # Start the comparison process.
        run_through_comparisons(
            out,
            nc_a,
            nc_b,
            show_chunks=show_chunks,
            show_attributes=show_attributes,
        )

        # Write to CSV and Excel files.
        if file_csv:
            out.write_history_to_csv(filename=file_csv)
        if file_xlsx:
            out.write_history_to_excel(filename=file_xlsx)

        out.print("\nDone.", colors=False)


def run_through_comparisons(
    out: Outputter,
    nc_a: Union[str, Path],
    nc_b: Union[str, Path],
    show_chunks: bool,
    show_attributes: bool,
) -> None:
    """Execute a series of comparisons between two netCDF files.

    Parameters
    ----------
    out
        instance of Outputter
    nc_a
        path to the first netCDF file
    nc_b
        path to the second netCDF file
    show_chunks
        whether to include data chunk sizes in the displayed comparison of variables
    show_attributes
        whether to include variable attributes in the displayed comparison of variables
    """
    # Show the dimensions of each file and evaluate differences.
    out.print(Fore.LIGHTBLUE_EX + "\nRoot-level Dimensions:", add_to_history=True)
    list_a = _get_dims(nc_a)
    list_b = _get_dims(nc_b)
    _, _, _ = out.lists_diff(list_a, list_b)

    # Show the groups in each NetCDF file and evaluate differences.
    out.print(Fore.LIGHTBLUE_EX + "\nRoot-level Groups:", add_to_history=True)
    list_a = _get_groups(nc_a)
    list_b = _get_groups(nc_b)
    _, _, _ = out.lists_diff(list_a, list_b)

    out.print(Fore.LIGHTBLUE_EX + "\nAll variables:", add_to_history=True)
    _, _, _ = compare_two_nc_files(
        out, nc_a, nc_b, show_chunks=show_chunks, show_attributes=show_attributes
    )


def walk_common_groups_tree(
    top_a_name: str,
    top_a: Union[netCDF4.Dataset, netCDF4.Group],
    top_b_name: str,
    top_b: Union[netCDF4.Dataset, netCDF4.Group],
) -> Iterator[GroupPair]:
    """Yield names and groups from a netCDF4's group tree.

    Parameters
    ----------
    top_a_name
        name of the first group or dataset
    top_a
        the first group or dataset
    top_b_name
        name of the second group or dataset
    top_b
        the second group or dataset

    Yields
    ------
    tuple
        group A name : str
        group A object : netCDF4.Group or None
        group B name : str
        group B object : netCDF4.Group or None
    """
    for _, group_a_name, group_b_name in common_elements(
        top_a.groups if top_a is not None else "",
        top_b.groups if top_b is not None else "",
    ):
        yield GroupPair(
            group_a_name=top_a_name + "/" + group_a_name if group_a_name else "",
            group_a=(
                top_a[group_a_name] if (group_a_name and (group_a_name in top_a.groups)) else None
            ),
            group_b_name=top_b_name + "/" + group_b_name if group_b_name else "",
            group_b=(
                top_b[group_b_name] if (group_b_name and (group_b_name in top_b.groups)) else None
            ),
        )

    for _, subgroup_a_name, subgroup_b_name in common_elements(
        top_a.groups if top_a is not None else "",
        top_b.groups if top_b is not None else "",
    ):
        yield from walk_common_groups_tree(
            top_a_name + "/" + subgroup_a_name if subgroup_a_name else "",
            (
                top_a[subgroup_a_name]
                if (subgroup_a_name and (subgroup_a_name in top_a.groups))
                else None
            ),
            top_a_name + "/" + subgroup_b_name if subgroup_b_name else "",
            (
                top_b[subgroup_b_name]
                if (subgroup_b_name and (subgroup_b_name in top_b.groups))
                else None
            ),
        )


def compare_two_nc_files(
    out: Outputter,
    nc_one: Union[str, Path],
    nc_two: Union[str, Path],
    show_chunks: bool = False,
    show_attributes: bool = False,
) -> tuple[int, int, int]:
    """Go through all groups and all variables, and show them side by side,
    highlighting whether they align and where they don't.

    Parameters
    ----------
    out
        instance of Outputter
    nc_one
        path to the first dataset
    nc_two
        path to the second dataset
    show_chunks
        whether to include chunks alongside variables
    show_attributes
        whether to include variable attributes

    Returns
    -------
    tuple
        int
            number of entries only present in the first (left) dataset
        int
            number of entries only present in the second (right) dataset
        int
            number of entries shared among the first (left) and second (right) datasets
    """
    out.side_by_side(" ", "File A", "File B", force_display_even_if_same=True)
    num_group_diffs: SummaryDifferencesDict = {
        "shared": 0,
        "left": 0,
        "right": 0,
        "both": 0,
        "difference_types": set(),
    }
    num_var_diffs: SummaryDifferencesDict = {
        "shared": 0,
        "left": 0,
        "right": 0,
        "both": 0,
        "difference_types": set(),
    }
    num_attribute_diffs: SummaryDifferencesDict = {
        "shared": 0,
        "left": 0,
        "right": 0,
        "both": 0,
        "difference_types": set(),
    }
    with netCDF4.Dataset(nc_one) as nc_a, netCDF4.Dataset(nc_two) as nc_b:
        out.side_by_side(
            "All Variables", " ", " ", dash_line=False, force_display_even_if_same=True
        )
        out.side_by_side("-", "-", "-", dash_line=True, force_display_even_if_same=True)

        group_counter = 0
        _print_group_details_side_by_side(
            out,
            nc_a,
            "/",
            nc_b,
            "/",
            group_counter,
            num_var_diffs,
            num_attribute_diffs,
            show_attributes,
            show_chunks,
        )
        group_counter += 1

        for group_pair in walk_common_groups_tree("", nc_a, "", nc_b):
            if group_pair.group_a_name == "":
                num_group_diffs["right"] += 1
            elif group_pair.group_b_name == "":
                num_group_diffs["left"] += 1
            else:
                num_group_diffs["shared"] += 1

            _print_group_details_side_by_side(
                out,
                group_pair.group_a,
                group_pair.group_a_name,
                group_pair.group_b,
                group_pair.group_b_name,
                group_counter,
                num_var_diffs,
                num_attribute_diffs,
                show_attributes,
                show_chunks,
            )
            group_counter += 1

    out.side_by_side("-", "-", "-", dash_line=True, force_display_even_if_same=True)
    out.side_by_side("SUMMARY", "-", "-", dash_line=True, force_display_even_if_same=True)

    _print_summary_count_comparison_side_by_side(out, "variable", num_var_diffs)
    _print_summary_count_comparison_side_by_side(out, "group", num_group_diffs)
    _print_summary_count_comparison_side_by_side(out, "attribute", num_attribute_diffs)
    if num_attribute_diffs["difference_types"]:
        out.print(
            Fore.LIGHTBLUE_EX + "\nDifferences were found in these attributes:", add_to_history=True
        )
        out.print(
            Fore.LIGHTBLUE_EX + f"\n{sorted(num_attribute_diffs['difference_types'])}",
            add_to_history=True,
        )

    return num_var_diffs["left"], num_var_diffs["right"], num_var_diffs["shared"]


def _print_summary_count_comparison_side_by_side(
    out: Outputter,
    item_type: str,
    diff_dictionary: SummaryDifferencesDict,
) -> None:
    # Tally up instances where there were non-empty entries on both left and right sides.
    diff_dictionary["left"] += diff_dictionary["both"]
    diff_dictionary["right"] += diff_dictionary["both"]

    out.side_by_side(
        f"Total # of shared {item_type}s:",
        str(diff_dictionary["shared"]),
        str(diff_dictionary["shared"]),
        force_display_even_if_same=True,
    )

    out.side_by_side(
        f"Total # of non-shared {item_type}s:",
        str(diff_dictionary["left"]),
        str(diff_dictionary["right"]),
        force_display_even_if_same=True,
    )


def _print_group_details_side_by_side(
    out,
    group_a: Union[netCDF4.Dataset, netCDF4.Group],
    group_a_name: str,
    group_b: Union[netCDF4.Dataset, netCDF4.Group],
    group_b_name: str,
    group_counter: int,
    num_var_diffs: SummaryDifferencesDict,
    num_attribute_diffs: SummaryDifferencesDict,
    show_attributes: bool,
    show_chunks: bool,
) -> None:
    """Align and display group details side by side."""
    out.side_by_side(
        " ", " ", " ", dash_line=False, highlight_diff=False, force_display_even_if_same=True
    )
    out.side_by_side(
        f"GROUP #{group_counter:02}",
        group_a_name.strip(),
        group_b_name.strip(),
        dash_line=True,
        highlight_diff=False,
        force_display_even_if_same=True,
    )

    # Count the number of variables in this group as long as this group exists.
    vars_a_sorted: Union[list, str] = ""
    vars_b_sorted: Union[list, str] = ""
    if group_a:
        vars_a_sorted = sorted(group_a.variables)
    if group_b:
        vars_b_sorted = sorted(group_b.variables)
    out.side_by_side(
        "num variables in group:",
        len(vars_a_sorted),
        len(vars_b_sorted),
        highlight_diff=True,
        force_display_even_if_same=True,
    )
    out.side_by_side("-", "-", "-", dash_line=True, force_display_even_if_same=True)

    # Count differences between the lists of variables in this group.
    left, right, shared = count_diffs(vars_a_sorted, vars_b_sorted)
    num_var_diffs["left"] += left
    num_var_diffs["right"] += right
    num_var_diffs["shared"] += shared

    # Go through each variable in the current group.
    for variable_pair in common_elements(vars_a_sorted, vars_b_sorted):
        # Get and print the properties of each variable
        _print_var_properties_side_by_side(
            out,
            _var_properties(group_a, variable_pair[1]),
            _var_properties(group_b, variable_pair[2]),
            num_attribute_diffs,
            show_chunks=show_chunks,
            show_attributes=show_attributes,
        )


def _print_var_properties_side_by_side(
    out: Outputter,
    v_a: VarProperties,
    v_b: VarProperties,
    num_attribute_diffs: SummaryDifferencesDict,
    show_chunks: bool = False,
    show_attributes: bool = False,
) -> None:
    """Align and display variable properties side by side."""
    # Gather all variable property pairs first, before printing,
    # so we can decide whether to highlight the variable header.
    pairs_to_check_and_show = [
        (v_a.dtype, v_b.dtype),
        (v_a.dimensions, v_b.dimensions),
        (v_a.shape, v_b.shape),
    ]
    if show_chunks:
        pairs_to_check_and_show.append((v_a.chunking, v_b.chunking))
    if show_attributes:
        for attr_a_key, attr_a, attr_b_key, attr_b in _get_and_check_variable_attributes(v_a, v_b):
            # Check whether attr_a_key is empty,
            # because it might be if the variable doesn't exist in File A.
            pairs_to_check_and_show.append((attr_a, attr_b))
    # Scale Factor
    scale_factor_pair = _get_and_check_variable_scale_factor(v_a, v_b)
    if scale_factor_pair:
        pairs_to_check_and_show.append((scale_factor_pair[0], scale_factor_pair[1]))

    there_is_a_difference = False
    for pair in pairs_to_check_and_show:
        if pair[0] != pair[1]:
            there_is_a_difference = True
            break

    # If all attributes are the same, and keep-only-diffs is set -> DON'T print
    # If all attributes are the same, and keep-only-diffs is NOT set -> print
    # If some attributes are different -> print no matter else
    if there_is_a_difference or (not out.keep_only_diffs):
        out.side_by_side(
            "-----VARIABLE-----:",
            v_a.varname[:47],
            v_b.varname[:47],
            highlight_diff=False,
            force_display_even_if_same=True,
        )

    # Go through each attribute, show differences, and add differences to running tally.
    def _var_attribute_side_by_side(attribute_name, attribute_a, attribute_b):
        diff_condition: SummaryDifferenceKeys = out.side_by_side(
            f"{attribute_name}:", attribute_a, attribute_b, highlight_diff=True
        )
        num_attribute_diffs[diff_condition] += 1
        if diff_condition in ("left", "right", "both"):
            num_attribute_diffs["difference_types"].add(attribute_name)

    _var_attribute_side_by_side("dtype", v_a.dtype, v_b.dtype)
    _var_attribute_side_by_side("dimensions", v_a.dimensions, v_b.dimensions)
    _var_attribute_side_by_side("shape", v_a.shape, v_b.shape)
    # Chunking
    if show_chunks:
        _var_attribute_side_by_side("chunksize", v_a.chunking, v_b.chunking)
    # Scale Factor
    scale_factor_pair = _get_and_check_variable_scale_factor(v_a, v_b)
    if scale_factor_pair:
        _var_attribute_side_by_side("scale_factor", scale_factor_pair[0], scale_factor_pair[1])
    # Other attributes
    if show_attributes:
        for attr_a_key, attr_a, attr_b_key, attr_b in _get_and_check_variable_attributes(v_a, v_b):
            # Check whether attr_a_key is empty,
            # because it might be if the variable doesn't exist in File A.
            attribute_key = attr_a_key if attr_a_key else attr_b_key
            _var_attribute_side_by_side(attribute_key, attr_a, attr_b)


def _get_and_check_variable_scale_factor(
    v_a: VarProperties, v_b: VarProperties
) -> Union[None, tuple[str, str]]:
    """Get a string representation of the scale factor for two variables."""
    if getattr(v_a.variable, "scale_factor", None):
        sf_a = v_a.variable.scale_factor
    else:
        sf_a = " "
    if getattr(v_b.variable, "scale_factor", None):
        sf_b = v_b.variable.scale_factor
    else:
        sf_b = " "
    if (sf_a != " ") or (sf_b != " "):
        return str(sf_a), str(sf_b)
    else:
        return None


def _get_and_check_variable_attributes(
    v_a: VarProperties, v_b: VarProperties
) -> Iterator[tuple[str, str, str, str]]:
    """Go through and yield each attribute pair for two variables."""
    # Get the name of attributes if they exist
    attrs_a_names = []
    if v_a.attributes:
        attrs_a_names = v_a.attributes.keys()
    attrs_b_names = []
    if v_b.attributes:
        attrs_b_names = v_b.attributes.keys()
    # Iterate and print each attribute
    for _, attr_a_key, attr_b_key in common_elements(attrs_a_names, attrs_b_names):
        attr_a = _get_attribute_value_as_str(v_a, attr_a_key)
        attr_b = _get_attribute_value_as_str(v_b, attr_b_key)
        yield attr_a_key, attr_a, attr_b_key, attr_b


def _var_properties(group: Union[netCDF4.Dataset, netCDF4.Group], varname: str) -> VarProperties:
    """Get the properties of a variable.

    Parameters
    ----------
    group
        a dataset or group of variables
    varname
        the name of the variable

    Returns
    -------
    VarProperties
    """
    if varname:
        the_variable = group.variables[varname]
        v_dtype = str(the_variable.dtype)
        v_dimensions = str(the_variable.dimensions)
        v_shape = str(the_variable.shape).strip()
        v_chunking = str(the_variable.chunking()).strip()

        v_attributes = {}
        for name in the_variable.ncattrs():
            try:
                v_attributes[name] = the_variable.getncattr(name)
            except KeyError as key_err:
                # Added this check because of "unsupported datatype" error that prevented
                # fully running comparisons on S5P_OFFL_L1B_IR_UVN collections.
                v_attributes[name] = f"netCDF error: {str(key_err)}"
    else:
        the_variable = None
        v_dtype = ""
        v_dimensions = ""
        v_shape = ""
        v_chunking = ""
        v_attributes = None

    return VarProperties(
        varname, the_variable, v_dtype, v_dimensions, v_shape, v_chunking, v_attributes
    )


def _get_attribute_value_as_str(varprops: VarProperties, attribute_key: str) -> str:
    """Get a string representation of the attribute value."""
    if attribute_key and (attribute_key in varprops.attributes):
        attr = varprops.attributes[attribute_key]
        if isinstance(attr, Iterable) and not isinstance(attr, (str, float)):
            # TODO: by truncating a list (or other iterable) here,
            #  we are preventing any subsequent difference checker from detecting
            #  differences past the 5th element in the iterable.
            #  So, we need to figure out a way to still check for other differences past the 5th element.
            return "[" + ", ".join([str(x) for x in attr[:5]]) + ", ..." + "]"  # type:ignore[index]

        return str(attr)

    return ""


def _get_groups(nc_filepath: Union[str, Path]) -> list:
    """Get a list of groups from a netCDF."""
    with netCDF4.Dataset(nc_filepath) as dataset:
        groups_list = list(dataset.groups.keys())
    return groups_list


def _get_dims(nc_filepath: Union[str, Path]) -> list:
    """Get a list of dimensions from a netCDF."""

    def __get_dim_list(decode_times=True):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with xr.open_dataset(nc_filepath, decode_times=decode_times) as dataset:
                return list(dataset.sizes.items())

    try:
        dims_list = __get_dim_list()
    except ValueError as err:
        if "decode_times" in str(err):  # then try again without decoding the times
            dims_list = __get_dim_list(decode_times=False)
        else:
            raise err from None  # "from None" prevents additional trace (see https://stackoverflow.com/a/18188660)

    return dims_list
