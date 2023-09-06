"""Compare the structure of two NetCDF files."""
# pylint: disable=too-many-arguments
# pylint: disable=consider-using-f-string
# pylint: disable=no-member
# pylint: disable=fixme
import random
import traceback
from collections import namedtuple
from collections.abc import Iterable
from pathlib import Path
from typing import Union

import netCDF4
import numpy as np
import xarray as xr
from colorama import Fore, Style

from ncompare.printing import Outputter
from ncompare.sequence_operations import common_elements, count_diffs
from ncompare.utils import ensure_valid_path_exists, ensure_valid_path_with_suffix

VarProperties = namedtuple("VarProperties", "varname, variable, dtype, shape, chunking, attributes")

def compare(nc_a: Union[str, Path],
            nc_b: Union[str, Path],
            comparison_var_group: str = None,
            comparison_var_name: str = None,
            no_color: bool = False,
            show_chunks: bool = False,
            show_attributes: bool = False,
            file_text: str = None,
            file_csv: str = None,
            file_xlsx: str = None
            ) -> None:
    """Compare the variables contained within two different NetCDF datasets.

    Parameters
    ----------
    nc_a : str
        filepath to NetCDF4
    nc_b : str
        filepath to NetCDF4
    comparison_var_group : str, optional
        The name of a group which contains a desired comparison variable
    comparison_var_name : str, optional
        The name of a variable for which we want to compare values
    no_color : bool, default False
        Turns off the use of ANSI escape character sequences for producing colored terminal text
    show_chunks : bool, default False
        Whether to include data chunk sizes in the displayed comparison of variables
    show_attributes : bool, default False
        Whether to include variable attributes in the displayed comparison of variables
    file_text : str
        filepath destination to save captured text output as a TXT file.
    file_csv : str
        filepath destination to save comparison output as comma separated values (CSV).
    file_xlsx : str
        filepath destination to save comparison output as an Excel workbook.

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
    with Outputter(keep_print_history=True, no_color=no_color, text_file=file_text) as out:
        out.print(f"File A: {nc_a}")
        out.print(f"File B: {nc_b}")
        out.side_by_side(' ', str(nc_a), str(nc_b))

        # Start the comparison process.
        run_through_comparisons(out,
                                nc_a, nc_b,
                                comparison_var_group=comparison_var_group,
                                comparison_var_name=comparison_var_name,
                                show_chunks=show_chunks,
                                show_attributes=show_attributes)

        # Write to CSV and Excel files.
        if file_csv:
            out.write_history_to_csv(filename=file_csv)
        if file_xlsx:
            out.write_history_to_excel(filename=file_xlsx)

        out.print("\nDone.", colors=False)

def run_through_comparisons(out: Outputter,
                            nc_a: Union[str, Path],
                            nc_b: Union[str, Path],
                            comparison_var_group: str,
                            comparison_var_name: str,
                            show_chunks: bool,
                            show_attributes: bool) -> None:
    """Execute a series of comparisons between two NetCDF files.

    Parameters
    ----------
    out
    nc_a
    nc_b
    comparison_var_group
    comparison_var_name
    show_chunks
    show_attributes
    """
    # Show the dimensions of each file and evaluate differences.
    out.print(Fore.LIGHTBLUE_EX + "\nRoot-level Dimensions:", add_to_history=True)
    list_a = _get_dims(nc_a)
    list_b = _get_dims(nc_b)
    _, _, _ = out.lists_diff(list_a, list_b)

    # Show the groups in each NetCDF file and evaluate differences.
    out.print(Fore.LIGHTBLUE_EX + "\nGroups:", add_to_history=True)
    list_a = _get_groups(nc_a)
    list_b = _get_groups(nc_b)
    _, _, _ = out.lists_diff(list_a, list_b)

    if comparison_var_group:

        # Show the variables within the selected group.
        out.print(Fore.LIGHTBLUE_EX + "\nVariables within specified group <%s>:" % comparison_var_group,
                  add_to_history=True)
        vlist_a = _get_vars(nc_a, comparison_var_group)
        vlist_b = _get_vars(nc_b, comparison_var_group)
        _, _, _ = out.lists_diff(vlist_a, vlist_b)

        if comparison_var_name:
            try:
                # Print the first part of the values array for the selected variable.
                out.print(Fore.LIGHTBLUE_EX + "\nSample values within specified variable <%s>:" % comparison_var_name)
                _print_sample_values(out, nc_a, comparison_var_group, comparison_var_name)
                _print_sample_values(out, nc_b, comparison_var_group, comparison_var_name)
                # compare_sample_values(nc_a, nc_b, groupname=comparison_var_group, varname=comparison_var_name)

                out.print(Fore.LIGHTBLUE_EX + "\nChecking multiple random values within specified variable <%s>:"
                          % comparison_var_name)
                compare_multiple_random_values(out, nc_a, nc_b, groupname=comparison_var_group)

            except KeyError:
                out.print(Style.BRIGHT + Fore.RED + "\nError when comparing values for variable <%s> in group <%s>." %
                          (comparison_var_name, comparison_var_group))
                out.print(traceback.format_exc())
                out.print("\n")
        else:
            out.print(Fore.LIGHTBLACK_EX + "\nNo variable selected for comparison. Skipping..")
    else:
        out.print(Fore.LIGHTBLACK_EX + "\nNo variable group selected for comparison. Skipping..")

    out.print(Fore.LIGHTBLUE_EX + "\nAll variables:", add_to_history=True)
    _, _, _ = compare_two_nc_files(out, nc_a, nc_b, show_chunks=show_chunks, show_attributes=show_attributes)

def compare_multiple_random_values(out: Outputter,
                                   nc_a: Path,
                                   nc_b: Path,
                                   groupname: str,
                                   num_comparisons: int = 100):
    """Iterate through N random samples, and evaluate whether the differences exceed a threshold."""
    # Open a variable from each NetCDF
    nc_var_a = xr.open_dataset(nc_a, backend_kwargs={"group": groupname}).varname
    nc_var_b = xr.open_dataset(nc_b, backend_kwargs={"group": groupname}).varname

    num_mismatches = 0
    for _ in range(num_comparisons):
        match_result = _match_random_value(out, nc_var_a, nc_var_b)
        if match_result is True:
            out.print(".", colors=False, end="")
        elif match_result is None:
            out.print("n", colors=False, end="")
        else:
            out.print("x", colors=False, end="")
            num_mismatches += 1

    if num_mismatches > 0:
        out.print(Fore.RED + f" {num_mismatches} mismatches, out of {num_comparisons} samples.")
    else:
        out.print(Fore.CYAN + " No mismatches.")
    out.print("Done.", colors=False)

def walk_common_groups_tree(top_a_name: str,
                            top_a: Union[netCDF4.Dataset, netCDF4.Group],
                            top_b_name: str,
                            top_b: Union[netCDF4.Dataset, netCDF4.Group]
                            ) -> tuple[str, netCDF4.Group, str, netCDF4.Group]:
    """Yield names and groups from a netCDF4's group tree.

    Parameters
    ----------
    top_a_name : str
    top_a : netCDF4.Dataset or netCDF4.Group
    top_b_name : str
    top_b : netCDF4.Dataset or netCDF4.Group

    Yields
    ------
    group A name : str
    group A object : netCDF4.Group
    group B name : str
    group B object : netCDF4.Group
    """
    yield (
        (top_a_name + "/" + group_a_name if group_a_name else "",
         top_a[group_a_name] if (group_a_name and (group_a_name in top_a.groups)) else None,
         top_b_name + "/" + group_b_name if group_b_name else "",
         top_b[group_b_name] if (group_b_name and (group_b_name in top_b.groups)) else None,
         )
        for (_, group_a_name, group_b_name)
        in common_elements(
            top_a.groups if top_a is not None else "",
            top_b.groups if top_b is not None else ""
        )
    )

    for _, subgroup_a_name, subgroup_b_name in common_elements(
            top_a.groups if top_a is not None else "",
            top_b.groups if top_a is not None else ""
    ):
        yield from walk_common_groups_tree(
            top_a_name + "/" + subgroup_a_name if subgroup_a_name else "",
            top_a[subgroup_a_name] if (subgroup_a_name and (subgroup_a_name in top_a.groups)) else None,
            top_a_name + "/" + subgroup_b_name if subgroup_b_name else "",
            top_b[subgroup_b_name] if (subgroup_b_name and (subgroup_b_name in top_b.groups)) else None
        )

def compare_two_nc_files(out: Outputter,
                         nc_one: Path,
                         nc_two: Path,
                         show_chunks: bool = False,
                         show_attributes: bool = False
                         ) -> tuple[int, int, int]:
    """Go through all groups and all variables, and show them side by side - whether they align and where they don't."""
    out.side_by_side(' ', 'File A', 'File B')

    num_var_diffs = {"left": 0, "right": 0, "both": 0}
    with netCDF4.Dataset(nc_one) as nc_a, netCDF4.Dataset(nc_two) as nc_b:

        out.side_by_side('All Variables', ' ', ' ', dash_line=False)
        out.side_by_side('-', '-', '-', dash_line=True)

        group_counter = 0
        _print_group_details_side_by_side(out, nc_a, "/", nc_b, "/", group_counter, num_var_diffs, show_attributes,
                                          show_chunks)
        group_counter += 1

        for group_pairs in walk_common_groups_tree("", nc_a, "", nc_b):
            for group_a_name, group_a, group_b_name, group_b in group_pairs:

                _print_group_details_side_by_side(out, group_a, group_a_name, group_b, group_b_name, group_counter,
                                                  num_var_diffs, show_attributes, show_chunks)
                group_counter += 1

    out.side_by_side('-', '-', '-', dash_line=True)
    out.side_by_side('Total number of shared items:', str(num_var_diffs['both']), str(num_var_diffs['both']))
    out.side_by_side('Total number of non-shared items:', str(num_var_diffs['left']), str(num_var_diffs['right']))
    return num_var_diffs['left'], num_var_diffs['right'], num_var_diffs['both']


