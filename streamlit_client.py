import traceback
from contextlib import AsyncExitStack
import os
import json

# MCP Client Imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Langchain Imports
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'content'):
            return {'type': o.__class__.__name__, 'content': o.content}
        return super().default(o)


# Ensure correct config path
os.environ["mcp_config_2"] = os.path.join(os.path.dirname(__file__), "mcp_config_2.json")


def read_config_json():
    config_path = os.getenv('mcp_config_2')
    if not config_path:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'mcp_config_2.json')

    with open(config_path, 'r') as f:
        return json.load(f)


async def run_agent(logs):
    # OpenAI GPT 4 LLM Integration
    llm = ChatAnthropic(
        model='claude-sonnet-4-20250514',
        temperature=0,
        max_retries=2,
        anthropic_api_key='Your-API-Key'
    )

    configu = read_config_json()
    mcp_servers = configu.get('mcpServers', {})

    try:
        async with AsyncExitStack() as stack:
            tools = []
            for server_name, server_info in mcp_servers.items():
                print(f"🔌 Connecting to MCP server")

                server_params = StdioServerParameters(
                    command=server_info['command'],
                    args=server_info['args']
                )

                try:
                    read, write = await stack.enter_async_context(stdio_client(server_params))
                    session = await stack.enter_async_context(ClientSession(read, write))
                    print("✅ MCP subprocess started, waiting for session initialization...")
                    await session.initialize()
                    server_tools = await load_mcp_tools(session)
                except Exception as e:
                    print(f"🚨 MCP Connection Failed for {server_name}")
                    traceback.print_exception(type(e), e, e.__traceback__)
                    raise e

                for tool in server_tools:
                    print(f"✅ Loaded tool: {tool.name}")
                    tools.append(tool)

                print(f"📦 {len(server_tools)} tools loaded from {server_name}.")

            agent = create_react_agent(llm, tools)

            try:
                print("🤖 Invoking agent...")
                response = await agent.ainvoke({
                    "messages": [
                        {"role": "user",
                         "content": f"Please analyze these logs: {json.dumps(logs, indent=2)} and suggest fixes."}
                    ]
                })
                print("✅ Agent response received")
                return response

            except Exception as e:
                print("❌ Agent invocation failed:", e)
                traceback.print_exc()
                return {"error": "Agent invocation failed", "details": traceback.format_exc()}

    except Exception as e:
        print("🚨 Unexpected exception in run_agent()")
        traceback.print_exc()
        return {"error": str(e), "details": traceback.format_exc()}
