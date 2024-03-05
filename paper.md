---
title: 'ncompare: A Python package for comparing netCDF structures'
tags:
  - Python
  - netCDF
  - comparison
  - data storage
authors:
  - name:
        given-names: Daniel E.
        surname: Kaufman
    orcid: 0000-0002-1487-7298
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name:
        given-names: Walter E.
        surname: Baskin
    orcid: 0000-0002-2241-3266
    affiliation: "1, 3"
affiliations:
 - name: NASA Langley Research Center, Atmospheric Science Data Center, Hampton, VA, USA
   index: 1
 - name: Booz Allen Hamilton, Inc., McLean, VA, USA
   index: 2
 - name: Adnet Systems, Inc., Bethesda, MD, USA
   index: 3
date: 11 January 2024
bibliography: paper.bib
---

# Summary

<!--- _A summary describing the high-level functionality and purpose of the software for a diverse,
non-specialist audience._ --->

`ncompare` compares the structure of two Network Common Data Form
(netCDF) files at the command line, thus providing rapid and human-readable evaluation of netCDF
pairs. The essential inputs to `ncompare` are the filepaths of two netCDF datasets, and the output
is a report that automatically aligns and highlights differences between the matching and
non-matching groups, variables, and associated metadata (e.g., dimension lengths, attributes,
chunking). The user is provided the option to colorize the terminal output for ease of viewing,
to save comparison reports in text, comma-separated value (CSV), and/or Microsoft Excel formats,
and to compare values for a particular variable of interest. `ncompare` is written using the Python
programming language [@python; @VanRossumAndDrake2009]. To use `ncompare`, it can be given input
from a command line interface (CLI), or its functions can be called directly from within a running
Python kernel. The order of operations proceeds through these steps: comparing root-level
dimensions, groups, structure and values of an optional user-specified group/variable, and finally
all the variables in each group.


# Statement of need

<!---_A Statement of need section that clearly illustrates the research purpose of the software and
places it in the context of related work. Mention (if applicable) a representative set of past or
ongoing research projects using the software and recent scholarly publications enabled by it._ --->

The Network Common Data Form (netCDF) file format enables the storage and use of multidimensional
data [@RewAndDavis1990; @BrownEtAl1993]. It is widely applied to research problems throughout
the Earth sciences — e.g., to store and compare output from climate models, to store and prepare
oceanographic or atmospheric reanalyses, and to store and analyze observational data. When creating
or modifying netCDF files, there is often a need to evaluate the
differences between an original unmodified file and a new modified file, especially for
regression testing. Despite the availability of tools (such as `ncmpidiff` or `nccmp`) that compare
the _values_ of variables, there was not a readily available, Python-based tool for rapid visual
comparisons of group and variable _structures_, _attributes_, and _chunking_. `ncompare` was
developed to avoid the inefficient process of manually opening two netCDF files and inspecting their
contents to determine whether there are differences in the structure and shapes of groups and
variables.

`ncompare` has been used by the National Aeronautics and Space Administration (NASA)
Atmospheric Science Data Center (ASDC) to examine preliminary science data products in
preparation for ingesting, archiving, and distributing satellite-based instrument retrievals.
For example, to prepare for new data streams from the recently launched
Tropospheric Emissions Monitoring of Pollution (TEMPO) instrument [@Zoogman2017JQSRT] —
which collects measurements of major air pollutants,
including ozone, nitrogen dioxide, and formaldehyde —
the ASDC used `ncompare` to identify data structure changes,
or the lack thereof, in a variety of settings.
For instance, as data and metadata requirements were being established and refined,
`ncompare` was used to assess changes from one version of data files to another.
The `ncompare` package was used to confirm whether NASA's data transformation services,
including those that perform data subsetting and concatenation,
modified dataset variables and attributes appropriately.
By allowing data scientists at ASDC to quickly identify any and all changes in netCDF structures,
`ncompare` sped up and enhanced the process of validating data integrity,
critical to ensuring the discoverability and usability of TEMPO air quality observations
for air quality monitoring, research, and forecasting.

The `ncompare` package fills a gap in the currently available range of netCDF evaluation tools.
The `cdo` (climate data operators) library [@cdo_2022_Schulzweida]
[does not support NetCDF4 groups](https://code.mpimet.mpg.de/boards/2/topics/12073).
The `ncdiff` function in the `nco` (netCDF Operators) library [@Zender2008EMS] computes value
differences, but --- as far as the authors are aware ---
does not have a simple function to show structural differences between netCDF version 4 (netCDF4)
datasets. `h5diff`, provided in the HDF5 (Hierarchical Data Format) software [@hdf5],
can be used to compare netCDF4 files; however, there are notable differences. In contrast to
`h5diff`, `ncompare` is written and runnable in Python; `ncompare` provides
an _aligned_ and _colorized_ difference report for more efficient and intuitive assessments of
groups, variable names, types, shapes, and attributes; and can generate report files formatted for
other applications. However, note that `h5diff` provides comparison of "hidden" hdf5
properties, such as _Netcdf4Dimid or _Netcdf4Coordinates, which are not currently assessed by
`ncompare`.

# Development Notes

`ncompare` is developed as an open-source package on GitHub; contributions
and feature suggestions are welcome. Continuous Integration using GitHub Actions ensures code
linting (via `ruff`), formatting (via `black`), version updating, and testing (via `pytest`) is
routinely performed. `ncompare` is available on PyPI (The Python Package Index) and can be
installed using pip. It is released under the NASA Open Source Agreement, and its source code is
available at https://github.com/nasa/ncompare.


# Acknowledgements

<!--- _Acknowledgement of any financial support._ --->

This project was supported as part of the STARSS and RSES contracts to the NASA Langley Research
Center and Atmospheric Science Data Center. `ncompare` makes use of
numpy [@harris2020array], netCDF4, xarray [@Hoyer2017], colorama, and openpyxl.

# References
