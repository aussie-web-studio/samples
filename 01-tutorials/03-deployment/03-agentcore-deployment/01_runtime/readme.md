# Test locally

## Start your agent

uv run my_agent.py

## Test it (in another terminal)

curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'

# Deploy to AWS

## Configure and deploy (auto-creates all required resources)

agentcore configure -e my_agent.py -n my_runtime
agentcore launch

## Test your deployed agent

agentcore invoke '{"prompt": "tell me a joke"}'

## Clean up

delete agentcore runtime
delete ECR
delete Cloudwatch LogGroup