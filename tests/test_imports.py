"""Test that importing ncompare stays lightweight."""

import subprocess
import sys


def test_import_does_not_load_xarray_or_openpyxl():
    """`import ncompare` should not pull in xarray or openpyxl.

    These are deferred until they are actually needed (see #374), and this guards
    against them being reintroduced at module level. The check runs in a fresh
    interpreter, because the test suite itself imports xarray.
    """
    code = (
        "import sys; import ncompare; "
        "assert 'xarray' not in sys.modules, 'xarray loaded at import time'; "
        "assert 'openpyxl' not in sys.modules, 'openpyxl loaded at import time'"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr