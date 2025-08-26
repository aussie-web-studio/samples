import os
from dotenv import load_dotenv

from agentcore_app.config import Config
from agentcore_app.gateway import AgentCoreGateway
from agentcore_app.resource_store import ResourceStore
from agentcore_app.agent_runtime import create_agentcore_app

def main():
    load_dotenv()  # Load .env variables here

    model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-7-sonnet-20250219-v1:0")
    region = os.getenv("AWS_REGION", Config.REGION)

    store = ResourceStore()
    gateway_manager = AgentCoreGateway(region=region, resource_store=store)
    resources = gateway_manager.setup_or_load_resources()
    access_token = gateway_manager.get_access_token(resources["cognito"])
    gateway_url = resources["gateway"]["gatewayUrl"]

    print("Starting BedrockAgentCoreApp with configured Gateway...")
    app = create_agentcore_app(
        model_id=model_id,
        region=region,
        gateway_url=gateway_url,
        gateway_access_token=access_token,
    )
    app.run()

if __name__ == "__main__":
    main()
