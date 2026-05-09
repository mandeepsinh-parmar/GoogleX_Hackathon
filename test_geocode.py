import os
from dotenv import load_dotenv
load_dotenv()
from agents.scraper_agent import _geocode_park, GOOGLE_MAPS_API_KEY

print("API Key length:", len(GOOGLE_MAPS_API_KEY))
print("First few chars:", GOOGLE_MAPS_API_KEY[:10])

res1 = _geocode_park("Industrial Estate", "Karbi Anglong", "ASSAM")
print("Result 1:", res1)
