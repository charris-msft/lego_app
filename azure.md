# Azure Container App Environments

This document lists all Azure Container App environments in your subscription and their locations, to help with deployment planning for the LEGO Collection Manager app.

## How to populate this document

**Option 1: Use the helper script (Recommended)**
1. Ensure you're logged into Azure CLI: `az login`
2. Run the helper script to automatically update this file:
```bash
chmod +x scripts/update-azure-environments.sh
./scripts/update-azure-environments.sh
```

**Option 2: Manual CLI command**
To get the actual list of your Container App environments manually, run the following Azure CLI command after ensuring you're logged in (`az login`):

```bash
az containerapp env list --query "[].{Name:name, Location:location, ResourceGroup:resourceGroup}" -o table
```

## Container App Environments

> **Note:** This section will be populated with your actual environments. Run the command above to get the current list.

| Environment Name | Location/Region | Resource Group |
|------------------|-----------------|----------------|
| (Run the command above to populate this table) | | |

## Additional Information

### Commands for more detailed information:

1. **List all environments with full details:**
```bash
az containerapp env list -o table
```

2. **Get details for a specific environment:**
```bash
az containerapp env show --name <environment-name> --resource-group <resource-group-name>
```

3. **Check available locations for Container Apps:**
```bash
az provider show --namespace Microsoft.App --query "resourceTypes[?resourceType=='managedEnvironments'].locations" -o table
```

## Deployment Preparation

Once you have identified the Container App environments, you can proceed with deploying the LEGO Collection Manager application. Consider the following:

- **Location**: Choose an environment in the same region as your PostgreSQL database (`lego-postgres-server.postgres.database.azure.com`) for optimal performance
- **Resource Group**: Ensure the environment is in a resource group where you have appropriate permissions
- **Network Configuration**: Verify the environment's network setup aligns with your application requirements

## Next Steps

1. Run the command above to populate the environments list
2. Choose an appropriate environment based on location and requirements
3. Prepare your containerized application for deployment
4. Configure environment variables and secrets for the Container App