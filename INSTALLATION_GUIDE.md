# VectorCode Installation & Troubleshooting Guide

This document outlines the steps taken to set up VectorCode with ChromaDB and integrate it with Claude via MCP.

## Setup Process

### 1. Environment Setup

VectorCode was installed using `pipx`, which creates an isolated environment for the tool:

```bash
pipx install vectorcode
```

### 2. ChromaDB Setup

We encountered issues with ChromaDB version compatibility. VectorCode expects ChromaDB version 0.6.3 or earlier, but the Docker container was running version 1.0.0.

#### Resolution:

1. Stopped the existing ChromaDB container:

   ```bash
   docker stop [container_name]
   ```

2. Started a compatible ChromaDB 0.6.0 container:

   ```bash
   docker run -d -p 8000:8000 chromadb/chroma:0.6.0
   ```

3. Configured VectorCode to use the running ChromaDB server by creating/updating the config file at `~/.config/vectorcode/config.json`:
   ```json
   {
     "db_settings": {
       "host": "localhost",
       "port": 8000
     },
     "db_url": "http://localhost:8000",
     "hnsw": {
       "hnsw:construction_ef": 100, <-- 100 is the default value
       "hnsw:M": 1024 <-- Adjust this value based on your needs, bigger means better, but slower and more memory intensive
     }
   }
   ```

### 3. Testing VectorCode

We tested VectorCode by creating and indexing a simple test project:

```bash
mkdir -p test-project
echo "print('hello world')" > test-project/test.py
vectorcode vectorise test-project/test.py
```

This successfully indexed the file and made it available for queries.

### 4. MCP Integration Setup

To enable VectorCode integration with Claude via MCP, we:

1. Installed the MCP dependencies:

   ```bash
   pipx install vectorcode[mcp]
   ```

2. Added the VectorCode MCP configuration to Claude Desktop's config file at `~/Library/Application Support/Claude/claude_desktop_config.json`:

   ```json
   {
     "mcpServers": {
       "vectorcode": {
         "command": "vectorcode-mcp-server",
         "args": ["--number", "10", "--ls-on-start"]
       }
     }
   }
   ```

3. Restarted Claude Desktop to enable the integration.

## Usage Tips

### Indexing Code

To index code repositories for searching:

```bash
cd /path/to/your/project
vectorcode vectorise [files or directories]
```

For the VectorCode repository itself:

```bash
cd /Users/jasonschulz/Developer/01-AI_Development_Tools/VectorCode
vectorcode vectorise src lua plugin docs
```

For work projects:

```bash
cd /Users/jasonschulz/Developer/00-Work_Projects
vectorcode vectorise [specific directories or files]
```

### Querying Code

Once code is indexed, you can query it directly with the CLI:

```bash
vectorcode query "your search terms here" -n 5
```

Or use it through Claude Desktop with the MCP integration.

## Troubleshooting

If you encounter issues:

1. Check ChromaDB server is running:

   ```bash
   curl http://localhost:8000/api/v1/heartbeat
   ```

2. Verify VectorCode configuration:

   ```bash
   cat ~/.config/vectorcode/config.json
   ```

3. For version conflicts, confirm ChromaDB compatibility:

   ```bash
   docker exec [container_name] chroma --version
   ```

   VectorCode expects version 0.6.x.

4. For MCP integration issues, check:
   ```bash
   vectorcode-mcp-server --help
   ```
   And verify the MCP configuration in Claude Desktop.

## Resources

- [VectorCode Documentation](https://github.com/Davidyz/VectorCode/tree/main/docs)
- [ChromaDB Documentation](https://docs.trychroma.com)
- [Model Context Protocol (MCP) Documentation](https://modelcontextprotocol.io)
