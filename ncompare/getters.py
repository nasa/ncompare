import warnings
from collections.abc import Iterable, Iterator
from typing import Union

import h5py
import netCDF4
import xarray as xr

from ncompare.core_types import FileToCompare, VarProperties
from ncompare.sequence_operations import common_elements


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


def _get_var_properties(
    group: Union[netCDF4.Dataset, netCDF4.Group], varname: str
) -> VarProperties:
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


def _get_root_groups(file: FileToCompare) -> list:
    """Get a list of groups from a netCDF."""
    if file.type == "netcdf":
        with netCDF4.Dataset(file.path) as dataset:
            groups_list = list(dataset.groups.keys())
    elif file.type == "hdf5":
        with h5py.File(file.path) as dataset:
            groups_list = list(dataset.keys())
    return groups_list


def _get_root_dims(file: FileToCompare) -> list:
    """Get a list of dimensions from a netCDF or HDF5."""

    def __get_dim_list(decode_times=True):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if file.type == "netcdf":
                xarray_engine = "netcdf4"
            elif file.type == "hdf5":
                xarray_engine = "h5netcdf"

            with xr.open_dataset(
                file.path, decode_times=decode_times, engine=xarray_engine
            ) as dataset:
                return list(dataset.sizes.items())

    try:
        dims_list = __get_dim_list()
    except ValueError as err:
        if "decode_times" in str(err):  # then try again without decoding the times
            dims_list = __get_dim_list(decode_times=False)
        else:
            raise err from None  # "from None" prevents additional trace (see https://stackoverflow.com/a/18188660)

    return dims_list
