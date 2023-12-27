import pandas as pd

from ncompare.core import compare

from . import data_for_tests_dir


def test_full_run_to_text_output(temp_data_dir):
    # Compare the `ncompare` output (of test_a.nc vs. test_b.nc) against a pre-computed 'golden' file
    out_path = temp_data_dir / "output_file.txt"

    compare(
        data_for_tests_dir / "test_a.nc",
        data_for_tests_dir / "test_b.nc",
        show_chunks=True,
        show_attributes=True,
        file_text=str(out_path),
    )

    with open(data_for_tests_dir / "a-b_test_golden_file.txt") as f1, open(str(out_path)) as f2:
        exclude_n_lines = 3

        for _ in range(exclude_n_lines):
            next(f1)
            next(f2)

        for line1, line2 in zip(f1, f2):
            assert line1 in line2


def test_full_run_to_csv_output(temp_data_dir):
    # Compare the `ncompare` output (of test_a.nc vs. test_b.nc) against a pre-computed 'golden' file
    out_path = temp_data_dir / "output_file.csv"

    compare(
        data_for_tests_dir / "test_a.nc",
        data_for_tests_dir / "test_b.nc",
        show_chunks=True,
        show_attributes=True,
        file_csv=str(out_path),
    )

    with open(data_for_tests_dir / "a-b_test_golden_file.csv") as f1, open(str(out_path)) as f2:
        exclude_n_lines = 3

        for _ in range(exclude_n_lines):
            next(f1)
            next(f2)

        for line1, line2 in zip(f1, f2):
            assert line1 in line2


def test_full_run_to_xlsx_output(temp_data_dir):
    # Compare the `ncompare` output (of test_a.nc vs. test_b.nc) against a pre-computed 'golden' file
    out_path = temp_data_dir / "output_file.xlsx"

    compare(
        data_for_tests_dir / "test_a.nc",
        data_for_tests_dir / "test_b.nc",
        show_chunks=True,
        show_attributes=True,
        file_xlsx=str(out_path),
    )

    df1 = pd.read_excel(data_for_tests_dir / "a-b_test_golden_file.xlsx")
    df2 = pd.read_excel(out_path)

    difference = df1[df1 != df2]
    rows_with_differences = [(idx, row) for idx, row in difference.notnull().iterrows() if any(row)]

    if len(rows_with_differences) != 0:
        print(
            f"Test will fail because of differences in <{len(rows_with_differences)}> rows. "
            f"Differences identified (Row index ----> row contents):"
        )
        for idx, row in rows_with_differences:
            diff = difference.loc[idx]
            print(f"  {idx} ----> {diff}")

    assert len(rows_with_differences) == 0
