import json

from vectorcode.cli_utils import Config

prompt_strings = [
    "**Use at your discretion** when you feel you don't have enough information about the repository or project",
    "**Don't escape** special characters",
    "separate phrases into distinct keywords when appropriate",
    "If a class, type or function has been imported from another file, this tool may be able to find its source. Add the name of the imported symbol to the query",
    "Avoid retrieving one single file because the retrieval mechanism may not be very accurate",
    "When providing answers based on VectorCode results, try to give references such as paths to files and line ranges, unless you're told otherwise (but do not include the full source code context)",
    "VectorCode is the name of this tool. Do not include it in the query unless the user explicitly asks",
    "If the retrieval results do not contain the needed context, increase the file count so that the result will more likely contain the desired files",
    "If the returned paths are relative, they are relative to the root of the project directory",
    "Do not suggest edits to retrieved files that are outside of the current working directory, unless the user instructed otherwise",
    "When specifying the `project_root` parameter when making a query, make sure you run the `ls` tool first to retrieve a list of valid, indexed projects",
    "If a query failed to retrieve desired results, a new attempt should use different keywords that are orthogonal to the previous ones but with similar meanings",
    "Do not use exact query keywords that you have used in a previous tool call in the conversation, unless the user instructed otherwise, or with different count/project_root",
]


def prompts(configs: Config) -> int:
    if configs.pipe:
        print(json.dumps(prompt_strings))
    else:
        for i in prompt_strings:
            print(f"- {i}")
    return 0
