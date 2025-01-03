from pathlib import Path

import pytest

from ncompare.utility_types import FileToCompare


def test_FileToCompare():
    with pytest.raises(TypeError):
        assert FileToCompare(path=123, type="netcdf")

    with pytest.raises(ValueError):
        assert FileToCompare(path=Path(__file__), type="beebop_type")
