#!/usr/bin/env python
"""Command line interface for `ncompare` -- to compare the structure of two NetCDF files."""
import argparse
import importlib.metadata
import sys
import traceback

from ncompare.core import compare

__version__ = importlib.metadata.version('ncompare')


def _cli(args) -> argparse.Namespace:
    """Parse input arguments from the command line.

    Parameters
    ----------
    args : None or list[str]
        if None, then argparse will use sys.argv[1:]
    """
    parser = argparse.ArgumentParser(
        description="Compare the variables contained within two different NetCDF datasets"
    )
    parser.add_argument("nc_a", help="First NetCDF file")
    parser.add_argument("nc_b", help="First NetCDF file")
    parser.add_argument("-v", "--comparison_var_name", help="Comparison variable name")
    parser.add_argument("-g", "--comparison_var_group", help="Comparison variable group")
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
        "--no-color", action="store_true", default=False, help="Turn off all colorized output"
    )
    parser.add_argument(
        "--show-attributes",
        action="store_true",
        default=False,
        help="Include variable attributes in comparison",
    )
    parser.add_argument(
        "--show-chunks",
        action="store_true",
        default=False,
        help="Include chunk sizes in the table that compares variables",
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
        action='version',
        version=f'%(prog)s {__version__}',
        default=False,
        help="Show the current version.",
    )

    return parser.parse_args(args)


def main():  # pragma: no cover
    """Run from the command line."""
    args = _cli(None)

    delattr(args, 'version')

    try:
        compare(**vars(args))
    except Exception:  # pylint: disable=broad-exception-caught
        print(traceback.format_exc())
        sys.exit(1)
    sys.exit(0)  # a clean, no-issue, exit


if __name__ == '__main__':  # pragma: no cover
    main()
