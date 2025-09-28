import os
import datetime
import json
import sys
from dotenv import load_dotenv
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

# Load environment variables
load_dotenv()

app = BedrockAgentCoreApp()

def create_streamable_http_transport(mcp_url: str, access_token: str):
    return streamablehttp_client(mcp_url, headers={"Authorization": f"Bearer {access_token}"})

def get_full_tools_list(client):
    more_tools = True
    tools = []
    pagination_token = None
    while more_tools:
        tmp_tools = client.list_tools_sync(pagination_token=pagination_token)
        tools.extend(tmp_tools)
        if tmp_tools.pagination_token is None:
            more_tools = False
        else:
            more_tools = True
            pagination_token = tmp_tools.pagination_token
    return tools

# Embedded gateway info - copy from ../02_gateway/gateway_info.json
GATEWAY_INFO = {
    "gateway_id": "testgateway7730c499-s5puzwdzr4",
    "client_info": {
      "client_id": "4pr5hfs3eevrf81je01824v239",
      "client_secret": "19folarb2i4keqv4asucpmpemie3fd2kmea9h6dm2rp67ucp8b1a",
      "user_pool_id": "us-west-2_OFhKkCyn5",
      "token_endpoint": "https://agentcore-2975d8db.auth.us-west-2.amazoncognito.com/oauth2/token",
      "scope": "TestGateway/invoke",
      "domain_prefix": "agentcore-2975d8db"
    }
}

def get_gateway_info_for_id(gateway_id):
    """Get gateway info for specific gateway ID"""
    # Use embedded gateway info
    if GATEWAY_INFO["gateway_id"] == gateway_id:
        return GATEWAY_INFO
    
    # Try to load from local file as fallback
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, "../02_gateway/gateway_info.json")
    
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as f:
            data = json.load(f)
            gateways = data if isinstance(data, list) else [data]
            
            for gateway_info in gateways:
                if gateway_info.get("gateway_id") == gateway_id:
                    return gateway_info
    
    raise ValueError(f"Gateway {gateway_id} not found")

def get_gateway_access_token(gateway_id):
    """Get access token for specific gateway ID"""
    gateway_info = get_gateway_info_for_id(gateway_id)
    client_info = gateway_info["client_info"]
    gateway_client = GatewayClient(region_name="us-west-2")
    return gateway_client.get_access_token_for_cognito(client_info)

def get_gateway_url(gateway_id):
    """Get gateway URL for specific gateway ID"""
    return f"https://{gateway_id}.gateway.bedrock-agentcore.us-west-2.amazonaws.com/mcp"

# System prompt
today = datetime.datetime.today().strftime("%A, %B %d, %Y")

SYSTEM_PROMPT = f"""
You are an expert AI assistant with access to powerful tools through AgentCore Gateway.
You can help users with various tasks using the available tools from the gateway.

**Today's Date:** {today}

Your capabilities include:
- Weather information (get_weather function)
- Time information (get_time function)
- DynamoDB operations (if available)
- Lambda function execution (if available)  
- API integrations (if available)
- Any other tools configured in the gateways

You have access to tools from multiple AgentCore Gateways including get_weather and get_time functions.

Always use the appropriate tools to help users accomplish their tasks effectively.
"""

def create_gateway_mcp_client(gateway_id):
    """Create MCP client for a specific gateway"""
    access_token = get_gateway_access_token(gateway_id)
    gateway_url = get_gateway_url(gateway_id)
    return MCPClient(lambda: create_streamable_http_transport(gateway_url, access_token))

def load_tools_from_gateways(gateway_ids):
    """Load tools from multiple gateways"""
    all_tools = []
    
    for gateway_id in gateway_ids:
        try:
            mcp_client = create_gateway_mcp_client(gateway_id)
            
            with mcp_client:
                tools = get_full_tools_list(mcp_client)
                all_tools.extend(tools)
                print(f"Loaded {len(tools)} tools from gateway {gateway_id}: {[tool.tool_name for tool in tools]}")
        except Exception as e:
            print(f"Warning: Could not load tools from gateway {gateway_id}: {e}")
    
    return all_tools

# Use embedded gateway ID
gateway_ids = [GATEWAY_INFO["gateway_id"]]
print(f"Loading tools from gateways: {gateway_ids}")
gateway_tools = load_tools_from_gateways(gateway_ids)

# Initialize the agent with fresh gateway connections per invocation
def create_agent_with_fresh_tools():
    """Create agent with fresh gateway tool connections"""
    # Use embedded gateway ID
    gw_ids = [GATEWAY_INFO["gateway_id"]]
    
    print(f"Creating agent with gateways: {gw_ids}")
    tools = load_tools_from_gateways(gw_ids)
    
    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
        region_name="us-west-2",
    )
    
    return Agent(
        model=bedrock_model,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
    )

# For local development, create agent once
if __name__ == "__main__":
    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
        region_name="us-west-2",
    )
    
    agent = Agent(
        model=bedrock_model,
        system_prompt=SYSTEM_PROMPT,
        tools=gateway_tools,
    )

@app.entrypoint
def invoke(payload):
    """Your AI gateway agent function"""
    user_message = payload.get("prompt", "What would you like me to help you with?")
    
    try:
        # Create fresh agent with active gateway connections for each invocation
        agent = create_agent_with_fresh_tools()
        
        result = agent(user_message)
        return {"result": result.message}
    except Exception as e:
        print(f"Error in invoke: {e}")
        return {"result": f"Error: {str(e)}"}



if __name__ == "__main__":
    if not gateway_ids:
        print("\nExample usage:")
        print("uv run my_agent_us_west_2_gateway.py testgatewayc0acbfb3-d4rcqjevuv")
        print("uv run my_agent_us_west_2_gateway.py gateway1 gateway2")
        print("Add GATEWAY_IDS=gateway1,gateway2 to .env file")
        print("export GATEWAY_IDS='gateway1,gateway2' && uv run my_agent_us_west_2_gateway.py")
    app.run()