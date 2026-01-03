# VIBE Agent Framework Workflow

This repository contains example agents built with Microsoft Agent Framework and Azure OpenAI Foundry, demonstrating various capabilities including basic chat and function calling.

## Agents

### 1. Joker Agent
Python agent named **Joker** with system instructions: "you are good at telling jokes". It uses Azure OpenAI deployed in a Microsoft Foundry project and authenticates via Azure CLI login (AzureCliCredential).

### 2. Weather Agent (Function Calling)
Python agent that demonstrates **function calling** capabilities using the `AzureOpenAIChatClient`. It includes a `get-weather` function tool that can be invoked by the agent to provide weather information for any location.

### 3. Website Summarizer Workflow (Multi-Agent)
A **multi-agent workflow** that demonstrates agent orchestration and chaining. This workflow consists of two specialized agents:
- **Get Content Agent**: Fetches and extracts text content from a website URL using web scraping tools
- **Summarize Content Agent**: Processes the content and generates a concise bulleted list summary

The workflow takes a website URL as input, retrieves its content with the first agent, and passes it to the second agent for summarization.

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

## Run the Website Summarizer Workflow (Multi-Agent Demo)
```bash
poetry run python -m joker_agent.run_website_summarizer
```
This demonstrates a multi-agent workflow where:
1. The **Get Content Agent** fetches website content from a URL
2. The **Summarize Content Agent** creates a concise bulleted summary
3. The workflow orchestrator chains both agents together seamlessly

## Documentation

### Quick Start
- **[QUICKSTART.md](QUICKSTART.md)** - Get started quickly with examples and common patterns

### Comprehensive Guides
- **[WEATHER_AGENT_PLAN.md](WEATHER_AGENT_PLAN.md)** - Detailed plan for implementing agents with function calling
- **[WEBSITE_SUMMARIZER_PLAN.md](WEBSITE_SUMMARIZER_PLAN.md)** - Detailed plan for implementing multi-agent workflows
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Summary of the implementation and architecture
- **[examples/README.md](examples/README.md)** - Example scripts and usage patterns

## Notes
- If the `microsoft-agentframework` package name/version differs, update `pyproject.toml` accordingly.
- Set `AZURE_TENANT_ID`/`AZURE_SUBSCRIPTION_ID` env vars if your CLI default context doesn’t match the target subscription.
