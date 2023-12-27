import os


def test_console_version():
    exit_status = os.system('ncompare --version')
    assert exit_status == 0


def test_console_help():
    exit_status = os.system('ncompare --help')
    assert exit_status == 0
