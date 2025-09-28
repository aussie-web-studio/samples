#!/usr/bin/env python3
"""
Get Bearer Token for Gateway

This script retrieves and prints the bearer token for a specific gateway.
"""

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
import sys
import boto3
import json
import os


def main():
    """Get and print bearer token for gateway"""
    
    if len(sys.argv) != 2:
        print("Usage: python get_bearer_token.py <gateway_id>")
        sys.exit(1)
    
    gateway_id = sys.argv[1]
    session = boto3.Session()
    region = session.region_name or "us-west-2"
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, "gateway_info.json")
    
    # Try to load client info from saved file first
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as f:
            data = json.load(f)
            # Handle both old single gateway format and new list format
            gateways = data if isinstance(data, list) else [data]
            
            for gateway_info in gateways:
                if gateway_info.get("gateway_id") == gateway_id:
                    client_info = gateway_info["client_info"]
                    gateway_client = GatewayClient(region_name=region)
                    access_token = gateway_client.get_access_token_for_cognito(client_info)
                    print(access_token)
                    return
    else:
        print(f"JSON file not found at: {json_file_path}")
    
    print(f"Error: No saved client info found for gateway {gateway_id}")
    print("Please run quickstart_gateway.py first to create the gateway and save client info.")
    sys.exit(1)


if __name__ == "__main__":
    main()