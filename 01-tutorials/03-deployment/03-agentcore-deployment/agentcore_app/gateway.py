from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
import logging
from agentcore_app.config import Config

class AgentCoreGateway:
    def __init__(self, region, resource_store):
        self.client = GatewayClient(region_name=region)
        self.client.logger.setLevel(logging.INFO)
        self.store = resource_store

    def setup_or_load_resources(self):
        resources = self.store.load()
        changed = False

        if "cognito" not in resources:
            print("Creating Cognito authorizer...")
            cognito = self.client.create_oauth_authorizer_with_cognito(Config.GATEWAY_NAME)
            resources["cognito"] = cognito
            changed = True
        else:
            cognito = resources["cognito"]

        if "gateway" not in resources:
            print("Creating MCP Gateway...")
            gateway = self.client.create_mcp_gateway(authorizer_config=cognito["authorizer_config"], name=Config.GATEWAY_NAME)
            resources["gateway"] = gateway
            changed = True
        else:
            gateway = resources["gateway"]

        if "lambda_target" not in resources:
            print("Creating Lambda Target...")
            target = self.client.create_mcp_gateway_target(gateway=gateway, target_type="lambda")
            resources["lambda_target"] = target
            changed = True

        if changed:
            self.store.save(resources)
        return resources

    def get_access_token(self, cognito):
        return self.client.get_access_token_for_cognito(cognito["client_info"])
