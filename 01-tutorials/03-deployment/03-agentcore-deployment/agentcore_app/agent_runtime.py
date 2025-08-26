from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client

def create_streamable_http_transport(mcp_url: str, access_token: str):
    return streamablehttp_client(mcp_url, headers={"Authorization": f"Bearer {access_token}"})

def get_all_tools(mcp_client):
    tools = []
    pagination_token = None
    while True:
        tmp_tools = mcp_client.list_tools_sync(pagination_token=pagination_token)
        tools.extend(tmp_tools)
        if getattr(tmp_tools, "pagination_token", None) is None:
            break
        pagination_token = tmp_tools.pagination_token
    return tools

def create_agentcore_app(
    model_id: str,
    region: str,
    gateway_url: str,
    gateway_access_token: str,
    temperature: float = 0.4,
    system_prompt: str = "You are a helpful AI assistant. Please answer the user's questions to the best of your ability."
):
    app = BedrockAgentCoreApp(mcp_url=gateway_url, access_token=gateway_access_token)

    # Setup MCP client to get tools from gateway
    mcp_client = MCPClient(lambda: create_streamable_http_transport(gateway_url, gateway_access_token))
    with mcp_client:
        tools = get_all_tools(mcp_client)

    bedrock_model = BedrockModel(
        model_id=model_id,
        temperature=temperature,
        region=region
    )

    agent = Agent(
        system_prompt=system_prompt,
        model=bedrock_model,
        tools=tools
    )

    @app.entrypoint
    def invoke(payload):
        user_message = payload.get("prompt", "Hello! How can I help you today?")
        result = agent(user_message)
        return {"result": result.message}

    return app
