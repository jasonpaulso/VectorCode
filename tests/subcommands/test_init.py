import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from vectorcode.cli_utils import Config
from vectorcode.subcommands.init import init


@pytest.mark.asyncio
async def test_init_new_project(capsys):
    with tempfile.TemporaryDirectory() as temp_dir:
        configs = Config(project_root=temp_dir, force=False)
        return_code = await init(configs)
        assert return_code == 0
        assert os.path.isdir(os.path.join(temp_dir, ".vectorcode"))
        captured = capsys.readouterr()
        assert (
            f"VectorCode project root has been initialised at {temp_dir}"
            in captured.out
        )


@pytest.mark.asyncio
async def test_init_already_initialized(capsys):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize the project once
        configs = Config(project_root=temp_dir, force=False)
        await init(configs)

        # Try to initialize again without force
        return_code = await init(configs)
        assert return_code == 1
        captured = capsys.readouterr()
        assert f"{temp_dir} is already initialised for VectorCode." in captured.err


@pytest.mark.asyncio
async def test_init_already_initialized_with_force(capsys):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize the project once
        configs = Config(project_root=temp_dir, force=False)
        await init(configs)

        # Initialize again with force
        configs = Config(project_root=temp_dir, force=True)
        return_code = await init(configs)
        assert return_code == 0
        captured = capsys.readouterr()
        assert (
            f"VectorCode project root has been initialised at {temp_dir}"
            in captured.out
        )


@pytest.mark.asyncio
async def test_init_copies_global_config(capsys):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a dummy global config file
        global_config_content = '{"test": "value"}'
        with tempfile.NamedTemporaryFile(delete=False) as global_config_file:
            global_config_file.write(global_config_content.encode())
            global_config_path = global_config_file.name

        project_config_file = os.path.join(temp_dir, ".vectorcode", "config.json")

        # Mock os.path.isfile to return True only for the temporary global config file
        isfile_mock = Mock(return_value=True)

        # Mock shutil.copyfile to assert that the correct files were copied
        copyfile_mock = Mock()
        original_global_config_path = os.path.join(
            os.path.expanduser("~"), ".config", "vectorcode", "config.json"
        )

        with (
            patch("os.path.isfile", isfile_mock),
            patch("shutil.copyfile", copyfile_mock),
        ):
            # Initialize the project
            configs = Config(project_root=temp_dir, force=False)
            await init(configs)

            # Assert that shutil.copyfile was called with the correct arguments
            copyfile_mock.assert_called_once_with(
                original_global_config_path, project_config_file
            )

            # Check if the project config was created
            assert os.path.isfile(project_config_file)

            captured = capsys.readouterr()
            assert "The global configuration at" in captured.out

        # Clean up the global config file
        os.remove(global_config_path)
