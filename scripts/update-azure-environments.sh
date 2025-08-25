#!/bin/bash
# Script to populate azure.md with actual Container App environment data
# Run this after logging in with 'az login'

echo "🔍 Checking Azure CLI authentication..."

# Check if user is logged in
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

echo "✅ Azure CLI authenticated"
echo "📋 Current subscription: $(az account show --query name -o tsv)"
echo ""

echo "🔍 Fetching Container App environments..."

# Get container app environments
ENVS=$(az containerapp env list --query "[].{Name:name, Location:location, ResourceGroup:resourceGroup}" -o tsv)

if [ -z "$ENVS" ]; then
    echo "⚠️  No Container App environments found in this subscription."
    echo "   You may need to create one first or check if you're using the right subscription."
    exit 0
fi

# Create backup of existing azure.md
if [ -f "azure.md" ]; then
    cp azure.md azure.md.backup
    echo "📄 Backed up existing azure.md to azure.md.backup"
fi

# Generate updated azure.md
cat > azure.md << 'EOF'
# Azure Container App Environments

This document lists all Azure Container App environments in your subscription and their locations, to help with deployment planning for the LEGO Collection Manager app.

*Last updated: $(date)*
*Subscription: $(az account show --query name -o tsv)*

## Container App Environments

| Environment Name | Location/Region | Resource Group |
|------------------|-----------------|----------------|
EOF

# Add environment data
echo "$ENVS" | while IFS=$'\t' read -r name location rg; do
    echo "| $name | $location | $rg |" >> azure.md
done

# Add the rest of the content
cat >> azure.md << 'EOF'

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

1. Choose an appropriate environment based on location and requirements
2. Prepare your containerized application for deployment
3. Configure environment variables and secrets for the Container App
4. Deploy the LEGO Collection Manager to Azure Container Apps
EOF

echo "✅ Updated azure.md with your Container App environments"
echo "📊 Found $(echo "$ENVS" | wc -l) environment(s)"
echo ""
echo "🎯 Next: Review azure.md and choose an environment for deployment"