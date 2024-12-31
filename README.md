# ncompare
_____

<a href="https://www.repostatus.org/#active" target="_blank">
    <img src="https://www.repostatus.org/badges/latest/active.svg" alt="Project Status: Active – The project has reached a stable, usable state and is being actively developed">
</a>
<a href="https://codecov.io/gh/nasa/ncompare">
 <img src="https://codecov.io/gh/nasa/ncompare/graph/badge.svg?token=5JJUNA1Z6S" alt="Code coverage">
</a>
<a href="https://ncompare.readthedocs.io/en/latest/?badge=latest">
    <img src="https://readthedocs.org/projects/ncompare/badge/?version=latest" alt="Documentation Status">
</a>
<a href="https://pypi.org/project/ncompare/" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/ncompare.svg" alt="Python Versions">
</a>
<a href="https://pypi.org/project/ncompare" target="_blank">
    <img src="https://img.shields.io/pypi/v/ncompare?color=%2334D058label=pypi%20package" alt="Package version">
</a>
<a href="https://mypy-lang.org/" target="_blank">
    <img src="https://www.mypy-lang.org/static/mypy_badge.svg" alt="Mypy checked">
</a>
<a href="https://github.com/nasa/ncompare/issues" target="_blank">
    <img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?" alt="Contributions welcome">
</a>
<a href="https://doi.org/10.5281/zenodo.10625407" target="_blank">
    <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.10625407.svg" alt="Zenodo">
</a>
<a href="https://github.com/pyOpenSci/software-review/issues/146" target="_blank">
    <img src="https://tinyurl.com/y22nb8up?" alt="pyOpenSci">
</a>
<a style="border-width:0" href="https://doi.org/10.21105/joss.06490">
  <img src="https://joss.theoj.org/papers/10.21105/joss.06490/status.svg" alt="DOI badge" >
</a>

Compare the structure of two [netCDF](https://www.unidata.ucar.edu/software/netcdf) files 
at the command line or via Python. `ncompare` generates a view of the matching and 
non-matching groups and variables between two netCDF datasets.

Allthough tailored for netCDF files, `ncompare`
also works with some [HDF5](https://www.hdfgroup.org/solutions/hdf5/) files 
(see [notes and known limitations](#notes-and-known-limitations)).


## Installing

The latest release of `ncompare` can be installed with `mamba`, `conda` or `pip`:

```bash
mamba install -c conda-forge ncompare
```
```bash
conda install -c conda-forge ncompare
```
```bash
pip install ncompare
```

## Usage Examples

### At a command line:
To compare two netCDF files,
pass the filepaths for each of the two netCDF files directly to ncompare, as follows:

```console
ncompare <netcdf file #1> <netcdf file #2>
```

<img src="https://github.com/nasa/ncompare/assets/114174502/1964096e-829d-4fe1-96a5-63581ade2d38" width="600" />


With an additional `--file-text` argument specified,
a common use of _ncompare_ may look like this example:

```console
ncompare S001G01.nc S001G01_SUBSET.nc --file-text subset_comparison.txt
```

### In a Python kernel:

```python
from ncompare import compare

total_number_of_differences = compare("<netcdf file 1>", "<netcdf file 2>", only_diffs=True,
                                      show_chunks=True, show_attributes=True)
```


### More complete usage demonstrations, with example output, are shown in [this example notebook](https://ncompare.readthedocs.io/en/latest/example/ncompare-example-usage/).

## Contributing

Contributions are welcome! For more information, see [CONTRIBUTING.md](CONTRIBUTING.md).
_ncompare_ is licensed under the Apache License 2.0,
which is included in the [LICENSE](LICENSE) file.


### Developing

Development within this repository should occur on a feature branch.
Pull Requests (PRs) are created with a target of the `develop` branch before being reviewed and merged.

### Installing locally

For local development, one can clone the repository and then use poetry or pip from the local directory:

```console
git clone https://github.com/nasa/ncompare.git
```

###### (Option A) using poetry:
ii) Follow the instructions for installing `poetry` [here](https://python-poetry.org/docs/).

iii) Run ```poetry install``` from the repository directory.

###### (Option B) using pip:

ii) Run ```pip install .``` from the repository directory.


### Testing locally

If installed using a `poetry` environment, the tests can be run with:
```console
poetry run pytest tests
```

Or from another virtual environment, one can use:
```console
pytest tests
```

### To run as a locally installed poetry module

```console
poetry run ncompare <netcdf file #1> <netcdf file #2>
```


## Why ncompare?

The `cdo` (climate data operators) tool
[does not support netCDF4 groups](https://code.mpimet.mpg.de/boards/2/topics/12073).
Moreover, `nco` operators' `ncdiff` function computes value differences, but
--- as far as the developers of this tool are aware ---
`nco` does not have a simple function to show structural differences between NetCDF4 datasets.
 Note that `h5diff`, provided in the HDF5 software, can also be used to find differences.
In comparison to `h5diff`, `ncompare` is written and runnable in Python; `ncompare` provides _aligned_ and
_colorized_ difference report for quicker assessments of groups, variable names, types, shapes, and attributes;
and can generate report files formatted for other applications. However, note that
`h5diff` provides comparison of some otherwise "hidden" hdf5 properties, such as _Netcdf4Dimid or _Netcdf4Coordinates,
which are not currently assessed by `ncompare`.

## Notes and known limitations

- `ncompare` works successfully with select HDF5 files,
  although it has not been tested extensively; therefore,
  it would not be surprising to find additional limitations with other HDF files.
- `ncompare` uses `xarray` to access the root-level dimensions.
In some cases, `xarray` will miss dimensions whose names do not also exist as variable names in the dataset
  (also known as non-coordinate dimensions).
- Some underlying HDF5 properties, such as _Netcdf4Dimid or _Netcdf4Coordinates, are not currently assesssed by `ncompare`.

# Notices:

Copyright 2023 United States Government as represented by the Administrator of the
National Aeronautics and Space Administration. All Rights Reserved.

This software calls the following third-party software,
which is subject to the terms and conditions of its licensor,
as applicable at the time of licensing.
The third-party software is not bundled with this software but may be available from the licensor.

License hyperlinks are provided here for information purposes only.


| Title    |                               license                               | link                                                          |
|:---------|:-------------------------------------------------------------------:|:--------------------------------------------------------------|
| colorama |                            BSD-3-Clause                             | https://opensource.org/licenses/BSD-3-Clause                  |
| netCDF4  |                             MIT License                             | https://opensource.org/licenses/MIT                           |
| numpy    |                            BSD-3-Clause                             | https://opensource.org/licenses/BSD-3-Clause                  |
| openpyxl |                             MIT License                             | https://opensource.org/licenses/MIT                           |
| xarray   |                     Apache License, version 2.0                     | https://www.apache.org/licenses/LICENSE-2.0                   |
| Python   | Standard Library Python Software Foundation (PSF) License Agreement | https://docs.python.org/3/license.html#psf-licenseDisclaimers |


The ncompare: NetCDF structural comparison tool framework is licensed under the Apache License,
Version 2.0 (the "License");
you may not use this application except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

---
This package is NASA Software Release Authorization (SRA) # LAR-20274-1
