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
<a href="https://github.com/python/black" target="_blank">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style">
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

Compare the structure of two NetCDF files at the command line.
`ncompare` generates a view of the matching and non-matching groups and variables between two NetCDF datasets.


## Installing

Install the latest version of the package from the Python Package Index (PyPI):
```console
pip install ncompare
```


## Usage

To compare two netCDF files,
pass the filepaths for each of the two netCDF files directly to ncompare, as follows:

```console
ncompare <netcdf file #1> <netcdf file #2>
```

With an additional `--file-text` argument specified,
a common use of _ncompare_ may look like this example:

```console
ncompare S001G01.nc S001G01_SUBSET.nc --file-text subset_comparison.txt
```


**A more complete usage demonstration with example output is shown in
[this example notebook](https://ncompare.readthedocs.io/en/latest/example/ncompare-example-usage/).**

### Options

- `-h`, `--help` : Show this help message and exit.
- `--file-text` [FILE_PATH]: Text file to write output to.
- `--file-csv` [FILE_PATH]: Comma-separated values (CSV) file to write output to.
- `--file-xlsx` [FILE_PATH]: Excel file to write output to.
- `--only-diffs` : Only display variables and attributes that are different
- `--no-color` : Turn off all colorized output.
- `--show-attributes` : Include variable attributes in the table that compares variables.
- `--show-chunks` : Include chunk sizes in the table that compares variables.
- `-v` (`--comparison_var_name`) [VAR_NAME]: Compare specific values for this variable.
- `-g` (`--comparison_var_group`) [VAR_GROUP]: Group that contains the `comparison_var_name`.
- `--column-widths` [WIDTH, WIDTH, WIDTH]: Width, in number of characters, of the three columns in the comparison report
- `--version` : Show the current version and then exit.

## Contributing

Contributions are welcome! For more information, see [CONTRIBUTING.md](CONTRIBUTING.md).
_ncompare_ is licensed under the NASA Open Source Agreement, which is included
[in this repository's license directory](license/LAR-20274-1_ncompare_NetCDF_structural_comparison_tool_NOSA_1.3.pdf)
and [on the Open Source Initiative website](https://opensource.org/license/nasa1-3-php/).


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
[does not support NetCDF4 groups](https://code.mpimet.mpg.de/boards/2/topics/12073).
Moreover, `nco` operators' `ncdiff` function computes value differences, but
--- as far as the developers of this tool are aware ---
`nco` does not have a simple function to show structural differences between NetCDF4 datasets.
 Note that `h5diff`, provided in the HDF5 software, can also be used to find differences.
In comparison to `h5diff`, `ncompare` is written and runnable in Python; `ncompare` provides _aligned_ and
_colorized_ difference report for quicker assessments of groups, variable names, types, shapes, and attributes;
and can generate report files formatted for other applications. However, note that
`h5diff` provides comparison of some otherwise "hidden" hdf5 properties, such as _Netcdf4Dimid or _Netcdf4Coordinates,
which are not currently assessed by `ncompare`.

## Known limitations

- `ncompare` uses `xarray` to access the root-level dimensions.
In some cases, `xarray` will miss dimensions whose names do not also exist as variable names in the dataset
  (also known as non-coordinate dimensions).
- Some underlying HDF5 properties, such as _Netcdf4Dimid or _Netcdf4Coordinates, are not currently assesssed by `ncompare`.

# Notices:

Copyright 2023 United States Government as represented by the Administrator of the National Aeronautics and Space Administration.  All Rights Reserved.

### Third-Party Software:
This software calls the following third-party software, which is subject to the terms and conditions of its licensor,
as applicable at the time of licensing. Third-party software is not bundled with this software,
but may be available from the licensor.

License hyperlinks are provided here for information purposes only:

| item     |                               license                               | link                                                          |
|:---------|:-------------------------------------------------------------------:|:--------------------------------------------------------------|
| colorama |                            BSD-3-Clause                             | https://opensource.org/licenses/BSD-3-Clause                  |
| netCDF4  |                             MIT License                             | https://opensource.org/licenses/MIT                           |
| numpy    |                            BSD-3-Clause                             | https://opensource.org/licenses/BSD-3-Clause                  |
| openpyxl |                             MIT License                             | https://opensource.org/licenses/MIT                           |
| xarray   |                     Apache License, version 2.0                     | https://www.apache.org/licenses/LICENSE-2.0                   |
| Python   | Standard Library Python Software Foundation (PSF) License Agreement | https://docs.python.org/3/license.html#psf-licenseDisclaimers |


### No Warranty:
THE SUBJECT SOFTWARE IS PROVIDED "AS IS" WITHOUT ANY WARRANTY OF ANY KIND, EITHER EXPRESSED, IMPLIED,
OR STATUTORY, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTY THAT THE SUBJECT SOFTWARE WILL CONFORM TO SPECIFICATIONS,
ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR FREEDOM FROM INFRINGEMENT,
ANY WARRANTY THAT THE SUBJECT SOFTWARE WILL BE ERROR FREE, OR ANY WARRANTY THAT DOCUMENTATION, IF PROVIDED,
WILL CONFORM TO THE SUBJECT SOFTWARE. THIS AGREEMENT DOES NOT, IN ANY MANNER,
CONSTITUTE AN ENDORSEMENT BY GOVERNMENT AGENCY OR ANY PRIOR RECIPIENT OF ANY RESULTS, RESULTING DESIGNS, HARDWARE,
SOFTWARE PRODUCTS OR ANY OTHER APPLICATIONS RESULTING FROM USE OF THE SUBJECT SOFTWARE.
FURTHER, GOVERNMENT AGENCY DISCLAIMS ALL WARRANTIES AND LIABILITIES REGARDING THIRD-PARTY SOFTWARE,
IF PRESENT IN THE ORIGINAL SOFTWARE, AND DISTRIBUTES IT "AS IS."

### Waiver and Indemnity:
RECIPIENT AGREES TO WAIVE ANY AND ALL CLAIMS AGAINST THE UNITED STATES GOVERNMENT,
ITS CONTRACTORS AND SUBCONTRACTORS, AS WELL AS ANY PRIOR RECIPIENT. IF RECIPIENT'S USE OF THE SUBJECT SOFTWARE RESULTS
IN ANY LIABILITIES, DEMANDS, DAMAGES, EXPENSES OR LOSSES ARISING FROM SUCH USE, INCLUDING ANY DAMAGES FROM PRODUCTS
BASED ON, OR RESULTING FROM, RECIPIENT'S USE OF THE SUBJECT SOFTWARE, RECIPIENT SHALL INDEMNIFY AND HOLD HARMLESS
THE UNITED STATES GOVERNMENT, ITS CONTRACTORS AND SUBCONTRACTORS, AS WELL AS ANY PRIOR RECIPIENT,
TO THE EXTENT PERMITTED BY LAW. RECIPIENT'S SOLE
REMEDY FOR ANY SUCH MATTER SHALL BE THE IMMEDIATE, UNILATERAL TERMINATION OF THIS AGREEMENT.
