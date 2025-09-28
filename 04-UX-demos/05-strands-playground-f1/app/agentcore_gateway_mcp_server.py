from strands import Agent, tool
from strands.tools.mcp import MCPClient
from strands.models import BedrockModel
import os
import json


# Import environment variables for MCP model
mcp_model = os.getenv("mcp_model", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
mcp_region = os.getenv("mcp_region", "us-west-2")

def create_streamable_http_transport(mcp_url: str, access_token: str):
    from mcp.client.streamable_http import streamablehttp_client
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

def _gateway_tool_function(query: str, gateway_id: str) -> str:
    """Internal function to connect to a specific gateway."""
    bedrock_model = BedrockModel(model_id=mcp_model, region_name=mcp_region)
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(script_dir, "gateway_info.json")
        
        if not os.path.exists(json_file_path):
            return "Error: No gateway configuration found. Please run quickstart_gateway.py first."
            
        with open(json_file_path, "r") as f:
            data = json.load(f)
            gateways = data if isinstance(data, list) else [data]
            
        gateway_info = None
        for gw in gateways:
            if gw.get("gateway_id") == gateway_id:
                gateway_info = gw
                break
                
        if not gateway_info:
            return f"Error: Gateway {gateway_id} not found in configuration."
            
        from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
        import boto3
        
        gateway_client = GatewayClient(region_name=mcp_region)
        access_token = gateway_client.get_access_token_for_cognito(gateway_info["client_info"])
        
        boto_client = boto3.client("bedrock-agentcore-control", region_name=mcp_region)
        gateway_details = boto_client.get_gateway(gatewayIdentifier=gateway_info['gateway_id'])
        gateway_url = gateway_details['gatewayUrl']
        
        mcp_client = MCPClient(lambda: create_streamable_http_transport(gateway_url, access_token))

        with mcp_client:
            tools = get_full_tools_list(mcp_client)
            
            if not tools:
                return "No tools available from the gateway."

            gateway_agent = Agent(
                model=bedrock_model,
                system_prompt=f"""
                You are an AI assistant with access to tools from Amazon Bedrock AgentCore Gateway {gateway_id}.
                Available tools: {[tool.tool_name for tool in tools]}
                
                Use these tools to help answer the user's query effectively.
                """,
                tools=tools,
            )
            
            return str(gateway_agent(query))

    except Exception as e:
        return f"Error connecting to AgentCore Gateway {gateway_id}: {str(e)}"

def get_available_gateways():
    """Get list of available gateways and create tools for each."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, "gateway_info.json")
    
    gateway_tools = {}
    
    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, "r") as f:
                data = json.load(f)
                gateways = data if isinstance(data, list) else [data]
                
            for gateway_info in gateways:
                gateway_id = gateway_info.get("gateway_id")
                if gateway_id:
                    # Create a proper function for this specific gateway
                    def create_gateway_func(gw_id):
                        def gateway_func(query: str) -> str:
                            return _gateway_tool_function(query, gw_id)
                        gateway_func.__name__ = f"gateway_{gw_id.replace('-', '_')}"
                        gateway_func.__doc__ = f"Connect to AgentCore Gateway {gw_id} and execute queries using its tools."
                        return gateway_func
                    
                    tool_func = create_gateway_func(gateway_id)
                    gateway_tools[f"gateway_{gateway_id.replace('-', '_')}"] = tool(tool_func)
                    
        except Exception as e:
            print(f"Error loading gateway info: {e}")
    
    return gateway_tools

def get_gateway_available_tools(gateway_id: str) -> list:
    """Get list of available tools for a specific gateway."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(script_dir, "gateway_info.json")
        
        if not os.path.exists(json_file_path):
            return []
            
        with open(json_file_path, "r") as f:
            data = json.load(f)
            gateways = data if isinstance(data, list) else [data]
            
        gateway_info = None
        for gw in gateways:
            if gw.get("gateway_id") == gateway_id:
                gateway_info = gw
                break
                
        if not gateway_info:
            return []
            
        from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
        import boto3
        
        gateway_client = GatewayClient(region_name=mcp_region)
        access_token = gateway_client.get_access_token_for_cognito(gateway_info["client_info"])
        
        boto_client = boto3.client("bedrock-agentcore-control", region_name=mcp_region)
        gateway_details = boto_client.get_gateway(gatewayIdentifier=gateway_info['gateway_id'])
        gateway_url = gateway_details['gatewayUrl']
        
        mcp_client = MCPClient(lambda: create_streamable_http_transport(gateway_url, access_token))

        with mcp_client:
            tools = get_full_tools_list(mcp_client)
            return [tool.tool_name for tool in tools]
            
    except Exception:
        return []

# Create tools for all available gateways
gateway_tools = get_available_gateways()

@tool
def agentcore_gateway_mcp_server(query: str, gateway_id: str = None) -> str:
    """
    Connect to Amazon Bedrock AgentCore Gateway and execute queries using available tools.
    
    Args:
        query: The user's question or task
        gateway_id: Optional gateway ID to use (if not provided, will use first available gateway)
    
    Returns:
        A helpful response from the gateway tools
    """
    if gateway_id:
        return _gateway_tool_function(query, gateway_id)
    
    # Use first available gateway if no specific ID provided
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, "gateway_info.json")
    
    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, "r") as f:
                data = json.load(f)
                gateways = data if isinstance(data, list) else [data]
            
            if gateways:
                first_gateway_id = gateways[0].get("gateway_id")
                if first_gateway_id:
                    return _gateway_tool_function(query, first_gateway_id)
        except Exception as e:
            return f"Error loading gateway configuration: {str(e)}"
    
    return "Error: No gateway configuration found. Please run quickstart_gateway.py first to create a gateway."


if __name__ == "__main__":
    # Test with first available gateway
    gateways = get_available_gateways()
    if gateways:
        first_gateway = list(gateways.keys())[0]
        gateway_id = first_gateway.replace('gateway_', '').replace('_', '-')
        print(f"Testing gateway: {first_gateway}")
        print(f"Available tools: {get_gateway_available_tools(gateway_id)}")
        result = list(gateways.values())[0]("What tools are available?")
        print(result)
    else:
        print("No gateways found. Please run quickstart_gateway.py first.")