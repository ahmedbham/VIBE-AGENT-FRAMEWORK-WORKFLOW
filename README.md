# Joker Agent (Microsoft Agent Framework + Azure OpenAI Foundry)

Python agent named **Joker** with system instructions: "you are good at telling jokes". It uses Azure OpenAI deployed in a Microsoft Foundry project and authenticates via Azure CLI login (AzureCliCredential).

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

## Notes
- If the `microsoft-agentframework` package name/version differs, update `pyproject.toml` accordingly.
- Set `AZURE_TENANT_ID`/`AZURE_SUBSCRIPTION_ID` env vars if your CLI default context doesn’t match the target subscription.
