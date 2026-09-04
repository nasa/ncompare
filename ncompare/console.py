#!/usr/bin/env python
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

"""Command line interface for `ncompare` -- to compare the structure of two NetCDF files."""

import argparse
import importlib.metadata
import sys
import traceback
from collections.abc import Sequence

from ncompare.core import compare

__version__ = importlib.metadata.version("ncompare")


def _cli(args: Sequence[str] | None) -> argparse.Namespace:
    """Parse input arguments from the command line.

    Parameters
    ----------
    args
        if None, then argparse will use `sys.argv[1:]`
    """
    parser = argparse.ArgumentParser(
        description="Compare the variables contained within two different netCDF datasets"
    )
    parser.add_argument("path_a", help="First (netCDF or HDF) file")
    parser.add_argument("path_b", help="Second (netCDF or HDF) file")
    parser.add_argument(
        "--only-diffs",
        action="store_true",
        default=False,
        help="Only display variables and attributes that are different",
    )
    parser.add_argument("--file-text", help="A text file to which the output will be written.")
    parser.add_argument(
        "--file-csv",
        help="A csv (comma separated values) file to which the output will be written.",
    )
    parser.add_argument("--file-xlsx", help="An Excel file to which the output will be written.")
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Turn off all colorized output",
    )
    parser.add_argument(
        "--show-attributes",
        action="store_true",
        default=False,
        help="Include variable and global (root-level) attributes in the comparison",
    )
    parser.add_argument(
        "--show-chunks",
        action="store_true",
        default=False,
        help="Include chunk sizes in the table that compares variables",
    )

    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit 1 if any differences are found, instead of 0 "
        "(useful in scripts and CI). A failed comparison always exits 2, "
        "whether or not this flag is given",
    )

    parser.add_argument(
        "--column-widths",
        nargs=3,
        default=None,
        type=int,
        help="Width, in number of characters, of the three columns in the comparison report",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        default=False,
        help="Show the current version.",
    )

    return parser.parse_args(args)


def main() -> None:  # pragma: no cover
    """Run from the command line."""
    args = _cli(None)

    delattr(args, "version")
    # `exit_code` is a CLI-only concern; it isn't a parameter of `compare`.
    exit_on_difference = args.exit_code
    delattr(args, "exit_code")

    # Exit codes follow the convention used by diff(1), cmp(1), and grep(1):
    #   0  compared successfully; no differences
    #   1  compared successfully; differences found (only with --exit-code)
    #   2  could not compare
    # Reserving 2 for failure keeps "differences found" distinguishable from
    # "something went wrong", which matters when the exit code is what a script
    # branches on. It also matches argparse, which already exits 2 for usage
    # errors such as an unrecognized flag or a missing operand.
    try:
        total_diff_count = compare(**vars(args))
    except Exception:  # pylint: disable=broad-exception-caught
        # Diagnostics go to stderr, so that stdout carries only the comparison
        # report and its difference count. That keeps stdout parseable by a
        # caller even when the run fails.
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(2)  # the comparison could not be completed
    print(total_diff_count)
    if exit_on_difference and (total_diff_count > 0):
        sys.exit(1)  # differences found, and the caller asked us to signal that
    sys.exit(0)  # a clean, no-issue, exit


if __name__ == "__main__":  # pragma: no cover
    main()
