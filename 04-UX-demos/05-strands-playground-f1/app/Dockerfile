FROM public.ecr.aws/docker/library/python:3.12-slim

WORKDIR /app

# # Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY main.py .
COPY static/ static/
COPY aws_documentation_researcher.py .
COPY aws_diagram_drawer.py .
COPY aws_knowledge_mcp_server.py .
COPY aws_data_processing_mcp_server.py .
COPY agentcore_gateway_mcp_server.py .

# Expose the port the app runs on
EXPOSE 8003

# Running as non-root 
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]