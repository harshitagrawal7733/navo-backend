from datetime import datetime

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    OKGREEN = "\033[92m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    ENDC = RESET
    WARNING = YELLOW
    HEADER = MAGENTA

def display_welcome_message():
    print("\n🚀 Welcome to the Engineering Knowledge Assistant!")
    print("I can help you perform semantic search across your engineering knowledge base:")
    print("")
    print("🔍 Try asking things like:")
    print("  • 'Find similar PRs where we solved retry logic issues in Kafka consumers'")
    print("  • 'Search Confluence for architecture docs on async order processing'")
    print("  • 'Show Jira tickets related to payment gateway timeouts'")
    print("  • 'Retrieve ServiceNow incidents linked to login failures'")
    print("  • 'Find PRs that mention circuit breaker patterns'")
    print("  • '    '")
    print("")
    print("💡 I use vector embeddings + semantic search to bring you the most relevant results from GitHub, Confluence, Jira, and ServiceNow.")
    print("Let's get started!\n")

def display_help():
    """Display detailed help information."""
    print(f"\n{Colors.HEADER}🔍 NAVO HELP - AVAILABLE COMMANDS{Colors.ENDC}")
    print(f"{Colors.CYAN}")
    print("FINANCIAL ANALYSIS COMMANDS:")
    print("  net worth     - Complete financial overview")
    print("  assets        - Asset breakdown and allocation")
    print("  investments   - Investment performance summary")
    print("  mutual funds  - MF portfolio analysis")
    print("  stocks        - Equity holdings review")
    print("  credit        - Credit score and card analysis")
    print("  spending      - Expense tracking and insights")
    print("  epf           - EPF balance and retirement planning")
    print()
    print("SYSTEM COMMANDS:")
    print("  help          - Show this help message")
    print("  status        - Show system and session status")
    print("  clear         - Clear conversation history")
    print("  logged in     - Mark yourself as logged in after web login")
    print("  refresh       - Reset session and get new login URL")
    print("  exit/quit     - Exit the application")
    print(f"{Colors.ENDC}")

def display_system_status(session):
    """Display current system and session status."""
    print(f"\n{Colors.HEADER}📊 SYSTEM STATUS{Colors.ENDC}")
    print(f"{Colors.CYAN}")
    print(f"User: {session.state.get('user_name', 'Unknown')}")
    print(f"Session ID: {session.id}")
    print(f"Current Agent: {session.state.get('current_agent', 'Unknown')}")
    print(f"System Status: {session.state.get('system_status', 'Unknown')}")
    print(f"Error Count: {session.state.get('error_count', 0)}")
    print(f"Interactions: {len(session.state.get('interaction_history', []))}")
    print(f"{Colors.ENDC}")

def handle_system_commands(command, session, session_service, app_name, user_id, session_id):
    """Handle system commands like help, status, clear."""
    command = command.lower().strip()
    
    if command == "help":
        display_help()
        return True
    elif command == "status":
        display_system_status(session)
        return True
    elif command == "clear":
        session.state["interaction_history"] = []
        session.state["conversation_context"] = []
        print(f"{Colors.GREEN}✅ Conversation history cleared.{Colors.ENDC}")
        return True
    elif command in ["logged in", "login done", "login complete", "logged"]:
        # FIX: Ensure state is properly updated
        session.state["is_authenticated"] = True
        session.state["system_status"] = "authenticated"
        session.state["use_existing_mcp_session"] = True
        
        # ADD: Force session state update
        print(f"{Colors.YELLOW}DEBUG - Setting auth state: is_authenticated = True{Colors.RESET}")
        
        print(f"{Colors.GREEN}✅ Login status updated. You can now access your financial data.{Colors.ENDC}")
        if session.state.get("mcp_session_id"):
            print(f"{Colors.GREEN}🔑 Using MCP Session: {session.state.get('mcp_session_id')}{Colors.ENDC}")
        
        # ADD: Verify the state was set
        print(f"{Colors.YELLOW}DEBUG - Verification: is_authenticated = {session.state.get('is_authenticated')}{Colors.RESET}")
        
        return True
    elif command.startswith("mcp-session-") or (command.startswith("mcp_") and len(command) > 20):
        # Extract MCP session ID from command
        mcp_session_id = command
        session.state["mcp_session_id"] = mcp_session_id
        session.state["is_authenticated"] = True
        session.state["system_status"] = "authenticated"
        session.state["use_existing_mcp_session"] = True
        print(f"{Colors.GREEN}✅ MCP Session ID stored: {mcp_session_id}{Colors.ENDC}")
        print(f"{Colors.GREEN}✅ You can now access your financial data.{Colors.ENDC}")
        return True
    elif command in ["refresh", "reset", "new session"]:
        session.state["mcp_session_id"] = None
        session.state["is_authenticated"] = False
        session.state["system_status"] = "ready"
        session.state["use_existing_mcp_session"] = False
        session.state["session_login_url"] = None
        print(f"{Colors.YELLOW}🔄 Session reset. You'll get a new login URL on your next request.{Colors.ENDC}")
        return True
    elif command in ["exit", "quit", "bye"]:
        print(f"{Colors.CYAN}👋 Thank you for using Navo! Goodbye!{Colors.ENDC}")
        return "exit"
    
    return False

