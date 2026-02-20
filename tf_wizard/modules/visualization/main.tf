# Visualization Module - Architecture Diagrams and Documentation

# Local file for architecture diagram (Mermaid format)
resource "local_file" "architecture_diagram" {
  filename = "${path.module}/architecture_diagram.md"
  content  = templatefile("${path.module}/templates/architecture_diagram.tmpl", {
    hub_resource_group_name     = var.hub_resource_group_name
    hub_vnet_name              = var.hub_vnet_name
    hub_address_space          = var.hub_address_space
    spoke_resource_groups      = var.spoke_resource_groups
    spoke_vnets                = var.spoke_vnets
    enable_aks                 = var.enable_aks
    aks_clusters               = var.aks_clusters
    enable_app_gateway         = var.enable_app_gateway
    enable_storage             = var.enable_storage
    enable_key_vault           = var.enable_key_vault
    enable_acr                 = var.enable_acr
    enable_monitoring          = var.enable_monitoring
    user_groups                = var.user_groups
    custom_roles               = var.custom_roles
    tags                       = var.tags
  })
}

# Local file for infrastructure documentation
resource "local_file" "infrastructure_doc" {
  filename = "${path.module}/infrastructure_documentation.md"
  content  = templatefile("${path.module}/templates/infrastructure_doc.tmpl", {
    hub_resource_group_name     = var.hub_resource_group_name
    hub_vnet_name              = var.hub_vnet_name
    hub_address_space          = var.hub_address_space
    spoke_resource_groups      = var.spoke_resource_groups
    spoke_vnets                = var.spoke_vnets
    enable_aks                 = var.enable_aks
    aks_clusters               = var.aks_clusters
    enable_app_gateway         = var.enable_app_gateway
    enable_storage             = var.enable_storage
    enable_key_vault           = var.enable_key_vault
    enable_acr                 = var.enable_acr
    enable_monitoring          = var.enable_monitoring
    user_groups                = var.user_groups
    custom_roles               = var.custom_roles
    location                   = var.location
    subscription_id            = var.subscription_id
    tenant_id                  = var.tenant_id
    tags                       = var.tags
  })
}

# Local file for deployment guide
resource "local_file" "deployment_guide" {
  filename = "${path.module}/deployment_guide.md"
  content  = templatefile("${path.module}/templates/deployment_guide.tmpl", {
    hub_resource_group_name     = var.hub_resource_group_name
    spoke_resource_groups      = var.spoke_resource_groups
    enable_aks                 = var.enable_aks
    aks_clusters               = var.aks_clusters
    enable_app_gateway         = var.enable_app_gateway
    enable_storage             = var.enable_storage
    enable_key_vault           = var.enable_key_vault
    enable_acr                 = var.enable_acr
    enable_monitoring          = var.enable_monitoring
    user_groups                = var.user_groups
    custom_roles               = var.custom_roles
    location                   = var.location
    subscription_id            = var.subscription_id
    tenant_id                  = var.tenant_id
  })
}

# Local file for security overview
resource "local_file" "security_overview" {
  filename = "${path.module}/security_overview.md"
  content  = templatefile("${path.module}/templates/security_overview.tmpl", {
    hub_resource_group_name     = var.hub_resource_group_name
    spoke_resource_groups      = var.spoke_resource_groups
    enable_aks                 = var.enable_aks
    aks_clusters               = var.aks_clusters
    enable_app_gateway         = var.enable_app_gateway
    enable_storage             = var.enable_storage
    enable_key_vault           = var.enable_key_vault
    enable_acr                 = var.enable_acr
    enable_monitoring          = var.enable_monitoring
    user_groups                = var.user_groups
    custom_roles               = var.custom_roles
    location                   = var.location
    subscription_id            = var.subscription_id
    tenant_id                  = var.tenant_id
    tags                       = var.tags
  })
}

