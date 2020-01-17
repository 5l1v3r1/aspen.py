import sys

import pytest
from aspen.testing import Harness, teardown


@pytest.fixture
def sys_path_scrubber():
    before = set(sys.path)
    yield
    after = set(sys.path)
    for name in after - before:
        sys.path.remove(name)


@pytest.fixture
def harness(sys_path_scrubber):
    harness = Harness()
    yield harness
    harness.teardown()


def pytest_runtest_teardown():
    teardown()