def _print_group_details_side_by_side(out,
                                      group_a: Union[netCDF4.Dataset, netCDF4.Group],
                                      group_a_name: str,
                                      group_b: Union[netCDF4.Dataset, netCDF4.Group],
                                      group_b_name: str,
                                      group_counter: int,
                                      num_var_diffs: dict,
                                      show_attributes: bool,
                                      show_chunks: bool) -> None:
    out.side_by_side(" ", " ", " ", dash_line=False, highlight_diff=False)
    out.side_by_side(f"GROUP #{group_counter:02}", group_a_name.strip(), group_b_name.strip(),
                     dash_line=True, highlight_diff=False)

    # Count the number of variables in this group as long as this group exists.
    vars_a_sorted, vars_b_sorted = "", ""
    if group_a:
        vars_a_sorted = sorted(group_a.variables)
    if group_b:
        vars_b_sorted = sorted(group_b.variables)
    out.side_by_side('num variables in group:', len(vars_a_sorted), len(vars_b_sorted), highlight_diff=True)
    out.side_by_side('-', '-', '-', dash_line=True)

    # Count differences between the lists of variables in this group.
    left, right, both = count_diffs(vars_a_sorted, vars_b_sorted)
    num_var_diffs['left'] += left
    num_var_diffs['right'] += right
    num_var_diffs['both'] += both

    # Go through each variable in the current group.
    for variable_pair in common_elements(vars_a_sorted, vars_b_sorted):
        # Get and print the properties of each variable
        _print_var_properties_side_by_side(out,
                                           _var_properties(group_a, variable_pair[1]),
                                           _var_properties(group_b, variable_pair[2]),
                                           show_chunks=show_chunks, show_attributes=show_attributes)


