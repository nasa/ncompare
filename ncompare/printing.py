"""Utility functions for printing to the console or a text file."""
# pylint: disable=too-many-arguments
import csv
import re
import warnings
from collections.abc import Iterable
from pathlib import Path
from typing import Optional, TextIO, Union

import colorama
import openpyxl
from colorama import Fore, Style
from openpyxl.cell import Cell
from openpyxl.styles import Font

from ncompare.sequence_operations import common_elements, count_diffs

# Set up regex remover of ANSI color escape sequences
#   From <https://stackoverflow.com/a/14693789>
ansi_escape = re.compile(
    r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''',
    re.VERBOSE,
)


class Outputter:
    """Handler for print statements and saving to text and/or csv files."""

    _difference_marker = "***"

    def __init__(
        self,
        keep_print_history: bool = False,
        keep_only_diffs: bool = False,
        no_color: bool = False,
        text_file: Optional[Union[str, Path]] = None,
        column_widths: Optional[tuple[Union[int, str], Union[int, str], Union[int, str]]] = None,
    ):
        """Set up the handling of printing and saving destinations.

        Parameters
        ----------
        keep_print_history
        """
        # Parse the print history option.
        self._keep_print_history = keep_print_history
        self._line_history: list[list[str]] = []
        self.keep_only_diffs = keep_only_diffs

        # Assign column widths according to input, if
        default_widths = [33, 48, 48]
        if column_widths is not None:
            assert len(column_widths) == 3

            new_widths = default_widths
            for idx, width in enumerate(column_widths):
                if isinstance(width, str) and width.isdigit() and (int(width) > 0):
                    # note: isdigit() ensures integer
                    new_widths[idx] = int(width)
                elif isinstance(width, int) and width > 0:
                    new_widths[idx] = width
                else:
                    warnings.warn(
                        "Column-width input was not a positive integer. Reverting to default."
                    )
            self._column_widths = tuple(new_widths)
        else:
            self._column_widths = tuple(default_widths)

        if no_color:
            # Replace colorized styles with blank strings.
            for k, _ in Fore.__dict__.items():
                Fore.__dict__[k] = ""
            for k, _ in Style.__dict__.items():
                Style.__dict__[k] = ""
        else:
            colorama.init(autoreset=True)

        # Open a file
        if text_file:
            filepath = Path(text_file)
            if filepath.exists():
                pass
            # This will overwrite any existing file at this path if one exists.
            self._text_file_obj: Optional[TextIO] = open(
                filepath, "w", encoding="utf-8"
            )  # pylint: disable=consider-using-with
        else:
            self._text_file_obj = None

    def __enter__(self):  # noqa: D105
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):  # noqa: D105
        if self._text_file_obj:
            self._text_file_obj.close()

    def print(
        self, string: str = "", colors: bool = False, add_to_history: bool = False, **print_args
    ) -> None:
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

        def _parse_single_str(s):  # pylint: disable=invalid-name
            # Remove ANSI escape sequences before adding to a parsed string list.
            result = ansi_escape.sub('', s)
            # Remove any leading or trailing newlines.
            return result.strip("\n")

        if isinstance(args, str):
            parsed_strings = [_parse_single_str(args)]
        elif isinstance(args, Iterable):
            parsed_strings = []
            for item in args:
                if not isinstance(item, str):
                    try:
                        string = str(item)
                    except Exception as err:
                        raise TypeError(
                            f"Error <{err}> with {str(item)}! Expected a string; got a <{type(item)}>."
                        ) from err
                else:
                    string = item

                parsed_strings.append(_parse_single_str(string))
        else:
            raise TypeError(f"Invalid type <{type(args)}>. Expected a `str` or `list`.")

        if self._keep_print_history:
            self._line_history.append(parsed_strings)

    @staticmethod
    def _make_normal(string):
        """Return text with normal color and style."""
        return Fore.WHITE + Style.RESET_ALL + str(string)

    def side_by_side(
        self,
        str_a,
        str_b,
        str_c,
        dash_line=False,
        highlight_diff=False,
        force_display_even_if_same=False,
        force_color=None,
    ) -> None:
        """Print three strings on one line, with customized formatting and an optional marker in the fourth column.

        Parameters
        ----------
        str_a
        str_b
        str_c
        dash_line : bool, default False
        highlight_diff : bool, default False
        """
        are_different = str_b != str_c
        if (
            (force_display_even_if_same is False)
            and (are_different is False)
            and self.keep_only_diffs
        ):
            return None

        # If the 'b' and 'c' strings are different (or force_color is set),
        #   then change the font of 'a' to the color red.
        if (highlight_diff and are_different) or (force_color is not None):
            default_color = Fore.RED
            if force_color is not None:
                str_a = force_color + str_a
            else:
                str_a = default_color + str_a
            colors = False
            extra_style_space = " " * len(default_color)
            str_marker = self._difference_marker
        else:
            colors = True
            extra_style_space = ""
            str_marker = ""

        if dash_line:
            self.print(
                f" {extra_style_space}"
                f"{str_a:>{self._column_widths[0]}} "
                f"{str_b:->{self._column_widths[1]}} "
                f"{str_c:->{self._column_widths[2]}}",
                colors=colors,
            )
        else:
            self.print(
                f" {extra_style_space}"
                f"{str_a:>{self._column_widths[0]}} "
                f"{str_b:>{self._column_widths[1]}} "
                f"{str_c:>{self._column_widths[2]}}",
                colors=colors,
            )

        self._add_to_history(str_a, str_b, str_c, str_marker)

    def side_by_side_list_diff(self, list_a: list, list_b: list, counter_prefix="") -> None:
        """Print the items from two lists vertically (i.e., side by side), with customized formatting.

        Parameters
        ----------
        list_a
        list_b
        counter_prefix
        """
        for idx, item_a, item_b in common_elements(list_a, list_b):
            self.side_by_side(
                f"{counter_prefix} #{idx:02}",
                item_a.strip(),
                item_b.strip(),
                dash_line=True,
                highlight_diff=True,
            )

    def lists_diff(
        self,
        list_a: list,
        list_b: list,
        ignore_order: bool = True,
    ) -> tuple[int, int, int]:
        """Compare two lists and state whether there are differences."""
        set_a, set_b = set(list_a), set(list_b)

        s_union = set_a.union(set_b)

        # Are these list contents the same?
        if ignore_order:
            contents_are_same = set_a == set_b
        else:
            contents_are_same = list_a == list_b

        # Display the comparison result
        if contents_are_same:
            msg = "\t" + Fore.CYAN + f"Are all items the same? ---> {str(contents_are_same)}."

            if len(set_a) > 0:
                self.print(msg, add_to_history=True)
                self.print("\t" + Fore.CYAN + str(sorted(set_a)))
            else:
                self.print(msg + "  (No items exist.)", add_to_history=True)
            return 0, 0, len(list_a)

        # If contents are not the same, continue...
        left, right, both = count_diffs(list_a, list_b)
        self.print(
            "\t" + "Are all items the same? ---> " + Fore.RED + f"{str(contents_are_same)}."
            f"  ({_item_is_or_are(both)} shared, out of {len(s_union)} total.)",
            add_to_history=True,
        )

        # Which variables are different?
        self.print("\t" + Fore.RED + "Which items are different?")
        # print(Fore.RED + "Which items are different? ---> %s." %
        #       str(set(list_a).symmetric_difference(list_b)))

        self.side_by_side(' ', 'File A', 'File B')
        self.side_by_side_list_diff(list_a, list_b)
        self.side_by_side('Number of non-shared items:', str(left), str(right))

        return left, right, both

    def write_history_to_csv(self, filename: Union[str, Path] = "test.csv"):
        """Save the line history that's been stored to a CSV file."""
        headers = ['Info', 'File A', 'File B', 'Other marks']
        with open(filename, 'w', encoding="utf-8") as target:
            writer = csv.writer(target)
            writer.writerow(headers)
            writer.writerows(self._line_history)

    def write_history_to_excel(self, filename: Union[str, Path] = "test.xlsx"):
        """Save the line history that's been stored to a CSV file."""
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        # Add a header row
        sheet.append(['Info', 'File A', 'File B'])

        # Add rows and apply styles
        for row in self._line_history:
            if (len(row) > 3) and (row[3] == self._difference_marker):
                # The case where there is a difference that we want to highlight
                #   First, remove difference marker that is redundant with styles applied to the row (unlike in the CSV)
                del row[3]
                sheet.append(_excel_red_cells(row, sheet))
            elif (len(row) == 1) or ((len(row) == 3) and ((row[1] == '') and (row[2] == ''))):
                # The case where there is a subheader and no information in the second and third columns.
                sheet.append(_excel_bold_underline_cells(row, sheet))
            else:
                sheet.append(row)

        # Wrap up
        workbook.save(filename)


def _item_is_or_are(count):
    if count == 1:
        return f"{count} item is"

    return f"{count} items are"


def _excel_red_cells(data, sheet):
    """Stylize cells in Excel with a red font."""
    for cell in data:
        cell = Cell(sheet, column="A", row=1, value=cell)
        cell.font = Font(bold=True, color="FFFF0000")
        yield cell


def _excel_bold_underline_cells(data, sheet):
    """Stylize cells in Excel with a bold and underlined font."""
    for cell in data:
        cell = Cell(sheet, column="A", row=1, value=cell)
        cell.font = Font(bold=True, underline='single')
        yield cell
