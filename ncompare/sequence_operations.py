"""Helper functions for operating on iterables, such as lists or sets."""
from collections.abc import Generator, Iterable
from typing import Union

from ncompare.utils import coerce_to_str


def common_elements(
    sequence_a: Iterable, sequence_b: Iterable
) -> Generator[tuple[int, str, str], None, None]:
    """Loop over combined items of two iterables, and yield aligned item pairs.

    Note
    ----
    When there isn't a matching item, an empty string is used instead.

    Yields
    ------
    int
        an increasing index value assigned to each item pair
    str
        item from sequence_a, or an empty string
    str
        item from sequence_b, or an empty string
    """
    a_sorted = sorted(map(coerce_to_str, sequence_a))
    b_sorted = sorted(map(coerce_to_str, sequence_b))
    all_items = sorted(set(a_sorted).union(set(b_sorted)))

    for i, item in enumerate(all_items):
        item_a = item
        item_b = item
        if (item not in a_sorted) and (item not in b_sorted):
            raise ValueError(
                "Unexpected condition where an item was not found "
                "but all items should exist in at least one list."
            )

        if item not in a_sorted:
            item_a = ''
        elif item not in b_sorted:
            item_b = ''

        yield i, item_a, item_b


def count_diffs(
    list_a: Union[list[str], list[int], str], list_b: Union[list[str], list[int], str]
) -> tuple[int, int, int]:
    """Count how many elements are either uniquely in one list or the other, or in both.

    Note
    ----
    Duplicates are ignored, i.e., any elements present more than once in a list are treated
    as if they only occur once.

    Returns
    -------
    int
        Number of items only in the *left* list ("a")
    int
        Number of items only in the *right* list ("b")
    int
        Number of items in both lists ("a" and "b")
    """
    # Lists are converted to sets, where each element is treated as a str.
    set_a = set(map(coerce_to_str, list_a))
    set_b = set(map(coerce_to_str, list_b))

    # The number of differences is computed.
    left = len(set_a - set_b)
    right = len(set_b - set_a)
    both = len(set_a.intersection(set_b))

    return left, right, both
