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

## Installation

🌍 Use [conda](https://docs.conda.io/projects/conda/en/latest/index.html#) to
create a minimal Python environment:

```shell script
conda env create --file=environment.yml
conda activate ncompare
```

🌍 Use [poetry](https://python-poetry.org) to
install dependencies and the package:

```shell script
poetry install
```

## Basic usage at a command line:
```
poetry run ncompare <netcdf file #1> <netcdf file #2>
```

Example:
`ncompare S001G01.nc S001G01_SUBSET.nc -g product -v ozone_profile --report subset_comparison.txt`



## Options

- `-r` (`--report`) : A file to write the output to, as a report.
- `-v` (`--comparison_var_name`) : Compare specific values for this variable.
- `-g` (`--comparison_var_group`) : Group that contains the `comparison_var_name`.
- `--no-color` : Turn off all colorized output.
- `--show-chunks` : Include chunk sizes in the table that compares variables.

## Known limitations
This currently works with NetCDF hierarchies containing no more than one level of groups.
