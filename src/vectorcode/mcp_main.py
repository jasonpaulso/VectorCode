import asyncio
import os
import sys
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    print(
        "MCP Python SDK not installed. Please install it by installing `vectorcode[mcp]` dependency group.",
        file=sys.stderr,
    )
    sys.exit(1)
import sys

from vectorcode.cli_utils import Config, find_project_config_dir, load_config_file
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

    config = await load_config_file(
        os.path.join(project_root, ".vectorcode", "config.json")
    )
    config.project_root = project_root
    client = await get_client(config)
    collection = await get_collection(client, config)

    @mcp.tool(
        "list_collections",
        description="List all projects indexed by VectorCode.",
    )
    async def list_collections() -> list[str]:
        names: list[str] = []
        async for col in get_collections(client):
            if col.metadata is not None:
                names.append(str(col.metadata.get("path")))
        return names

    @mcp.tool(
        "query",
        description="Use VectorCode to perform vector similarity search on the repository and return a list of relevant file paths and contents.",
    )
    async def query_tool(
        n_query: int, query_messages: list[str]
    ) -> list[dict[str, str]]:
        """
        collection_path: Directory to the repository;
        n_query: number of files to retrieve;
        query_messages: keywords to query.
        """
        result_paths = await get_query_result_files(
            collection=collection,
            configs=await config.merge_from(
                Config(n_result=n_query, query=query_messages)
            ),
        )
        results = []
        for path in result_paths:
            if os.path.isfile(path):
                with open(path) as fin:
                    results.append({"path": path, "document": fin.read()})
        return results

    # mcp.add_tool(
    #     fn=query_tool,
    #     name="query_tool",
    #     description="Perform vector similarity search on the repository and return a list of relevant file paths and contents.",
    # )
    await mcp.run_stdio_async()
    return 0


def main():
    return asyncio.run(mcp_server())


if __name__ == "__main__":
    main()
