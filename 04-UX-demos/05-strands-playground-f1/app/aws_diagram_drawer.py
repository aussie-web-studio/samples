from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from strands_tools import file_write
from strands.models import BedrockModel
import sys

# import the environment variable for MCP model
import os
mcp_model = os.getenv("mcp_model", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
mcp_region = os.getenv("mcp_region", "us-west-2")

@tool
def aws_diagram_drawer(query: str) -> str:
    """
    Process and respond AWS related queries.

    Args:
        query: The user's question

    Returns:
        A helpful response addressing user query
    """

    formatted_query = f"Analyze and respond to this question: {query}"
    
    bedrock_model = BedrockModel(model_id=mcp_model,region_name=mcp_region)
    response = str()

    try:
        diagram_mcp_server = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="uvx", args=["awslabs.aws-diagram-mcp-server@latest"], env={"FASTMCP_LOG_LEVEL": "ERROR"}
                )
            )
        )

        with diagram_mcp_server:

            tools = diagram_mcp_server.list_tools_sync() + [file_write]

            # Create the research agent with specific capabilities
            research_agent = Agent(
                model=bedrock_model,
                system_prompt="""You are a thorough AWS diagram drawer specialized in creating accurate diagrams based on AWS services. For each question:
                1. Determine what information you need
                2. Extract key information and create a diagram
                3. Store important findings in memory for future reference
                4. Synthesize what you've found into a clear, comprehensive answer
                When researching, focus only on AWS documentation. Always provide citations
                for the information you find.
                Finally output your response to a file in folder name output in the current directory with nicely format, keep the final diagram only, not the individual icons.
                """,
                tools=tools,
            )
            response = str(research_agent(formatted_query))
            
            print("\n\n")

        if len(response) > 0:
            return response

        return "I apologize, but I couldn't properly analyze your question. Could you please rephrase or provide more context?"

    # Return specific error message for English queries
    except Exception as e:
        return f"Error processing your query: {str(e)}"


if __name__ == "__main__":
    result = aws_diagram_drawer("Draw a diagram for a simple web application architecture using AWS services.")
    print(result)
