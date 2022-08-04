# ncompare
Compare the structure of two NetCDF files at the command line.
`ncompare` generates a view of the matching and non-matching groups and variables between two NetCDF datasets.

### Installation

🌍 Using [conda](https://docs.conda.io/projects/conda/en/latest/index.html#),
create a runtime/development environment with the dependencies.

```shell script
conda env create --file=environment.yml
conda activate ncompare
```

💾 Install the package:
```shell script
pip install .
```

### Basic usage at a command line:
```
ncompare <netcdf file #1> <netcdf file #2>
```

Example:
`ncompare S001G01.nc S001G01_SUBSET.nc -g product -v ozone_profile --report subset_comparison.txt`

### Options

- `-r` (`--report`) : A file to write the output to, as a report.
- `-v` (`--comparison_var_name`) : Compare specific values for this variable.
- `-g` (`--comparison_var_group`) : Group that contains the `comparison_var_name`.
- `--no-color` : Turn off all colorized output.
- `--show-chunks` : Include chunk sizes in the table that compares variables.
