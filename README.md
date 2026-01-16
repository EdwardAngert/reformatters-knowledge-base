# Reformatters Knowledge Base

> **Project Status & Context**
>
> This repository represents an exploration of how to make technical documentation more accessible to both humans and AI tools, particularly for teams without dedicated technical writers.

## The Problem We're Solving

**Challenge:** Large codebases need good documentation, but:
- AI tools struggle with large documentation sites (context limits, scattered information)
- "Just read the docs" fails when docs span hundreds of pages across multiple locations
- Teams without technical writers need a lightweight way to maintain quality documentation
- AI assistants lose context between sessions and repeat mistakes

**What we wanted:**
- Documentation that's easy for humans to navigate and AI to parse
- Persistent context that AI can reference (architecture, patterns, style decisions)
- Session memory so AI doesn't forget previous work
- Team-wide accessibility without complex infrastructure

## What We Tried: MCP Server Approach

We initially built an MCP (Model Context Protocol) server to serve reformatters documentation through AI-accessible tools.

**What didn't work:**
- **Remote deployment limitations:** Claude Desktop only supports local stdio connections, making Railway deployment unusable for the primary use case
- **Circular dependencies:** Dataset tools required the main reformatters package, defeating the purpose of a separate repo
- **Overcomplexity:** Required separate repo, deployment infrastructure, and maintenance burden
- **Architecture mismatch:** Built HTTP/SSE server that couldn't be used by intended clients

**Key insight:** MCP isn't mature enough yet for team-wide remote access. It's currently best for local-only, individual developer use.

## Current Direction: Sidecar Context + Plugin

