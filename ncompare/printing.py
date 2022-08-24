"""Utility functions for printing to the console or a text file."""
from colorama import Fore, Style

from ncompare.sequence_operations import common_elements, count_diffs


def side_by_side(str_a, str_b, str_c,
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
        print_func = print

        extra_style_space = " " * len(Fore.RED)
        # print(f" {str_a:>28}")
        # print(f" {extra_style_space}{str_a:>28}")
        # print("done testing.")
    else:
        print_func = print_normal
        extra_style_space = ""

    if dash_line:
        print_func(f" {extra_style_space}{str_a:>28} {str_b:->48} {str_c:->48}")
    else:
        print_func(f" {extra_style_space}{str_a:>28} {str_b:>48} {str_c:>48}")


def side_by_side_list_diff(list_a: list, list_b: list, counter_prefix="") -> None:
    """Print the items from two lists vertically (i.e., side by side), with customized formatting.

    Parameters
    ----------
    list_a
    list_b
    counter_prefix
    """
    for i, a, b in common_elements(list_a, list_b):
        side_by_side(f"{counter_prefix} #{i:02}", a.strip(), b.strip(),
                     dash_line=True, highlight_diff=True)


def lists_diff(a: list, b: list,
               ignore_order: bool = True
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
            print(msg)
            print("\t" + Fore.CYAN + str(sa))
        else:
            print(msg + "  (No items exist.)")
        return 0, 0, len(a)

    else:
        left, right, both = count_diffs(a, b)
        print("\t" + "Are all items the same? ---> " + Fore.RED + f"{str(contents_are_same)}."
              f"  ({_singular_or_plural(both)} shared, out of {len(s_union)} total.)")

        # Which variables are different?
        print("\t" + Fore.RED + "Which items are different?")
        # print(Fore.RED + "Which items are different? ---> %s." %
        #       str(set(list_a).symmetric_difference(list_b)))
        side_by_side(' ', 'File A', 'File B')
        side_by_side_list_diff(a, b)
        side_by_side('Number of non-shared items:', str(left), str(right))

        return left, right, both

def _singular_or_plural(x):
    if x == 1:
        return f"{x} item is"
    else:
        return f"{x} items are"

def print_normal(string, **kwargs):
    """Print normal color and style text to the console."""
    print(Fore.WHITE + Style.RESET_ALL + str(string), **kwargs)
