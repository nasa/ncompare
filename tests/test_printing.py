def test_list_of_strings_diff(outputter_to_console):
    left, right, both = outputter_to_console.lists_diff(
        ['hey', 'yo', 'beebop'], ['what', 'is', 'this', 'beebop']
    )

    assert (left, right, both) == (2, 3, 1)
