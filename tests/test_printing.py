import pytest


def test_list_of_strings_diff(outputter_obj):
    left, right, both = outputter_obj.lists_diff(['hey', 'yo', 'beebop'],
                                                 ['what', 'is', 'this', 'beebop'])

    assert (left, right, both) == (2, 3, 1)
