# Strands Playground F1 App

## Run the app
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8003
```

## Test individual MCP modules

### AWS Data Processing MCP Server
```bash
uv run aws_data_processing_mcp_server.py
```

### AgentCore Gateway MCP Server
```bash
# First create a gateway (run from gateway directory)
uv run ../01-tutorials/03-deployment/03-agentcore-deployment/02_gateway/quickstart_gateway.py

copy the gateway_info.json to the app folder.

# Then test the module
uv run agentcore_gateway_mcp_server.py
```

## References
- [AWS MCP Server Documentation](https://awslabs.github.io/mcp/servers/aws-dataprocessing-mcp-server)
- [AgentCore Gateway Documentation](../01-tutorials/03-deployment/03-agentcore-deployment/02_gateway/README.md)
