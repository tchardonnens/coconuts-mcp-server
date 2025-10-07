from mcp.server.fastmcp import FastMCP
from coconuts.database import GoogleMapsDatabase, SavedPlace
from typing import List, Dict, Any, Optional
import json

# Create an MCP server
mcp = FastMCP("Coconuts")

# Initialize the database
db = GoogleMapsDatabase()

@mcp.tool()
def save_place(
    name: str,
    address: str,
    latitude: float,
    longitude: float,
    place_id: Optional[str] = None,
    types: Optional[List[str]] = None,
    rating: Optional[float] = None,
    user_ratings_total: Optional[int] = None,
    price_level: Optional[int] = None,
    website: Optional[str] = None,
    phone_number: Optional[str] = None,
    opening_hours: Optional[Dict[str, Any]] = None,
    photos: Optional[List[str]] = None,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Save a Google Maps place to the database"""
    place = SavedPlace(
        name=name,
        address=address,
        latitude=latitude,
        longitude=longitude,
        place_id=place_id,
        types=types or [],
        rating=rating,
        user_ratings_total=user_ratings_total,
        price_level=price_level,
        website=website,
        phone_number=phone_number,
        opening_hours=opening_hours,
        photos=photos or [],
        notes=notes,
        tags=tags or []
    )
    
    place_id = db.save_place(place)
    return {
        "success": True,
        "message": f"Place '{name}' saved successfully",
        "place_id": place_id
    }

@mcp.tool()
def get_place(place_id: int) -> Dict[str, Any]:
    """Get a saved place by its database ID"""
    place = db.get_place(place_id)
    if place:
        return {
            "success": True,
            "place": {
                "id": place.id,
                "name": place.name,
                "address": place.address,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "place_id": place.place_id,
                "types": place.types,
                "rating": place.rating,
                "user_ratings_total": place.user_ratings_total,
                "price_level": place.price_level,
                "website": place.website,
                "phone_number": place.phone_number,
                "opening_hours": place.opening_hours,
                "photos": place.photos,
                "notes": place.notes,
                "tags": place.tags,
                "created_at": place.created_at,
                "updated_at": place.updated_at
            }
        }
    else:
        return {
            "success": False,
            "message": f"Place with ID {place_id} not found"
        }

@mcp.tool()
def get_all_places(limit: Optional[int] = None, offset: int = 0) -> Dict[str, Any]:
    """Get all saved places with optional pagination"""
    places = db.get_all_places(limit=limit, offset=offset)
    return {
        "success": True,
        "places": [
            {
                "id": place.id,
                "name": place.name,
                "address": place.address,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "rating": place.rating,
                "tags": place.tags,
                "created_at": place.created_at
            }
            for place in places
        ],
        "total": len(places)
    }

@mcp.tool()
def search_places(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search saved places by name, address, or tags"""
    places = db.search_places(query, limit=limit)
    return {
        "success": True,
        "query": query,
        "places": [
            {
                "id": place.id,
                "name": place.name,
                "address": place.address,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "rating": place.rating,
                "tags": place.tags,
                "created_at": place.created_at
            }
            for place in places
        ],
        "total": len(places)
    }

@mcp.tool()
def get_places_by_location(latitude: float, longitude: float, radius_km: float = 10.0) -> Dict[str, Any]:
    """Get places within a radius of the given coordinates"""
    places = db.get_places_by_location(latitude, longitude, radius_km)
    return {
        "success": True,
        "location": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "places": [
            {
                "id": place.id,
                "name": place.name,
                "address": place.address,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "rating": place.rating,
                "tags": place.tags,
                "distance_km": getattr(place, 'distance', None)
            }
            for place in places
        ],
        "total": len(places)
    }

@mcp.tool()
def get_places_by_tag(tag: str) -> Dict[str, Any]:
    """Get all places with a specific tag"""
    places = db.get_places_by_tag(tag)
    return {
        "success": True,
        "tag": tag,
        "places": [
            {
                "id": place.id,
                "name": place.name,
                "address": place.address,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "rating": place.rating,
                "tags": place.tags,
                "created_at": place.created_at
            }
            for place in places
        ],
        "total": len(places)
    }

@mcp.tool()
def update_place(place_id: int, **updates) -> Dict[str, Any]:
    """Update a saved place with new information"""
    success = db.update_place(place_id, **updates)
    if success:
        return {
            "success": True,
            "message": f"Place with ID {place_id} updated successfully",
            "updated_fields": list(updates.keys())
        }
    else:
        return {
            "success": False,
            "message": f"Failed to update place with ID {place_id}"
        }

@mcp.tool()
def delete_place(place_id: int) -> Dict[str, Any]:
    """Delete a saved place by its ID"""
    success = db.delete_place(place_id)
    if success:
        return {
            "success": True,
            "message": f"Place with ID {place_id} deleted successfully"
        }
    else:
        return {
            "success": False,
            "message": f"Failed to delete place with ID {place_id}"
        }

@mcp.tool()
def get_database_statistics() -> Dict[str, Any]:
    """Get statistics about the saved places database"""
    stats = db.get_statistics()
    return {
        "success": True,
        "statistics": stats
    }

@mcp.tool()
def import_places_from_json(json_data: str) -> Dict[str, Any]:
    """Import multiple places from JSON data"""
    try:
        places_data = json.loads(json_data)
        if not isinstance(places_data, list):
            return {
                "success": False,
                "message": "JSON data must be an array of places"
            }
        
        imported_count = 0
        errors = []
        
        for place_data in places_data:
            try:
                place = SavedPlace(**place_data)
                db.save_place(place)
                imported_count += 1
            except Exception as e:
                errors.append(f"Error importing place '{place_data.get('name', 'Unknown')}': {str(e)}")
        
        return {
            "success": True,
            "message": f"Imported {imported_count} places successfully",
            "imported_count": imported_count,
            "errors": errors
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "message": f"Invalid JSON data: {str(e)}"
        }

@mcp.tool()
def export_places_to_json(limit: Optional[int] = None) -> Dict[str, Any]:
    """Export all saved places to JSON format"""
    places = db.get_all_places(limit=limit)
    places_data = []
    
    for place in places:
        place_dict = {
            "name": place.name,
            "address": place.address,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "place_id": place.place_id,
            "types": place.types,
            "rating": place.rating,
            "user_ratings_total": place.user_ratings_total,
            "price_level": place.price_level,
            "website": place.website,
            "phone_number": place.phone_number,
            "opening_hours": place.opening_hours,
            "photos": place.photos,
            "notes": place.notes,
            "tags": place.tags,
            "created_at": place.created_at,
            "updated_at": place.updated_at
        }
        places_data.append(place_dict)
    
    return {
        "success": True,
        "places": places_data,
        "total": len(places_data),
        "json": json.dumps(places_data, indent=2)
    }