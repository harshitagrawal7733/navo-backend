import asyncio
import os
import logging
import re
from datetime import datetime
from dotenv import load_dotenv
import yaml
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from root_agent.agent import root_agent
from utils import (
    Colors,
    display_welcome_message,
    display_help,
    display_system_status,
    handle_system_commands,
    update_session_state_after_execution,
    handle_execution_error,
    display_agent_outputs
)
"""
Load BASE_URL from config.yaml
"""
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'root_agent', 'config', 'config.yaml')
try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    env = config.get('env', 'local')
    BASE_URL = config.get(env, {}).get('server', {}).get('base_url', 'http://localhost:8080')
except Exception as e:
    print(f"[WARN] Could not load BASE_URL from config.yaml: {e}")
    BASE_URL = 'http://localhost:8080'

load_dotenv()
# DEBUG: Print the loaded GOOGLE_GENAI_API_KEY to verify .env loading
print("DEBUG: GOOGLE_GENAI_API_KEY =", os.environ.get("GOOGLE_GENAI_API_KEY"))
# Ensure API_KEY is set for libraries that expect it
if "GOOGLE_GENAI_API_KEY" in os.environ:
    os.environ["API_KEY"] = os.environ["GOOGLE_GENAI_API_KEY"]

# Reduce logging verbosity
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google_adk").setLevel(logging.ERROR)


# ===== Initial Session State =====
initial_state = {
    # Essential User Profile
    "user_id": "1",
    "phone_number": "6666666666",
    "user_email": "Sushrut@123gmail.com",
    "user_name": "Sushrut",
    "age": "21",
    "city": "Mumbai",
    "maritial_status":"Unmarried",
    "dependents":"None",
    "is_authenticated": True,  # Start as not authenticated
    "career_stage": "early_career",
    "preferred_language": "Hindi",

    "mcp_session_id": None,  # No static session
    "session_login_url": None,
    "available_tools": [],
    "tool_execution_history": [],
    "use_existing_mcp_session": False,
    
    # Agent State (Simplified)
    "current_agent": "finara_coordinator",
    "last_active_subagent": None,
    "last_agent_response": None,
    
    # Conversation Management
    "conversation_context": [],
    "interaction_history": [],
    
    # System Health (Essential)
    "error_count": 0,
    "last_error": None,
    "system_status": "ready",  # Start as ready, not authenticated
}

async def process_agent_response(event):
    """Process and display agent response events """
    final_response = None
    
    # Check for final response
    if event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            # Simplified response display
            print(f"\n{Colors.CYAN}🤖 {final_response}{Colors.RESET}\n")
        else:
            print(f"{Colors.YELLOW}⚠️ No response content received{Colors.RESET}")

    return final_response


async def call_agent_async(runner, user_id, session_id, query, session_with_auth_state):
    """Call the agent asynchronously with the user's query - with conversation context."""
    
    # Use the session that has the authentication state instead of getting a fresh one
    session = session_with_auth_state

    # *** ADD THIS: Ensure the runner's session has the latest state ***
    try:
        # Update the runner's session with our current state
        runner_session = await runner.session_service.get_session(
            app_name=runner.app_name, user_id=user_id, session_id=session_id
        )
        # Sync critical state to the runner's session
        runner_session.state.update({
            "mcp_session_id": session.state.get("mcp_session_id"),
            "is_authenticated": session.state.get("is_authenticated"),
            "use_existing_mcp_session": session.state.get("use_existing_mcp_session"),
            "authenticated_mcp_session": session.state.get("mcp_session_id")  # Additional key for tool
        })
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Could not sync session state: {e}{Colors.RESET}")
    
    # Build conversation context for the agent 
    interaction_history = session.state.get("interaction_history", [])
    context_messages = []
    
    # Check authentication status
    is_authenticated = session.state.get("is_authenticated", False)
    mcp_session_id = session.state.get("mcp_session_id")
    
    if interaction_history:
        context_messages.append("=== CONVERSATION HISTORY ===")
        for interaction in interaction_history[-5:]:  # Last 5 interactions
            if interaction.get("type") == "user_query":
                user_query_text = interaction.get('query', '')
                context_messages.append(f"User: {user_query_text}")
                # Explicitly highlight authentication messages
                if any(phrase in user_query_text.lower() for phrase in ['logged in', 'login done', 'login complete']):
                    context_messages.append("^^ USER CONFIRMED LOGIN COMPLETION ^^")
            elif interaction.get("type") == "agent_response":
                response = interaction.get('response', '')[:150]  # Truncate long responses
                context_messages.append(f"Assistant: {response}...")
        context_messages.append("=== END HISTORY ===")
        context_messages.append("")  # Empty line
    
    # Combine context and current query
    if context_messages:
        full_message = "\n".join(context_messages) + f"Current Query: {query}"
    else:
        full_message = query
    
    # DEBUG: Print what we're sending to the agent
    print(f"{Colors.YELLOW}DEBUG - Sending to agent:{Colors.RESET}")
    print(f"{Colors.YELLOW}{full_message[:500]}...{Colors.RESET}")
    
    content = types.Content(role="user", parts=[types.Part(text=full_message)])
    print(f"{Colors.BLUE}🤖 Processing: {query}{Colors.RESET}")
    
    final_response_text = None
    active_agent_name = None

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # Only capture agent name, no excessive logging
            if event.author:
                active_agent_name = event.author

            response = await process_agent_response(event)
            if response:
                final_response_text = response
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")

    # Simplified session update
    if final_response_text and active_agent_name:
        try:
            session = await runner.session_service.get_session(
                app_name=runner.app_name, user_id=user_id, session_id=session_id
            )
            
            # Store response without excessive logging
            agent_output_key = f"{active_agent_name}_output"
            session.state[agent_output_key] = final_response_text
            session.state["last_active_subagent"] = active_agent_name
            session.state["last_agent_response"] = final_response_text
            
            # Add to history
            interaction_history = session.state.get("interaction_history", [])
            interaction_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "agent_response",
                "agent": active_agent_name,
                "response": final_response_text
            })
            session.state["interaction_history"] = interaction_history
            
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not update session: {e}{Colors.RESET}")

    return final_response_text

