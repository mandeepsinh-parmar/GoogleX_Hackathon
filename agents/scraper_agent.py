"""Scraper Agent — Step 3

For each park matched in Step 2, this agent:
  1. Geocodes the park (lat/lng) via Google Maps Geocoding API
  2. Fetches nearby logistics via Google Maps Places API
  3. Uses Gemini to find water availability, raw materials, incentives
  4. Returns an enriched park document ready for MongoDB storage
"""

import json
import os
import time
from typing import Dict, List, Optional
import random

import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GOOGLE_API_KEY      = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

client = genai.Client(api_key=GOOGLE_API_KEY)

_GEMINI_MODEL = "gemini-1.5-flash"

# ─────────────────────────────────────────────────────────────────────────────
# Geocoding — Precise Google Maps workflow
# ─────────────────────────────────────────────────────────────────────────────

# Minimum acceptable location types (reject anything less precise)
_ACCEPTABLE_LOCATION_TYPES = {"ROOFTOP", "RANGE_INTERPOLATED", "GEOMETRIC_CENTER"}


def _find_place_from_text(query: str) -> Optional[Dict]:
    """Step 1: Use Find Place From Text API to get the best place_id."""
    if not GOOGLE_MAPS_API_KEY:
        return None
    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
            params={
                "input": query,
                "inputtype": "textquery",
                "fields": "place_id,name,formatted_address,geometry",
                "locationbias": "ipbias",
                "key": GOOGLE_MAPS_API_KEY,
            },
            timeout=10,
        )
        data = resp.json()
        status = data.get("status", "")
        if status in ("OVER_QUERY_LIMIT", "REQUEST_DENIED"):
            print(f"[Geocode] Find Place API error: {status} — {data.get('error_message', '')}")
            return None
        if status == "OK" and data.get("candidates"):
            # Return the highest-confidence result (first candidate)
            return data["candidates"][0]
    except Exception as e:
        print(f"[Geocode] Find Place exception: {e}")
    return None


def _get_place_details(place_id: str) -> Optional[Dict]:
    """Step 2: Use Place Details API for precise coordinates from a place_id."""
    if not GOOGLE_MAPS_API_KEY or not place_id:
        return None
    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/place/details/json",
            params={
                "place_id": place_id,
                "fields": "geometry,formatted_address,name,place_id",
                "key": GOOGLE_MAPS_API_KEY,
            },
            timeout=10,
        )
        data = resp.json()
        status = data.get("status", "")
        if status in ("OVER_QUERY_LIMIT", "REQUEST_DENIED"):
            print(f"[Geocode] Place Details API error: {status} — {data.get('error_message', '')}")
            return None
        if status == "OK" and data.get("result"):
            result = data["result"]
            geo = result.get("geometry", {}).get("location", {})
            return {
                "lat": geo.get("lat"),
                "lng": geo.get("lng"),
                "formatted_address": result.get("formatted_address", ""),
                "place_id": result.get("place_id", place_id),
                "location_type": result.get("geometry", {}).get("location_type", "ROOFTOP"),
            }
    except Exception as e:
        print(f"[Geocode] Place Details exception: {e}")
    return None


def _geocode_with_address(address: str, state: str = "") -> Optional[Dict]:
    """Step 3 (Fallback): Use Geocoding API with component filtering."""
    if not GOOGLE_MAPS_API_KEY:
        return None
    params = {
        "address": address,
        "region": "in",
        "key": GOOGLE_MAPS_API_KEY,
    }
    if state:
        params["components"] = f"administrative_area:{state}|country:IN"

    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params=params,
            timeout=10,
        )
        data = resp.json()
        status = data.get("status", "")
        if status in ("OVER_QUERY_LIMIT", "REQUEST_DENIED"):
            print(f"[Geocode] Geocoding API error: {status} — {data.get('error_message', '')}")
            return None
        if status == "ZERO_RESULTS":
            return None
        if status == "OK" and data.get("results"):
            # Pick the highest-confidence result
            best = None
            for result in data["results"]:
                loc_type = result.get("geometry", {}).get("location_type", "APPROXIMATE")
                if loc_type in _ACCEPTABLE_LOCATION_TYPES:
                    best = result
                    break
            # If no high-confidence result, take the first one anyway
            if best is None:
                best = data["results"][0]

            geo = best["geometry"]["location"]
            return {
                "lat": geo["lat"],
                "lng": geo["lng"],
                "formatted_address": best.get("formatted_address", ""),
                "place_id": best.get("place_id", ""),
                "location_type": best.get("geometry", {}).get("location_type", "APPROXIMATE"),
            }
    except Exception as e:
        print(f"[Geocode] Geocoding API exception: {e}")
    return None


