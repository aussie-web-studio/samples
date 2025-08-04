from strands import Agent, tool
from strands.multiagent import Swarm

# Load environment variables
from dotenv import load_dotenv
import os
load_dotenv()

# Integrating Arize for observability
from arize.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor

# Using OpenAI model
from strands.models.openai import OpenAIModel

# Rertieve OpenAI API key from environment variables

openai_api_key = os.getenv("OpenAI_API_KEY")
SPACE_ID = os.environ["ARIZE_SPACE_ID"]
API_KEY = os.environ["ARIZE_API_KEY"]
ENDPOINT = "otlp.arize.com:443"

tracer_provider = register(
    space_id=SPACE_ID,
    api_key=API_KEY,
    project_name="swarm-agent",
)

OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

model = OpenAIModel(
    client_args={
        "api_key": openai_api_key,
    },
    # **model_config
    model_id="gpt-4o",
    params={
        "max_tokens": 1000,
        "temperature": 0.7,
    }
)

# Create specialized agents with different expertise
research_agent = Agent(
    system_prompt=("""You are a Research Agent specializing in gathering and analyzing information.
    Your role in the swarm is to provide factual information and research insights on the topic.
    You should focus on providing accurate data and identifying key aspects of the problem.
    When receiving input from other agents, evaluate if their information aligns with your research.
    """), 
    name="research_agent",
    model=model,
    trace_attributes={
        "session.id": "abc-1234",
        "user.id": "andypham",
        "arize.tags": [
            "Agent-SDK",
            "Arize-Project",
            "OpenInference-Integration",
        ]
    }
    )

creative_agent = Agent(
    system_prompt=("""You are a Creative Agent specializing in generating innovative solutions.
    Your role in the swarm is to think outside the box and propose creative approaches.
    You should build upon information from other agents while adding your unique creative perspective.
    Focus on novel approaches that others might not have considered.
    """), 
    name="creative_agent",
    model=model,
    trace_attributes={
        "session.id": "abc-1234",
        "user.id": "andypham",
        "arize.tags": [
            "Agent-SDK",
            "Arize-Project",
            "OpenInference-Integration",
        ]
    }
    )

critical_agent = Agent(
    system_prompt=("""You are a Critical Agent specializing in analyzing proposals and finding flaws.
    Your role in the swarm is to evaluate solutions proposed by other agents and identify potential issues.
    You should carefully examine proposed solutions, find weaknesses or oversights, and suggest improvements.
    Be constructive in your criticism while ensuring the final solution is robust.
    """), 
    name="critical_agent",
    model=model,
    trace_attributes={
        "session.id": "abc-1234",
        "user.id": "andypham",
        "arize.tags": [
            "Agent-SDK",
            "Arize-Project",
            "OpenInference-Integration",
        ]
    }    
    )

summarizer_agent = Agent(
    system_prompt=("""You are a Summarizer Agent specializing in synthesizing information.
    Your role in the swarm is to gather insights from all agents and create a cohesive final solution.
    You should combine the best ideas and address the criticisms to create a comprehensive response.
    Focus on creating a clear, actionable summary that addresses the original query effectively.
    """),
    name="summarizer_agent",
    model=model,
    trace_attributes={
        "session.id": "abc-1234",
        "user.id": "andypham",
        "arize.tags": [
            "Agent-SDK",
            "Arize-Project",
            "OpenInference-Integration",
        ]
    }    
    )
# Create a swarm with these agents
swarm = Swarm(
    [research_agent, creative_agent, critical_agent, summarizer_agent],
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=900.0,  # 15 minutes
    node_timeout=300.0,       # 5 minutes per agent
    repetitive_handoff_detection_window=8,  # There must be >= 3 unique agents in the last 8 handoffs
    repetitive_handoff_min_unique_agents=3
)

if __name__ == "__main__":
    print("\n👨‍🍳 RecipeBot: Give me a complex task and I will provide you the great answer! Type 'exit' to quit.\n")

    # Run the agent in a loop for interactive conversation
    while True:
        user_input = input("\nYou > ")
        if user_input.lower() == "exit":
            print("Happy researching! 🍽️")
            break
        
        result = swarm(user_input)

        # Access the final result
        print(f"Status: {result.status}")
