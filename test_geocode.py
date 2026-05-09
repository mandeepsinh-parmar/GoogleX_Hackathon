import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
print(f"Maps API Key: {API_KEY[:10]}...{API_KEY[-4:]}")

# Test 1: Find Place From Text
query = "Khed City, Pune, MAHARASHTRA, India"
print(f"\n--- Test 1: Find Place From Text ---")
print(f"Query: {query}")
resp = requests.get(
    "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
    params={
        "input": query,
        "inputtype": "textquery",
        "fields": "place_id,name,formatted_address,geometry",
        "key": API_KEY,
    },
    timeout=10,
)
data = resp.json()
print(f"Status: {data.get('status')}")
if data.get("error_message"):
    print(f"Error: {data['error_message']}")
if data.get("candidates"):
    c = data["candidates"][0]
    print(f"Name: {c.get('name')}")
    print(f"Address: {c.get('formatted_address')}")
    print(f"Place ID: {c.get('place_id')}")
    geo = c.get("geometry", {}).get("location", {})
    print(f"Lat/Lng: {geo.get('lat')}, {geo.get('lng')}")
    
    # Test 2: Place Details
    place_id = c.get("place_id")
    if place_id:
        print(f"\n--- Test 2: Place Details ---")
        resp2 = requests.get(
            "https://maps.googleapis.com/maps/api/place/details/json",
            params={
                "place_id": place_id,
                "fields": "geometry,formatted_address,name",
                "key": API_KEY,
            },
            timeout=10,
        )
        data2 = resp2.json()
        print(f"Status: {data2.get('status')}")
        if data2.get("error_message"):
            print(f"Error: {data2['error_message']}")
        if data2.get("result"):
            r = data2["result"]
            geo2 = r.get("geometry", {}).get("location", {})
            print(f"Name: {r.get('name')}")
            print(f"Address: {r.get('formatted_address')}")
            print(f"Precise Lat/Lng: {geo2.get('lat')}, {geo2.get('lng')}")
else:
    print("No candidates found.")
    
    # Test 3: Geocoding fallback
    print(f"\n--- Test 3: Geocoding API fallback ---")
    resp3 = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        params={
            "address": query,
            "region": "in",
            "key": API_KEY,
        },
        timeout=10,
    )
    data3 = resp3.json()
    print(f"Status: {data3.get('status')}")
    if data3.get("error_message"):
        print(f"Error: {data3['error_message']}")
    if data3.get("results"):
        r = data3["results"][0]
        geo3 = r["geometry"]["location"]
        print(f"Address: {r.get('formatted_address')}")
        print(f"Lat/Lng: {geo3['lat']}, {geo3['lng']}")
        print(f"Location Type: {r['geometry'].get('location_type')}")