# Local file for cost estimation
resource "local_file" "cost_estimation" {
  filename = "${path.module}/cost_estimation.md"
  content  = templatefile("${path.module}/templates/cost_estimation.tmpl", {
    hub_resource_group_name     = var.hub_resource_group_name
    spoke_resource_groups      = var.spoke_resource_groups
    enable_aks                 = var.enable_aks
    aks_clusters               = var.aks_clusters
    enable_app_gateway         = var.enable_app_gateway
    enable_storage             = var.enable_storage
    enable_key_vault           = var.enable_key_vault
    enable_acr                 = var.enable_acr
    enable_monitoring          = var.enable_monitoring
    location                   = var.location
    tags                       = var.tags
  })
}

# Create templates directory and template files
resource "local_file" "architecture_diagram_template" {
  filename = "${path.module}/templates/architecture_diagram.tmpl"
  content  = <<EOF
# Enterprise Hub-and-Spoke Architecture Diagram

```mermaid
graph TB
    %% Azure AD and Users
    subgraph "Azure Active Directory"
        AAD[Azure AD]
        UG[User Groups<br/>${join('<br/>', var.user_groups)}]
        CR[Custom Roles<br/>${join('<br/>', var.custom_roles)}]
    end

    %% Hub Resources
    subgraph "Hub Resource Group: ${var.hub_resource_group_name}"
        HUB_VNET["Hub VNET<br/>${var.hub_vnet_name}<br/>${join(', ', var.hub_address_space)}"]

        subgraph "Hub Networking"
            FW[Azure Firewall]
            GW[VPN Gateway]
            ER[ExpressRoute]
            BAST[Azure Bastion]
        end

        subgraph "Hub Security"
            KV[Key Vault<br/>${var.enable_key_vault ? 'Enabled' : 'Disabled'}]
            NSG[Network Security Groups]
        end
    end

    %% Spoke Resources
    ${join('\n    ', [for i, rg in var.spoke_resource_groups : "subgraph \"Spoke Resource Group: ${rg}\""])}
    ${join('\n        ', [for i, vnet in var.spoke_vnets : "${vnet.name}[\"Spoke VNET<br/>${vnet.name}<br/>${join(', ', vnet.address_space)}\"]"])}
    ${var.enable_aks ? join('\n        ', [for cluster in var.aks_clusters : "AKS${index(var.aks_clusters, cluster)}[\"AKS Cluster<br/>${cluster.name}<br/>${cluster.node_count} nodes\"]"]) : ''}
    ${var.enable_app_gateway ? join('\n        ', [for i, rg in var.spoke_resource_groups : "APPGW${i}[\"Application Gateway<br/>WAF Enabled\"]"]) : ''}
    ${var.enable_storage ? join('\n        ', [for i, rg in var.spoke_resource_groups : "STOR${i}[\"Storage Account<br/>${var.enable_static_website ? 'Static Website' : 'Blob Storage'}\"]"]) : ''}
    ${var.enable_acr ? join('\n        ', [for i, rg in var.spoke_resource_groups : "ACR${i}[\"Container Registry\"]"]) : ''}
    ${join('\n    ', [for i, rg in var.spoke_resource_groups : "end"])}

    %% Monitoring
    ${var.enable_monitoring ? "subgraph \"Monitoring\"
        LAW[\"Log Analytics<br/>Workspace\"]
        AM[\"Azure Monitor<br/>Container Insights\"]
    end" : ''}

    %% Connections
    AAD --> UG
    UG --> CR

    HUB_VNET --> FW
    HUB_VNET --> GW
    HUB_VNET --> ER
    HUB_VNET --> BAST

    HUB_VNET --> KV
    HUB_VNET --> NSG

    ${join('\n    ', [for i, rg in var.spoke_resource_groups : "HUB_VNET --> SPOKE_VNET_${i}"])}
    ${var.enable_aks ? join('\n    ', [for i, cluster in var.aks_clusters : "SPOKE_VNET_${index(var.spoke_vnets, firsttrue([for v in var.spoke_vnets : v if v.resource_group == cluster.resource_group], var.spoke_vnets[0]))} --> AKS${index(var.aks_clusters, cluster)}"]) : ''}
    ${var.enable_app_gateway ? join('\n    ', [for i, rg in var.spoke_resource_groups : "SPOKE_VNET_${i} --> APPGW${i}"]) : ''}
    ${var.enable_storage ? join('\n    ', [for i, rg in var.spoke_resource_groups : "SPOKE_VNET_${i} --> STOR${i}"]) : ''}
    ${var.enable_acr ? join('\n    ', [for i, rg in var.spoke_resource_groups : "SPOKE_VNET_${i} --> ACR${i}"]) : ''}

    ${var.enable_monitoring ? join('\n    ', [for cluster in var.aks_clusters : "AKS${index(var.aks_clusters, cluster)} --> LAW"]) : ''}
    ${var.enable_monitoring ? "LAW --> AM" : ''}

    %% Styling
    classDef hub fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef spoke fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef security fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    classDef monitoring fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px

    class HUB_VNET,FIREWALL,GATEWAY,BASTION hub
    class SPOKE_VNET,AKS,APPGW,STOR,ACR spoke
    class KV,NSG security
    class LAW,AM monitoring
```

## Architecture Overview

This diagram represents an enterprise-grade hub-and-spoke network architecture deployed in Azure.

### Hub Components
- **Virtual Network**: ${var.hub_vnet_name} (${join(', ', var.hub_address_space)})
- **Security**: Azure Firewall, Network Security Groups, Key Vault
- **Connectivity**: VPN Gateway, ExpressRoute, Azure Bastion

### Spoke Components
${join('\n', [for rg in var.spoke_resource_groups : "- **Resource Group**: ${rg}"])}

${var.enable_aks ? "### AKS Clusters\n" + join('\n', [for cluster in var.aks_clusters : "- **${cluster.name}**: ${cluster.node_count} nodes, Kubernetes ${cluster.kubernetes_version}"]) : ''}

${var.enable_app_gateway ? "### Application Gateway\n- WAF-enabled Application Gateway for web application protection\n" : ''}

${var.enable_storage ? "### Storage\n- Azure Storage Account with ${var.enable_static_website ? 'static website hosting' : 'blob storage'}\n" : ''}

${var.enable_key_vault ? "### Key Vault\n- Azure Key Vault for secrets management\n" : ''}

${var.enable_acr ? "### Container Registry\n- Azure Container Registry for container images\n" : ''}

${var.enable_monitoring ? "### Monitoring\n- Azure Monitor and Log Analytics for comprehensive observability\n" : ''}

### User Management
- **Groups**: ${join(', ', var.user_groups)}
- **Roles**: ${join(', ', var.custom_roles)}

### Tags Applied
${length(var.tags) > 0 ? join('\n', [for k, v in var.tags : "- ${k}: ${v}"]) : 'No tags applied'}
EOF
}

