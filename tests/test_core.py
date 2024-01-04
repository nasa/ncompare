import pytest
import xarray as xr

from ncompare.core import _get_vars, _match_random_value, _print_sample_values, compare


def test_dataset_compare_does_not_raise_exception(ds_3dims_2vars_4coords, ds_4dims_3vars_5coords):
    compare(ds_3dims_2vars_4coords, ds_4dims_3vars_5coords)


def test_dataset_compare_does_not_raise_exception_2(
    ds_3dims_2vars_4coords, ds_3dims_3vars_4coords_1group
):
    compare(ds_3dims_2vars_4coords, ds_3dims_3vars_4coords_1group)


def test_matching_random_values(
    ds_3dims_2vars_4coords,
    ds_4dims_3vars_5coords,
    ds_3dims_3vars_4coords_1group,
    outputter_to_console,
):
    variable_array_1 = xr.open_dataset(ds_3dims_2vars_4coords).variables['z1']
    variable_array_2 = xr.open_dataset(ds_4dims_3vars_5coords).variables['z1']

    assert (
        _match_random_value(
            outputter_to_console,
            variable_array_1,
            variable_array_1,
        )
        is True
    )
    assert (
        _match_random_value(
            outputter_to_console,
            variable_array_1,
            variable_array_2,
        )
        is False
    )


def test_print_values_runs_with_no_error(ds_3dims_3vars_4coords_1group, outputter_to_console):
    _print_sample_values(
        outputter_to_console, ds_3dims_3vars_4coords_1group, groupname="Group1", varname="step"
    )
    assert True


def test_print_values_to_text_file_runs_with_no_error(
    ds_3dims_3vars_4coords_1group, outputter_to_text_file, temp_test_text_file_path
):
    _print_sample_values(
        outputter_to_text_file, ds_3dims_3vars_4coords_1group, groupname="Group1", varname="step"
    )
    outputter_to_text_file._text_file_obj.close()

    comparison_variable = xr.open_dataset(
        ds_3dims_3vars_4coords_1group, backend_kwargs={"group": "Group1"}
    )["step"]

    with open(temp_test_text_file_path) as f:
        lines = f.readlines()
        assert lines[0].strip().replace("[", "").replace("]", "").split() == [
            str(round(x, 1)) for x in comparison_variable[:].values
        ]


def test_comparison_group_no_error_for_duplicate_dataset(
    ds_3dims_3vars_4coords_1group, temp_test_text_file_path
):
    compare(
        ds_3dims_3vars_4coords_1group,
        ds_3dims_3vars_4coords_1group,
        comparison_var_group="Group1",
        file_text=temp_test_text_file_path,
    )

    found_expected = False
    with open(temp_test_text_file_path) as f:
        for line in f.readlines():
            if "Variables within specified group <Group1>:" in line:
                found_expected = True

    if found_expected:
        assert True
    else:
        assert False


def test_comparison_var_no_error_for_duplicate_dataset(
    ds_3dims_3vars_4coords_1group, temp_test_text_file_path
):
    compare(
        ds_3dims_3vars_4coords_1group,
        ds_3dims_3vars_4coords_1group,
        comparison_var_group="Group1",
        comparison_var_name="var1",
        file_text=temp_test_text_file_path,
    )

    found_expected = False
    with open(temp_test_text_file_path) as f:
        for line in f.readlines():
            if "Sample values within specified variable <var1>:" in line:
                found_expected = True

    if found_expected:
        assert True
    else:
        assert False


def test_get_vars_with_group(ds_3dims_3vars_4coords_1group):
    result = _get_vars(ds_3dims_3vars_4coords_1group, groupname="Group1")
    assert set(result) == {'step', 'var1', 'var2', 'w'}


def test_get_vars_error_when_no_group(ds_3dims_2vars_4coords):
    with pytest.raises(OSError):
        _get_vars(ds_3dims_2vars_4coords, groupname="nonexistent_group")
