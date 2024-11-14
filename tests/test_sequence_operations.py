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

import pytest

from ncompare.sequence_operations import common_elements, count_diffs


@pytest.fixture
def two_example_lists() -> tuple[list[str], list[str]]:
    a = ['yo', 'beebop', 'hey']
    b = ['what', 'does', 'this', 'beebop', 'mean']
    return a, b


def test_common_elements(two_example_lists):
    composed_pairs = [e for e in common_elements(*two_example_lists)]

    should_be = [
        (0, 'beebop', 'beebop'),
        (1, '', 'does'),
        (2, 'hey', ''),
        (3, '', 'mean'),
        (4, '', 'this'),
        (5, '', 'what'),
        (6, 'yo', ''),
    ]

    assert composed_pairs == should_be


def test_count_str_list_diffs(two_example_lists):
    left, right, both = count_diffs(*two_example_lists)

    assert (left, right, both) == (2, 4, 1)


def test_count_int_list_diffs():
    left, right, both = count_diffs([1, 9, 5, 44, 89, 13], [3, 0, 5, 1])

    assert (left, right, both) == (4, 2, 2)