def _print_var_properties_side_by_side(out,
                                       v_a: VarProperties,
                                       v_b: VarProperties,
                                       show_chunks: bool = False,
                                       show_attributes: bool = False):
    # Variable name
    out.side_by_side("-----VARIABLE-----:", v_a.varname[:47], v_b.varname[:47], highlight_diff=False)

    # Data type
    out.side_by_side("dtype:", v_a.dtype, v_b.dtype, highlight_diff=True)
    # Shape
    out.side_by_side("shape:", v_a.shape, v_b.shape, highlight_diff=True)
    # Chunking
    if show_chunks:
        out.side_by_side("chunksize:", v_a.chunking, v_b.chunking, highlight_diff=True)
    # Attributes
    if show_attributes:
        # Get name of attributes if they exist
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
            # Check whether attr_a_key is empty, because it might be if the variable doesn't exist in File A.
            out.side_by_side(f"{attr_a_key if attr_a_key else attr_b_key}:", attr_a, attr_b, highlight_diff=True)

    # Scale Factor
    if getattr(v_a.variable, 'scale_factor', None):
        sf_a = v_a.variable.scale_factor
    else:
        sf_a = ' '
    if getattr(v_b.variable, 'scale_factor', None):
        sf_b = v_b.variable.scale_factor
    else:
        sf_b = ' '
    if (sf_a != " ") or (sf_b != " "):
        out.side_by_side("sf:", str(sf_a), str(sf_b), highlight_diff=True)

