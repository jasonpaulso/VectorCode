import pytest

from vectorcode.cli_utils import GLOBAL_CONFIG_PATH


@pytest.fixture(autouse=True)
def restore_global_config_path():
    global GLOBAL_CONFIG_PATH
    original_global_config_path = GLOBAL_CONFIG_PATH
    yield
    GLOBAL_CONFIG_PATH = original_global_config_path
