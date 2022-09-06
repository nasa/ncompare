"""Compare the structure of two NetCDF files."""
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
from ncompare.utils import ensure_valid_path_exists


VarProperties = namedtuple("VarProperties", "varname, variable, dtype, shape, chunking, attributes")

def compare(nc_a: Union[str, Path],
            nc_b: Union[str, Path],
            comparison_var_group: str = None,
            comparison_var_name: str = None,
            no_color: bool = False,
            show_chunks: bool = False,
            show_attributes: bool = False,
            file_text: str = None,
            file_csv: str = None
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

    Returns
    -------
    int
        Exit code: 0 for a no-issue exit, anything greater than 0 for a problematic exit.
    """
    nc_a = ensure_valid_path_exists(nc_a)
    nc_b = ensure_valid_path_exists(nc_b)

    with Outputter(keep_print_history=True, no_color=no_color, text_file=file_text) as out:
        out.print(f"File A: {nc_a}")
        out.print(f"File B: {nc_b}")

        run_through_comparisons(out,
                                nc_a, nc_b,
                                comparison_var_group=comparison_var_group,
                                comparison_var_name=comparison_var_name,
                                show_chunks=show_chunks,
                                show_attributes=show_attributes)

        # Write to CSV
        out.write_history_to_csv(filename=file_csv)

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
    rootdims_left, rootdims_right, rootdims_both = out.lists_diff(list_a, list_b)

    # Show the groups in each NetCDF file and evaluate differences.
    out.print(Fore.LIGHTBLUE_EX + "\nGroups:", add_to_history=True)
    list_a = _get_groups(nc_a)
    list_b = _get_groups(nc_b)
    groups_left, groups_right, groups_both = out.lists_diff(list_a, list_b)

    if comparison_var_group:

        # Show the variables within the selected group.
        out.print(Fore.LIGHTBLUE_EX + "\nVariables within specified group <%s>:" % comparison_var_group,
                  add_to_history=True)
        vlist_a = _get_vars(nc_a, comparison_var_group)
        vlist_b = _get_vars(nc_b, comparison_var_group)
        left, right, both = out.lists_diff(vlist_a, vlist_b)

        if comparison_var_name:
            try:
                # Print the first part of the values array for the selected variable.
                out.print(Fore.LIGHTBLUE_EX + "\nSample values within specified variable <%s>:" % comparison_var_name)
                _print_sample_values(out, nc_a, comparison_var_group, comparison_var_name)
                _print_sample_values(out, nc_b, comparison_var_group, comparison_var_name)
                # compare_sample_values(nc_a, nc_b, groupname=comparison_var_group, varname=comparison_var_name)

                out.print(Fore.LIGHTBLUE_EX + "\nChecking multiple random values within specified variable <%s>:"
                          % comparison_var_name)
                compare_multiple_random_values(out, nc_a, nc_b,
                                               groupname=comparison_var_group, varname=comparison_var_name)

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
    vars_left, vars_right, vars_both = compare_two_nc_files(out, nc_a, nc_b,
                                                            show_chunks=show_chunks, show_attributes=show_attributes)

def compare_multiple_random_values(out: Outputter,
                                   nc_a: Path,
                                   nc_b: Path,
                                   groupname: str,
                                   varname: str,
                                   num_comparisons: int = 100):
    """Iterate through N random samples, and evaluate whether the differences exceed a threshold."""
    # Open a variable from each NetCDF
    nc_var_a = xr.open_dataset(nc_a, backend_kwargs={"group": groupname}).varname
    nc_var_b = xr.open_dataset(nc_b, backend_kwargs={"group": groupname}).varname

    num_mismatches = 0
    for i in range(num_comparisons):
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

def compare_two_nc_files(out: Outputter,
                         nc_one: Path, nc_two: Path,
                         show_chunks: bool = False,
                         show_attributes: bool = False
                         ) -> tuple[int, int, int]:
    """Go through all groups and all variables, and show them side by side - whether they align and where they don't."""
    out.side_by_side(' ', 'File A', 'File B')
    with netCDF4.Dataset(nc_one) as nc_a, netCDF4.Dataset(nc_two) as nc_b:

        out.side_by_side('All Variables', ' ', ' ', dash_line=False)
        out.side_by_side('-', '-', '-', dash_line=True)
        out.side_by_side('num variables in root group:', len(nc_a.variables), len(nc_b.variables))
        out.side_by_side('-', '-', '-', dash_line=True)

        # Count differences between the lists of variables in the root group.
        vars_left, vars_right, vars_both = count_diffs(nc_a.variables, nc_b.variables)

        # Go through root-level variables.
        for v_idx, v_a, v_b in common_elements(nc_a.variables, nc_b.variables):
            # Get the properties of each variable
            var_a_props = _var_properties(nc_a, v_a)
            var_b_props = _var_properties(nc_b, v_b)
            _print_var_properties_side_by_side(out, var_a_props, var_b_props,
                                               show_chunks=show_chunks, show_attributes=show_attributes)

        # Go through each group.
        for g_idx, g_a, g_b in common_elements(nc_a.groups, nc_b.groups):
            out.side_by_side(" ", " ", " ", dash_line=False, highlight_diff=False)
            out.side_by_side(f"GROUP #{g_idx:02}", g_a.strip(), g_b.strip(), dash_line=True, highlight_diff=False)

            # Count the number of variables in this group as long as this group exists.
            vars_a_sorted = ""
            vars_b_sorted = ""
            if g_a:
                vars_a_sorted = sorted(nc_a.groups[g_a].variables)
            if g_b:
                vars_b_sorted = sorted(nc_b.groups[g_b].variables)
            out.side_by_side('num variables in group:', len(vars_a_sorted), len(vars_b_sorted))
            out.side_by_side('-', '-', '-', dash_line=True)

            # Count differences between the lists of variables in this group.
            left, right, both = count_diffs(vars_a_sorted, vars_b_sorted)
            vars_left += left
            vars_right += right
            vars_both += both

            # Go through each variable in the current group.
            for v_idx, v_a, v_b in common_elements(vars_a_sorted, vars_b_sorted):
                # Get the properties of each variable
                var_a_props = _var_properties(nc_a, v_a, g_a)
                var_b_props = _var_properties(nc_b, v_b, g_b)
                # Print the properties
                _print_var_properties_side_by_side(out, var_a_props, var_b_props,
                                                   show_chunks=show_chunks, show_attributes=show_attributes)

    out.side_by_side('-', '-', '-', dash_line=True)
    out.side_by_side('Total number of shared items:', str(vars_both), str(vars_both))
    out.side_by_side('Total number of non-shared items:', str(vars_left), str(vars_right))
    return vars_left, vars_right, vars_both

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
        for attr_idx, attr_a_key, attr_b_key in common_elements(attrs_a_names, attrs_b_names):
            attr_a = _get_attribute_value_as_str(v_a, attr_a_key)
            attr_b = _get_attribute_value_as_str(v_b, attr_b_key)
            out.side_by_side(f"{attr_a_key}:", attr_a, attr_b, highlight_diff=True)

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

def _var_properties(ds: netCDF4.Dataset,
                    varname: str,
                    groupname: str = None) -> VarProperties:
    """Get the properties of a variable.

    Parameters
    ----------
    ds : `netCDF4.Dataset`
    varname : str
    groupname : str, optional
        if None, the variable is retrieved from the 'root' group of the NetCDF

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
        if groupname:
            the_variable = ds.groups[groupname].variables[varname]
        else:
            the_variable = ds.variables[varname]
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
    # Get a random indexer
    rand_index = []
    for d in nc_var_a.shape:
        rand_index.append(random.randint(0, d - 1))
    rand_index = tuple(rand_index)

    # Get the values from each variable
    v1 = nc_var_a.values[rand_index]
    v2 = nc_var_b.values[rand_index]

    # Evaluate the values
    if np.isnan(v1) or np.isnan(v2):
        return None
    else:
        diff = v2 - v1
        if abs(diff) > thresh:
            out.print()
            out.print(Fore.RED + f"Difference exceeded threshold (diff == {diff}")
            out.print(f"var shape: {nc_var_a.shape}", colors=False)
            out.print(f"indices:   {rand_index}", colors=False)
            out.print(f"value a: {v1}", colors=False)
            out.print(f"value b: {v2}", colors=False, end="\n\n")
            return False
        else:
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
        else:
            return str(attr)
    else:
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
    with netCDF4.Dataset(nc_filepath) as ds:
        groups_list = list(ds.groups.keys())
    return groups_list

def _get_dims(nc_filepath: Path,
              ) -> list:
    with xr.open_dataset(nc_filepath) as ds:
        dims_list = list(ds.dims.items())

    return dims_list
