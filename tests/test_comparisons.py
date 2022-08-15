from ncompare.core import _count_diffs, lists_diff


def test_count_str_list_diffs():
    left, right, both = _count_diffs(['hey', 'yo', 'beebop'],
                                     ['what', 'is', 'this', 'beebop'])

    print(f"left={left}, right={right}, both={both}")
    assert (left, right, both) == (2, 3, 1)

def test_count_int_list_diffs():
    left, right, both = _count_diffs([1, 9, 5, 44, 89, 13],
                                     [3, 0, 5, 1])

    print(f"left={left}, right={right}, both={both}")
    assert (left, right, both) == (4, 2, 2)

def test_list_of_strings_diff():
    left, right, both = lists_diff(['hey', 'yo', 'beebop'],
                                   ['what', 'is', 'this', 'beebop'])

    print(f"left={left}, right={right}, both={both}")
    assert (left, right, both) == (2, 3, 1)
