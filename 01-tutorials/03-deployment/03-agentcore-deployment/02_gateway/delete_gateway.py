#!/usr/bin/env python3
"""
Delete Gateway

This script deletes a specific gateway.
"""

import boto3
import sys
import json
import os


def main():
    """Delete gateway by ID"""
    
    if len(sys.argv) != 2:
        print("Usage: python delete_gateway.py <gateway_id>")
        sys.exit(1)
    
    gateway_id = sys.argv[1]
    session = boto3.Session()
    region = session.region_name or "us-east-1"
    
    boto_client = boto3.client("bedrock-agentcore-control", region_name=region)
    
    # List and delete all targets first
    try:
        gateway_targets = boto_client.list_gateway_targets(gatewayIdentifier=gateway_id)
        targets = gateway_targets.get('items', [])
        
        if targets:
            print(f"Found {len(targets)} targets to delete...")
            for target in targets:
                target_id = target['targetId']
                print(f"Deleting target: {target_id}")
                boto_client.delete_gateway_target(
                    gatewayIdentifier=gateway_id,
                    targetId=target_id
                )
                print(f"Target {target_id} deleted")
        else:
            print("No targets found")
    except Exception as e:
        print(f"Error deleting targets: {e}")
        sys.exit(1)
    
    # Delete the gateway
    try:
        boto_client.delete_gateway(gatewayIdentifier=gateway_id)
        print(f"Gateway {gateway_id} deleted successfully")
    except Exception as e:
        print(f"Error deleting gateway: {e}")
        sys.exit(1)
    
    # Delete Cognito user pool if gateway info exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, "gateway_info.json")
    
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as f:
            data = json.load(f)
            # Handle both old single gateway format and new list format
            gateways = data if isinstance(data, list) else [data]
            
        # Find and remove the specific gateway
        gateway_to_delete = None
        remaining_gateways = []
        
        for gateway_info in gateways:
            if gateway_info.get("gateway_id") == gateway_id:
                gateway_to_delete = gateway_info
            else:
                remaining_gateways.append(gateway_info)
        
        if gateway_to_delete:
            user_pool_id = gateway_to_delete["client_info"]["user_pool_id"]
            domain_prefix = gateway_to_delete["client_info"]["domain_prefix"]
            
            cognito_client = boto3.client("cognito-idp", region_name=region)
            
            try:
                # Delete user pool domain first
                cognito_client.delete_user_pool_domain(
                    Domain=domain_prefix,
                    UserPoolId=user_pool_id
                )
                print(f"Cognito domain {domain_prefix} deleted")
                
                # Delete user pool after domain is deleted
                cognito_client.delete_user_pool(UserPoolId=user_pool_id)
                print(f"Cognito user pool {user_pool_id} deleted")
            except Exception as e:
                print(f"Error deleting Cognito resources: {e}")
            
            # Update the JSON file with remaining gateways
            with open(json_file_path, "w") as f:
                json.dump(remaining_gateways, f, indent=2)
            print(f"Gateway {gateway_id} removed from gateway info file")


if __name__ == "__main__":
    main()