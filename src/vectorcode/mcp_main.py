import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from chromadb.api import AsyncClientAPI
from chromadb.api.models.AsyncCollection import AsyncCollection

try:
    from mcp import ErrorData, McpError
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


default_config: Optional[Config] = None
default_client: Optional[AsyncClientAPI] = None
default_collection: Optional[AsyncCollection] = None


async def mcp_server():
    global default_config, default_client, default_collection
    # sys.stderr = open(os.devnull, "w")
    local_config_dir = await find_project_config_dir(".")

    if local_config_dir is not None:
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
    async def list_collections() -> list[str]:
        names: list[str] = []
        client = default_client
        if client is None:
            # load from global config when failed to detect a project-local config.
            client = await get_client(await load_config_file())
        async for col in get_collections(client):
            if col.metadata is not None:
                names.append(str(col.metadata.get("path")))
        return names

    @mcp.tool(
        "query",
        description="Use VectorCode to perform vector similarity search on the repository and return a list of relevant file paths and contents.",
    )
    async def query_tool(
        n_query: int, query_messages: list[str], project_root: Optional[str] = None
    ) -> list[str]:
        """
        n_query: number of files to retrieve;
        query_messages: keywords to query.
        collection_path: Directory to the repository;
        """
        if project_root is None:
            if default_collection is None or default_config is None:
                raise McpError(
                    ErrorData(code=1, message="Please specify project_root.")
                )
            collection = default_collection
            config = default_config
        else:
            config = await get_project_config(project_root)
            config.project_root = project_root
            client = await get_client(config)
            try:
                collection = await get_collection(client, config, False)
            except (ValueError, IndexError):
                raise McpError(
                    ErrorData(
                        code=1,
                        message=f"Failed to access the collection at {project_root}",
                    )
                )
        query_config = await config.merge_from(
            Config(n_result=n_query, query=query_messages)
        )
        result_paths = await get_query_result_files(
            collection=collection,
            configs=query_config,
        )
        results: list[str] = []
        for path in result_paths:
            if os.path.isfile(path):
                with open(path) as fin:
                    rel_path = os.path.relpath(path, config.project_root)
                    results.append(
                        f"<path>{rel_path}</path>\n<content>{fin.read()}</content>",
                    )

        return results

    await mcp.run_stdio_async()
    return 0


def main():
    return asyncio.run(mcp_server())


if __name__ == "__main__":
    main()
