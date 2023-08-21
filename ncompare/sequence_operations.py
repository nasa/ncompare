"""Helper functions for operating on iterables, such as lists or sets."""
from collections.abc import Iterable
from typing import Union

from ncompare.utils import coerce_to_str


def common_elements(sequence_a: Iterable,
                    sequence_b: Iterable
                    ) -> tuple[int, str, str]:
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

    iter_a = iter(a_sorted)
    iter_b = iter(b_sorted)

    item_a = next(iter_a, None)
    item_b = next(iter_b, None)

    index = 0

    while item_a is not None or item_b is not None:
        if item_a == item_b:
            yield index, item_a, item_b
            item_a = next(iter_a, None)
            item_b = next(iter_b, None)
        elif item_a is None or (item_b is not None and item_a > item_b):
            yield index, '', item_b
            item_b = next(iter_b, None)
        else:
            yield index, item_a, ''
            item_a = next(iter_a, None)

        index += 1



def count_diffs(list_a: list[Union[str, int]],
                list_b: list[Union[str, int]]
                ) -> tuple[int, int, int]:
    """Count how many elements are either uniquely in one list or the other, or in both.

    Note
    ----
    Duplicates are ignored, i.e. any elements present more than once in a list are treated as if they only occur once.

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

    # The number of differences are computed.
    left = len(set_a.difference(set_b))
    right = len(set_b.difference(set_a))
    both = len(set_a.intersection(set_b))

    return left, right, both
