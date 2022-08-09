#!/usr/bin/env python
"""Command line interface for `ncompare` -- to compare the structure of two NetCDF files."""
import argparse
import sys
import traceback
from pathlib import Path

from ncompare.core import compare


def _cli() -> argparse.Namespace:
    """Parse input arguments from the command line."""
    parser = argparse.ArgumentParser(description="Compare the variables contained within two different NetCDF datasets")
    parser.add_argument("nc_a", help="First NetCDF file")
    parser.add_argument("nc_b", help="First NetCDF file")
    parser.add_argument("-r", "--report", help="A file to write the output to, as a report")
    parser.add_argument("-v", "--comparison_var_name", help="Comparison variable name")
    parser.add_argument("-g", "--comparison_var_group", help="Comparison variable group")
    parser.add_argument("--no-color", action="store_true", default=False,
                        help="Turn off all colorized output")
    parser.add_argument("--show-chunks", action="store_true", default=False,
                        help="Include chunk sizes in the table that compares variables")

    return parser.parse_args()

class _Logger:

    def __init__(self, filename):
        """Send print statements, i.e., stdout, to a file.

        Note
        ----
        This class is derived from https://stackoverflow.com/a/14906787.
        """
        self.terminal = sys.stdout
        filepath = Path(filename)
        if filepath.exists():
            pass
        # This will overwrite any existing file at this path, if one exists.
        self.log = open(filepath, "w")

    def write(self, message):
        """Write message to output."""
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        """Handle the flush command by doing nothing.

        Note
        ----
        The flush method is needed for python 3 compatibility.
        # you might want to specify some extra behavior here.
        """
        pass


def main():
    """Run from command line."""
    args = _cli()

    if args.report:
        sys.stdout = _Logger(args.report)
    args.__delattr__("report")

    try:
        compare(**vars(args))
    except Exception:
        print(traceback.format_exc())
        sys.exit(1)
    sys.exit(0)  # a clean, no-issue, exit


if __name__ == '__main__':
    main()
