# ncompare
Compare the structure of two NetCDF files at the command line. 
`ncompare` generates a view of the matching and non-matching groups and variables between two NetCDF datasets.

### Basic usage at a command line:
```
./ncompare.py <netcdf file #1> <netcdf file #2>
```

### Options

- `-r` (`--report`) : A file to write the output to, as a report.
- `-v` (`--comparison_var_name`) : Compare specific values for this variable.
- `-g` (`--comparison_var_group`) : Group that contains the `comparison_var_name`.
- `--no-color` : Turn off all colorized output.
