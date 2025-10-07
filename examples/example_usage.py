#!/usr/bin/env python3
"""
Example usage of the Google Maps saved places database
"""

from coconuts.database import GoogleMapsDatabase, SavedPlace
import json

def main():
    # Initialize the database
    db = GoogleMapsDatabase("../data/google_maps_places.db")
    
    print("🗺️  Google Maps Saved Places Database Example")
    print("=" * 50)
    
    # Example 1: Save some places
    print("\n1. Saving example places...")
    
    places_to_save = [
        SavedPlace(
            name="Central Park",
            address="New York, NY 10024, USA",
            latitude=40.7829,
            longitude=-73.9654,
            place_id="ChIJ4zGFAZpYwokRGUGph3Mf37k",
            types=["park", "tourist_attraction"],
            rating=4.6,
            user_ratings_total=150000,
            tags=["nature", "recreation", "family-friendly"]
        ),
        SavedPlace(
            name="The Metropolitan Museum of Art",
            address="1000 5th Ave, New York, NY 10028, USA",
            latitude=40.7794,
            longitude=-73.9632,
            place_id="ChIJKxjxuxNYwokRwJ8J8J8J8J8",
            types=["museum", "art_gallery", "tourist_attraction"],
            rating=4.7,
            user_ratings_total=45000,
            price_level=2,
            website="https://www.metmuseum.org/",
            phone_number="+1 212-535-7710",
            tags=["art", "culture", "museum", "educational"]
        ),
        SavedPlace(
            name="Joe's Pizza",
            address="7 Carmine St, New York, NY 10014, USA",
            latitude=40.7306,
            longitude=-74.0027,
            place_id="ChIJKxjxuxNYwokRwJ8J8J8J8J8",
            types=["restaurant", "food", "point_of_interest"],
            rating=4.3,
            user_ratings_total=2500,
            price_level=1,
            phone_number="+1 212-366-1182",
            opening_hours={
                "monday": "11:00-04:00",
                "tuesday": "11:00-04:00",
                "wednesday": "11:00-04:00",
                "thursday": "11:00-04:00",
                "friday": "11:00-04:00",
                "saturday": "11:00-04:00",
                "sunday": "11:00-04:00"
            },
            tags=["pizza", "food", "casual", "late-night"]
        )
    ]
    
    for place in places_to_save:
        place_id = db.save_place(place)
        print(f"   ✅ Saved: {place.name} (ID: {place_id})")
    
    # Example 2: Get all places
    print("\n2. Retrieving all saved places...")
    all_places = db.get_all_places()
    for place in all_places:
        print(f"   📍 {place.name} - {place.address}")
        print(f"      Rating: {place.rating}/5.0 ({place.user_ratings_total} reviews)")
        print(f"      Tags: {', '.join(place.tags)}")
        print()
    
    # Example 3: Search places
    print("3. Searching for 'pizza'...")
    pizza_places = db.search_places("pizza")
    for place in pizza_places:
        print(f"   🍕 {place.name} - {place.address}")
    
    # Example 4: Find places by location
    print("\n4. Finding places near Central Park (within 2km)...")
    nearby_places = db.get_places_by_location(40.7829, -73.9654, radius_km=2.0)
    for place in nearby_places:
        distance = getattr(place, 'distance', 'Unknown')
        print(f"   🗺️  {place.name} - {distance:.2f}km away")
    
    # Example 5: Get places by tag
    print("\n5. Finding places tagged as 'museum'...")
    museum_places = db.get_places_by_tag("museum")
    for place in museum_places:
        print(f"   🏛️  {place.name} - {place.address}")
    
    # Example 6: Update a place
    print("\n6. Updating Central Park with notes...")
    db.update_place(
        all_places[0].id,
        notes="Great place for a picnic! Don't forget to visit the Bethesda Fountain."
    )
    updated_place = db.get_place(all_places[0].id)
    print(f"   📝 Notes added: {updated_place.notes}")
    
    # Example 7: Get database statistics
    print("\n7. Database Statistics...")
    stats = db.get_statistics()
    print(f"   📊 Total places: {stats['total_places']}")
    print(f"   ⭐ Average rating: {stats['average_rating']}")
    print(f"   🏷️  Most common tags:")
    for tag, count in stats['most_common_tags'][:5]:
        print(f"      - {tag}: {count} places")
    
    # Example 8: Export to JSON
    print("\n8. Exporting places to JSON...")
    export_data = []
    for place in all_places:
        place_dict = {
            "name": place.name,
            "address": place.address,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "rating": place.rating,
            "tags": place.tags,
            "notes": place.notes
        }
        export_data.append(place_dict)
    
    with open("exported_places.json", "w") as f:
        json.dump(export_data, f, indent=2)
    print(f"   💾 Exported {len(export_data)} places to 'exported_places.json'")
    
    print("\n🎉 Example completed successfully!")
    print("You can now use the MCP server tools to interact with your saved places.")

if __name__ == "__main__":
    main()
