import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from mcp import ErrorData, McpError

try:
    from mcp import types
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    print(
        "MCP Python SDK not installed. Please install it by installing `vectorcode[mcp]` dependency group.",
        file=sys.stderr,
    )
    sys.exit(1)
import sys

from vectorcode.cli_utils import (
    Config,
    find_project_config_dir,
    get_project_config,
    load_config_file,
)
from vectorcode.common import get_client, get_collection, get_collections
from vectorcode.subcommands.query import get_query_result_files

mcp = FastMCP("VectorCode")


async def mcp_server():
    sys.stderr = open(os.devnull, "w")
    local_config_dir = await find_project_config_dir(".")
    if local_config_dir is None:
        project_root = os.path.abspath(".")
    else:
        project_root = str(Path(local_config_dir).parent.resolve())

    default_config = await load_config_file(
        os.path.join(project_root, ".vectorcode", "config.json")
    )
    default_config.project_root = project_root
    default_client = await get_client(default_config)
    default_collection = await get_collection(default_client, default_config)

    @mcp.tool(
        "list_collections",
        description="List all projects indexed by VectorCode.",
    )
    async def list_collections() -> list[types.TextContent]:
        names: list[str] = []
        async for col in get_collections(default_client):
            if col.metadata is not None:
                names.append(str(col.metadata.get("path")))
        return [types.TextContent(text=i, type="text") for i in names]

    @mcp.tool(
        "query",
        description="Use VectorCode to perform vector similarity search on the repository and return a list of relevant file paths and contents.",
    )
    async def query_tool(
        n_query: int, query_messages: list[str], project_root: Optional[str] = None
    ) -> list[types.TextContent]:
        """
        n_query: number of files to retrieve;
        query_messages: keywords to query.
        collection_path: Directory to the repository;
        """
        if project_root is None:
            collection = default_collection
            config = default_config
        else:
            config = await get_project_config(project_root)
            config.project_root = project_root
            client = await get_client(config)
            try:
                collection = await get_collection(client, config, False)
            except (ValueError, IndexError):
                # TODO: properly throw an error
                raise McpError(
                    ErrorData(
                        code=1,
                        message=f"Failed to access the collection at {project_root}",
                    )
                )
        result_paths = await get_query_result_files(
            collection=collection,
            configs=await config.merge_from(
                Config(n_result=n_query, query=query_messages)
            ),
        )
        results: list[types.TextContent] = []
        for path in result_paths:
            if os.path.isfile(path):
                with open(path) as fin:
                    results.append(
                        types.TextContent(
                            text=f"<path>{os.path.relpath(path, config.project_root)}</path>\n<content>{fin.read()}</content>",
                            type="text",
                        )
                    )
        return results

    await mcp.run_stdio_async()
    return 0


def main():
    return asyncio.run(mcp_server())


if __name__ == "__main__":
    main()
