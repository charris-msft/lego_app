# Azure Container App Environments

This document lists all Azure Container App Environments available in the subscription for deploying the LEGO Collection Manager application.

## Available Container App Environments

### 1. env-x4f3cwx7gx7zs
- **Location**: West US 2
- **Resource Group**: rg-flask-upload
- **Domain**: purpletree-f5ae3935.westus2.azurecontainerapps.io
- **Static IP**: 4.242.84.153
- **Status**: Succeeded
- **Created**: 2025-03-04 by charris@microsoft.com

### 2. mcp-env
- **Location**: West US 2
- **Resource Group**: azure-mcp-server
- **Domain**: greensky-168796fe.westus2.azurecontainerapps.io
- **Static IP**: 4.149.195.238
- **Status**: Succeeded
- **Tags**: mcpVersion=latest
- **Created**: 2025-08-08 by charris@microsoft.com

### 3. cae-2n62atx27lezw
- **Location**: Canada Central
- **Resource Group**: rg-charris-buggyapp-01
- **Domain**: gentlesmoke-ed02725b.canadacentral.azurecontainerapps.io
- **Static IP**: 130.107.18.55
- **Status**: Succeeded
- **Warning**: Environment has been idle and will be deleted after 6/22/2025 if unused
- **Created**: 2025-03-25 by charris@microsoft.com

### 4. cae-phu-iewnncd4nvaee
- **Location**: East US
- **Resource Group**: rg-photouploader-dev
- **Domain**: wonderfuldesert-514f19a3.eastus.azurecontainerapps.io
- **Static IP**: 135.234.229.65
- **Status**: Succeeded
- **Tags**: Environment=dev, Project=photouploader, azd-env-name=dev
- **Created**: 2025-07-22 by charris@microsoft.com

### 5. cae-js2ut63qvamdg
- **Location**: East US
- **Resource Group**: rg-photo-secure
- **Domain**: gentlegrass-850cd734.eastus.azurecontainerapps.io
- **Static IP**: 51.8.247.55
- **Status**: Succeeded
- **Tags**: azd-env-name=photo-secure
- **Created**: 2025-08-20 by charris@microsoft.com

### 6. caeu2s7w375exuv2
- **Location**: East US 2
- **Resource Group**: rg-azure-mcp-server
- **Domain**: livelysand-82e9a78e.eastus2.azurecontainerapps.io
- **Static IP**: 20.161.171.57
- **Status**: Succeeded
- **Tags**: azd-env-name=azure-mcp-server
- **Created**: 2025-08-08 by charris@microsoft.com

## Summary by Location

- **East US**: 2 environments
- **East US 2**: 1 environment
- **West US 2**: 2 environments
- **Canada Central**: 1 environment

## Deployment Recommendations

For deploying the LEGO Collection Manager application:

1. **Primary Options**: Consider East US or West US 2 regions for best performance
2. **Development**: Use environments tagged with development indicators
3. **Production**: Create a new dedicated environment or use existing production-ready environments

## Notes

- All environments are configured with Dapr and KEDA
- Log Analytics is configured for most environments
- Each environment has a unique default domain for application access
- Zone redundancy is disabled on all current environments

## Next Steps

To deploy the LEGO Collection Manager to one of these environments:

1. Choose the appropriate environment based on your deployment requirements
2. Configure the container registry and application settings
3. Deploy using Azure Container Apps CLI or Azure Portal
4. Update DNS and configure custom domains if needed