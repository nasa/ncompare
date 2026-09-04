import warnings
from collections.abc import Iterable, Iterator

import h5py
import netCDF4
import numpy as np
import xarray as xr

from ncompare.sequence_operations import common_elements
from ncompare.utility_types import FileToCompare, VarProperties


def get_and_check_variable_scale_factor(
    v_a: VarProperties, v_b: VarProperties
) -> None | tuple[str, str]:
    """Get a string representation of the scale factor for two variables."""
    sf_a = getattr(v_a.variable, "scale_factor", " ")
    sf_b = getattr(v_b.variable, "scale_factor", " ")

    if (sf_a != " ") or (sf_b != " "):
        return str(sf_a), str(sf_b)
    else:
        return None


def get_and_check_variable_attributes(
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
        attr_a = get_attribute_value_as_str(v_a, attr_a_key)
        attr_b = get_attribute_value_as_str(v_b, attr_b_key)
        yield attr_a_key, attr_a, attr_b_key, attr_b


def _value_to_comparable_str(value: object) -> str:
    """Render an attribute value as the string ncompare compares and displays.

    Byte strings are decoded first: ``h5py`` returns HDF5 fixed-length string
    attributes as ``bytes`` (``b'NASA'``) whereas the equivalent netCDF attribute
    is a ``str`` (``'NASA'``), and decoding keeps the two comparable and free of an
    ugly ``b'...'`` in the report. It has to happen before the iterable check
    below, because ``bytes`` is itself iterable and would otherwise render as a
    list of integers (``[78, 65, 83, 65]``).

    Parameters
    ----------
    value
        the raw attribute value, as returned by ``netCDF4`` or ``h5py``

    Returns
    -------
    str
        the value as a string; a long iterable is truncated to five elements
    """
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.ndarray) and value.dtype.kind in ("S", "O"):
        value = [
            item.decode("utf-8", errors="replace") if isinstance(item, bytes) else item
            for item in value.tolist()
        ]
    if isinstance(value, Iterable) and not isinstance(value, (str, float)):
        # TODO: by truncating a list (or other iterable) here,
        #  we are preventing any subsequent difference checker from detecting
        #  differences past the 5th element in the iterable.
        #  So, we need to figure out a way to still check for other differences past the 5th element.
        return "[" + ", ".join([str(x) for x in list(value)[:5]]) + ", ..." + "]"
    return str(value)


def get_attribute_value_as_str(varprops: VarProperties, attribute_key: str) -> str:
    """Get a string representation of the attribute value."""
    if attribute_key and (attribute_key in varprops.attributes):
        return _value_to_comparable_str(varprops.attributes[attribute_key])

    return ""


def get_root_groups(file: FileToCompare) -> list:
    """Get a list of groups from a netCDF."""
    if file.type == "netcdf":
        with netCDF4.Dataset(file.path) as dataset:
            groups_list = list(dataset.groups.keys())
    elif file.type == "hdf5":
        with h5py.File(file.path) as dataset:
            groups_list = list(dataset.keys())
    return groups_list


def get_root_attributes(file: FileToCompare) -> dict:
    """Get the global (root-level) attributes of a netCDF or HDF5 file.

    Parameters
    ----------
    file
        the file whose root-level attributes are wanted

    Returns
    -------
    dict
        attribute name -> value, each rendered with ``_value_to_comparable_str``;
        an empty dict if the file's attributes cannot be read
    """
    attributes: dict = {}
    try:
        if file.type == "netcdf":
            with netCDF4.Dataset(file.path, mode="r") as dataset:
                for name in dataset.ncattrs():
                    attributes[name] = _value_to_comparable_str(dataset.getncattr(name))
        elif file.type == "hdf5":
            with h5py.File(file.path, mode="r") as dataset:
                for name in dataset.attrs.keys():
                    attributes[name] = _value_to_comparable_str(dataset.attrs[name])
    except (OSError, RuntimeError, KeyError):
        # Mirrors _get_hdf5_root_dims: some files can't be introspected; degrade gracefully.
        return {}
    return attributes


def get_subgroups(node: netCDF4.Dataset | netCDF4.Group | h5py.Group, file_type: str) -> list:
    """Get a list of subgroups from a netCDF or HDF5 group.

    Parameters
    ----------
    node
    file_type

    Returns
    -------
    list or None
        subgroups under the node
    """
    if node is None:
        return []
    elif file_type == "hdf5":
        return [key for key in node.keys() if isinstance(node[key], h5py.Group)]
    else:  # should be "netcdf"
        return list(node.groups)


def get_variables(node: netCDF4.Dataset | netCDF4.Group | h5py.Group, file_type: str) -> list:
    """Get a sorted list of variables from a netCDF or HDF5 group."""
    if file_type == "hdf5":
        return [key for key in node.keys() if isinstance(node[key], h5py.Dataset)]
    else:  # should be "netcdf"
        return sorted(node.variables)


def get_root_dims(file: FileToCompare) -> list:
    """Get a list of root-level dimensions from a netCDF or HDF5 file."""
    if file.type == "hdf5":
        return _get_hdf5_root_dims(file.path)
    return _get_netcdf_root_dims(file.path)


def _get_netcdf_root_dims(path) -> list:
    """Get a list of root-level dimensions from a netCDF file (via xarray)."""

    def __get_dim_list(decode_times=True):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with xr.open_dataset(path, decode_times=decode_times, engine="netcdf4") as dataset:
                return list(dataset.sizes.items())

    try:
        return __get_dim_list()
    except ValueError as err:
        if "decode_times" in str(err):  # then try again without decoding the times
            return __get_dim_list(decode_times=False)
        raise err from None  # "from None" prevents additional trace (see https://stackoverflow.com/a/18188660)


def _get_hdf5_root_dims(path) -> list:
    """Get a list of root-level dimensions from an HDF5 file (via h5py).

    HDF5 has no netCDF-style named dimensions; they are represented by optional
    HDF5 dimension scales. Files with dimension scales -- including netCDF4 files,
    which are a subset of HDF5 -- report those; a pure HDF5 file with none reports
    no root-level dimensions rather than raising, so the rest of the structural
    comparison can still proceed.
    """
    dims: list[tuple[str, int]] = []
    try:
        with h5py.File(path, "r") as dataset:
            for name, obj in dataset.items():
                if not isinstance(obj, h5py.Dataset):
                    continue
                class_attr = obj.attrs.get("CLASS")
                if isinstance(class_attr, bytes):
                    class_attr = class_attr.decode("utf-8", errors="replace")
                if class_attr == "DIMENSION_SCALE":
                    size = obj.shape[0] if obj.shape else obj.size
                    dims.append((name, int(size)))
    except (OSError, RuntimeError, KeyError):
        # Some HDF5 files cannot be introspected for dimensions; degrade gracefully.
        return []
    return sorted(dims)
