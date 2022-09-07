"""Utility functions for printing to the console or a text file."""
import csv
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Union

import colorama
from colorama import Fore, Style

from ncompare.sequence_operations import common_elements, count_diffs


# Set up regex remover of ANSI color escape sequences
#   From <https://stackoverflow.com/a/14693789>
ansi_escape = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)

class Outputter:
    """Handler for print statements and saving to text and/or csv files."""

    def __init__(self,
                 keep_print_history: bool = False,
                 no_color: bool = False,
                 text_file: Union[str, Path] = None):
        """Set up the handling of printing and saving destinations.

        Parameters
        ----------
        keep_print_history
        """
        # Parse the print history option.
        self._keep_print_history = keep_print_history
        if self._keep_print_history:
            self._line_history = list()
        else:
            self._line_history = None

        if no_color:
            # Replace colorized styles with blank strings.
            for k, v in Fore.__dict__.items():
                Fore.__dict__[k] = ""
            for k, v in Style.__dict__.items():
                Style.__dict__[k] = ""
        else:
            colorama.init(autoreset=True)

        # Open a file
        if text_file:
            filepath = Path(text_file)
            if filepath.exists():
                pass
            # This will overwrite any existing file at this path, if one exists.
            self._text_file_obj = open(filepath, "w")
        else:
            self._text_file_obj = None

    def __enter__(self):  # noqa: D105
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):  # noqa: D105
        if self._text_file_obj:
            self._text_file_obj.close()

    def print(self,
              string: str = "",
              colors: bool = False,
              add_to_history: bool = False,
              **print_args) -> None:
        """Print text using custom options.

        Parameters
        ----------
        string : str
        colors : bool
            If False, ANSI colors will be turned off.
        add_to_history : bool
        print_args
            Additional keyword arguments that are passed to the standard Python print() function.
        """
        # Decide if colors are to be used or not.
        if colors is False:
            text_to_print = self._make_normal(string)
        else:
            text_to_print = string

        # Execute the print command.
        print(text_to_print, **print_args)

        # Optional - write text to file
        if self._text_file_obj:
            # Remove ANSI escape sequences.
            result = ansi_escape.sub('', text_to_print)
            self._text_file_obj.write(result + "\n")

        # Optional - save text to a history list
        if add_to_history:
            self._add_to_history(text_to_print)

    def _add_to_history(self, *args):
        """Convert a list of items to a comma-separated string that is added to the csv history."""

        def _parse_single_str(s):
            # Remove ANSI escape sequences before adding to parsed string list.
            result = ansi_escape.sub('', s)
            # Remove any leading or trailing newlines.
            return result.strip("\n")

        if isinstance(args, str):
            parsed_strings = [_parse_single_str(args)]
        elif isinstance(args, Iterable):
            parsed_strings = []
            for x in args:
                if not isinstance(x, str):
                    try:
                        string = str(x)
                    except Exception as err:
                        raise TypeError("Error <%s> with %s! Expected a string; got a <%s>.", err, str(x), type(x))
                else:
                    string = x

                parsed_strings.append(_parse_single_str(string))
        else:
            raise TypeError("Invalid type <%s>. Expected a `str` or `list`.", type(args))

        if self._line_history is not None:
            self._line_history.append(parsed_strings)

    @staticmethod
    def _make_normal(string):
        """Return text with normal color and style."""
        return Fore.WHITE + Style.RESET_ALL + str(string)

    def side_by_side(self, str_a, str_b, str_c,
                     dash_line=False, highlight_diff=False) -> None:
        """Print three strings on one line, with customized formatting.

        Parameters
        ----------
        str_a
        str_b
        str_c
        dash_line : bool, default False
        highlight_diff : bool, default False
        """
        # If the 'b' and 'c' strings are different, then change the font of 'a' to the color red.
        if highlight_diff and (str_b != str_c):
            str_a = Fore.RED + str_a
            colors = False
            extra_style_space = " " * len(Fore.RED)
        else:
            colors = True
            extra_style_space = ""

        if dash_line:
            self.print(f" {extra_style_space}{str_a:>33} {str_b:->48} {str_c:->48}", colors=colors)
        else:
            self.print(f" {extra_style_space}{str_a:>33} {str_b:>48} {str_c:>48}", colors=colors)

        self._add_to_history(str_a, str_b, str_c)

    def side_by_side_list_diff(self, list_a: list, list_b: list, counter_prefix="") -> None:
        """Print the items from two lists vertically (i.e., side by side), with customized formatting.

        Parameters
        ----------
        list_a
        list_b
        counter_prefix
        """
        for i, a, b in common_elements(list_a, list_b):
            self.side_by_side(f"{counter_prefix} #{i:02}", a.strip(), b.strip(),
                              dash_line=True, highlight_diff=True)

    def lists_diff(self,
                   a: list, b: list,
                   ignore_order: bool = True,
                   ) -> tuple[int, int, int]:
        """Compare two lists and state whether there are differences."""
        sa = set(a)
        sb = set(b)
        s_union = sa.union(sb)

        # Are these list contents the same?
        if ignore_order:
            contents_are_same = sa == sb
        else:
            contents_are_same = a == b

        # Display the comparison result
        if contents_are_same:
            msg = "\t" + Fore.CYAN + f"Are all items the same? ---> {str(contents_are_same)}."

            if len(sa) > 0:
                self.print(msg, add_to_history=True)
                self.print("\t" + Fore.CYAN + str(sa))
            else:
                self.print(msg + "  (No items exist.)", add_to_history=True)
            return 0, 0, len(a)

        else:
            left, right, both = count_diffs(a, b)
            self.print("\t" + "Are all items the same? ---> " + Fore.RED + f"{str(contents_are_same)}."
                       f"  ({_singular_or_plural(both)} shared, out of {len(s_union)} total.)", add_to_history=True)

            # Which variables are different?
            self.print("\t" + Fore.RED + "Which items are different?")
            # print(Fore.RED + "Which items are different? ---> %s." %
            #       str(set(list_a).symmetric_difference(list_b)))

            self.side_by_side(' ', 'File A', 'File B')
            self.side_by_side_list_diff(a, b)
            self.side_by_side('Number of non-shared items:', str(left), str(right))

            return left, right, both

    def write_history_to_csv(self, filename: Union[str, Path] = "test.csv"):
        """Save the line history that's been stored to a CSV file."""
        headers = ['Info', 'File A', 'File B']
        with open(filename, 'w') as target:
            writer = csv.writer(target)
            writer.writerow(headers)
            writer.writerows(self._line_history)

def _singular_or_plural(x):
    if x == 1:
        return f"{x} item is"
    else:
        return f"{x} items are"
