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
        (6, 'yo', '')
    ]

    assert composed_pairs == should_be

def test_count_str_list_diffs(two_example_lists):
    left, right, both = count_diffs(*two_example_lists)

    assert (left, right, both) == (2, 4, 1)

def test_count_int_list_diffs():
    left, right, both = count_diffs([1, 9, 5, 44, 89, 13],
                                    [3, 0, 5, 1])

    assert (left, right, both) == (4, 2, 2)
