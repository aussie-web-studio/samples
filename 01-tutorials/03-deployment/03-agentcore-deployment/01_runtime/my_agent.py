from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models.bedrock import BedrockModel
import os
from dotenv import load_dotenv


# Construct the path to the .env file in the parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

# Load the environment variables from the specified path
load_dotenv(dotenv_path=env_path)

# Get the model and region from environment variables or set defaults
model = os.getenv("model", "anthropic.claude-3-5-sonnet-20241022-v2:0")
region = os.getenv("region", "ap-southeast-2")


app = BedrockAgentCoreApp()

bedrock_model = BedrockModel(model_id=model, temperature=0.4, region=region)
agent = Agent(
    system_prompt="""You are a helpful AI assistant. Please answer the user's questions to the best of your ability.""",
    model=bedrock_model
)

#agent = Agent()

@app.entrypoint
def invoke(payload):
    """Your AI agent function"""
    user_message = payload.get("prompt", "Hello! How can I help you today?")
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()