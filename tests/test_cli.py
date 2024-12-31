# Copyright 2024 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software calls the following third-party software,
# which is subject to the terms and conditions of its licensor, as applicable.
# Users must license their own copies; the links are provided for convenience only.
#
# colorama - BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause
# netCDF4 - MIT License - https://opensource.org/licenses/MIT
# numpy - BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause
# openpyxl - MIT License - https://opensource.org/licenses/MIT
# xarray - Apache License, version 2.0 - https://www.apache.org/licenses/LICENSE-2.0
# Python Standard Library - Python Software Foundation (PSF) License Agreement-
#   https://docs.python.org/3/license.html#psf-license
#
# The ncompare: NetCDF structural comparison tool platform is licensed under the
# Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import os

from ncompare.console import _cli


def test_console_version():
    exit_status = os.system("ncompare --version")
    assert exit_status == 0


def test_console_help():
    exit_status = os.system("ncompare --help")
    assert exit_status == 0


def test_arg_parser():
    parsed = _cli(["first_netcdf.nc", "second_netcdf.nc"])

    assert getattr(parsed, "file_a") == "first_netcdf.nc"
    assert getattr(parsed, "file_b") == "second_netcdf.nc"
    assert getattr(parsed, "show_attributes") is False
    assert getattr(parsed, "show_chunks") is False
    assert getattr(parsed, "only_diffs") is False
