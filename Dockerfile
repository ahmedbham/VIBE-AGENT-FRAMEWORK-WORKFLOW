# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Configure Poetry to not create virtual environments (since we're in a container)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy application source code
COPY src/ ./src/
COPY .env.example .env.example

# Set Python path
ENV PYTHONPATH=/app

# Expose port (Azure Container Apps will override this)
EXPOSE 8000

# Run the Website Summarizer Workflow application
# This will be the default command, but can be overridden
CMD ["python", "-m", "joker_agent.run_website_summarizer"]
