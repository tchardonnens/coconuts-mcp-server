# Coconuts MCP Server

A Model Context Protocol (MCP) server for managing Google Maps saved places in a SQLite database.

## Project Structure

```
coconuts-mcp-server/
├── src/
│   └── coconuts/           # Main package
│       ├── __init__.py
│       ├── database.py     # Database models and operations
│       └── server.py       # MCP server implementation
├── examples/               # Usage examples
│   └── example_usage.py
├── data/                   # Data files
│   ├── google_maps_places.db
│   └── exported_places.json
├── docs/                   # Documentation
│   └── README.md
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Installation

```bash
uv sync
```

## Usage

See the [detailed documentation](docs/README.md) for complete usage instructions.

## Running Examples

```bash
uv run coconuts/example_usage.py
```

## Development

This project follows Python packaging best practices with a `src/` layout for better isolation and testing.

### Development Setup

```bash
uv sync
uv run mcp dev coconuts/server.py
```

### Running Examples

```bash
uv run coconuts/example_usage.py
```