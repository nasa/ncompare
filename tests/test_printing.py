from ncompare.printing import lists_diff


def test_list_of_strings_diff():
    left, right, both = lists_diff(['hey', 'yo', 'beebop'],
                                   ['what', 'is', 'this', 'beebop'])

    assert (left, right, both) == (2, 3, 1)
