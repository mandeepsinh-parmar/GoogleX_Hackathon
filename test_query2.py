from tools.location_tools import query_parks

for state in ["ASSAM", "MIZORAM", "PUNJAB", "HARYANA", "BIHAR", "JHARKHAND", "CHHATTISGARH", "ODISHA"]:
    res = query_parks(sector="electronics", state=state)
    print(f"State {state}: {res['returned']} parks")
