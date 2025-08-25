from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
import sys
import json
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from root_agent.agent import root_agent

# === Initial Session State ===
initial_state = {
    "tool": [],       # Multiple tools supported
    "role": "",
    "team": "",
    "project": ""
}

# === Initialize Flask App ===
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS

# === Setup Logging ===
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
handler.setFormatter(formatter)
logger.handlers = [handler]

logging.info("🔹 Flask app starting...")

# === Setup Session Service ===
session_service = InMemorySessionService()
session = session_service.create_session(app_name="Navo", user_id="user1", state=initial_state)
SESSION_ID = session.id
logging.info(f"🔹 Session created with ID: {SESSION_ID}")


# === Chat Endpoint ===
@app.route("/navo/chat", methods=["POST"])
def chat():
    try:
        # Log full request JSON
        logging.debug(f"📥 Incoming request: {request.json}")

        user_query = request.json.get("query", "")
        preferences = request.json.get("preferences", {})  # Optional preferences

        logging.info(f"📌 User query: {user_query}")
        logging.info(f"📌 User preferences: {preferences}")

        # Update session state with preferences
        if preferences:
            session.state.update({
                "tool": preferences.get("tool", []),
                "role": preferences.get("role", ""),
                "team": preferences.get("team", ""),
                "project": preferences.get("project", "")
            })
            logging.info(f"🔄 Updated session preferences: {session.state}")

        if not user_query:
            return jsonify({"reply": "❗ No query provided."}), 400

        # Prepare content for agent

        query_text = user_query
        if preferences:
            query_text += f"\nPreferences: {json.dumps(preferences)}"
        logging.debug(f"📥 Incoming user query: {query_text}")
        content = types.Content(role="user", parts=[types.Part(text=query_text)])
        root_agent_instance = root_agent(session=session)
        
        runner = Runner(agent=root_agent_instance, app_name="Navo", session_service=session_service)

        # Async call wrapper
        async def run_runner():   
            async for event in runner.run_async(user_id="user1", session_id=SESSION_ID, new_message=content):
                if event.is_final_response() and event.content and event.content.parts:
                    final_text = event.content.parts[0].text.strip()
                    logging.debug(f"📤 Agent final response: {final_text}")
                    return final_text
            return "⚠️ No final response from agent."

        response_text = asyncio.run(run_runner())
        logging.info(f"✅ Sending response: {response_text}")
        return jsonify({"reply": response_text})

    except Exception as e:
        logging.exception("❌ Error during chat processing")
        return jsonify({"reply": f"❌ Error: {str(e)}"}), 500


# === Entry Point ===
if __name__ == "__main__":
    logging.info("🔹 Running Flask app on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