async def execute_user_query(session, session_service, app_name, user_id, session_id, user_query):
    """Execute user query with proper error handling and state management."""
    try:
        # ADD: Debug current session state before proceeding
        print(f"{Colors.YELLOW}DEBUG - Session state before query: is_authenticated = {session.state.get('is_authenticated')}{Colors.RESET}")
        
        # Add query to interaction history
        interaction_history = session.state.get("interaction_history", [])
        interaction_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "user_query",
            "query": user_query
        })
        session.state["interaction_history"] = interaction_history

        # *** ADD THIS: Create coordinator with current session state ***
   
        
        # Get fresh session data for coordinator
        # fresh_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)

        # Create runner with up-to-date coordinator
        root_agent_instance = root_agent(session=None)
        runner = Runner(
           agent=root_agent_instance,
           app_name=app_name,
           session_service=session_service,
        )
    
        # *** ADD THIS: Ensure runner's session is synced before execution ***
        try:
            runner_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
            runner_session.state.update(session.state)  # Sync all state
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not sync runner session: {e}{Colors.RESET}")
        
        # Don't set any static session - let the proper login flow work
        if session.state.get("mcp_session_id"):
            existing_session = session.state.get("mcp_session_id")
            print(f"{Colors.GREEN}🔑 Using existing MCP session: {existing_session}{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}🔑 No MCP session found. Login flow will be triggered.{Colors.ENDC}")

        # Execute the agent
        final_response = await call_agent_async(runner, user_id, session_id, user_query, session)
        
        # Check if response contains login URL and extract MCP session ID
        if final_response and "mockWebPage?sessionId=" in final_response:
            match = re.search(r'sessionId=([^)\s&]+)', final_response)
            if match:
                mcp_session_id = match.group(1)
                session.state["mcp_session_id"] = mcp_session_id
                session.session.state["session_login_url"] = f"{BASE_URL}/mockWebPage?sessionId={mcp_session_id}"
                session.state["is_authenticated"] = True
                print(f"{Colors.GREEN}📝 Stored MCP Session ID: {mcp_session_id}{Colors.ENDC}")
        
        # Update session state after successful execution
        update_session_state_after_execution(session, final_response)
        
        # Display results
        print(f"\n{Colors.GREEN}✅ Analysis Complete{Colors.ENDC}")
        display_agent_outputs(session.state)
        
        return True
        
    except Exception as e:
        handle_execution_error(session, e, user_query)
        
        # Print detailed error for debugging if needed
        if session.state.get("error_count", 0) >= 2:
            print(f"\n{Colors.YELLOW}Debug Information:{Colors.ENDC}")
            print(f"{Colors.YELLOW}Error Type: {type(e).__name__}{Colors.ENDC}")
            print(f"{Colors.YELLOW}Error Details: {str(e)[:200]}...{Colors.ENDC}")
        
        return False

async def main():
    """Enhanced main async function to run the Finara agent system."""
    # Define App constants
    APP_NAME = "Finara"
    USER_ID = initial_state["user_id"]

    print(f"{Colors.GREEN}🚀 Initializing Finara Financial Assistant...{Colors.ENDC}")
    
    try:
        # Create session service and session properly with await
        session_service = InMemorySessionService()
        
        # Create a new session and set its initial state (await the async call)
        # Removed await
        session =  session_service.create_session(app_name=APP_NAME, user_id=USER_ID, state=initial_state)
        SESSION_ID = session.id
        
        print(f"{Colors.GREEN}✅ Session created with ID: {SESSION_ID}{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to initialize session: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Please check your ADK setup and try again.{Colors.ENDC}")
        return
    
    # Display welcome message
    display_welcome_message()

    # Main interaction loop
    while True:
        try:
            user_query = input(f"\n{Colors.BOLD}💬 You: {Colors.ENDC}").strip()
            
            if not user_query:
                continue
                
            # Handle system commands
            command_result = handle_system_commands(user_query, session, session_service, APP_NAME, USER_ID, SESSION_ID)
            if command_result == "exit":
                break
            elif command_result:
                continue
            
            # Execute user query
            success = await execute_user_query(session, session_service, APP_NAME, USER_ID, SESSION_ID, user_query)
            
            if not success and session.state.get("error_count", 0) >= 5:
                print(f"{Colors.RED}❌ Too many errors encountered. Please restart the application.{Colors.ENDC}")
                break
                
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}👋 Session interrupted. Goodbye!{Colors.ENDC}")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ Critical system error: {e}{Colors.ENDC}")
            session.state["system_status"] = "critical_error"
            break

    # Cleanup and final status
    print(f"\n{Colors.HEADER}📊 FINAL SESSION SUMMARY{Colors.ENDC}")
    print(f"{Colors.CYAN}Total Interactions: {len(session.state.get('interaction_history', []))}{Colors.ENDC}")
    print(f"{Colors.CYAN}Errors Encountered: {session.state.get('error_count', 0)}{Colors.ENDC}")
    print(f"{Colors.GREEN}Thank you for using Finara! 🏦✨{Colors.ENDC}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"{Colors.RED}❌ Fatal error starting Finara: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Please check your environment setup and try again.{Colors.ENDC}")