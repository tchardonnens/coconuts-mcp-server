import sqlite3
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os


@dataclass
class SavedPlace:
    """Data model for a Google Maps saved place"""
    id: Optional[int] = None
    name: str = ""
    address: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    place_id: Optional[str] = None
    types: List[str] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    price_level: Optional[int] = None
    website: Optional[str] = None
    phone_number: Optional[str] = None
    opening_hours: Optional[Dict[str, Any]] = None
    photos: Optional[List[str]] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        if self.types is None:
            self.types = []
        if self.photos is None:
            self.photos = []
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()


class GoogleMapsDatabase:
    """SQLite database manager for Google Maps saved places"""
    
    def __init__(self, db_path: str = "data/google_maps_places.db"):
        self.db_path = db_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self) -> None:
        """Initialize the database with the required tables"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS saved_places (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    place_id TEXT UNIQUE,
                    types TEXT,  -- JSON array of place types
                    rating REAL,
                    user_ratings_total INTEGER,
                    price_level INTEGER,
                    website TEXT,
                    phone_number TEXT,
                    opening_hours TEXT,  -- JSON object
                    photos TEXT,  -- JSON array of photo URLs
                    notes TEXT,
                    tags TEXT,  -- JSON array of user tags
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_place_id ON saved_places(place_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_location ON saved_places(latitude, longitude)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON saved_places(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON saved_places(created_at)")
            
            conn.commit()
    
    def save_place(self, place: SavedPlace) -> int:
        """Save a place to the database and return its ID"""
        place.updated_at = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO saved_places 
                (name, address, latitude, longitude, place_id, types, rating, 
                 user_ratings_total, price_level, website, phone_number, 
                 opening_hours, photos, notes, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                place.name,
                place.address,
                place.latitude,
                place.longitude,
                place.place_id,
                json.dumps(place.types),
                place.rating,
                place.user_ratings_total,
                place.price_level,
                place.website,
                place.phone_number,
                json.dumps(place.opening_hours) if place.opening_hours else None,
                json.dumps(place.photos),
                place.notes,
                json.dumps(place.tags),
                place.created_at,
                place.updated_at
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_place(self, place_id: int) -> Optional[SavedPlace]:
        """Get a place by its database ID"""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM saved_places WHERE id = ?", (place_id,)).fetchone()
            if row:
                return self._row_to_place(row)
            return None
    
    def get_place_by_google_id(self, google_place_id: str) -> Optional[SavedPlace]:
        """Get a place by its Google Place ID"""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM saved_places WHERE place_id = ?", (google_place_id,)).fetchone()
            if row:
                return self._row_to_place(row)
            return None
    
    def get_all_places(self, limit: Optional[int] = None, offset: int = 0) -> List[SavedPlace]:
        """Get all saved places with optional pagination"""
        with self.get_connection() as conn:
            query = "SELECT * FROM saved_places ORDER BY created_at DESC"
            params = []
            
            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_place(row) for row in rows]
    
    def search_places(self, query: str, limit: Optional[int] = None) -> List[SavedPlace]:
        """Search places by name, address, or tags"""
        with self.get_connection() as conn:
            search_query = """
                SELECT * FROM saved_places 
                WHERE name LIKE ? OR address LIKE ? OR tags LIKE ?
                ORDER BY created_at DESC
            """
            params = [f"%{query}%", f"%{query}%", f"%{query}%"]
            
            if limit:
                search_query += " LIMIT ?"
                params.append(limit)
            
            rows = conn.execute(search_query, params).fetchall()
            return [self._row_to_place(row) for row in rows]
    
    def get_places_by_location(self, latitude: float, longitude: float, radius_km: float = 10.0) -> List[SavedPlace]:
        """Get places within a radius of the given coordinates"""
        with self.get_connection() as conn:
            # Using Haversine formula for distance calculation
            query = """
                SELECT *, 
                (6371 * acos(cos(radians(?)) * cos(radians(latitude)) * 
                cos(radians(longitude) - radians(?)) + sin(radians(?)) * 
                sin(radians(latitude)))) AS distance
                FROM saved_places 
                WHERE distance <= ?
                ORDER BY distance
            """
            rows = conn.execute(query, (latitude, longitude, latitude, radius_km)).fetchall()
            return [self._row_to_place(row) for row in rows]
    
    def get_places_by_tag(self, tag: str) -> List[SavedPlace]:
        """Get all places with a specific tag"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM saved_places WHERE tags LIKE ? ORDER BY created_at DESC",
                (f'%"{tag}"%',)
            ).fetchall()
            return [self._row_to_place(row) for row in rows]
    
    def update_place(self, place_id: int, **updates) -> bool:
        """Update a place with the given fields"""
        if not updates:
            return False
        
        place = self.get_place(place_id)
        if not place:
            return False
        
        # Update the place object
        for key, value in updates.items():
            if hasattr(place, key):
                setattr(place, key, value)
        
        place.updated_at = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE saved_places SET
                name = ?, address = ?, latitude = ?, longitude = ?, place_id = ?,
                types = ?, rating = ?, user_ratings_total = ?, price_level = ?,
                website = ?, phone_number = ?, opening_hours = ?, photos = ?,
                notes = ?, tags = ?, updated_at = ?
                WHERE id = ?
            """, (
                place.name, place.address, place.latitude, place.longitude, place.place_id,
                json.dumps(place.types), place.rating, place.user_ratings_total, place.price_level,
                place.website, place.phone_number, 
                json.dumps(place.opening_hours) if place.opening_hours else None,
                json.dumps(place.photos), place.notes, json.dumps(place.tags),
                place.updated_at, place_id
            ))
            conn.commit()
            return True
    
    def delete_place(self, place_id: int) -> bool:
        """Delete a place by its ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM saved_places WHERE id = ?", (place_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            total_places = conn.execute("SELECT COUNT(*) FROM saved_places").fetchone()[0]
            
            # Get most common tags
            all_tags = []
            rows = conn.execute("SELECT tags FROM saved_places WHERE tags IS NOT NULL").fetchall()
            for row in rows:
                tags = json.loads(row['tags'])
                all_tags.extend(tags)
            
            tag_counts = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Get places by rating
            avg_rating = conn.execute("SELECT AVG(rating) FROM saved_places WHERE rating IS NOT NULL").fetchone()[0]
            
            return {
                "total_places": total_places,
                "average_rating": round(avg_rating, 2) if avg_rating else None,
                "most_common_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            }
    
    def _row_to_place(self, row: sqlite3.Row) -> SavedPlace:
        """Convert a database row to a SavedPlace object"""
        return SavedPlace(
            id=row['id'],
            name=row['name'],
            address=row['address'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            place_id=row['place_id'],
            types=json.loads(row['types']) if row['types'] else [],
            rating=row['rating'],
            user_ratings_total=row['user_ratings_total'],
            price_level=row['price_level'],
            website=row['website'],
            phone_number=row['phone_number'],
            opening_hours=json.loads(row['opening_hours']) if row['opening_hours'] else None,
            photos=json.loads(row['photos']) if row['photos'] else [],
            notes=row['notes'],
            tags=json.loads(row['tags']) if row['tags'] else [],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
