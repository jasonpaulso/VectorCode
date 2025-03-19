import io
import json
import sys

from vectorcode.cli_utils import Config
from vectorcode.subcommands import prompt


def test_prompts_pipe_true():
    configs = Config(pipe=True)

    # Mock stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output

    return_code = prompt.prompts(configs)

    sys.stdout = sys.__stdout__  # Reset stdout

    expected_output = json.dumps(prompt.prompt_strings) + "\n"
    assert captured_output.getvalue() == expected_output
    assert return_code == 0


def test_prompts_pipe_false():
    configs = Config(pipe=False)

    # Mock stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output

    return_code = prompt.prompts(configs)

    sys.stdout = sys.__stdout__  # Reset stdout

    expected_output = ""
    for i in prompt.prompt_strings:
        expected_output += f"- {i}\n"

    assert captured_output.getvalue() == expected_output
    assert return_code == 0
