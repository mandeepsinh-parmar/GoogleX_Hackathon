import requests

reqs = {
    "sector": "electronics",
    "investment_inr": 50000000,
    "land_required_acres": 5,
    "preferred_state": "GUJARAT",
    "logistics_required": False,
    "labor_required": False,
    "water_required": False,
    "plug_and_play": False,
    "max_results": 15
}

try:
    print("Testing /api/find-parks...")
    res = requests.post("http://127.0.0.1:5000/api/find-parks", json=reqs)
    print(res.status_code)
    data = res.json()
    print(f"Status: {data.get('status')}")
    print(f"Parks: {len(data.get('parks', []))}")
except Exception as e:
    import traceback
    traceback.print_exc()