# Template for infrastructure documentation
resource "local_file" "infrastructure_doc_template" {
  filename = "${path.module}/templates/infrastructure_doc.tmpl"
  content  = <<EOF
# Infrastructure Documentation

## Overview
This document provides comprehensive documentation for the enterprise hub-and-spoke architecture deployed in Azure.

## Deployment Information
- **Subscription ID**: ${var.subscription_id}
- **Tenant ID**: ${var.tenant_id}
- **Location**: ${var.location}
- **Deployment Date**: ${timestamp()}

## Hub Infrastructure

### Resource Group: ${var.hub_resource_group_name}
**Purpose**: Central hub for shared networking and security services

#### Virtual Network: ${var.hub_vnet_name}
- **Address Space**: ${join(', ', var.hub_address_space)}
- **Purpose**: Central connectivity hub for all spoke networks

#### Security Components
- **Azure Firewall**: Centralized network security and filtering
- **Network Security Groups**: Subnet-level traffic control
- **Key Vault**: Centralized secrets management

#### Connectivity
- **VPN Gateway**: Site-to-site VPN connectivity
- **ExpressRoute**: Dedicated private connectivity
- **Azure Bastion**: Secure RDP/SSH access to VMs

## Spoke Infrastructure

${join('\n', [for i, rg in var.spoke_resource_groups : format("### Resource Group: %s\n**Purpose**: Application-specific resources and workloads\n", rg)])}

${join('\n', [for i, vnet in var.spoke_vnets : format("#### Virtual Network: %s\n- **Address Space**: %s\n- **Resource Group**: %s\n- **Peering**: Connected to hub VNET\n", vnet.name, join(', ', vnet.address_space), vnet.resource_group)])}

${var.enable_aks ? "## AKS Clusters\n" + join('\n', [for cluster in var.aks_clusters : format("### %s\n- **Resource Group**: %s\n- **Node Count**: %s\n- **Kubernetes Version**: %s\n- **Network Plugin**: Azure CNI\n- **RBAC**: Azure AD integration enabled\n", cluster.name, cluster.resource_group, cluster.node_count, cluster.kubernetes_version)]) : ''}

${var.enable_app_gateway ? "## Application Gateway\n- **SKU**: WAF_v2\n- **WAF Mode**: Prevention\n- **Rule Set**: OWASP 3.2\n- **Purpose**: Web application firewall and load balancing\n" : ''}

${var.enable_storage ? "## Storage Accounts\n- **Purpose**: Blob storage and static website hosting\n- **Redundancy**: Geo-redundant storage (GRS)\n- **Security**: Private endpoints and network restrictions\n" : ''}

${var.enable_key_vault ? "## Key Vault\n- **Purpose**: Secrets, keys, and certificates management\n- **Security**: Soft delete and purge protection enabled\n- **Access**: Role-based access control\n" : ''}

${var.enable_acr ? "## Container Registry\n- **Purpose**: Docker container image storage and management\n- **SKU**: Basic\n- **Security**: Private endpoints and admin user disabled\n" : ''}

${var.enable_monitoring ? "## Monitoring and Observability\n- **Log Analytics Workspace**: Centralized logging\n- **Azure Monitor**: Container insights and metrics\n- **Purpose**: Comprehensive monitoring and alerting\n" : ''}

## User Management and Access Control

### Azure AD Groups
${join('\n', [for group in var.user_groups : format("- **%s**: %s", group, lookup({
  "Platform-Administrators": "Full access to all resources",
  "Developers": "Application development and deployment",
  "DevOps-Engineers": "Infrastructure and CI/CD management",
  "Security-Auditors": "Read-only security monitoring",
  "End-Users": "Application access only"
}, group, "Custom group"))))}

### Custom Roles
${join('\n', [for role in var.custom_roles : format("- **%s**: %s", role, lookup({
  "Platform Administrator": "Full resource management permissions",
  "Developer": "Application deployment permissions",
  "DevOps Engineer": "Infrastructure management permissions",
  "Security Auditor": "Read-only monitoring permissions"
}, role, "Custom role"))))}

## Security Considerations

### Network Security
- Hub-and-spoke topology with centralized firewall
- Network segmentation with NSGs
- Private endpoints for PaaS services
- Forced tunneling through hub

### Identity and Access
- Azure AD integration for all services
- Role-based access control (RBAC)
- Principle of least privilege
- Conditional access policies

### Data Protection
- Encryption at rest and in transit
- Key Vault for secrets management
- Soft delete and backup policies

## Compliance and Governance
- Resource tagging for cost tracking
- Azure Policy for governance
- Azure Security Center for threat detection
- Regular security assessments

## Operational Procedures

### Backup and Recovery
- Automated backups for critical data
- Geo-redundant storage for high availability
- Disaster recovery procedures documented

### Monitoring and Alerting
- Centralized logging with Log Analytics
- Application performance monitoring
- Security incident response procedures

### Maintenance Windows
- Planned maintenance notifications
- Rolling updates for AKS clusters
- Backup verification procedures

## Contact Information
- **Platform Team**: platform@company.com
- **Security Team**: security@company.com
- **DevOps Team**: devops@company.com

---
*This documentation is auto-generated. Last updated: ${timestamp()}*
EOF
}

