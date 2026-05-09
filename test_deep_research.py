from agents.ranking_agent import _deep_research_park

park = {
    "name": "Test Park",
    "state": "Gujarat",
    "district": "Ahmedabad",
    "sector": "Mixed",
    "available_area_acres": 50,
    "water_availability": "Yes",
    "nearest_highway_km": 10,
    "nearest_railway_km": 20,
    "incentives": ["Tax holiday", "Power subsidy"]
}
reqs = {"sector": "electronics", "investment_inr": 50000000}

print("Testing _deep_research_park...")
res = _deep_research_park(park, reqs)
print("Result:", res)
