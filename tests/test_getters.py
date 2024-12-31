import netCDF4 as nc

from ncompare.getters import get_and_check_variable_scale_factor, get_var_properties


def test_var_properties(ds_3dims_3vars_4coords_1group):
    with nc.Dataset(ds_3dims_3vars_4coords_1group) as ds:
        result = get_var_properties(ds.groups["Group1"], varname="step")
        assert result.varname == "step"
        assert result.dtype == "float32"
        assert result.shape == "(3,)"
        assert result.chunking == "contiguous"
        assert result.attributes == {"add_offset": 5, "scale_factor": 0.5}


def test_get_scale_factor(ds_3dims_3vars_4coords_1group):
    with nc.Dataset(ds_3dims_3vars_4coords_1group) as ds:
        step_varProps = get_var_properties(ds.groups["Group1"], varname="step")

        result = get_and_check_variable_scale_factor(step_varProps, step_varProps)
        assert result == ("0.5", "0.5")