# Template for deployment guide
resource "local_file" "deployment_guide_template" {
  filename = "${path.module}/templates/deployment_guide.tmpl"
  content  = <<EOF
# Deployment Guide

## Prerequisites
Before deploying this infrastructure, ensure you have:

1. **Azure Subscription** with sufficient permissions
2. **Azure CLI** or **Azure PowerShell** installed
3. **Terraform** v1.0+ installed
4. **Azure AD** permissions for user/group management

## Authentication
```bash
# Login to Azure
az login

# Set subscription
az account set --subscription ${var.subscription_id}
```

## Deployment Steps

### 1. Initialize Terraform
```bash
terraform init
```

### 2. Review Configuration
```bash
terraform plan
```

### 3. Deploy Infrastructure
```bash
terraform apply
```

### 4. Verify Deployment
```bash
# Check resource groups
az group list --query "[].name" -o table

# Verify VNET peering
az network vnet peering list --resource-group ${var.hub_resource_group_name} --vnet-name ${var.hub_vnet_name} -o table
```

${var.enable_aks ? format("### 5. Configure AKS Access\n```bash\n# Get AKS credentials\n%s\n\n# Verify cluster access\nkubectl get nodes\n```", join('\n', [for cluster in var.aks_clusters : format("az aks get-credentials --resource-group %s --name %s", cluster.resource_group, cluster.name)])) : ''}

## Post-Deployment Configuration

### User Access Setup
1. Add users to appropriate Azure AD groups
2. Assign custom roles as needed
3. Configure conditional access policies

### Network Configuration
1. Configure VPN or ExpressRoute connections
2. Set up DNS resolution
3. Configure firewall rules

${var.enable_app_gateway ? "### Application Gateway Setup\n1. Configure backend pools\n2. Set up health probes\n3. Configure routing rules\n4. Enable WAF policies\n" : ''}

${var.enable_storage ? "### Storage Configuration\n1. Create storage containers\n2. Configure lifecycle policies\n3. Set up replication\n4. Configure access policies\n" : ''}

${var.enable_key_vault ? "### Key Vault Setup\n1. Add secrets and certificates\n2. Configure access policies\n3. Set up key rotation\n4. Enable monitoring\n" : ''}

${var.enable_acr ? "### Container Registry Configuration\n1. Enable admin user (if needed)\n2. Configure geo-replication\n3. Set up retention policies\n4. Configure security scanning\n" : ''}

${var.enable_monitoring ? "### Monitoring Setup\n1. Configure diagnostic settings\n2. Set up alerts\n3. Configure log retention\n4. Enable container insights\n" : ''}

## Validation Checklist

### Hub Infrastructure
- [ ] Hub resource group created
- [ ] Hub VNET with correct address space
- [ ] Azure Firewall deployed
- [ ] VPN Gateway configured
- [ ] Azure Bastion accessible

### Spoke Infrastructure
${join('\n', [for rg in var.spoke_resource_groups : format("- [ ] Resource group %s created", rg)])}
${join('\n', [for vnet in var.spoke_vnets : format("- [ ] VNET %s peered with hub", vnet.name)])}

${var.enable_aks ? "### AKS Validation\n" + join('\n', [for cluster in var.aks_clusters : format("- [ ] AKS cluster %s accessible\n- [ ] Node pools healthy\n- [ ] Azure AD integration working\n", cluster.name)]) : ''}

### Security Validation
- [ ] Azure AD groups created
- [ ] Custom roles assigned
- [ ] Network security groups configured
- [ ] Key Vault accessible by authorized users

### Monitoring Validation
- [ ] Log Analytics workspace receiving data
- [ ] Azure Monitor configured
- [ ] Alerts set up

## Troubleshooting

### Common Issues

#### VNET Peering Issues
```bash
# Check peering status
az network vnet peering show --resource-group SPOKE_RG --vnet-name SPOKE_VNET --name HUB_PEERING

# Check routing
az network vnet subnet list --resource-group SPOKE_RG --vnet-name SPOKE_VNET
```

#### AKS Connection Issues
```bash
# Reset AKS credentials
az aks get-credentials --resource-group CLUSTER_RG --name CLUSTER_NAME --overwrite-existing

# Check cluster status
kubectl cluster-info
```

#### Permission Issues
```bash
# Check role assignments
az role assignment list --assignee USER_PRINCIPAL --all

# Check group membership
az ad user get-member-groups --id USER_PRINCIPAL
```

## Rollback Procedures

### Emergency Rollback
```bash
# Destroy all resources
terraform destroy

# Selective destruction
terraform destroy -target=module.spoke
```

### Partial Rollback
```bash
# Remove specific components
terraform destroy -target=azurerm_kubernetes_cluster.aks
terraform destroy -target=azurerm_application_gateway.appgw
```

## Support Contacts
- **Deployment Issues**: devops@company.com
- **Security Concerns**: security@company.com
- **Azure Support**: Create ticket in Azure portal

---
*This guide is auto-generated. Last updated: ${timestamp()}*
EOF
}

