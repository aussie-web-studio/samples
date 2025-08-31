# Test locally

## Start your agent - Note to update the region and model in .aws config file and env

uv run my_agent_ap_southeast_2.py

uv run my_agent_us_west_2.py

## Test it (in another terminal)

curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'

# Deploy to AWS

## Configure and deploy (auto-creates all required resources)

uv run agentcore configure -e my_agent.py -n my_runtime
uv run agentcore launch

## Test your deployed agent

agentcore invoke '{"prompt": "tell me a joke"}'

## Clean up

delete agentcore runtime
delete ECR
delete Cloudwatch LogGroup