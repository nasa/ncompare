import os

from ncompare.console import _cli


def test_console_version():
    exit_status = os.system('ncompare --version')
    assert exit_status == 0


def test_console_help():
    exit_status = os.system('ncompare --help')
    assert exit_status == 0


def test_arg_parser():
    parsed = _cli(["first_netcdf.nc", "second_netcdf.nc"])

    assert getattr(parsed, "nc_a") == "first_netcdf.nc"
    assert getattr(parsed, "nc_b") == "second_netcdf.nc"
    assert getattr(parsed, "show_attributes") is False
    assert getattr(parsed, "show_chunks") is False
    assert getattr(parsed, "only_diffs") is False