# Template for security overview
resource "local_file" "security_overview_template" {
  filename = "${path.module}/templates/security_overview.tmpl"
  content  = <<EOF
# Security Overview

## Executive Summary
This document outlines the security measures implemented in the enterprise hub-and-spoke architecture.

## Security Architecture

### Defense in Depth
The architecture implements multiple layers of security controls:

1. **Identity and Access Management**
2. **Network Security**
3. **Application Security**
4. **Data Protection**
5. **Monitoring and Response**

## Identity and Access Management

### Azure Active Directory Integration
- **Groups**: ${join(', ', var.user_groups)}
- **Roles**: ${join(', ', var.custom_roles)}
- **MFA**: Required for all administrative access
- **Conditional Access**: Location and device-based policies

### Role-Based Access Control (RBAC)
- **Principle of Least Privilege**: Users have minimum required permissions
- **Custom Roles**: Tailored permissions for specific job functions
- **Regular Reviews**: Access rights reviewed quarterly

## Network Security

### Hub-and-Spoke Topology
- **Centralized Security**: All traffic flows through hub
- **Network Segmentation**: Isolated spoke networks
- **Forced Tunneling**: Internet traffic routed through firewall

### Security Components
- **Azure Firewall**: Next-generation firewall with threat intelligence
- **Network Security Groups**: Subnet-level traffic filtering
- **Application Gateway WAF**: Web application firewall protection
- **Private Endpoints**: Secure access to PaaS services

### Encryption
- **Data in Transit**: TLS 1.2+ for all communications
- **Data at Rest**: Azure-managed encryption keys
- **Key Management**: Azure Key Vault for cryptographic keys

## Application Security

${var.enable_aks ? "### AKS Security\n- **Azure AD Integration**: RBAC for cluster access\n- **Pod Security Standards**: Security contexts and policies\n- **Network Policies**: Traffic isolation between pods\n- **Image Security**: Container image scanning\n" : ''}

${var.enable_app_gateway ? "### Web Application Security\n- **WAF Policies**: OWASP rule sets\n- **DDoS Protection**: Azure DDoS Protection Standard\n- **SSL/TLS**: End-to-end encryption\n- **Bot Protection**: Automated threat mitigation\n" : ''}

## Data Protection

### Storage Security
${var.enable_storage ? "- **Encryption**: Server-side encryption with customer-managed keys\n- **Access Control**: Private endpoints and SAS tokens\n- **Data Classification**: Sensitivity labels and retention policies\n- **Backup**: Geo-redundant storage with cross-region replication\n" : ''}

### Key Management
${var.enable_key_vault ? "- **HSM Protection**: Hardware security modules for key operations\n- **Access Logging**: Comprehensive audit logging\n- **Key Rotation**: Automated key rotation policies\n- **Backup and Recovery**: Secure key backup procedures\n" : ''}

## Monitoring and Incident Response

### Security Monitoring
${var.enable_monitoring ? "- **Azure Security Center**: Unified security management\n- **Log Analytics**: Centralized security logging\n- **Azure Monitor**: Real-time threat detection\n- **Microsoft Defender**: Advanced threat protection\n" : ''}

### Incident Response
- **Alerting**: Automated alerts for security events
- **Playbooks**: Predefined response procedures
- **Forensics**: Log retention for investigation
- **Communication**: Incident notification procedures

## Compliance and Governance

### Regulatory Compliance
- **Azure Policy**: Automated compliance enforcement
- **Resource Tags**: Classification and ownership tracking
- **Audit Logs**: Comprehensive activity logging
- **Regular Assessments**: Quarterly security reviews

### Risk Management
- **Threat Modeling**: Architecture security analysis
- **Vulnerability Management**: Regular scanning and patching
- **Change Management**: Controlled configuration changes
- **Business Continuity**: Disaster recovery procedures

## Security Controls Matrix

| Control Category | Control | Implementation | Status |
|------------------|---------|----------------|--------|
| Access Control | Azure AD Groups | ${join(', ', var.user_groups)} | ✅ Implemented |
| Access Control | Custom RBAC Roles | ${join(', ', var.custom_roles)} | ✅ Implemented |
| Network Security | Hub-and-Spoke | Centralized security architecture | ✅ Implemented |
| Network Security | Azure Firewall | Threat intelligence enabled | ✅ Implemented |
| Network Security | NSGs | Subnet-level filtering | ✅ Implemented |
${var.enable_app_gateway ? "| Application Security | WAF | OWASP rule sets | ✅ Implemented |" : ""}
${var.enable_aks ? "| Container Security | AKS Security | Azure AD RBAC, network policies | ✅ Implemented |" : ""}
${var.enable_storage ? "| Data Protection | Storage Encryption | SSE with CMK | ✅ Implemented |" : ""}
${var.enable_key_vault ? "| Key Management | Key Vault | HSM-protected keys | ✅ Implemented |" : ""}
${var.enable_monitoring ? "| Monitoring | Security Center | Unified threat detection | ✅ Implemented |" : ''}

## Security Recommendations

### Immediate Actions
1. **Review Access Rights**: Audit user permissions quarterly
2. **Update Security Policies**: Regular policy review and updates
3. **Monitor Security Alerts**: Respond to alerts within SLA
4. **Conduct Penetration Testing**: Annual security assessments

### Ongoing Activities
1. **Security Training**: Regular security awareness training
2. **Patch Management**: Automated patching procedures
3. **Configuration Management**: Infrastructure as Code for consistency
4. **Incident Response Drills**: Regular simulation exercises

## Contact Information
- **Security Team**: security@company.com
- **Compliance Officer**: compliance@company.com
- **CISO**: ciso@company.com

---
*This security overview is auto-generated. Last updated: ${timestamp()}*
EOF
}

