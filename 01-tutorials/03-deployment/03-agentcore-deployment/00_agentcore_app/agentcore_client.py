import boto3
import json
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class AgentCoreRuntime:
    arn: str
    name: str
    status: str

class AgentCoreClient:
    def __init__(self, region: str = 'us-west-1'):
        self.session = boto3.Session()
        self.client = self.session.client('bedrock-agentcore', region_name=region)
        self.control_client = self.session.client('bedrock-agentcore-control', region_name=region)
        self.region = region

    def list_runtimes(self) -> List[AgentCoreRuntime]:
        """List all available AgentCore runtimes in the region"""
        try:
            paginator = self.control_client.get_paginator('list_agent_runtimes')
            pages = paginator.paginate()
            
            runtimes = []
            for page in pages:
                for runtime in page.get('agentRuntimes', []):
                    arn = runtime.get('agentRuntimeArn')
                    name = arn.split('/')[-1] if arn and '/' in arn else 'Unknown Runtime'
                    status = runtime.get('status', 'UNKNOWN')
                    
                    runtimes.append(AgentCoreRuntime(
                        arn=arn,
                        name=name,
                        status=status
                    ))
            return runtimes
        except Exception as e:
            print(f"Error retrieving agent runtimes: {e}")
            return []
    
    def connect_to_runtime(self, runtime_arn: str) -> tuple[AgentCoreRuntime, str]:
        """Connect to a specific runtime and validate it"""
        try:
            runtime_name = runtime_arn.split('/')[-1] if '/' in runtime_arn else 'AgentCore Runtime'
            
            print(f"DEBUG: Attempting to connect to {runtime_arn} in region {self.region}")
            
            # Test the runtime and get session ID
            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=runtime_arn,
                payload=json.dumps({"prompt": "test"}).encode('utf-8')
            )
            
            print(f"DEBUG: Connection successful, response: {response}")
            
            # Extract session ID from response
            session_id = response.get('runtimeSessionId', 'Unknown')
            
            runtime = AgentCoreRuntime(
                arn=runtime_arn,
                name=runtime_name,
                status="ACTIVE"
            )
            
            return runtime, session_id
        except Exception as e:
            print(f"DEBUG: Connection failed with error: {str(e)}")
            runtime_name = runtime_arn.split('/')[-1] if '/' in runtime_arn else 'AgentCore Runtime'
            
            # Check if it's a runtime error vs connection error
            if "RuntimeClientError" in str(e) and "500" in str(e):
                status = "ERROR"
            elif "ResourceNotFoundException" in str(e):
                status = "NOT_FOUND"
            else:
                status = "INACTIVE"
            
            runtime = AgentCoreRuntime(
                arn=runtime_arn,
                name=runtime_name,
                status=status
            )
            return runtime, None

    def validate_runtime(self, runtime_arn: str) -> bool:
        """Validate runtime status"""
        try:
            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=runtime_arn,
                payload=json.dumps({"prompt": "test"}).encode('utf-8')
            )
            return True
        except Exception as e:
            if "ResourceNotFoundException" in str(e) or "No endpoint" in str(e):
                return False
            return False

    def send_message(self, runtime_arn: str, message: str) -> str:
        """Send message to AgentCore runtime"""
        try:
            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=runtime_arn,
                payload=json.dumps({"prompt": message}).encode('utf-8')
            )
            
            response_body = response['response'].read().decode('utf-8')
            try:
                response_data = json.loads(response_body)
                # Extract text from the response
                if 'result' in response_data and 'content' in response_data['result']:
                    content = response_data['result']['content']
                    if isinstance(content, list) and len(content) > 0 and 'text' in content[0]:
                        return content[0]['text']
            except:
                pass
            
            return response_body
        except Exception as e:
            raise Exception(f"Failed to send message: {str(e)}")