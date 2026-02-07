import os


def pytest_configure(config=None):
    # Prevent runtime GGUF loads during pytest runs
    os.environ.setdefault('ECHO_TESTING', '1')