# Template for cost estimation
resource "local_file" "cost_estimation_template" {
  filename = "${path.module}/templates/cost_estimation.tmpl"
  content  = <<EOF
# Cost Estimation

## Overview
This document provides cost estimates for the enterprise hub-and-spoke architecture.

## Cost Breakdown

### Hub Infrastructure Costs

#### Networking (${var.location})
- **Virtual Network**: ~$0.05/hour
- **Azure Firewall**: ~$1.25/hour (basic policy)
- **VPN Gateway**: ~$0.19/hour (VpnGw1)
- **Azure Bastion**: ~$0.19/hour
- **ExpressRoute**: ~$0.12/hour per hour (if used)

**Monthly Estimate**: $800 - $1,200

### Spoke Infrastructure Costs

${join('\n', [for rg in var.spoke_resource_groups : format("#### Resource Group: %s\n- **Virtual Network**: ~$0.05/hour\n", rg)])}

${var.enable_aks ? "#### AKS Clusters\n" + join('\n', [for cluster in var.aks_clusters : format("- **%s** (%s nodes): ~$%s/month\n", cluster.name, cluster.node_count, cluster.node_count * 100)]) : ''}

${var.enable_app_gateway ? "#### Application Gateway\n- **WAF_v2**: ~$0.36/hour\n- **Estimated Monthly**: $250\n" : ''}

${var.enable_storage ? "#### Storage Account\n- **Standard GRS**: ~$0.05/GB/month\n- **Operations**: ~$0.01/10,000 operations\n- **Estimated Monthly**: $50-200 (depending on usage)\n" : ''}

${var.enable_key_vault ? "#### Key Vault\n- **Standard**: ~$0.03/10,000 operations\n- **HSM Keys**: Additional $1/key/month\n- **Estimated Monthly**: $10-50\n" : ''}

${var.enable_acr ? "#### Container Registry\n- **Basic**: ~$0.67/month\n- **Storage**: ~$0.02/GB\n- **Estimated Monthly**: $20-100\n" : ''}

${var.enable_monitoring ? "#### Monitoring\n- **Log Analytics**: ~$2.30/GB ingested\n- **Application Insights**: ~$2.30/GB\n- **Estimated Monthly**: $100-500\n" : ''}

### Total Monthly Cost Estimate

| Component | Cost Range | Notes |
|-----------|------------|-------|
| Hub Networking | $800-1,200 | Firewall, VPN, Bastion |
${join('\n', [for rg in var.spoke_resource_groups : format("| Spoke %s | $50-100 | VNET, subnets |", rg)])}
${var.enable_aks ? format("| AKS Clusters | $%s-%s | %s nodes total |", length(var.aks_clusters) * 100, length(var.aks_clusters) * 500, sum([for cluster in var.aks_clusters : cluster.node_count])) : ''}
${var.enable_app_gateway ? "| Application Gateway | $200-300 | WAF enabled |" : ''}
${var.enable_storage ? "| Storage | $50-200 | GRS, operations |" : ''}
${var.enable_key_vault ? "| Key Vault | $10-50 | Standard tier |" : ''}
${var.enable_acr ? "| Container Registry | $20-100 | Basic tier |" : ''}
${var.enable_monitoring ? "| Monitoring | $100-500 | Logs and metrics |" : ''}

**Total Estimated Monthly Cost**: $${800 + (length(var.spoke_resource_groups) * 75) + (var.enable_aks ? length(var.aks_clusters) * 300 : 0) + (var.enable_app_gateway ? 250 : 0) + (var.enable_storage ? 125 : 0) + (var.enable_key_vault ? 30 : 0) + (var.enable_acr ? 60 : 0) + (var.enable_monitoring ? 300 : 0)}-$${1200 + (length(var.spoke_resource_groups) * 100) + (var.enable_aks ? length(var.aks_clusters) * 500 : 0) + (var.enable_app_gateway ? 300 : 0) + (var.enable_storage ? 200 : 0) + (var.enable_key_vault ? 50 : 0) + (var.enable_acr ? 100 : 0) + (var.enable_monitoring ? 500 : 0)}

## Cost Optimization Recommendations

### Reserved Instances
- **AKS**: 1-year reservations save 20-30%
- **VMs**: 3-year reservations save 40-60%

### Autoscaling
- Configure AKS node pool autoscaling
- Use Azure Functions for event-driven workloads

### Storage Optimization
- Use lifecycle policies for blob storage
- Choose appropriate redundancy levels
- Use Azure Files for shared storage

### Monitoring Optimization
- Set appropriate log retention periods
- Use sampling for high-volume telemetry
- Configure alert thresholds

### Networking Optimization
- Use Azure Firewall policies efficiently
- Optimize VPN gateway sizing
- Consider ExpressRoute for high-volume transfers

## Budget Alerts
Set up the following budget alerts in Azure Cost Management:

1. **Monthly Budget**: Alert at 80% of monthly budget
2. **Resource Group Budgets**: Individual alerts per spoke
3. **Service Budgets**: Alerts for high-cost services (AKS, Storage)

## Cost Tracking Tags
All resources are tagged with:
${length(var.tags) > 0 ? join('\n', [for k, v in var.tags : format("- **%s**: %s", k, v)]) : '- No specific cost tracking tags applied'}

## Reporting
- **Azure Cost Management**: Daily cost reports
- **Resource Usage**: Monitor utilization metrics
- **Budget vs Actual**: Monthly budget reviews

---
*Cost estimates are approximate and based on ${var.location} pricing. Actual costs may vary based on usage patterns and Azure pricing changes. Last updated: ${timestamp()}*
EOF
}
EOF
}

# Create templates directory
resource "local_file" "create_templates_dir" {
  filename = "${path.module}/templates/.gitkeep"
  content  = ""
}