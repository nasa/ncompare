from ncompare.core import compare


def test_dataset_compare_does_not_raise_exception(ds_3dims_2vars_4coords, ds_4dims_3vars_5coords):
    compare(ds_3dims_2vars_4coords, ds_4dims_3vars_5coords)

def test_dataset_compare_does_not_raise_exception_2(ds_3dims_2vars_4coords, ds_3dims_3vars_4coords_1group):
    compare(ds_3dims_2vars_4coords, ds_3dims_3vars_4coords_1group)
