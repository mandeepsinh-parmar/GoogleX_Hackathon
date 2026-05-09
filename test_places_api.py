import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
print("API Key loaded, length:", len(api_key))

query = "Industrial Estate Karbi Anglong ASSAM India"
resp = requests.get(
    "https://maps.googleapis.com/maps/api/place/textsearch/json",
    params={"query": query, "key": api_key}
)
print("Places API Response:", resp.json())

resp_geo = requests.get(
    "https://maps.googleapis.com/maps/api/geocode/json",
    params={"address": query, "key": api_key, "region": "in"}
)
print("Geocoding API Response:", resp_geo.json())
