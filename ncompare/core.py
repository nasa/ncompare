"""Compare the structure of two NetCDF files."""
import random
import traceback
from pathlib import Path

import colorama
import netCDF4
import numpy as np
import xarray as xr
from colorama import Fore, Style

from ncompare.utils import make_valid_path, print_normal


def compare(nc_a: str,
            nc_b: str,
            comparison_var_group: str = None,
            comparison_var_name: str = None,
            no_color: bool = False,
            show_chunks: bool = False
            ) -> int:
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
    show_chunks : bool, default False

    Returns
    -------
    int
        Exit code: 0 for a no-issue exit, anything greater than 0 for a problematic exit.
    """
    nc_a = make_valid_path(nc_a)
    nc_b = make_valid_path(nc_b)

    if no_color:
        for k, v in Fore.__dict__.items():
            Fore.__dict__[k] = ""
    else:
        colorama.init(autoreset=True)

    print(Fore.LIGHTBLUE_EX + "\nDimensions:")
    compare_dimensions(nc_a, nc_b)

    print(Fore.LIGHTBLUE_EX + "\nGroups:")
    compare_groups(nc_a, nc_b)

    if comparison_var_group:
        print(Fore.LIGHTBLUE_EX + "\nVariables within specified group <%s>:" % comparison_var_group)
        compare_ingroup_variables(nc_a, nc_b, groupname=comparison_var_group)

        if comparison_var_name:
            try:
                print(Fore.LIGHTBLUE_EX + "\nSample values within specified variable <%s>:" % comparison_var_name)
                compare_sample_values(nc_a, nc_b, groupname=comparison_var_group, varname=comparison_var_name)

                print(Fore.LIGHTBLUE_EX + "\nChecking multiple random values within specified variable <%s>:"
                      % comparison_var_name)
                compare_multiple_random_values(nc_a, nc_b, groupname=comparison_var_group, varname=comparison_var_name)

            except KeyError:
                print(Style.BRIGHT + Fore.RED + "\nError when comparing values for variable <%s> in group <%s>." %
                      (comparison_var_name, comparison_var_group))
                print(traceback.format_exc())
                print("\n")
        else:
            print(Fore.LIGHTBLACK_EX + "\nNo variable selected for comparison. Skipping..")
    else:
        print(Fore.LIGHTBLACK_EX + "\nNo variable group selected for comparison. Skipping..")

    print(Fore.LIGHTBLUE_EX + "\nAll variables:")
    compare_two_nc_files(nc_a, nc_b, show_chunks=show_chunks)

    print(Fore.LIGHTBLUE_EX + "\nDone.")
    return 0  # a clean, no-issue, exit

def compare_dimensions(nc_a: Path, nc_b: Path) -> None:
    """Show the dimensions of each file."""
    _print_dims(nc_a)
    _print_dims(nc_b)

def compare_groups(nc_a: Path, nc_b: Path) -> None:
    """Show the groups in each NetCDF file."""
    glist_a = _print_groups(nc_a)
    glist_b = _print_groups(nc_b)
    _lists_diff(glist_a, glist_b)

def compare_ingroup_variables(nc_a: Path, nc_b: Path, groupname: str) -> None:
    """Show the variables within the selected group."""
    vlist_a = _print_vars(nc_a, groupname)
    vlist_b = _print_vars(nc_b, groupname)
    _lists_diff(vlist_a, vlist_b)

def compare_sample_values(nc_a: Path, nc_b: Path, groupname: str, varname: str) -> None:
    """Print the first part of the values array for the selected variable."""
    _print_sample_values(nc_a, groupname, varname)
    _print_sample_values(nc_b, groupname, varname)

def compare_multiple_random_values(nc_a: Path, nc_b: Path, groupname: str, varname: str, num_comparisons: int = 100):
    """Iterate through N random samples, and evaluate whether the differences exceed a threshold."""
    # Open a variable from each NetCDF
    nc_var_a = xr.open_dataset(nc_a, backend_kwargs={"group": groupname})[varname]
    nc_var_b = xr.open_dataset(nc_b, backend_kwargs={"group": groupname})[varname]

    num_mismatches = 0
    for i in range(num_comparisons):
        if _match_random_value(nc_var_a, nc_var_b):
            print_normal(".", end="")
        else:
            num_mismatches += 1

    if num_mismatches > 0:
        print(Fore.RED + f" {num_mismatches} mismatches, out of {num_comparisons} samples.")
    else:
        print(Fore.CYAN + " No mismatches.")
    print_normal("Done.")

def compare_two_nc_files(nc_one: Path, nc_two: Path,
                         show_chunks: bool = False
                         ) -> None:
    """Go through all groups and all variables, and show them side by side - whether they align and where they don't."""
    _side_by_side(' ', 'File A', 'File B')
    with netCDF4.Dataset(nc_one) as nc_a, netCDF4.Dataset(nc_two) as nc_b:

        _side_by_side('-', '-', '-', dash_line=True)
        _side_by_side('num variables in root group:', len(nc_a.variables), len(nc_b.variables))
        for v_idx, v_a, v_b in _common_elements(nc_a.variables, nc_b.variables):
            _print_var_properties_side_by_side(v_a, v_b, nc_a, nc_b, show_chunks=show_chunks)

        for g_idx, g_a, g_b in _common_elements(nc_a.groups, nc_b.groups):
            _side_by_side(f"group #{g_idx:02}", g_a.strip(), g_b.strip(), dash_line=True, highlight_diff=False)

            vars_a_sorted = ""
            vars_b_sorted = ""
            if g_a:
                vars_a_sorted = sorted(nc_a.groups[g_a].variables)
            if g_b:
                vars_b_sorted = sorted(nc_b.groups[g_b].variables)
            _side_by_side('num variables in groups:', len(vars_a_sorted), len(vars_b_sorted))

            for v_idx, v_a, v_b in _common_elements(vars_a_sorted, vars_b_sorted):
                _print_var_properties_side_by_side(v_a, v_b, nc_a, nc_b, g_a=g_a, g_b=g_b, show_chunks=show_chunks)

