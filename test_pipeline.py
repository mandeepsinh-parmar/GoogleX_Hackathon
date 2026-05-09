import requests

reqs = {
    "parks": [
        {"name": "Test Park", "district": "Ahmedabad", "state": "GUJARAT", "sector": "Mixed"}
    ],
    "requirements": {
        "sector": "electronics",
        "investment_inr": 50000000,
        "land_required_acres": 5,
        "preferred_state": "GUJARAT"
    }
}

try:
    print("Testing /api/run-pipeline...")
    # It's an SSE stream, so we use stream=True
    res = requests.post("http://127.0.0.1:5000/api/run-pipeline", json=reqs, stream=True)
    for line in res.iter_lines():
        if line:
            print(line.decode('utf-8'))
except Exception as e:
    import traceback
    traceback.print_exc()
