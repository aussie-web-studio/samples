# Test locally

## Start your agent - Note to update the region in .aws config file

uv run my_agent_ap_southeast_2.py

uv run my_agent_us_west_2.py

## Start your research agent

uv run my_agent_us_west_2_research.py

## Start your gateway agent with specific gateway IDs

# Single gateway (command line)
uv run my_agent_us_west_2_gateway.py testgatewayc0acbfb3-d4rcqjevuv

# Multiple gateways (command line)
uv run my_agent_us_west_2_gateway.py gateway1 gateway2 gateway3

# Using .env file (add GATEWAY_IDS=gateway1,gateway2 to .env)
uv run my_agent_us_west_2_gateway.py

# Using environment variable
export GATEWAY_IDS='gateway1,gateway2' && uv run my_agent_us_west_2_gateway.py

# Show usage (no gateways)
uv run my_agent_us_west_2_gateway.py

## Test it (in another terminal)

curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'

# Deploy to AWS

## Configure and deploy (auto-creates all required resources)

# For regular agents
uv run agentcore configure -e my_agent_us_west_2.py -n my_runtime
uv run agentcore launch

# For research agent
uv run agentcore configure -e my_agent_us_west_2_research.py -n my_research_runtime
uv run agentcore launch

# For gateway agent (gateway info is embedded in the code)

# The gateway credentials are embedded directly in my_agent_us_west_2_gateway.py
# No environment variables needed!

uv run agentcore configure -e my_agent_us_west_2_gateway.py -n my_gateway_runtime_new
uv run agentcore launch

# Troubleshooting deployment issues:
# 1. Delete existing runtime: uv run agentcore delete -n my_gateway_runtime
# 2. Reconfigure: uv run agentcore configure -e my_agent_us_west_2_gateway.py -n my_gateway_runtime_new
# 3. Launch: uv run agentcore launch

## Test your deployed agent

agentcore invoke '{"prompt": "tell me a joke"}'

## Clean up

delete agentcore runtime
delete ECR
delete Cloudwatch LogGroup