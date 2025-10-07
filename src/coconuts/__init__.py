"""
Coconuts MCP Server - Google Maps Saved Places

A Model Context Protocol (MCP) server for managing Google Maps saved places in a SQLite database.
"""

from .database import GoogleMapsDatabase, SavedPlace
from .server import mcp

__version__ = "0.1.0"
__all__ = ["GoogleMapsDatabase", "SavedPlace", "mcp"]
