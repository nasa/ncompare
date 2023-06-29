# ncompare
_____
Compare the structure of two NetCDF files at the command line.
`ncompare` generates a view of the matching and non-matching groups and variables between two NetCDF datasets.

## Motivation

The `cdo` (climate data operators) tool
[does not support NetCDF4 groups](https://code.mpimet.mpg.de/boards/2/topics/12073).
Moreover, `nco` operators' `ncdiff` function computes value differences, but
--- as far as the developers of this tool are aware ---
`nco` does not have a simple function to show structural differences between NetCDF4 datasets.

## Initial setup

#### 1. 🌍 Create a minimal Python environment, using [conda](https://docs.conda.io/projects/conda/en/latest/index.html#):

```shell script
conda env create --file=environment.yml
conda activate ncompare
```

#### 2. 💾 Install _ncompare_, with its dependencies

###### Option A) Install using poetry:

i) Follow the instructions for installing `poetry` [here](https://python-poetry.org/docs/).

ii) Run ```poetry install``` from the repository directory.

###### Option B) Install using pip:

i) Run ```pip install .``` from the repository directory.

## Basic usage at a command line:

If installed using a `poetry` environment:
```
poetry run ncompare <netcdf file #1> <netcdf file #2>
```

Otherwise:
```
ncompare <netcdf file #1> <netcdf file #2>
```

Example:
`ncompare S001G01.nc S001G01_SUBSET.nc -g product -v ozone_profile --report subset_comparison.txt`



## Options

- `--file-text` [FILE_PATH]: Text file to write output to.
- `--file-csv` [FILE_PATH]: Comma separated values (CSV) file to write output to.
- `--file-xlsx` [FILE_PATH]: Excel file to write output to.
- `--no-color` : Turn off all colorized output.
- `--show-attributes` : Include variable attributes in the table that compares variables.
- `--show-chunks` : Include chunk sizes in the table that compares variables.
- `-v` (`--comparison_var_name`) [VAR_NAME]: Compare specific values for this variable.
- `-g` (`--comparison_var_group`) [VAR_GROUP]: Group that contains the `comparison_var_name`.

## Known limitations
- This currently works with netCDF hierarchies containing no more than one level of groups.
- This uses `xarray` to access the root-level dimensions.
In some cases, `xarray` will miss dimensions whose names do not also exist as variable names in the dataset
  (also known as non-coordinate dimensions).
