import filecmp

from ncompare.core import compare
from . import data_for_tests_dir


def test_full_run_to_text_output(temp_data_dir):
    # Compare the `ncompare` output (of test_a.nc vs. test_b.nc) against a pre-computed 'golden' file
    out_path = temp_data_dir / "output_file.txt"

    compare(data_for_tests_dir / "test_a.nc",
            data_for_tests_dir / "test_b.nc",
            show_chunks=True, show_attributes=True,
            file_text=str(out_path)
            )

    assert filecmp.cmp(data_for_tests_dir / "a-b_test_golden_file.txt", str(out_path))
