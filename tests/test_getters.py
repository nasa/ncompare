import h5py
import netCDF4
import numpy as np

from ncompare.getters import get_root_attributes, get_root_dims
from ncompare.utility_types import FileToCompare


def test_get_root_dims_pure_hdf5_without_dimension_scales(tmp_path):
    """A pure HDF5 file with no dimension scales reports no root dimensions (no crash)."""
    path = tmp_path / "pure.h5"
    with h5py.File(path, "w") as f:
        f.create_dataset("data", data=np.arange(4))

    assert get_root_dims(FileToCompare(path=path, type="hdf5")) == []


def test_get_root_dims_hdf5_with_dimension_scale(tmp_path):
    """Root dimensions are recovered from HDF5 dimension scales when present.

    Authored with netCDF4 (a coordinate variable is stored as an HDF5 dimension
    scale) so the scale is created portably; the file is then read via the h5py
    path in get_root_dims.
    """
    path = tmp_path / "scaled.h5"
    with netCDF4.Dataset(path, "w") as ds:
        ds.createDimension("x", 5)
        coordinate = ds.createVariable("x", "f4", ("x",))
        coordinate[:] = range(5)

    assert ("x", 5) in get_root_dims(FileToCompare(path=path, type="hdf5"))


def test_get_root_attributes_netcdf(tmp_path):
    filepath = tmp_path / "test_root_attrs.nc"
    with netCDF4.Dataset(filepath, mode="w") as ds:
        ds.setncattr("title", "Test Dataset")
        ds.setncattr("version", "1.0")

    result = get_root_attributes(FileToCompare(filepath, type="netcdf"))

    assert result == {"title": "Test Dataset", "version": "1.0"}


def test_get_root_attributes_hdf5(tmp_path):
    filepath = tmp_path / "test_root_attrs.h5"
    with h5py.File(filepath, mode="w") as ds:
        ds.attrs["title"] = "Test Dataset"
        ds.attrs["version"] = "1.0"

    result = get_root_attributes(FileToCompare(filepath, type="hdf5"))

    assert result == {"title": "Test Dataset", "version": "1.0"}


def test_get_root_attributes_hdf5_fixed_length_string_matches_netcdf(tmp_path):
    """HDF5 fixed-length string attributes should normalize to the same str as netCDF.

    ``h5py`` returns fixed-length string attributes as ``bytes`` (``b'NASA'``); without
    decoding, this would not compare equal to the netCDF ``str`` attribute (``'NASA'``)
    and would surface as a false root-attribute difference.
    """
    nc_path = tmp_path / "fixed_len.nc"
    with netCDF4.Dataset(nc_path, mode="w") as ds:
        ds.setncattr("source", "NASA")

    h5_path = tmp_path / "fixed_len.h5"
    with h5py.File(h5_path, mode="w") as ds:
        # Fixed-length ASCII string attribute -> read back by h5py as bytes.
        ds.attrs.create("source", np.bytes_(b"NASA"))

    nc_attrs = get_root_attributes(FileToCompare(nc_path, type="netcdf"))
    h5_attrs = get_root_attributes(FileToCompare(h5_path, type="hdf5"))

    assert h5_attrs["source"] == "NASA"
    assert nc_attrs == h5_attrs


def test_get_root_attributes_hdf5_array_of_fixed_length_strings(tmp_path):
    """An HDF5 attribute holding multiple fixed-length strings decodes every element.

    Unlike a scalar string attribute, this value arrives from h5py as a
    ``numpy.ndarray`` of ``bytes`` (dtype kind ``"S"``), which takes a separate
    branch in ``_value_to_comparable_str`` from the scalar-``bytes`` case covered
    by ``test_get_root_attributes_hdf5_fixed_length_string_matches_netcdf`` above.
    """
    filepath = tmp_path / "multi_string_attr.h5"
    with h5py.File(filepath, mode="w") as ds:
        ds.attrs.create("sources", np.array([b"NASA", b"JPL", b"GSFC"]))

    result = get_root_attributes(FileToCompare(filepath, type="hdf5"))

    assert result["sources"] == "[NASA, JPL, GSFC, ...]"


def test_get_root_attributes_degrades_gracefully_on_unreadable_file(tmp_path):
    """A file that can't be opened yields an empty dict instead of raising.

    Mirrors ``get_root_dims``'s degrade-gracefully behavior (see
    ``test_get_root_dims_pure_hdf5_without_dimension_scales``), so a file that
    can't be introspected doesn't abort the whole comparison.
    """
    filepath = tmp_path / "not_actually_netcdf.nc"
    filepath.write_bytes(b"not a real netcdf file")

    assert get_root_attributes(FileToCompare(filepath, type="netcdf")) == {}


# def test_var_properties(ds_3dims_3vars_4coords_1group):
#     with nc.Dataset(ds_3dims_3vars_4coords_1group) as ds:
#         result = get_var_properties(ds.groups["Group1"], varname="step", file_type="netcdf")
#         assert result.varname == "step"
#         assert result.dtype == "float32"
#         assert result.shape == "(3,)"
#         assert result.chunking == "contiguous"
#         assert result.attributes == {"add_offset": 5, "scale_factor": 0.5}
#
#
# def test_get_scale_factor(ds_3dims_3vars_4coords_1group):
#     with nc.Dataset(ds_3dims_3vars_4coords_1group) as ds:
#         step_varProps = get_var_properties(ds.groups["Group1"], varname="step", file_type="netcdf")
#
#         result = get_and_check_variable_scale_factor(step_varProps, step_varProps)
#         assert result == ("0.5", "0.5")
