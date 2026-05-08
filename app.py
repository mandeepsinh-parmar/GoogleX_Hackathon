"""Flask Backend for Startup India Advisor

API Endpoints:
- GET  /              → Serves the main HTML interface
- POST /api/analyze   → Full ADK agent chain analysis
- POST /api/rank-states → Fast direct API for state rankings
- POST /api/parks     → Search industrial parks
- POST /api/schemes   → Match government schemes
- POST /api/subsidy   → Estimate subsidy value
- POST /api/chat      → Direct Gemini chat for Q&A
"""

import json
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ============================================================
# Import tools directly for fast API paths
# ============================================================
from tools.location_tools import (
    search_industrial_parks,
    get_state_infrastructure_score,
    geocode_location,
    get_nearby_logistics
)
from tools.scheme_tools import (
    match_government_schemes,
    estimate_subsidy_value
)
from tools.scoring_tools import (
    calculate_location_score,
    rank_states_for_business
)

# ============================================================
# ADK Runner (for full agent chain)
# ============================================================
try:
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from agent import startup_india_advisor

    session_service = InMemorySessionService()
    runner = Runner(
        agent=startup_india_advisor,
        app_name="startup_india_advisor",
        session_service=session_service
    )
    ADK_AVAILABLE = True
except Exception as e:
    print(f"ADK not available: {e}")
    ADK_AVAILABLE = False

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template(
        'index.html',
        maps_api_key=os.getenv('GOOGLE_MAPS_API_KEY', '')
    )


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Full AI analysis using ADK agent chain.

    This is the SLOW path (30-60 seconds) but provides the richest output.
    Uses the SequentialAgent: feasibility → location → schemes.
    """
    if not ADK_AVAILABLE:
        return jsonify({
            "status": "error",
            "message": "ADK agent not available. Use /api/rank-states for direct analysis."
        }), 503

    data = request.json or {}

    # Build natural language query for the agent
    query = f"""
I want to start a {data.get('sector', 'manufacturing')} business in India.
Investment size: Rs {data.get('investment', 0):,}.
Expected employment: {data.get('employment', 'unknown')} people.
Business type: {data.get('business_type', 'manufacturing')}.

My priorities (1-10 scale):
- Power reliability: {data.get('priority_power', 5)}
- Logistics/connectivity: {data.get('priority_logistics', 5)}
- Labor availability: {data.get('priority_labor', 5)}
- Low land cost: {data.get('priority_cost', 5)}
- Government incentives: {data.get('priority_schemes', 5)}

Please:
1. Rank the top 5 states for this business
2. Deep-dive into the #1 recommended state with specific industrial parks
3. Find all applicable central and state government schemes
4. Estimate total subsidy value I can expect
5. Provide a final go/no-go recommendation with confidence level
"""

    try:
        # Create session and run agent
        session = session_service.create_session(
            app_name="startup_india_advisor",
            user_id="hackathon_user"
        )

        events = runner.run(
            user_id="hackathon_user",
            session_id=session.id,
            new_message=query
        )

        # Extract final response
        final_response = ""
        for event in events:
            if event.is_final_response() and event.content.parts:
                final_response = event.content.parts[0].text

        return jsonify({
            "status": "success",
            "analysis": final_response,
            "session_id": session.id,
            "raw_input": data
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Agent execution failed: {str(e)}"
        }), 500


@app.route('/api/rank-states', methods=['POST'])
def rank_states():
    """Fast direct API for state ranking.

    This is the FAST path (< 1 second) using direct tool calls.
    Returns ranked states with scores and breakdowns.
    """
    data = request.json or {}

    try:
        result = rank_states_for_business(
            sector=data.get('sector', 'manufacturing'),
            investment_size_inr=float(data.get('investment', 0)),
            priority_power=int(data.get('priority_power', 5)),
            priority_logistics=int(data.get('priority_logistics', 5)),
            priority_labor=int(data.get('priority_labor', 5)),
            priority_cost=int(data.get('priority_cost', 5)),
            priority_schemes=int(data.get('priority_schemes', 5))
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Ranking failed: {str(e)}"
        }), 500


@app.route('/api/parks', methods=['POST'])
def parks():
    """Search industrial parks by state and sector."""
    data = request.json or {}

    try:
        result = search_industrial_parks(
            state=data.get('state', 'gujarat'),
            sector=data.get('sector', ''),
            min_area_acres=data.get('min_area'),
            max_budget_inr=data.get('max_budget')
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Park search failed: {str(e)}"
        }), 500


@app.route('/api/schemes', methods=['POST'])
def schemes():
    """Match government schemes for business profile."""
    data = request.json or {}

    try:
        result = match_government_schemes(
            business_type=data.get('business_type', 'manufacturing'),
            sector=data.get('sector', 'electronics'),
            investment_size_inr=float(data.get('investment', 0)),
            state=data.get('state', 'gujarat'),
            employment_target=int(data.get('employment', 0)),
            is_startup=bool(data.get('is_startup', False)),
            is_msme=bool(data.get('is_msme', False))
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Scheme matching failed: {str(e)}"
        }), 500


@app.route('/api/subsidy', methods=['POST'])
def subsidy():
    """Estimate subsidy value for a specific scheme."""
    data = request.json or {}

    try:
        result = estimate_subsidy_value(
            scheme_name=data.get('scheme_name', ''),
            investment_size_inr=float(data.get('investment', 0)),
            projected_revenue_inr=float(data.get('revenue', 0))
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Subsidy estimation failed: {str(e)}"
        }), 500


@app.route('/api/infrastructure', methods=['POST'])
def infrastructure():
    """Get state infrastructure score."""
    data = request.json or {}

    try:
        result = get_state_infrastructure_score(data.get('state', 'gujarat'))
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Infrastructure query failed: {str(e)}"
        }), 500


@app.route('/api/geocode', methods=['POST'])
def geocode():
    """Geocode an address using Google Maps."""
    data = request.json or {}

    try:
        result = geocode_location(data.get('address', ''))
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Geocoding failed: {str(e)}"
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Direct Gemini chat for Q&A about locations/schemes.

    Fallback when ADK is not available or for simple queries.
    """
    data = request.json or {}
    message = data.get('message', '')

    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

        model = genai.GenerativeModel('gemini-2.5-flash-preview')

        system_prompt = """You are an expert Indian government scheme and industrial location consultant.
        Answer questions about Indian states, industrial parks, government schemes, subsidies, and business feasibility.
        Always provide specific, actionable information with numbers where possible.
        If you don't know something, say so clearly."""

        response = model.generate_content(
            f"{system_prompt}\n\nUser: {message}\n\nAssistant:",
            generation_config={
                'temperature': 0.3,
                'max_output_tokens': 1024
            }
        )

        return jsonify({
            "status": "success",
            "response": response.text
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Chat failed: {str(e)}"
        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================
@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "adk_available": ADK_AVAILABLE,
        "version": "1.0.0-hackathon"
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
