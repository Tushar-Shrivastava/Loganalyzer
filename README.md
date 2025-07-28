# 🔍 MCP Log Analyzer

The **MCP Log Analyzer** is an AI-powered Streamlit app designed to analyze system log files, identify errors and warnings, and recommend fixes. It uses [FastMCP](https://github.com/langchain-ai/langchain/tree/main/libs/langchain-mcp-adapters), 
[LangGraph ReAct agents](https://github.com/langchain-ai/langgraph), and 
[Anthropic Claude](https://www.anthropic.com/) LLM to build a powerful multi-agent system.

---

## 📁 Project Structure

├── analyzer.py # MCP server with two tools: analyze_logs & suggest_fix
├── streamlit_ui.py # Streamlit web interface
├── streamlit_client.py # MCP client invoking tools via LangGraph + Claude
├── mcp_config_2.json # JSON config for MCP server commands
├── test_model.py # Placeholder test script
├── README.md # ← You're here
├── temp/ # Temporary files
├── Test logs/ # Sample or uploaded logs
├── Screenshots/ # UI screenshots
├── .venv/ # Python virtual environment

## Create Virtual Environment

python -m venv .venv
.\.venv\Scripts\activate

## Install Dependencies
pip install -r requirements.txt

### If requirements.txt doesn't exist, here are the needed packages:

pip install streamlit langchain langgraph langchain-anthropic anyio nest_asyncio
pip install mcp langchain-mcp-adapters

## 🧪 Run MCP Tool Server

python analyzer.py

## 🧠 Run the Streamlit Client App

streamlit run streamlit_ui.py

## 🧾 Sample mcp_config_2.json

{
    "mcpServers": {
        "LogAnalyzer": {
      "command": "{Your-directory}\\uv.EXE",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "{Your-directory}\\analyzer.py"
      ]
    }
    }
}

## 📦 Log File Format

Uploaded logs should be a list of JSON objects like:

[
  {
    "timestamp": "2025-07-26T12:30:01Z",
    "level": "ERROR",
    "component": "DataProcessor",
    "message": "NullPointerException in AuthService",
    "stack_trace": "java.lang.NullPointerException..."
  },
  ...
]


## 📌 Notes

Claude API key is required in streamlit_client.py. Replace 'Your-API-Key' with your actual key.

If using TCP transport instead of stdio (recommended on Windows), modify the server and client configs accordingly.

You can customize or add new tools in analyzer.py and expose them via @mcp.tool().


## 🧠 Credits

Built using:

LangChain MCP :- https://github.com/langchain-ai/langchain/tree/main/libs/langchain-mcp-adapters

Anthropic Claude :- https://www.anthropic.com/

Streamlit :- https://streamlit.io/

LangGraph Agents :- https://github.com/langchain-ai/langgraph


## 🛠️ Future Improvements

Add support for batch analysis or CSV uploads

Save session history

Enable tool reordering / multiple MCPs

Deploy to Hugging Face / Streamlit Cloud

## Screenshots :-

<img width="641" height="801" alt="Streamlit_app_1" src="https://github.com/user-attachments/assets/f87c6501-8067-406d-8134-709cbd0f1cee" />

<img width="691" height="829" alt="Streamlit_app_2" src="https://github.com/user-attachments/assets/0be2c09e-f943-4a46-abb0-b80a616f1821" />

<img width="598" height="822" alt="Streamlit_app_3" src="https://github.com/user-attachments/assets/2e1d7248-8087-47ec-bb4d-c2dbc5174d62" />

<img width="652" height="267" alt="python_terminal" src="https://github.com/user-attachments/assets/6a83c6d2-56b5-48fc-afa7-2c9eebb7b5ad" />





## 📃 License

MIT License


