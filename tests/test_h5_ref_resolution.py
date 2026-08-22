"""File B's HDF5 object references must resolve against File B.

_create_var_properties(group_b, ...) used to pass original_dataset=open_file1,
so reference attributes (e.g. DIMENSION_LIST) of File B's variables were
dereferenced against File A, producing wrong names or spurious diffs.
Regression for #341.
"""

import h5py
import numpy as np
import pytest

from ncompare.core import compare


@pytest.fixture
def differing_ref_pair(tmp_path):
    """Two HDF5 files whose /var variables carry a reference attribute
    pointing to differently-named target datasets within each file."""
    path_a = tmp_path / "file_a.h5"
    path_b = tmp_path / "file_b.h5"

    for path, target_name in ((path_a, "target_in_a"), (path_b, "target_in_b")):
        with h5py.File(path, "w") as f:
            target = f.create_dataset(target_name, data=np.arange(4, dtype="f4"))
            var = f.create_dataset("var", data=np.zeros(4, dtype="f4"))
            # An object reference attribute shaped like DIMENSION_LIST.
            var.attrs["ref_attr"] = np.array([[target.ref]], dtype=h5py.ref_dtype)

    return path_a, path_b


def test_file_b_references_resolve_against_file_b(tmp_path, differing_ref_pair, capsys):
    path_a, path_b = differing_ref_pair
    output_path = tmp_path / "out.txt"

    compare(
        path_a,
        path_b,
        file_text=output_path,
        show_chunks=False,
        show_attributes=True,
    )

    text = output_path.read_text()

    # The reference-attribute row must show each file's own target: File A's
    # reference resolved against File A and File B's against File B. Under
    # the bug both columns resolved against File A, printing File A's target
    # name twice.
    ref_attr_lines = [
        line for line in text.splitlines() if line.strip().startswith("ref_attr:")
    ]
    assert ref_attr_lines, "expected the ref_attr attribute row in the output"
    assert "/target_in_a" in ref_attr_lines[0]
    assert "/target_in_b" in ref_attr_lines[0]
