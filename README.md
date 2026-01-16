# VIBE Agent Framework Workflow

This repository contains example agents built with Microsoft Agent Framework and Azure OpenAI Foundry, demonstrating various capabilities including basic chat and function calling.

## Agents

### 1. Joker Agent
Python agent named **Joker** with system instructions: "you are good at telling jokes". It uses Azure OpenAI deployed in a Microsoft Foundry project and authenticates via Azure CLI login (AzureCliCredential).

### 2. Weather Agent (Function Calling)
Python agent that demonstrates **function calling** capabilities using the `AzureOpenAIChatClient`. It includes a `get-weather` function tool that can be invoked by the agent to provide weather information for any location.

### 3. Website Summarizer Workflow (Multi-Agent with WorkflowBuilder)
A **multi-agent workflow** built with Microsoft Agent Framework's **WorkflowBuilder** that demonstrates advanced agent orchestration. This workflow uses the Executor pattern with two specialized executors:
- **Get Content Executor**: Fetches and extracts text content from a website URL using web scraping tools
- **Summarize Content Executor**: Processes the content and generates a concise bulleted list summary

The workflow uses `WorkflowBuilder` to register executors, define edges, and orchestrate the sequential execution. Data flows from one executor to the next via `WorkflowContext`.

## Prerequisites
- Python >= 3.1.10
- Poetry
- Azure CLI (`az`) logged in with access to your subscription
- Azure ML/Foundry extension (if needed): `az extension add --name ml`

## Azure provisioning (CLI)
```bash
# 1) Resource group
az group create -n vibe-rg -l centralus

# 2) Foundry project (AI Foundry)
az ml workspace create \
  --name my-vibe-foundry \
  --resource-group vibe-rg \
  --location centralus \
  --kind project

# 3) Deploy base model gpt-4.1-mini
az ml foundry model deploy \
  --project-name my-vibe-foundry \
  --name gpt-4.1-mini \
  --base-model gpt-4.1-mini \
  --resource-group vibe-rg
```
> Capture the resulting endpoint URL, deployment name (here `gpt-4.1-mini`), and API version if returned.

## Configuration
Create a `.env` file in the project root:
```
FOUNDRY_ENDPOINT=https://<your-foundry-endpoint>
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2024-10-21
```
Authentication uses `AzureCliCredential`, so ensure `az login` has an active context.

## Install
```bash
poetry install
```

## Run the Joker agent
```bash
poetry run python -m joker_agent.run
```
The runner sends: "Tell me a joke about a pirate".

## Run the Weather agent (Function Calling Demo)
```bash
poetry run python -m joker_agent.run_weather_agent
```
This demonstrates function calling with the `get-weather` tool that returns: "The weather in {location} is cloudy with a high of 15°C."

## Run the Website Summarizer Workflow (Multi-Agent with WorkflowBuilder)
```bash
poetry run python -m joker_agent.run_website_summarizer
```
This demonstrates a multi-agent workflow built with **WorkflowBuilder** where:
1. The **Get Content Executor** fetches website content from a URL
2. The **Summarize Content Executor** creates a concise bulleted summary
3. The `WorkflowBuilder` orchestrates the executors with edges and manages data flow via `WorkflowContext`

## Deployment to Azure Container Apps

The Website Summarizer Workflow can be deployed to Azure Container Apps using two approaches:

### 1. GitHub Actions (Automated CI/CD)
Push to the main branch or manually trigger the deployment workflow. The application will be automatically built, containerized, and deployed to Azure.

```bash
# Deployment happens automatically on git push to main
git push origin main

# Or trigger manually via GitHub Actions UI
```

### 2. Azure Developer CLI (azd)
Use azd for command-line deployment with simple commands:

```bash
# First-time setup
azd auth login
azd init

# Set required environment variables
azd env set FOUNDRY_ENDPOINT "https://your-foundry.services.ai.azure.com"
azd env set AZURE_OPENAI_DEPLOYMENT "gpt-4.1-mini"
azd env set AZURE_OPENAI_API_VERSION "2024-10-21"

# Optional: Set Foundry Resource ID for automatic role assignment
# Get your Foundry resource ID first:
# az ml workspace show --name <your-foundry-name> --resource-group <foundry-rg> --query id -o tsv
azd env set FOUNDRY_RESOURCE_ID "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.MachineLearningServices/workspaces/<name>"

# Deploy everything (infrastructure + application)
azd up
```

**Important**: After deployment, the container app's managed identity needs permission to access your Foundry project. This can be configured:
- **Automatically**: Set `FOUNDRY_RESOURCE_ID` before deployment (shown above)
- **Manually**: Follow the steps in [MANUAL_CONFIGURATION_STEPS.md](MANUAL_CONFIGURATION_STEPS.md)

For detailed deployment instructions, see the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

## Documentation

### Quick Start
- **[QUICKSTART.md](QUICKSTART.md)** - Get started quickly with examples and common patterns

### Comprehensive Guides
- **[WEATHER_AGENT_PLAN.md](WEATHER_AGENT_PLAN.md)** - Detailed plan for implementing agents with function calling
- **[WEBSITE_SUMMARIZER_PLAN.md](WEBSITE_SUMMARIZER_PLAN.md)** - Detailed plan for implementing multi-agent workflows
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Summary of the implementation and architecture
- **[examples/README.md](examples/README.md)** - Example scripts and usage patterns

### Deployment to Azure
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete guide for deploying to Azure Container Apps
- **[ACA_DEPLOYMENT_QUICKREF.md](ACA_DEPLOYMENT_QUICKREF.md)** - Quick reference for Azure Container Apps deployment
- **[ACA_DEPLOYMENT_IMPLEMENTATION.md](ACA_DEPLOYMENT_IMPLEMENTATION.md)** - Implementation summary and technical details

## Notes
- If the `microsoft-agentframework` package name/version differs, update `pyproject.toml` accordingly.
- Set `AZURE_TENANT_ID`/`AZURE_SUBSCRIPTION_ID` env vars if your CLI default context doesn’t match the target subscription.
