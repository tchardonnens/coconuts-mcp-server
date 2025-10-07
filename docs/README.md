# Coconuts MCP Server - Google Maps Saved Places

A Model Context Protocol (MCP) server for managing Google Maps saved places in a SQLite database.

## Features

- **Save Places**: Store Google Maps places with comprehensive details
- **Search & Filter**: Find places by name, address, tags, or location
- **Location-based Queries**: Find places within a radius of coordinates
- **Tag Management**: Organize places with custom tags
- **Import/Export**: JSON import/export functionality
- **Statistics**: Get insights about your saved places

## Database Schema

The SQLite database stores places with the following fields:

- **Basic Info**: name, address, latitude, longitude
- **Google Data**: place_id, types, rating, user_ratings_total, price_level
- **Contact**: website, phone_number
- **Details**: opening_hours, photos, notes
- **Organization**: tags, created_at, updated_at

## MCP Tools Available

### Core Operations
- `save_place()` - Save a new place to the database
- `get_place(place_id)` - Retrieve a specific place by ID
- `get_all_places(limit, offset)` - Get all places with pagination
- `update_place(place_id, **updates)` - Update place information
- `delete_place(place_id)` - Remove a place from the database

### Search & Discovery
- `search_places(query, limit)` - Search by name, address, or tags
- `get_places_by_location(lat, lng, radius_km)` - Find nearby places
- `get_places_by_tag(tag)` - Filter by specific tags
- `get_database_statistics()` - Get database insights

### Data Management
- `import_places_from_json(json_data)` - Bulk import from JSON
- `export_places_to_json(limit)` - Export places to JSON format

## Usage Example

```python
from database import GoogleMapsDatabase, SavedPlace

# Initialize database
db = GoogleMapsDatabase()

# Save a place
place = SavedPlace(
    name="Central Park",
    address="New York, NY 10024, USA",
    latitude=40.7829,
    longitude=-73.9654,
    types=["park", "tourist_attraction"],
    rating=4.6,
    tags=["nature", "recreation"]
)
place_id = db.save_place(place)

# Search for places
pizza_places = db.search_places("pizza")
nearby_places = db.get_places_by_location(40.7829, -73.9654, radius_km=5.0)
```

## Running the Example

```bash
cd coconuts
python example_usage.py
```

This will create a sample database with example places and demonstrate all the features.

## Installation

The server uses SQLite (built into Python) and the MCP framework. Install dependencies with:

```bash
uv pip install -e .
```

## Database File

The database file (`google_maps_places.db`) is created automatically in the current directory when you first use the server.
