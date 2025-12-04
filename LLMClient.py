from dotenv import load_dotenv
load_dotenv()

import os
import json
import asyncio
from openai import OpenAI
from typing import List, Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack


class SystemMonitorLLM:
    """
    LLM-based system monitoring client.
    It processes natural language queries via OpenAI API and communicates with the FastMCP server.
    """

    def __init__(self, api_key: Optional[str] = None, server_path: str = "FastMCPServer.py"):
        """
        Initializes the LLM client.

        Args:
            api_key: OpenAI API key. If None, it will be read from the environment.
            server_path: Path to the FastMCP server file
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.conversation_history = []
        self.server_path = server_path

        # MCP connection objects
        self.exit_stack = None
        self.session = None
        self.available_tools = []

    async def connect_to_mcp_server(self):
        """Connects to the FastMCP server and fetches available tools."""
        self.exit_stack = AsyncExitStack()

        server_params = StdioServerParameters(
            command="python",
            args=[self.server_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        response = await self.session.list_tools()

        self.available_tools = self._convert_mcp_tools_to_openai_format(response.tools)

        print(f"✅ Connected to FastMCP server. {len(self.available_tools)} tools are available.")

    def _convert_mcp_tools_to_openai_format(self, mcp_tools) -> List[Dict[str, Any]]:
        """
        Converts MCP tool schemas into OpenAI function calling format.
        """
        openai_tools = []

        for tool in mcp_tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or f"Executes the {tool.name} function",
                    "parameters": tool.inputSchema if hasattr(tool, 'inputSchema') else {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            openai_tools.append(openai_tool)

        return openai_tools

    async def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Calls a tool on the FastMCP server.

        Args:
            tool_name: Tool name
            arguments: Tool parameters

        Returns:
            str: Tool result in JSON format
        """
        try:
            result = await self.session.call_tool(tool_name, arguments)

            if result.content:
                content_parts = []
                for content in result.content:
                    if hasattr(content, 'text'):
                        content_parts.append(content.text)
                    else:
                        content_parts.append(str(content))

                return "\n".join(content_parts)
            else:
                return json.dumps({"error": "No content returned from tool"})

        except Exception as e:
            return json.dumps({"error": f"MCP tool call failed: {str(e)}"})

    async def chat_async(self, user_message: str) -> str:
        """
        Processes user input and returns a response (async version).
        """

        if not self.conversation_history:
            system_message = {
                "role": "system",
                "content": """You are a system monitoring assistant. You help users ask questions about their operating system and manage system resources.

Your tasks:
1. Understand user questions and call the appropriate tools
2. Explain technical data in a clear and natural language
3. Warn users before critical operations (such as terminating processes)
4. Present numerical values and percentages clearly
5. Provide recommendations and solutions when necessary

Rules:
- Always ask for confirmation before dangerous actions like process termination
- Be extra careful with critical system processes (pid < 1000)
- Present data clearly and in an organized way
- Be user-friendly and helpful
- Always respond in English"""
            }
            self.conversation_history.append(system_message)

        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=self.conversation_history,
            tools=self.available_tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            self.conversation_history.append({
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            })

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"\n🔧 Calling tool: {function_name}")
                print(f"📝 Parameters: {function_args}")

                function_response = await self._call_mcp_tool(function_name, function_args)

                self.conversation_history.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response
                })

            final_response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=self.conversation_history
            )

            assistant_message = final_response.choices[0].message.content
        else:
            assistant_message = response_message.content

        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def chat(self, user_message: str) -> str:
        """Synchronous wrapper for the async chat method."""
        return asyncio.run(self.chat_async(user_message))

    def reset_conversation(self):
        """Resets the conversation history."""
        self.conversation_history = []
        print("✅ Conversation history has been reset.")

    async def close(self):
        """Closes the MCP connection."""
        if self.exit_stack:
            await self.exit_stack.aclose()
            print("✅ MCP connection closed.")


async def main_async():
    print("=" * 60)
    print("🖥️  LLM-Assisted System Monitor")
    print("=" * 60)
    print("\nConnecting to FastMCP server...")

    try:
        llm = SystemMonitorLLM()

        await llm.connect_to_mcp_server()

        print("\nYou can now ask questions about your system in natural language!")
        print("Example questions:")
        print("  - Show CPU usage")
        print("  - List the top 5 processes using the most RAM")
        print("  - Which PID is Chrome running on?")
        print("  - Show the system summary")
        print("\nType 'exit' to quit, 'reset' to reset the conversation.\n")

        while True:
            user_input = input("👤 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("\n👋 See you later!")
                break

            if user_input.lower() == "reset":
                llm.reset_conversation()
                continue

            print("\n🤖 Assistant: ", end="")
            response = await llm.chat_async(user_input)
            print(response)
            print()

        await llm.close()

    except KeyboardInterrupt:
        print("\n\n👋 Program terminated.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease check the following:")
        print("1. Make sure the OPENAI_API_KEY environment variable is set")
        print("2. Make sure FastMCPServer.py exists in the current directory")
        print("3. Make sure required packages are installed: pip install -r requirements.txt")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
