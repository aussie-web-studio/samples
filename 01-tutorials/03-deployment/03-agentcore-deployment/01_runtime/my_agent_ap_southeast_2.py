from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models.bedrock import BedrockModel


app = BedrockAgentCoreApp()
bedrock_model = BedrockModel(model_id="anthropic.claude-3-5-sonnet-20241022-v2:0", temperature=0.4, region="ap-southeast-2")
agent = Agent(system_prompt="""You are a helpful AI assistant. Please answer the user's questions to the best of your ability.""",
    model=bedrock_model)

@app.entrypoint
def invoke(payload):
    """Your AI agent function"""
    user_message = payload.get("prompt", "Hello! How can I help you today?")
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()