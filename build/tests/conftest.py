import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def config_dir(tmp_path):
    return tmp_path / ".ipam"


@pytest.fixture
def config_file(config_dir):
    return config_dir / "config"
