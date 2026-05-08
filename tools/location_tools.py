"""Location Intelligence Tools for Startup India Advisor

These tools provide:
- Industrial park search across Indian states
- State infrastructure scoring
- Google Maps geocoding
- Nearby logistics infrastructure discovery
"""

import json
import os
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

# Load pre-cached data
_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

with open(os.path.join(_DATA_DIR, 'industrial_parks.json')) as f:
    INDUSTRIAL_PARKS = json.load(f)

with open(os.path.join(_DATA_DIR, 'state_scores.json')) as f:
    STATE_SCORES = json.load(f)

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')


def search_industrial_parks(
    state: str,
    sector: str = "",
    min_area_acres: Optional[float] = None,
    max_budget_inr: Optional[float] = None
) -> Dict:
    """Search for industrial parks in a given state matching sector and budget.

    Args:
        state: Indian state name (e.g., 'gujarat', 'karnataka')
        sector: Business sector (e.g., 'manufacturing', 'IT', 'textile')
        min_area_acres: Minimum land area required
        max_budget_inr: Maximum budget for land

    Returns:
        List of matching industrial parks with details
    """
    state_parks = [
        p for p in INDUSTRIAL_PARKS 
        if p['state'].lower() == state.lower()
    ]

    if sector:
        state_parks = [
            p for p in state_parks 
            if sector.lower() in p.get('sector', '').lower()
        ]

    if min_area_acres:
        state_parks = [
            p for p in state_parks 
            if p.get('available_acres', 0) >= min_area_acres
        ]

    # Sort by infrastructure score descending
    state_parks.sort(
        key=lambda x: x.get('infrastructure_score', 0), 
        reverse=True
    )

    return {
        "status": "success",
        "count": len(state_parks),
        "parks": state_parks[:5]  # Top 5
    }


def get_state_infrastructure_score(state: str) -> Dict:
    """Get comprehensive infrastructure score for an Indian state.

    Args:
        state: State name in lowercase (e.g., 'gujarat')

    Returns:
        Infrastructure metrics and overall composite score
    """
    state_key = state.lower().replace(" ", "_")

    if state_key not in STATE_SCORES:
        return {
            "status": "error", 
            "message": f"State '{state}' not found in database"
        }

    data = STATE_SCORES[state_key]

    # Calculate composite score (weighted average)
    composite = (
        data['power_reliability'] * 0.25 +
        data['logistics_score'] * 0.25 +
        data['labor_availability'] * 0.20 +
        data['ease_of_business'] * 0.30
    )

    # Determine tier
    if composite >= 88:
        tier = "A"
        tier_label = "Highly Recommended"
    elif composite >= 80:
        tier = "B"
        tier_label = "Recommended"
    else:
        tier = "C"
        tier_label = "Consider Alternatives"

    return {
        "status": "success",
        "state": state_key,
        "composite_score": round(composite, 1),
        "tier": tier,
        "tier_label": tier_label,
        "metrics": data
    }


def geocode_location(address: str) -> Dict:
    """Geocode an address using Google Maps Geocoding API.

    Args:
        address: Full address or place name in India

    Returns:
        Latitude, longitude, and formatted address
    """
    if not GOOGLE_MAPS_API_KEY:
        return {
            "status": "error",
            "message": "Google Maps API key not configured"
        }

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address + ", India",
        "key": GOOGLE_MAPS_API_KEY,
        "region": "in"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if data['status'] != 'OK':
            return {
                "status": "error", 
                "message": f"Geocoding failed: {data['status']}"
            }

        result = data['results'][0]
        return {
            "status": "success",
            "lat": result['geometry']['location']['lat'],
            "lng": result['geometry']['location']['lng'],
            "formatted_address": result['formatted_address'],
            "place_id": result['place_id']
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}"
        }


def get_nearby_logistics(
    lat: float, 
    lng: float, 
    radius_km: int = 50
) -> Dict:
    """Find nearby logistics infrastructure using Google Maps Places API.

    Args:
        lat: Latitude
        lng: Longitude
        radius_km: Search radius in kilometers

    Returns:
        Nearby highways, railway stations, ports, airports
    """
    if not GOOGLE_MAPS_API_KEY:
        return {
            "status": "error",
            "message": "Google Maps API key not configured"
        }

    categories = {
        "highways": "highway",
        "railway_stations": "train_station",
        "airports": "airport",
        "ports": "harbor"
    }

    results = {}

    for name, place_type in categories.items():
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius_km * 1000,
            "type": place_type,
            "key": GOOGLE_MAPS_API_KEY
        }

        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()

            if data['status'] == 'OK':
                results[name] = [
                    {
                        "name": p['name'],
                        "rating": p.get('rating', 'N/A'),
                        "vicinity": p.get('vicinity', '')
                    }
                    for p in data['results'][:3]
                ]
            else:
                results[name] = []
        except Exception:
            results[name] = []

    return {
        "status": "success", 
        "infrastructure": results
    }
