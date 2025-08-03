# Import Agent and tools
import logging

from ddgs import DDGS
from ddgs.exceptions import DDGSException, RatelimitException
from strands import Agent, tool
# Load environment variables
from dotenv import load_dotenv
import os
load_dotenv()

# Configure logging
logging.getLogger("strands").setLevel(
    logging.INFO
)  # Set to DEBUG for more detailed logs

# Configure OpenTelemetry for observability
#from opentelemetry.sdk.trace.export import BatchSpanProcessor
#from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
#from strands_to_openinference_mapping import StrandsToOpenInferenceProcessor

from arize.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor


#from opentelemetry import trace
#import grpc


# Define a websearch tool
@tool
def websearch(
    keywords: str, region: str = "us-en", max_results: int | None = None
) -> str:
    """Search the web to get updated information.
    Args:
        keywords (str): The search query keywords.
        region (str): The search region: wt-wt, us-en, uk-en, ru-ru, etc..
        max_results (int | None): The maximum number of results to return.
    Returns:
        List of dictionaries with search results.
    """
    try:
        results = DDGS().text(keywords, region=region, max_results=max_results)
        return results if results else "No results found."
    except RatelimitException:
        return "RatelimitException: Please try again after a short delay."
    except DDGSException as d:
        return f"DuckDuckGoSearchException: {d}"
    except Exception as e:
        return f"Exception: {e}"


# Create a recipe assistant agent

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
    project_name="strands-agent-integration",
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


recipe_agent = Agent(
    system_prompt="""You are RecipeBot, a helpful cooking assistant.
    Help users find recipes based on ingredients and answer cooking questions.
    Use the websearch tool to find recipes when users mention ingredients or to look up cooking information.""",
    tools=[websearch],
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


if __name__ == "__main__":
    print("\n👨‍🍳 RecipeBot: Ask me about recipes or cooking! Type 'exit' to quit.\n")

    # Run the agent in a loop for interactive conversation
    while True:
        user_input = input("\nYou > ")
        if user_input.lower() == "exit":
            print("Happy cooking! 🍽️")
            break
        response = recipe_agent(user_input)
        print(f"\nRecipeBot > {response}")
