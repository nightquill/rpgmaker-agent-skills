import os
import pytest

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "example-mv-project")
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")


@pytest.fixture
def fixture_dir():
    return os.path.abspath(FIXTURE_DIR)


@pytest.fixture
def schema_dir():
    return os.path.abspath(SCHEMA_DIR)
