import json
from app import app
import sys

with open("generator_output.txt", "w") as f:
    with app.test_request_context('/api/run-pipeline', json={
        "parks": [{"name": "Test Park", "district": "Ahmedabad", "state": "GUJARAT", "sector": "Mixed"}],
        "requirements": {"sector": "electronics", "preferred_state": "GUJARAT"}
    }):
        from app import run_pipeline
        resp = run_pipeline()
        for chunk in resp.response:
            f.write(chunk + "\n")