def _var_properties(group: Union[netCDF4.Dataset, netCDF4.Group],
                    varname: str) -> VarProperties:
    """Get the properties of a variable.

    Parameters
    ----------
    group : `netCDF4.Dataset` or netCDF4.Group object
    varname : str

    Returns
    -------
    netCDF4.Variable
    str
        dtype of variable values
    tuple
        shape of variable
    tuple
        chunking
    dict
        any other attributes for this variable
    """
    if varname:
        the_variable = group.variables[varname]
        v_dtype = str(the_variable.dtype)
        v_shape = str(the_variable.shape).strip()
        v_chunking = str(the_variable.chunking()).strip()
        v_attributes = {name: getattr(the_variable, name)
                        for name in the_variable.ncattrs()}
    else:
        the_variable = None
        v_dtype = ""
        v_shape = ""
        v_chunking = ""
        v_attributes = None

    return VarProperties(varname, the_variable, v_dtype, v_shape, v_chunking, v_attributes)

def _match_random_value(out: Outputter,
                        nc_var_a: netCDF4.Variable,
                        nc_var_b: netCDF4.Variable,
                        thresh: float = 1e-6
                        ) -> Union[bool, None]:
    """Check whether a randomly selected data point matches between two variables.

    Returns
    -------
    None or bool
        None if data point is null for either variable
        True if values match
        False if the difference exceeds the given threshold
    """
    # Get a random indexer
    rand_index = []
    for dim_length in nc_var_a.shape:
        rand_index.append(random.randint(0, dim_length - 1))
    rand_index = tuple(rand_index)

    # Get the values from each variable
    value_a = nc_var_a.values[rand_index]
    value_b = nc_var_b.values[rand_index]

    # Check whether null
    if np.isnan(value_a) or np.isnan(value_b):
        return None

    # Evaluate difference between values
    diff = value_b - value_a
    if abs(diff) > thresh:
        out.print()
        out.print(Fore.RED + f"Difference exceeded threshold (diff == {diff}")
        out.print(f"var shape: {nc_var_a.shape}", colors=False)
        out.print(f"indices:   {rand_index}", colors=False)
        out.print(f"value a: {value_a}", colors=False)
        out.print(f"value b: {value_b}", colors=False, end="\n\n")
        return False

    return True

def _print_sample_values(out: Outputter, nc_filepath, groupname: str, varname: str) -> None:
    comparison_variable = xr.open_dataset(nc_filepath, backend_kwargs={"group": groupname})[varname]
    out.print(comparison_variable.values[0, :], colors=False)

def _get_attribute_value_as_str(varprops: VarProperties,
                                attribute_key: str) -> str:
    if attribute_key and (attribute_key in varprops.attributes):
        attr = varprops.attributes[attribute_key]
        if isinstance(attr, Iterable) and not isinstance(attr, (str, float)):
            # TODO: by truncating a list (or other iterable) here,
            #  we are preventing any subsequent difference checker from detecting
            #  differences past the 5th element in the iterable.
            #  So, we need to figure out a way to still check for other differences past the 5th element.
            return "[" + ", ".join([str(x) for x in attr[:5]]) + ", ..." + "]"

        return str(attr)

    return ""

def _get_vars(nc_filepath: Path,
              groupname: str,
              ) -> list:
    try:
        grp = xr.open_dataset(nc_filepath, backend_kwargs={"group": groupname})
    except OSError as err:
        print("\nError occurred when attempting to open group within <%s>.\n" % nc_filepath)
        raise err
    grp_varlist = sorted(list(grp.variables.keys()))

    return grp_varlist

def _get_groups(nc_filepath: Path,
                ) -> list:
    with netCDF4.Dataset(nc_filepath) as dataset:
        groups_list = list(dataset.groups.keys())
    return groups_list

def _get_dims(nc_filepath: Path,
              ) -> list:

    def __get_dim_list(decode_times=True):
        with xr.open_dataset(nc_filepath, decode_times=decode_times) as dataset:
            return list(dataset.dims.items())

    try:
        dims_list = __get_dim_list()
    except ValueError as err:
        if "decode_times" in str(err):  # then try again without decoding the times
            dims_list = __get_dim_list(decode_times=False)
        else:
            raise err from None  # "from None" prevents additional trace (see https://stackoverflow.com/a/18188660)

    return dims_list
