# PowerShell helper to deploy the ARM template to a resource group
param(
  [string]$ResourceGroupName = 'rg-tfe-aks-demo',
  [string]$Location = 'eastus',
  [string]$TemplateFile = 'arm_template.json'
)

if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
  Write-Error 'Azure CLI (az) is required to run this script.'
  exit 1
}

az group create --name $ResourceGroupName --location $Location
az deployment group create --resource-group $ResourceGroupName --template-file $TemplateFile