def _side_by_side_list_diff(list_a: list, list_b: list, counter_prefix=""):
    for i, a, b in _common_elements(list_a, list_b):
        _side_by_side(f"{counter_prefix} #{i:02}", a.strip(), b.strip(), dash_line=True, highlight_diff=True)

def _common_elements(sequence_a, sequence_b):
    """Loop over the combined items of two lists, and return them aligned, whether matching or not."""
    a_sorted = sorted(sequence_a)
    b_sorted = sorted(sequence_b)
    all_items = sorted(set(a_sorted).union(set(b_sorted)))

    for i, item in enumerate(all_items):
        item_a = item
        item_b = item
        if (item not in a_sorted) and (item not in b_sorted):
            raise ValueError(
                "Unexpected condition where an item was not found "
                "but all items should exist in at least one list.")
        elif item not in a_sorted:
            item_a = ''
        elif item not in b_sorted:
            item_b = ''

        yield i, item_a, item_b

def _print_var_properties_side_by_side(v_a, v_b, nc_a, nc_b,
                                       g_a=None,
                                       g_b=None,
                                       show_chunks=False):
    # Variable name
    _side_by_side("var:", v_a[:47], v_b[:47], highlight_diff=False)

    # Get the properties of each variable
    variable_a, v_a_dtype, v_a_shape, v_a_chunking = _var_properties(nc_a, v_a, g_a)
    variable_b, v_b_dtype, v_b_shape, v_b_chunking = _var_properties(nc_b, v_b, g_b)

    # Data type
    _side_by_side("dtype:", v_a_dtype, v_b_dtype, highlight_diff=False)
    # Shape
    _side_by_side("shape:", v_a_shape, v_b_shape, highlight_diff=False)
    # Chunking
    if show_chunks:
        _side_by_side("chunksize:", v_a_chunking, v_b_chunking, highlight_diff=False)

    # Scale Factor
    if getattr(variable_a, 'scale_factor', None):
        sf_a = variable_a.scale_factor
    else:
        sf_a = ' '
    if getattr(variable_b, 'scale_factor', None):
        sf_b = variable_b.scale_factor
    else:
        sf_b = ' '
    _side_by_side("sf:", str(sf_a), str(sf_b), highlight_diff=True)

