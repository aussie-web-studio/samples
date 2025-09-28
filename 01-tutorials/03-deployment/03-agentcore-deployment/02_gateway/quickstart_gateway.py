#!/usr/bin/env python3
"""
QuickStart: A Fully Managed MCP Server in 5 Minutes! 🚀

Amazon Bedrock AgentCore Gateway provides an easy and secure way for developers 
to build, deploy, discover, and connect to tools at scale.
"""

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
import json
import logging
import boto3


def main():
    """Main function to set up and test the Gateway"""
    
    # Setup
    session = boto3.Session()
    region = session.region_name or "us-west-2"
    client = GatewayClient(region_name=region)
    client.logger.setLevel(logging.DEBUG)
    
    print("🚀 Starting Gateway QuickStart...")
    
    # Step 1: Creating an OAuth Authorization Server
    print("🔒 Creating OAuth authorization server...")
    cognito_response = client.create_oauth_authorizer_with_cognito("MyGateway")
    print("✅ OAuth authorization server created")
    
    # Step 2: Creating a Gateway
    print("🌉 Creating Gateway...")
    gateway = client.create_mcp_gateway(
        name="My-Gateway",  # Auto-generated name
        role_arn=None,  # Auto-created role
        authorizer_config=cognito_response["authorizer_config"],
        enable_semantic_search=True,
    )
    print("✅ Gateway created successfully")
    
    # Step 3: Adding Lambda Targets
    print("🛠️ Adding Lambda function target...")
    lambda_target = client.create_mcp_gateway_target(
        gateway=gateway,
        name=None,  # Auto-generated name
        target_type="lambda",
        target_payload=None,  # Auto-created Lambda
        credentials=None,
    )
    print("✅ Lambda target added successfully")
    
    # Step 4: Getting Access Token
    print("🔐 Obtaining OAuth access token...")
    access_token = client.get_access_token_for_cognito(cognito_response["client_info"])
    print("✅ Access token obtained")
    
    # Save gateway info for token retrieval
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, "gateway_info.json")
    
    gateway_id = gateway.get('gatewayId') or gateway.get('id')
    
    new_gateway_info = {
        "gateway_id": gateway_id,
        "client_info": cognito_response["client_info"]
    }
    
    # Load existing gateways or create new list
    gateways = []
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as f:
            data = json.load(f)
            # Handle both old single gateway format and new list format
            if isinstance(data, list):
                gateways = data
            else:
                gateways = [data]  # Convert old format to list
    
    # Add new gateway
    gateways.append(new_gateway_info)
    
    with open(json_file_path, "w") as f:
        json.dump(gateways, f, indent=2)
    
    print("\n🎉 Gateway setup complete!")
    print(f"Gateway ID: {gateway_id}")
    print(f"Gateway Name: {gateway.get('name', 'N/A')}")
    print("Gateway info saved to gateway_info.json")
    print("You can now use this Gateway with your Strands agents!")


if __name__ == "__main__":
    main()