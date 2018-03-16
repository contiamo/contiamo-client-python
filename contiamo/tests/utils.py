import os


def file_test_data(filename):
    return os.path.join(os.path.dirname(__file__), 'data', filename)


def file_test_cassette(filename):
    return os.path.join(os.path.dirname(__file__), 'cassettes', filename)
