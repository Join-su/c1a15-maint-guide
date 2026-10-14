from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def data_dir() -> Path:
    return REPO / "data"


@pytest.fixture(scope="module")
def data_dir_module() -> Path:
    return REPO / "data"
