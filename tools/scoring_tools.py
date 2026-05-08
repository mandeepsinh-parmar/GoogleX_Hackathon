"""Multi-Criteria Scoring & Ranking Tools for Startup India Advisor

These tools provide:
- Weighted location suitability scoring
- State ranking for business sectors
- Comparative analysis
"""

from typing import Dict, List

from .location_tools import get_state_infrastructure_score
from .scheme_tools import match_government_schemes


def calculate_location_score(
    state: str,
    sector: str,
    investment_size_inr: float,
    priority_power: int = 5,
    priority_logistics: int = 5,
    priority_labor: int = 5,
    priority_cost: int = 5,
    priority_schemes: int = 5
) -> Dict:
    """Calculate weighted location suitability score.

    Args:
        state: Target state
        sector: Business sector
        investment_size_inr: Investment size
        priority_power: 1-10 priority for power reliability
        priority_logistics: 1-10 priority for logistics
        priority_labor: 1-10 priority for labor availability
        priority_cost: 1-10 priority for land cost
        priority_schemes: 1-10 priority for government incentives

    Returns:
        Weighted score breakdown and recommendation
    """
    infra = get_state_infrastructure_score(state)
    if infra["status"] == "error":
        return infra

    # Determine business type from sector
    manufacturing_sectors = ["electronics", "textile", "automobile", "pharma", 
                           "food_processing", "renewable_energy"]
    business_type = "manufacturing" if sector.lower() in manufacturing_sectors else "service"

    schemes = match_government_schemes(
        business_type=business_type,
        sector=sector,
        investment_size_inr=investment_size_inr,
        state=state
    )

    metrics = infra["metrics"]

    # Normalize priorities (1-10)
    total_priority = (
        priority_power + priority_logistics + priority_labor + 
        priority_cost + priority_schemes
    )

    if total_priority == 0:
        total_priority = 25  # Default equal weights

    # Cost efficiency score (inverse of land cost, normalized 0-100)
    max_land_cost = 6000000  # Maharashtra reference
    cost_score = max(0, 100 - (metrics["land_cost_per_acre_inr"] / max_land_cost * 100))

    # Scheme benefit score (0-100 based on number of schemes)
    total_schemes = (
        len(schemes["schemes"]["central"]) + 
        len(schemes["schemes"]["state"])
    )
    scheme_score = min(total_schemes * 15, 100)

    # Calculate weighted score
    score = (
        (metrics["power_reliability"] * priority_power / total_priority) +
        (metrics["logistics_score"] * priority_logistics / total_priority) +
        (metrics["labor_availability"] * priority_labor / total_priority) +
        (cost_score * priority_cost / total_priority) +
        (scheme_score * priority_schemes / total_priority)
    )

    # Recommendation
    if score >= 80:
        recommendation = "Highly Recommended"
    elif score >= 65:
        recommendation = "Recommended"
    elif score >= 50:
        recommendation = "Viable with Caveats"
    else:
        recommendation = "Consider Alternatives"

    return {
        "status": "success",
        "state": state,
        "overall_score": round(score, 1),
        "max_possible": 100,
        "recommendation": recommendation,
        "breakdown": {
            "power": round(metrics["power_reliability"] * priority_power / total_priority, 1),
            "logistics": round(metrics["logistics_score"] * priority_logistics / total_priority, 1),
            "labor": round(metrics["labor_availability"] * priority_labor / total_priority, 1),
            "cost_efficiency": round(cost_score * priority_cost / total_priority, 1),
            "scheme_benefit": round(scheme_score * priority_schemes / total_priority, 1)
        },
        "scheme_summary": {
            "total_schemes": total_schemes,
            "central_schemes": len(schemes["schemes"]["central"]),
            "state_schemes": len(schemes["schemes"]["state"])
        }
    }


def rank_states_for_business(
    sector: str,
    investment_size_inr: float,
    priority_power: int = 5,
    priority_logistics: int = 5,
    priority_labor: int = 5,
    priority_cost: int = 5,
    priority_schemes: int = 5
) -> Dict:
    """Rank all Indian states for a given business profile.

    Args:
        sector: Business sector
        investment_size_inr: Investment size
        priority_*: Priority weights (1-10)

    Returns:
        Ranked list of top states with scores
    """
    states = [
        "gujarat", "karnataka", "tamil_nadu", "maharashtra", 
        "telangana", "uttar_pradesh", "rajasthan", "andhra_pradesh"
    ]

    rankings = []

    for state in states:
        result = calculate_location_score(
            state=state,
            sector=sector,
            investment_size_inr=investment_size_inr,
            priority_power=priority_power,
            priority_logistics=priority_logistics,
            priority_labor=priority_labor,
            priority_cost=priority_cost,
            priority_schemes=priority_schemes
        )

        if result["status"] == "success":
            rankings.append({
                "state": state.replace("_", " ").title(),
                "state_key": state,
                "score": result["overall_score"],
                "recommendation": result["recommendation"],
                "breakdown": result["breakdown"],
                "scheme_summary": result["scheme_summary"]
            })

    # Sort by score descending
    rankings.sort(key=lambda x: x["score"], reverse=True)

    return {
        "status": "success",
        "sector": sector,
        "investment_size_inr": investment_size_inr,
        "total_states_analyzed": len(rankings),
        "rankings": rankings
    }
