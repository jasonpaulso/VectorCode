from unittest.mock import patch

import pytest

from vectorcode.cli_utils import CHECK_OPTIONS, Config
from vectorcode.subcommands import check


@pytest.mark.asyncio
async def test_check_config_success(capsys, tmp_path):
    # Create a temporary .vectorcode directory
    project_root = tmp_path / ".vectorcode"
    project_root.mkdir()

    config = Config(check_item="config")

    with patch("os.getcwd", return_value=str(tmp_path)):
        result = await check(config)
        captured = capsys.readouterr()

    assert result == 0
    assert str(tmp_path) == captured.out


@pytest.mark.asyncio
async def test_check_config_failure(capsys, tmp_path):
    # Ensure no .vectorcode directory exists
    config = Config(check_item="config")
    with patch("os.getcwd", return_value=str(tmp_path)):
        result = await check(config)
        captured = capsys.readouterr()

    assert result == 1
    assert "Failed!" in captured.err


@pytest.mark.asyncio
async def test_check_invalid_check_item():
    config = Config(check_item="invalid_item")
    with pytest.raises(AssertionError):
        await check(config)


def test_check_options():
    assert "config" in CHECK_OPTIONS
