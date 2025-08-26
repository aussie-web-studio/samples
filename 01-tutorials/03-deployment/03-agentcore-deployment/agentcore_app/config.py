import os
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv()

class Config:
    REGION = os.getenv("AWS_REGION", "us-east-1")
    RESOURCE_STORE_FILE = os.getenv("RESOURCE_STORE_FILE", "agentcore_resources.json")
    # Add more config variables here, e.g. Gateway name, profile, etc.
    GATEWAY_NAME = os.getenv("GATEWAY_NAME", "TestGateway")