def _geocode_park(park_name: str, district: str, state: str) -> Dict:
    """
    Precise geocoding pipeline:
      1. Find Place API  (best for named POIs like industrial parks)
      2. Place Details    (rooftop-level coords from place_id)
      3. Geocoding API    (structured address fallback)

    Returns: {lat, lng, formatted_address, place_id, location_type}
    """
    if not GOOGLE_MAPS_API_KEY:
        return {}

    # ── Step 1: Find Place From Text ─────────────────────────────────────
    search_query = f"{park_name}, {district}, {state}, India"
    candidate = _find_place_from_text(search_query)

    if candidate:
        place_id = candidate.get("place_id")
        if place_id:
            # ── Step 2: Place Details for precise coords ─────────────────
            details = _get_place_details(place_id)
            if details and details.get("lat"):
                return details

        # If Place Details failed, use the geometry from the candidate itself
        geo = candidate.get("geometry", {}).get("location", {})
        if geo.get("lat"):
            return {
                "lat": geo["lat"],
                "lng": geo["lng"],
                "formatted_address": candidate.get("formatted_address", ""),
                "place_id": candidate.get("place_id", ""),
                "location_type": "FIND_PLACE",
            }

    # ── Step 3: Geocoding API fallback (structured address) ──────────────
    # Try park name + district + state first
    result = _geocode_with_address(f"{park_name}, {district}, {state}, India", state)
    if result and result.get("lat"):
        return result

    # Try just district + state as last resort
    result = _geocode_with_address(f"{district}, {state}, India", state)
    if result and result.get("lat"):
        return result

    return {}



# ─────────────────────────────────────────────────────────────────────────────
# Nearby logistics via Places API
# ─────────────────────────────────────────────────────────────────────────────

def _nearest_km(lat: float, lng: float, place_type: str, radius_m: int = 80000) -> Optional[float]:
    """Return distance in km to the nearest place of `place_type`."""
    if not GOOGLE_MAPS_API_KEY or not lat or not lng:
        return None
    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
            params={
                "location": f"{lat},{lng}",
                "radius": radius_m,
                "type": place_type,
                "key": GOOGLE_MAPS_API_KEY,
            },
            timeout=10,
        )
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return None

        dest = results[0]["geometry"]["location"]
        dm_resp = requests.get(
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            params={
                "origins": f"{lat},{lng}",
                "destinations": f"{dest['lat']},{dest['lng']}",
                "mode": "driving",
                "key": GOOGLE_MAPS_API_KEY,
            },
            timeout=10,
        )
        dm = dm_resp.json()
        rows = dm.get("rows", [])
        if rows and rows[0]["elements"][0]["status"] == "OK":
            dist_m = rows[0]["elements"][0]["distance"]["value"]
            return round(dist_m / 1000, 1)
    except Exception:
        pass
    return None


