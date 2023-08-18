from pathlib import Path

import pytest

from ncompare.utils import coerce_to_str, ensure_valid_path_exists


def test_make_valid_path_with_simple_invalid_str_path():
    with pytest.raises(FileNotFoundError):
        ensure_valid_path_exists("whereisthatfile")

def test_make_valid_path_with_close_invalid_Path_path():
    with pytest.raises(FileNotFoundError):
        ensure_valid_path_exists(Path(__file__).parents[0].resolve() / "thisdoesntexist.py")

def test_make_valid_path_from_str_in_repo():
    returnval = ensure_valid_path_exists(str(Path(__file__).parents[0].resolve() / "conftest.py"))
    assert isinstance(returnval, Path)

def test_make_valid_path_from_Path_in_repo():
    returnval = ensure_valid_path_exists(Path(__file__).parents[0].resolve() / "conftest.py")
    assert isinstance(returnval, Path)

def test_coerce_int_to_str():
    assert coerce_to_str(5) == "5"

def test_coerce_tuple_to_str():
    assert coerce_to_str(('step', 123)) == "('step', 123)"
