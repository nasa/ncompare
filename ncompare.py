#!/usr/bin/env python
"""Compare the structure of two NetCDF files."""
import argparse
import sys
from pathlib import Path

from ncompare.core import compare


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
            raise FileExistsError("File selected for report already exists. Delete it or choose a different filename.")
        self.log = open(filepath, "a")

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

def _parse_cli() -> argparse.Namespace:
    """Parse input arguments from the command line."""
    parser = argparse.ArgumentParser(description="Compare the variables contained within two different NetCDF datasets")
    parser.add_argument("nc_a", help="First NetCDF file")
    parser.add_argument("nc_b", help="First NetCDF file")
    parser.add_argument("-r", "--report", help="A file to write the output to, as a report")
    parser.add_argument("-v", "--comparison_var_name", help="Comparison variable name")
    parser.add_argument("-g", "--comparison_var_group", help="Comparison variable group")
    parser.add_argument("--no-color", action="store_true", default=False,
                        help="Turn off all colorized output")

    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_cli()

    if args.report:
        sys.stdout = _Logger(args.report)
    args.__delattr__("report")

    sys.exit(compare(**vars(args)))
