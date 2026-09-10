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


import sys
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from threading import Barrier

import pytest
from colorama import Fore, Style

from ncompare.printing import Outputter, ansi_escape


def test_list_of_strings_diff(outputter_to_console):
    left, right, shared = outputter_to_console.lists_diff(
        ["hey", "yo", "beebop"], ["what", "is", "this", "beebop"]
    )

    assert (left, right, shared) == (2, 3, 1)


def test_column_widths_wrong_length_raises():
    """Passing other than three column widths is rejected with a ValueError (not an assert)."""
    with pytest.raises(ValueError):
        Outputter(column_widths=(10, 20))


def test_add_to_history_records_one_row_with_ansi_and_newlines_stripped():
    """A single call records one row; ANSI codes/newlines are stripped and non-strings coerced."""
    out = Outputter(keep_print_history=True)
    out._add_to_history("\x1b[31mred\x1b[0m", "plain\n", 42)

    assert out._line_history == [["red", "plain", "42"]]


class TerminalBuffer(StringIO):
    """Capture ANSI output without colorama treating the stream as a pipe."""

    def isatty(self):
        return True


@pytest.mark.parametrize("plain_first", [False, True])
def test_interleaved_outputters_keep_independent_colors(monkeypatch, plain_first):
    """The last constructed Outputter must not change the other one's palette."""
    terminal = TerminalBuffer()
    monkeypatch.setattr(sys, "stdout", terminal)
    first = Outputter(no_color=plain_first, keep_print_history=True)
    second = Outputter(no_color=not plain_first, keep_print_history=True)
    outputs = {}
    for out, no_color in [(first, plain_first), (second, not plain_first), (first, plain_first)]:
        terminal.seek(0)
        terminal.truncate(0)
        out.print_header("\nSection heading")
        out.lists_diff(["shared", "left"], ["shared", "right"])
        out.side_by_side("forced", "a", "b", force_color=Fore.LIGHTBLUE_EX)
        text = terminal.getvalue()
        assert ("\x1b[" not in text) == no_color
        outputs[no_color] = text
    assert ansi_escape.sub("", outputs[False]) == outputs[True]
    assert all(
        "\x1b[" not in cell for out in [first, second] for row in out._line_history for cell in row
    )


def test_no_color_does_not_mutate_colorama_even_on_exception():
    """Color constants remain usable by other libraries throughout the context."""
    original_fore, original_style = dict(Fore.__dict__), dict(Style.__dict__)
    with pytest.raises(RuntimeError, match="test exit"):
        with Outputter(no_color=True):
            assert Fore.__dict__ == original_fore
            assert Style.__dict__ == original_style
            raise RuntimeError("test exit")
    assert Fore.__dict__ == original_fore
    assert Style.__dict__ == original_style


def test_parallel_outputters_keep_independent_colors():
    """Synchronize construction to expose interference between opposite palettes."""
    barrier = Barrier(2)

    def render(no_color):
        out = Outputter(no_color=no_color)
        stream = StringIO()
        barrier.wait(timeout=5)
        out.print("parallel report", file=stream)
        return stream.getvalue()

    with ThreadPoolExecutor(max_workers=2) as pool:
        colored, plain = list(pool.map(render, [False, True]))
    assert "\x1b[" in colored
    assert "\x1b[" not in plain
    assert ansi_escape.sub("", colored) == plain


def test_no_color_strips_explicit_styles():
    """Explicitly styled input also obeys the Outputter's no-color setting."""
    stream = StringIO()
    with Outputter(no_color=True) as out:
        out.print("\x1b[31mred\x1b[0m", colors=True, file=stream)
    assert stream.getvalue() == "red\n"


@pytest.mark.parametrize("no_color", [False, True])
def test_outputter_does_not_replace_standard_streams(no_color):
    """Rendering must not install global colorama wrappers on caller streams."""
    stdout, stderr = sys.stdout, sys.stderr
    with Outputter(no_color=no_color) as out:
        out.print_header("heading")
        assert sys.stdout is stdout
        assert sys.stderr is stderr
    assert sys.stdout is stdout
    assert sys.stderr is stderr
