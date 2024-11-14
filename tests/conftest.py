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

from pathlib import Path

import netCDF4 as nC
import numpy as np
import pytest
from xarray import Dataset

from ncompare.printing import Outputter


@pytest.fixture(scope="session")
def temp_data_dir(tmpdir_factory) -> Path:
    return Path(tmpdir_factory.mktemp("data"))


@pytest.fixture(scope="function")
def outputter_to_console():
    return Outputter()


@pytest.fixture(scope="session")
def temp_test_text_file_path(temp_data_dir):
    return Path(temp_data_dir) / "temp_test_text_file_output.txt"


@pytest.fixture(scope="function")
def outputter_to_text_file(temp_test_text_file_path):
    return Outputter(keep_print_history=True, text_file=temp_test_text_file_path.resolve())


@pytest.fixture(scope="session")
def ds_3dims_2vars_4coords(temp_data_dir) -> Path:
    ds = Dataset(
        data_vars=dict(
            # "normal" (Gaussian) distribution of mean 0 and variance 1
            z1=(["y", "x"], np.random.randn(2, 8)),
            z2=(["time", "y"], np.random.randn(10, 2)),
        ),
        coords=dict(
            x=("x", np.linspace(0, 1.0, 8)),
            time=("time", np.linspace(0, 1.0, 10)),
            c=("y", ["a", "b"]),
            y=range(2),
        ),
    )
    filepath = temp_data_dir / "test_3dims_2vars_4coords.nc"
    ds.to_netcdf(path=filepath)

    return filepath


@pytest.fixture(scope="session")
def ds_1dim_1var_1coord(temp_data_dir) -> Path:
    ds = Dataset(
        data_vars=dict(z1=(["y"], np.array([5, 6]))),
        coords=dict(
            y=range(2),
        ),
    )
    filepath = temp_data_dir / "test_1dim_1var_1coord.nc"
    ds.to_netcdf(path=filepath)

    return filepath


@pytest.fixture(scope="session")
def ds_1dim_1var_allnan_1coord(temp_data_dir) -> Path:
    ds = Dataset(
        data_vars=dict(z1=(["y"], np.array([np.nan, np.nan]))),
        coords=dict(
            y=range(2),
        ),
    )
    filepath = temp_data_dir / "test_1dim_1var_allnan_1coord.nc"
    ds.to_netcdf(path=filepath)

    return filepath


@pytest.fixture(scope="session")
def ds_4dims_3vars_5coords(temp_data_dir):
    ds = Dataset(
        data_vars=dict(
            # "normal" (Gaussian) distribution of mean 10 and standard deviation 2.5
            z1=(["y", "x"], 10 + 2.5 * np.random.randn(2, 8)),
            z2=(["time", "y"], np.random.randn(10, 2)),
            z3=(["y", "z"], np.random.randn(2, 9)),
        ),
        coords=dict(
            x=("x", np.linspace(0, 1.0, 8)),
            time=("time", np.linspace(0, 1.0, 10)),
            c=("y", ["a", "b"]),
            y=range(2),
            z=range(9),
        ),
    )
    filepath = temp_data_dir / "test_4dims_3vars_5coords.nc"
    ds.to_netcdf(path=filepath)

    return filepath


@pytest.fixture(scope="session")
def ds_3dims_3vars_4coords_1group(temp_data_dir):
    filepath = temp_data_dir / "test_3dims_3vars_4coords_1group.nc"

    f = nC.Dataset(filename=filepath, mode="w")
    grp1 = f.createGroup("Group1")

    # A root variable
    f.createVariable("var0", "i2", ())

    # New/modified coordinates in grp1
    grp1.createDimension("x", 2)
    grp1.createDimension("step", 3)
    grp1.createDimension("track", 7)

    # Variables in grp1
    grp1.createVariable("var1", "f8", ())
    #
    grp1.createVariable("var2", "f4", ())
    #
    grp1.createVariable("step", "f4", ("step",), fill_value=False)
    grp1["step"][:] = [-0.9, -1.8, -2.7]
    #
    grp1.createVariable("w", "u1", ("x", "step"), fill_value=False)

    # Wrap up
    f.close()

    return filepath


@pytest.fixture(scope="session")
def ds_3dims_3vars_4coords_2groups(temp_data_dir):
    filepath = temp_data_dir / "test_3dims_3vars_4coords_2groups.nc"

    f = nC.Dataset(filename=filepath, mode="w")
    grp1 = f.createGroup("Group1")
    grp2 = f.createGroup("Group2")

    # A root variable
    f.createVariable("var0", "i2", ())

    # New/modified coordinates in grp1
    grp1.createDimension("x", 2)
    grp1.createDimension("step", 3)
    grp1.createDimension("track", 7)

    # Variables in grp1
    grp1.createVariable("var1", "f8", ())
    #
    grp1.createVariable("var2", "f4", ())
    #
    grp1.createVariable("step", "f4", ("step",), fill_value=False)
    grp1["step"][:] = [-0.9, -1.8, -2.7]
    #
    grp1.createVariable("w", "u1", ("x", "step"), fill_value=False)

    # New/modified coordinates in grp2
    grp2.createDimension("x", 2)
    grp2.createDimension("step", 3)
    grp2.createDimension("track", 7)
    grp2.createDimension("level", 4)

    # Variables in grp2
    grp2.createVariable("var3", "f8", ("level",), fill_value=False)

    # Wrap up
    f.close()

    return filepath


@pytest.fixture(scope="session")
def ds_3dims_3vars_4coords_1subgroup(temp_data_dir):
    filepath = temp_data_dir / "test_3dims_3vars_4coords_1subgroup.nc"

    f = nC.Dataset(filename=filepath, mode="w")
    grp1 = f.createGroup("Group1")
    grp2 = f.createGroup("Group2")
    grp2_subgroup = grp2.createGroup("Group2_subgroup")

    # A root variable
    f.createVariable("var0", "i2", ())

    # New/modified coordinates in grp1
    grp1.createDimension("x", 2)
    grp1.createDimension("step", 3)
    grp1.createDimension("track", 7)

    # Variables in grp1
    grp1.createVariable("var1", "f8", ())
    #
    grp1.createVariable("var2", "f4", ())
    #
    grp1.createVariable("step", "f4", ("step",), fill_value=False)
    grp1["step"][:] = [-0.9, -1.8, -2.7]
    #
    grp1.createVariable("w", "u1", ("x", "step"), fill_value=False)

    # New/modified coordinates in grp2
    grp2.createDimension("step", 3)
    grp2.createDimension("level", 4)

    # Variables in grp2
    grp2.createVariable("var3", "f8", ("step", "level"), fill_value=False)

    # New/modified coordinates in grp2
    # Variables in grp2
    grp2_subgroup.createVariable("var4", "f8", ("level",), fill_value=False)

    # Wrap up
    f.close()

    return filepath
