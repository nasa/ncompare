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
from pathlib import Path

import earthaccess
import netCDF4 as nC
import numpy as np
import pytest
from xarray import Dataset

from ncompare.printing import Outputter


@pytest.fixture(scope="session")
def icesat2_cache_dir():
    """Persistent cache directory for ICESat-2 test data."""
    cache_dir = Path.home() / ".cache" / "icesat2_test_data"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


@pytest.fixture(scope="session")
def earthdata_auth():
    """
    Authenticate with NASA Earthdata.
    Uses credentials from environment variables or .netrc file.
    """
    # Check for environment variables (used in CI)
    username = os.getenv("EARTHDATA_USERNAME")
    password = os.getenv("EARTHDATA_PASSWORD")

    if username and password:
        earthaccess.login(strategy="environment")
    else:
        # Use .netrc or prompt for local testing
        earthaccess.login()

    return True


@pytest.fixture(scope="session")
def icesat2_atl06_granule_1(icesat2_cache_dir, earthdata_auth):
    """
    Download or use cached ICESat-2 ATL06 granule #1 for comparison tests.
    Temporal range: 2023-08-16 16:16:15 to 2023-08-16 16:25:00
    """
    # Check if already cached
    cached_files = list(icesat2_cache_dir.glob("ATL06_20230816161508_*.h5"))
    if cached_files:
        return str(cached_files[0])

    # Download if not cached
    results = earthaccess.search_data(
        short_name="ATL06", temporal=("2023-08-16 16:16:15", "2023-08-16 16:25:00"), count=1
    )

    if not results:
        pytest.skip("ICESat-2 granule #1 not found for test")

    # Download the data
    files = earthaccess.download(results, str(icesat2_cache_dir))

    if not files:
        pytest.skip("Failed to download ICESat-2 granule #1")

    return files[0]


@pytest.fixture(scope="session")
def icesat2_atl06_granule_2(icesat2_cache_dir, earthdata_auth):
    """
    Download or use cached ICESat-2 ATL06 granule #2 for comparison tests.
    Temporal range: 2023-08-16 23:46:00 to 2023-08-16 23:48:00
    """
    # Check if already cached
    cached_files = list(icesat2_cache_dir.glob("ATL06_20230816234629_*.h5"))
    if cached_files:
        return str(cached_files[0])

    # Download if not cached
    results = earthaccess.search_data(
        short_name="ATL06", temporal=("2023-08-16 23:46:00", "2023-08-16 23:48:00"), count=1
    )

    if not results:
        pytest.skip("ICESat-2 granule #2 not found for test")

    # Download the data
    files = earthaccess.download(results, str(icesat2_cache_dir))

    if not files:
        pytest.skip("Failed to download ICESat-2 granule #2")

    return files[0]


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
    grp1["step"].scale_factor = 0.5
    grp1["step"].add_offset = 5
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