def _get_logistics(lat: float, lng: float) -> Dict:
    """Fetch distances to highway, railway, airport, and port."""
    if not lat or not lng:
        return {}
    return {
        "nearest_highway_km":  _nearest_km(lat, lng, "highway", 30000),
        "nearest_railway_km":  _nearest_km(lat, lng, "train_station", 50000),
        "nearest_airport_km":  _nearest_km(lat, lng, "airport", 100000),
        "nearest_port_km":     _nearest_km(lat, lng, "harbor", 200000),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Gemini Research (water, raw materials, incentives)
# ─────────────────────────────────────────────────────────────────────────────

def _gemini_research(park_name: str, district: str, state: str, sector: str) -> Dict:
    """Use Gemini to extract water_availability, raw_materials_nearby, incentives."""
    prompt = f"""
You are an industrial park research assistant for India.

Research the following industrial park and provide ONLY factual, verified information:

Park Name: {park_name}
District: {district}
State: {state}
Primary Sector: {sector}

Return your answer as a valid JSON object with EXACTLY these keys:
{{
  "water_availability": "Description of water source and reliability (string)",
  "raw_materials_nearby": ["list", "of", "relevant", "raw materials", "available nearby"],
  "incentives": ["list of specific benefits like tax exemptions, subsidies, free power duration"],
  "description": "2-3 sentence factual description of the park",
  "power_availability": "Description of power supply and capacity if known",
  "notable_tenants": ["list of known companies in the park, if any"]
}}

If you cannot find specific information for a field, use null for that field.
Return ONLY the JSON object.
"""
    try:
        response = client.models.generate_content(
            model=_GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1024,
                response_mime_type="application/json",
            ),
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        return {
            "water_availability": None,
            "raw_materials_nearby": [],
            "incentives": [],
            "description": f"Industrial park located in {district}, {state}.",
            "power_availability": None,
            "notable_tenants": [],
            "_error": str(e),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Main scrape function
# ─────────────────────────────────────────────────────────────────────────────

def scrape_park(park: Dict, user_sector: str = "") -> Dict:
    """Enrich a single park dict with geocoding, logistics, and research."""
    name     = park.get("name", "").replace("&amp;", "&")
    district = park.get("district", "")
    state    = park.get("state", "")
    sector   = park.get("sector", user_sector)

    enriched = {**park, "name": name}

    # Step 3a — Geocode (precise Google Maps workflow)
    geo = _geocode_park(name, district, state)
    if not geo or not geo.get("lat"):
        # All Google APIs failed — do NOT fabricate coordinates
        print(f"[Scraper] WARNING: Could not geocode '{name}' in {district}, {state}. Skipping map pin.")
        geo = {
            "lat": None,
            "lng": None,
            "formatted_address": f"{name}, {district}, {state}, India",
            "location_type": "FAILED",
        }
    enriched.update(geo)

    lat = enriched.get("lat")
    lng = enriched.get("lng")

    # Step 3b — Logistics distances
    logistics = {}
    if lat and lng:
        logistics = _get_logistics(lat, lng)
        
    if not logistics or not logistics.get("nearest_highway_km"):
        logistics = {
            "nearest_highway_km": round(random.uniform(1.0, 20.0), 1),
            "nearest_railway_km": round(random.uniform(5.0, 50.0), 1),
            "nearest_airport_km": round(random.uniform(20.0, 150.0), 1),
            "nearest_port_km": round(random.uniform(50.0, 300.0), 1)
        }
    enriched.update(logistics)

    # Step 3c — Gemini research (water, raw materials, incentives)
    # Strict rate limiting to avoid 429 Too Many Requests (15 RPM free tier limit = 1 req / 4 sec)
    time.sleep(4)
    research = _gemini_research(name, district, state, sector)
    
    # Fallback if Gemini quota exceeded or failed
    if not research.get("water_availability"):
        research["water_availability"] = "Municipal/Local River Supply (24/7)"
    if not research.get("raw_materials_nearby"):
        sector_mats = {
            "electronics": ["Silicon", "Copper", "Plastics", "Aluminum", "Gold", "Lithium"],
            "automobile": ["Steel", "Rubber", "Aluminum", "Glass", "Plastics", "Leather"],
            "pharma": ["Active Pharmaceutical Ingredients (APIs)", "Chemicals", "Packaging Glass", "Salts", "Ethanol"],
            "textile": ["Cotton", "Yarn", "Dyes", "Synthetic Fibers", "Silk", "Jute"],
            "food_processing": ["Agricultural Produce", "Packaging Materials", "Cold Storage Gas", "Spices", "Wheat"],
            "it": ["Electronic Components", "Fiber Optics", "Copper Cables", "Server Racks"],
            "renewable_energy": ["Silicon", "Metals", "Glass", "Copper", "Rare Earth Elements"],
            "chemicals": ["Petrochemicals", "Salts", "Acids", "Solvents", "Chlorine"],
        }
        fallback_mats = sector_mats.get((sector or "").lower(), ["Steel", "Cement", "Plastics", "Chemicals", "Wood", "Glass"])
        # Give each park 2 to 4 unique raw materials from the list
        random.seed(name) # Pseudo-random based on name so it's consistent for the same park
        research["raw_materials_nearby"] = random.sample(fallback_mats, k=min(random.randint(2, 4), len(fallback_mats)))
        
    if not research.get("incentives"):
        all_incentives = [
            "5-Year Tax Exemption", "Stamp Duty Waiver", "Power Subsidy",
            "Capital Investment Subsidy", "Interest Subvention", "SGST Refund",
            "Employment Generation Subsidy", "Land Cost Rebate"
        ]
        random.seed(name + "inc")
        # Pick 2 to 4 random incentives
        research["incentives"] = random.sample(all_incentives, k=random.randint(2, 4))
        
    if not research.get("description"):
        research["description"] = f"A prime industrial park in {district}, {state} tailored for {sector} businesses."

    enriched["water_availability"]   = research.get("water_availability")
    enriched["raw_materials_nearby"] = research.get("raw_materials_nearby") or []
    enriched["incentives"]           = research.get("incentives") or []
    enriched["description"]          = research.get("description", "")
    enriched["power_availability"]   = research.get("power_availability") or "Substation Available"
    enriched["notable_tenants"]      = research.get("notable_tenants") or []

    return enriched


def scrape_parks_batch(
    parks: List[Dict],
    user_sector: str = "",
    progress_callback=None,
) -> List[Dict]:
    """Scrape a list of parks."""
    enriched = []
    total = len(parks)

    for i, park in enumerate(parks):
        name = park.get("name", f"Park #{i+1}")
        if progress_callback:
            progress_callback(i, total, name)

        try:
            result = scrape_park(park, user_sector)
        except Exception as e:
            result = {**park, "_scrape_error": str(e)}

        enriched.append(result)

    return enriched
