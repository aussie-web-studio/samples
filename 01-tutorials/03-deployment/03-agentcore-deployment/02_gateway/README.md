# Gateway Management Scripts

This directory contains Python scripts to manage Amazon Bedrock AgentCore Gateways.

## Prerequisites

- AWS Account with credentials configured (`aws configure`)
- Python 3.10+
- Access to Anthropic's Sonnet 3.7 (or another model)

**Note:** All scripts automatically use the AWS region from your configuration file (`~/.aws/config` or `~/.aws/credentials`). If no region is configured, they default to `us-east-1`.

## Installation

Ensure you have uv installed and the project dependencies are available.

## Usage

### 1. Create Gateway

Create a new gateway with OAuth authorization and Lambda target:

```bash
uv run quickstart_gateway.py
```

This will:
- Create an OAuth authorization server using Cognito
- Create a Gateway with semantic search enabled
- Add a Lambda function target
- Print the Gateway ID (save this for the next steps)

### 2. Get Bearer Token

Retrieve the bearer token for a specific gateway using the Gateway ID from step 1:

```bash
uv run get_bearer_token.py <gateway_id>
```

Example:
```bash
uv run get_bearer_token.py gw-12345abcdef
```

**Note:** Replace `<gateway_id>` with the actual Gateway ID printed by the quickstart script.

### 3. Clean Up Resources

Delete a gateway and all its targets using the same Gateway ID:

```bash
uv run delete_gateway.py <gateway_id>
```

Example:
```bash
uv run delete_gateway.py gw-12345abcdef
```

**Note:** This will permanently delete the gateway and all associated resources.

This will:
- Delete all targets associated with the gateway
- Delete the gateway itself

## Files

- `quickstart_gateway.py` - Creates gateway with OAuth and Lambda target
- `get_bearer_token.py` - Retrieves bearer token for authentication
- `delete_gateway.py` - Cleans up gateway and all targets
- `quickstart.md` - Detailed documentation and examples