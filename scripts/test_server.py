from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import asyncio

async def run_test():
    server_params = StdioServerParameters(
        command="python",
        args=["src/server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            tools = await session.list_tools()
            print("Available tools:", [tool.name for tool in tools.tools])
            
            try:
                result = await session.call_tool("get_cpu_info", {})
                print("Tool result:", result)
            except Exception as e:
                print(f"Error calling tool: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
