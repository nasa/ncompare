import xarray as xr

from ncompare.core import compare, _match_random_value


def test_dataset_compare_does_not_raise_exception(ds_3dims_2vars_4coords, ds_4dims_3vars_5coords):
    compare(ds_3dims_2vars_4coords, ds_4dims_3vars_5coords)

def test_dataset_compare_does_not_raise_exception_2(ds_3dims_2vars_4coords, ds_3dims_3vars_4coords_1group):
    compare(ds_3dims_2vars_4coords, ds_3dims_3vars_4coords_1group)

def test_matching_random_values(ds_3dims_2vars_4coords, ds_4dims_3vars_5coords,
                                ds_3dims_3vars_4coords_1group, outputter_obj):
    variable_array_1 = xr.open_dataset(ds_3dims_2vars_4coords).variables['z1']
    variable_array_2 = xr.open_dataset(ds_4dims_3vars_5coords).variables['z1']

    assert _match_random_value(outputter_obj, variable_array_1, variable_array_1, ) is True
    assert _match_random_value(outputter_obj, variable_array_1, variable_array_2, ) is False