Based on proven patterns from other projects ([shared-docs-kb](https://github.com/edwardangert/shared-docs-kb), [documentation-agent-skill](https://github.com/EdwardAngert/documentation-agent-skill)), we're moving toward:

**Structure:**
```
reformatters/
├── docs/                      # Public documentation (MkDocs → GitHub Pages)
│   ├── .context/             # Sidecar context files (for AI)
│   │   ├── architecture.md   # How reformatters works
│   │   ├── patterns.md       # Common code patterns
│   │   ├── style-guide.md    # Documentation conventions
│   │   └── session-notes.md  # AI session memory
│   ├── guides/
│   ├── playbooks/
│   └── examples/
└── .claude/skills/
    └── load-context.py       # Auto-loads context for AI
```

**How it works:**
1. Public docs live in main repo (single source of truth)
2. Sidecar `.context/` files provide curated AI context
3. Plugin/skill loads context at session start
4. AI has both general methodology and project-specific knowledge
5. Session notes persist decisions between work sessions

**Why this is better:**
- ✅ Single repository (no sync issues)
- ✅ Works with any AI tool (not MCP-specific)
- ✅ Zero infrastructure costs
- ✅ Human-readable, git-versionable context
- ✅ Team can contribute by editing markdown
- ✅ Proven pattern from production use

## Current Status

This repository contains excellent documentation content (guides, playbooks, examples) that will be migrated into the main reformatters repository following the sidecar pattern above.

---

## Legacy MCP Server Documentation

The sections below document the MCP server implementation. This approach is deprecated but preserved for reference.

### Original Description

An MCP (Model Context Protocol) server that serves as an expert on the [reformatters](https://github.com/dynamical/reformatters) codebase. This is a support and documentation asset that helps engineers and support teams easily contribute documentation, playbooks, and guides.

## What is this?

This repository provides:

1. **Knowledge Base**: Human-contributed documentation (guides, playbooks, examples)
2. **MCP Server**: AI-accessible tools for documentation generation, code exploration, and support
3. **Two Access Modes**:
   - **Local**: Run directly on your machine for Claude Desktop
   - **Remote**: Deploy to Railway for team-wide HTTP access

## Quick Start

### For Local Development (Claude Desktop)

1. **Clone and install:**
   ```bash
   git clone https://github.com/dynamical/reformatters-knowledge-base.git
   cd reformatters-knowledge-base
   uv sync
   ```

2. **Configure Claude Desktop:**

   Edit your config file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

   Add this configuration (replace the path with yours):
   ```json
   {
     "mcpServers": {
       "reformatters-kb": {
         "command": "uv",
         "args": [
           "--directory",
           "/absolute/path/to/reformatters-knowledge-base",
           "run",
           "reformatters-kb-stdio"
         ]
       }
     }
   }
   ```

3. **Restart Claude Desktop** completely (quit and reopen)

4. **Test it** - Ask Claude:
   - "List all knowledge"
   - "Search guides for backfill"
   - "Search playbooks for troubleshooting"

### For Remote Deployment (Railway)

See [DEPLOYMENT.md](DEPLOYMENT.md) for deploying to Railway for team-wide access.

### For Contributors (Adding Documentation)

1. Clone this repository:
   ```bash
   git clone https://github.com/dynamical/reformatters-knowledge-base.git
   cd reformatters-knowledge-base
   ```

2. Add documentation:
   ```bash
   # Add a guide
   echo "# My Guide" > knowledge/guides/my-guide.md

   # Add a playbook
   echo "# Troubleshooting XYZ" > knowledge/playbooks/troubleshooting/xyz-issue.md

   # Commit and push
   git add knowledge/
   git commit -m "Add documentation for XYZ"
   git push
   ```

3. Documentation is automatically available via the MCP server!

## Development

### Project Structure

```
reformatters-knowledge-base/
├── knowledge/              # Human-contributed content
│   ├── guides/            # User guides
│   ├── playbooks/         # Support runbooks
│   ├── examples/          # Code examples
│   └── architecture/      # Architecture docs
├── src/mcp_server/        # MCP server implementation
│   ├── server.py         # HTTP/SSE server (for Railway)
│   ├── stdio_server.py   # Stdio server (for Claude Desktop)
│   ├── config.py         # Configuration
│   └── tools/            # MCP tool implementations
├── tests/                 # Tests
└── deploy/                # Deployment configs
```

### Two Server Modes

This project supports two deployment modes:

**1. Stdio Mode (Local Claude Desktop)**
- Uses: `reformatters-kb-stdio` command
- Transport: stdin/stdout
- For: Local development and testing
- Config: Claude Desktop `command` and `args`

**2. HTTP Mode (Remote Railway)**
- Uses: `uvicorn mcp_server.server:app`
- Transport: HTTP with Server-Sent Events (SSE)
- For: Team-wide remote access
- Endpoints: `/sse` and `/messages/`

### Testing the HTTP Server Locally

To test the Railway deployment locally:

```bash
# Install dependencies
uv sync

# Run the HTTP server
uv run uvicorn mcp_server.server:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/health  # Should return {"status":"healthy"}
```

**Note:** This HTTP server is **not** used by Claude Desktop. Claude Desktop uses the stdio server directly.

### Running Tests

```bash
uv run pytest
```

## Knowledge Base Content

### 📚 Comprehensive Documentation (17 Documents)

**Guides** (6 documents):
- **Getting Started** - Installation and first steps
- **Dataset Integration Guide** - Step-by-step integration
- **FAQ** - 60+ common questions and answers
- **Common Errors** - 30+ error patterns with solutions
- **CLI Cheatsheet** - Quick command reference
- **Architecture Overview** - System design and concepts

**Playbooks** (5 documents):
- **Backfill Failures** - Diagnosing and fixing backfill issues
- **AWS Credentials Errors** - Resolving permissions problems
- **Validation Failures** - Troubleshooting data validation
- **Memory and Resource Issues** - OOM, disk, CPU problems
- **Running Backfills** - Complete operational guide

**Examples** (3 code samples):
- **Minimal TemplateConfig** - Starting point for new datasets
- **Minimal RegionJob** - Processing logic example
- **Custom Validator** - Data validation examples

**For Technical Writers**: See [TECHNICAL_WRITER_GUIDE.md](TECHNICAL_WRITER_GUIDE.md) for comprehensive documentation roadmap and templates.

## Capabilities

### MCP Tools

**Knowledge Base Search**
- `search_guides` - Find relevant user guides
- `search_playbooks` - Find support playbooks
- `list_all_knowledge` - Browse entire knowledge base

**Dataset Tools** (requires reformatters package installed)
- `list_datasets` - List all reformatters datasets
- `get_dataset_info` - Get detailed dataset information
- `get_dataset_implementation` - Show implementation details

**Documentation Tools**
- `generate_dataset_readme` - Auto-generate dataset documentation
- `generate_cli_command` - Generate CLI commands

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Railway deployment instructions.

The HTTP server can be deployed to Railway for team-wide remote access. Note that Claude Desktop cannot connect to remote HTTP MCP servers - it only supports local stdio-based servers.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Adding guides
- Creating playbooks
- Contributing examples
- Testing with Claude Desktop

## License

MIT
