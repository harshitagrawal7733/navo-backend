from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from root_agent.agent import root_agent

# === Initialize Flask App ===
app = Flask(__name__)
CORS(app, resources={r"/finara/*": {"origins": "*"}})  # Enable CORS for React or other clients
logging.basicConfig(level=logging.INFO)

# === Initial Session State ===
initial_state = {
    "user_id": "1",
    "phone_number": "6666666666",
    "user_email": "Sushrut@123gmail.com",
    "user_name": "Sushrut",
    "age": "21",
    "city": "Mumbai",
    "maritial_status": "Unmarried",
    "dependents": "None",
    "is_authenticated": False,
    "career_stage": "early_career",
    "preferred_language": "English",
    "mcp_session_id": None,
    "session_login_url": None,
    "available_tools": [],
    "tool_execution_history": [],
    "use_existing_mcp_session": False,
    "current_agent": "finara_coordinator",
    "last_active_subagent": None,
    "last_agent_response": None,
    "conversation_context": [],
    "interaction_history": [],
    "error_count": 0,
    "last_error": None,
    "system_status": "ready",
}

# === Setup Session Service ===
session_service = InMemorySessionService()
session = session_service.create_session(app_name="Finara", user_id="user1", state=initial_state)
SESSION_ID = session.id


# === Chat Endpoint ===
@app.route("/finara/chat", methods=["POST"])
def chat():
    try:
        user_query = request.json.get("query", "")
        if not user_query:
            return jsonify({"reply": "❗ No query provided."}), 400

        logging.info(f"Received query: {user_query}")
        content = types.Content(role="user", parts=[types.Part(text=user_query)])
        root_agent_instance = root_agent(session=None)
        
    
        runner = Runner(agent=root_agent_instance, app_name="Finara", session_service=session_service)

        async def run_runner():
            async for event in runner.run_async(user_id="user1", session_id=SESSION_ID, new_message=content):
                if event.is_final_response() and event.content and event.content.parts:
                    return event.content.parts[0].text.strip()
            return "⚠️ No final response from agent."

        response_text = asyncio.run(run_runner())
        return jsonify({"reply": response_text})

    except Exception as e:
        logging.exception("Error during chat processing")
        return jsonify({"reply": f"❌ Error: {str(e)}"}), 500


# === Entry Point ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