def _var_properties(ds: netCDF4.Dataset, varname: str, groupname: str = None) -> tuple:
    """Get the properties of a variable.

    Parameters
    ----------
    ds
    varname
    groupname : optional
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
    """
    if varname:
        if groupname:
            the_variable = ds.groups[groupname].variables[varname]
        else:
            the_variable = ds.variables[varname]
        v_dtype = str(the_variable.dtype)
        v_shape = str(the_variable.shape).strip()
        v_chunking = str(the_variable.chunking()).strip()
    else:
        the_variable = None
        v_dtype = ""
        v_shape = ""
        v_chunking = ""

    return the_variable, v_dtype, v_shape, v_chunking

def _side_by_side(str_a, str_b, str_c, dash_line=False, highlight_diff=False):
    # If the 'b' and 'c' strings are different, then change the font of 'a' to the color red.
    if highlight_diff and (str_b != str_c):
        str_a = Fore.RED + str_a
        print_func = print
    else:
        print_func = print_normal

    if dash_line:
        print_func(f" {str_a:>28} {str_b:->48} {str_c:->48}")
    else:
        print_func(f" {str_a:>28} {str_b:>48} {str_c:>48}")

def _match_random_value(nc_var_a: netCDF4.Variable,
                        nc_var_b: netCDF4.Variable,
                        thresh: float = 1e-6):
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
        return True
    else:
        diff = v2 - v1
        if abs(diff) > thresh:
            print()
            print(Fore.RED + f"Difference exceeded threshold (diff == {diff}")
            print_normal(f"var shape: {nc_var_a.shape}")
            print_normal(f"indices:   {rand_index}")
            print_normal(f"value a: {v1}")
            print_normal(f"value b: {v2}", end="\n\n")
            return False
        else:
            return True

def _lists_diff(list_a, list_b):
    """Compare two lists and state whether there are differences."""
    # TODO: make this highlight the differences too.
    # Are these list contents the same?
    groups_are_same = set(list_a) == set(list_b)
    if groups_are_same:
        print(Fore.CYAN + "Are lists the same? ---> %s." % str(groups_are_same))
    else:
        print(Fore.RED + "Are lists the same? ---> %s." % str(groups_are_same))

        # Which variables are different?
        print(Fore.RED + "Which items are different?")
        # print(Fore.RED + "Which items are different? ---> %s." %
        #       str(set(list_a).symmetric_difference(list_b)))
        _side_by_side(' ', 'File A', 'File B')
        _side_by_side_list_diff(list_a, list_b)

def _print_sample_values(nc_filepath, groupname: str, varname: str) -> None:
    comparison_variable = xr.open_dataset(nc_filepath, backend_kwargs={"group": groupname})[varname]
    print_normal(comparison_variable.values[0, :])

def _print_vars(nc_filepath: Path, groupname: str) -> list:
    try:
        grp = xr.open_dataset(nc_filepath, backend_kwargs={"group": groupname})
    except OSError as err:
        print_normal("\nError occurred when attempting to open group within <%s>.\n" % nc_filepath)
        raise err
    grp_varlist = sorted(list(grp.variables.keys()))
    print_normal(grp_varlist)
    return grp_varlist

def _print_groups(nc_filepath: Path) -> list:
    with netCDF4.Dataset(nc_filepath) as ds:
        groups_list = list(ds.groups.keys())

    print_normal(sorted(groups_list))
    return groups_list

def _print_dims(nc_filepath: Path) -> None:
    with xr.open_dataset(nc_filepath) as ds:
        print_normal(str(sorted(ds.dims.items())))