def update_session_state_after_execution(session, final_response):
    """Update session state after agent execution."""
    try:
        # Update last active agent
        if hasattr(final_response, 'agent_used'):
            session.state["last_active_subagent"] = final_response.agent_used
        
        # Update system status
        session.state["system_status"] = "active"
        
        # Reset error count on successful execution
        session.state["error_count"] = 0
        session.state["last_error"] = None
        
        # Update conversation context 
        context = session.state.get("conversation_context", [])
        context.append({
            "timestamp": datetime.now().isoformat(),
            "response_summary": str(final_response)[:200] + "..." if len(str(final_response)) > 200 else str(final_response)
        })
        session.state["conversation_context"] = context[-10:]  # Keep last 10
        
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Could not update session state: {e}{Colors.ENDC}")

def handle_execution_error(session, error, user_query):
    """Handle and log execution errors with proper categorization."""
    session.state["error_count"] = session.state.get("error_count", 0) + 1
    session.state["last_error"] = {
        "message": str(error),
        "timestamp": datetime.now().isoformat(),
        "query": user_query,
        "error_type": type(error).__name__
    }
    session.state["system_status"] = "error"
    
    error_str = str(error).lower()
    
    if "authentication" in error_str or "session" in error_str:
        print(f"{Colors.YELLOW}🔐 Authentication Issue Detected{Colors.ENDC}")
        print(f"{Colors.CYAN}It looks like you need to log in to access your financial data.{Colors.ENDC}")
        print(f"{Colors.CYAN}The system will guide you through the login process on your next request.{Colors.ENDC}")
    elif "timeout" in error_str or "connection" in error_str:
        print(f"{Colors.YELLOW}🌐 Connection Issue Detected{Colors.ENDC}")
        print(f"{Colors.CYAN}There seems to be a connectivity issue. Please try again in a moment.{Colors.ENDC}")
    elif "tool" in error_str:
        print(f"{Colors.YELLOW}🔧 Tool Execution Issue{Colors.ENDC}")
        print(f"{Colors.CYAN}There was an issue executing the financial tool. Please try rephrasing your request.{Colors.ENDC}")
    else:
        print(f"{Colors.RED}❌ An unexpected error occurred: {error}{Colors.ENDC}")
        if session.state["error_count"] >= 3:
            print(f"{Colors.YELLOW}⚠️  Multiple errors detected. Type 'status' to check system health.{Colors.ENDC}")

def display_agent_outputs(state):
    """Display agent outputs from state """
    # Only show if there are actual outputs and they're different from what was just displayed
    outputs_found = False
    for key, value in state.items():
        if key.endswith('_output') and value:
            outputs_found = True
            break
    
    if not outputs_found:
        print(f"{Colors.YELLOW}No additional outputs to display.{Colors.RESET}")

