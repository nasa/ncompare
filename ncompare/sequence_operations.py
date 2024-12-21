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
    # Use sets for faster membership checking
    a_set = set(map(coerce_to_str, sequence_a))
    b_set = set(map(coerce_to_str, sequence_b))

    # Sort the union of both sets
    all_items = sorted(a_set | b_set)

    for i, item in enumerate(all_items):
        # Determine presence in each set
        item_a = item if item in a_set else ""
        item_b = item if item in b_set else ""
        yield i, item_a, item_b


def count_diffs(
    list_a: Union[list[str], list[int], str], list_b: Union[list[str], list[int], str]
) -> tuple[int, int, int]:
    """Count how many elements are either uniquely in one list or the other, or shared.

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
    shared = len(set_a & set_b)

    return left, right, shared
