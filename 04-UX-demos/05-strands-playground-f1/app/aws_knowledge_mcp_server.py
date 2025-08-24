from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from strands_tools import file_write
from strands.models import BedrockModel

# import the environment variable for MCP model
import os
mcp_model = os.getenv("mcp_model", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
mcp_region = os.getenv("mcp_region", "us-west-2")

@tool
def aws_knowledge_mcp_server(query: str) -> str:
    """
    Process and respond AWS related queries.

    Args:
        query: The user's question

    Returns:
        A helpful response addressing user query
    """

    formatted_query = f"Analyze and respond to this question, providing clear explanations with examples where appropriate: {query}"
    
    bedrock_model = BedrockModel(model_id=mcp_model,region_name=mcp_region)
    response = str()

    try:
        aws_knowledge_mcp_server = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="uvx", 
                    args=[
                        "mcp-proxy",
                        "--transport",
                        "streamablehttp",
                        "https://knowledge-mcp.global.api.aws"
                    ]
                )
            )
        )

        with aws_knowledge_mcp_server:

            tools = aws_knowledge_mcp_server.list_tools_sync() + [file_write]

            # Create the research agent with specific capabilities
            research_agent = Agent(
                model=bedrock_model,
                system_prompt="""You are a thorough AWS researcher specialized in finding accurate 
                information online. For each question:
                
                1. Determine what information you need
                2. Search the AWS Documentation using documenttation mcp server for reliable information
                3. Extract key information and cite your sources
                4. Store important findings in memory for future reference
                5. Synthesize what you've found into a clear, comprehensive answer
                
                When researching, focus only on AWS documentation. Always provide citations 
                for the information you find.
                
                Finally output your response to a file into output folder under current directory with nicely html format.
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
    aws_knowledge_mcp_server("What is Amazon Bedrock")
