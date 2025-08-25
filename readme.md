# GenAI-Powered Contextual Memory & Search Engine for Engineering Teams

## Overview
This project is a reusable GenAI-powered internal memory system designed to help engineering teams avoid reinventing the wheel. It retrieves solutions to similar problems from GitHub PRs, Jira tickets, Confluence docs, and ServiceNow incidents using semantic search and historical context awareness.

![Uploading image.png…]()



## Features
- **Semantic Search:** Find contextually similar incidents, code, or documentation from engineering history.
- **Memory Suggestions:** Get recommendations based on how similar issues were resolved in the past.
- **Real-time Assistant Integration:**
  - Auto-suggest related PRs in GitHub
  - Recommend Confluence pages and past bugs in Jira
  - Pop up similar cases in VSCode while coding
- **Mock Data Support:** Easily test and develop using local JSON files for each data source.

## Tech Stack
- **GenAI Embedding:** OpenAI, Cohere, HuggingFace models (mocked for local dev)
- **Vector DB:** Pinecone / Weaviate / FAISS / Redis Vector (mocked for local dev)
- **Indexing:** GitHub API, Jira API, Confluence REST API, SNOW API (mocked via JSON)
- **Orchestration:** LangChain or LangGraph
- **UI:** VSCode plugin / Slackbot / Internal Web Portal (future)
- **Storage:** S3 or MongoDB for raw docs (optional)

## Folder Structure
```
navo-backend/
├── app.py
├── main.py
├── requirements.txt
├── root_agent/
│   ├── agent.py
│   ├── sub_agents/
│   │   ├── github/
│   │   │   ├── agent.py
│   │   │   ├── prompt.py
│   │   ├── jira/
│   │   │   ├── agent.py
│   │   │   ├── prompt.py
│   │   ├── confluence/
│   │   │   ├── agent.py
│   │   │   ├── prompt.py
│   │   ├── service-now/
│   │   │   ├── agent.py
│   │   │   ├── prompt.py
│   ├── tools/
│   │   ├── github_tool.py
│   │   ├── jira_tool.py
│   │   ├── get_session_id.py
│   │   ├── tool_list_metadata.py
│   │   ├── tool_router.py
├── navo-projects/
│   ├── Team001/
│   │   ├── project001/
│   │   │   ├── github.json
│   │   │   ├── jira.json
│   │   │   ├── confluence.json
│   │   │   ├── servicenow.json
```

## How It Works
1. **Index Everything:**
   - PRs, issues, docs, and incidents are loaded from mock JSON files.
   - Each entry is chunked and embedded (mocked for local dev).
2. **Smart Query:**
   - Developer types a problem or query.
   - GenAI agent semantically searches the vector DB (mocked).
   - Returns contextually similar historical cases.
3. **Memory Suggestions:**
   - If a similar issue was resolved in the past, the agent suggests the solution.
4. **Integration:**
   - Can be extended to integrate with real APIs and UIs.

## Setup & Usage
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the application:**
   ```bash
   python app.py
   # or
   python main.py
   ```
3. **Test semantic search:**
   - Use the CLI to enter queries like:
     - "Find PRs about port binding issues"
     - "Show Jira tickets for payment gateway timeouts"

## Mock Data Format
- Each tool reads from its respective JSON file (e.g., `github.json`, `jira.json`).
- Example for `github.json`:
  ```json
  [
    {
      "id": 1,
      "title": "Fix port binding issue",
      "description": "Resolved port collision in Docker compose.",
      "author": "Alice",
      "date": "2024-08-01",
      "resolution": "Used dynamic ports."
    }
  ]
  ```

## Contributing
- Fork the repo and submit pull requests for improvements.
- Add new mock data files for additional sources.
- Extend agents to support real API integration.

## License
MIT License

## Contact
For questions or support, contact the Navo engineering team.
