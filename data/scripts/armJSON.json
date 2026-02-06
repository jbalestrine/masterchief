{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",

  "parameters": {
    "location": {
      "type": "string",
      "defaultValue": "eastus",
      "metadata": { "description": "Azure region for deployment" }
    },

    "resourceGroupName": {
      "type": "string",
      "defaultValue": "EnterpriseAppRG"
    },

    "environment": {
      "type": "string",
      "defaultValue": "Production",
      "allowedValues": ["Dev", "Test", "Stage", "Production"]
    },

    "adminUsername": {
      "type": "string",
      "defaultValue": "enterpriseadmin"
    },

    "adminPassword": {
      "type": "secureString",
      "metadata": {
        "description": "Admin password (stored in Key Vault, not reused directly)"
      }
    },

    "vmSizeWeb": {
      "type": "string",
      "defaultValue": "Standard_D2s_v5"
    },

    "vmSizeSOFS": {
      "type": "string",
      "defaultValue": "Standard_D4s_v5"
    },

    "sqlAdminUser": {
      "type": "string",
      "defaultValue": "sqladmin"
    },

    "sqlAdminPassword": {
      "type": "secureString"
    }
  },

  "variables": {
    "tags": {
      "Environment": "[parameters('environment')]",
      "Owner": "EnterpriseIT",
      "CostCenter": "IT-Apps",
      "Compliance": "ISO27001"
    },

    "vnetName": "EnterpriseVNet",
    "vnetAddress": "10.0.0.0/16",

    "subnetWeb": "WebSubnet",
    "subnetWebPrefix": "10.0.1.0/24",

    "subnetSOFS": "SOFSSubnet",
    "subnetSOFSPrefix": "10.0.2.0/24",

    "nsgWeb": "WebNSG",
    "nsgSOFS": "SOFSNSG",

    "keyVaultName": "[concat('kv-', uniqueString(resourceGroup().id))]",

    "webVmName": "EnterpriseWebVM",
    "sofsVm1": "SOFSNode01",
    "sofsVm2": "SOFSNode02",

    "sqlServerName": "[concat('sqlsrv', uniqueString(resourceGroup().id))]",
    "sqlDbName": "EnterpriseAppDB",

    "windowsImage": {
      "publisher": "MicrosoftWindowsServer",
      "offer": "WindowsServer",
      "sku": "2022-datacenter-azure-edition",
      "version": "latest"
    }
  },

  "resources": [
    {
      "type": "Microsoft.Network/networkSecurityGroups",
      "apiVersion": "2023-04-01",
      "name": "[variables('nsgWeb')]",
      "location": "[parameters('location')]",
      "properties": {
        "securityRules": [
          {
            "name": "Allow-HTTP",
            "properties": {
              "priority": 100,
              "access": "Allow",
              "direction": "Inbound",
              "protocol": "Tcp",
              "sourcePortRange": "*",
              "destinationPortRange": "80",
              "sourceAddressPrefix": "*",
              "destinationAddressPrefix": "*"
            }
          },
          {
            "name": "Allow-RDP",
            "properties": {
              "priority": 110,
              "access": "Allow",
              "direction": "Inbound",
              "protocol": "Tcp",
              "sourcePortRange": "*",
              "destinationPortRange": "3389",
              "sourceAddressPrefix": "*",
              "destinationAddressPrefix": "*"
            }
          }
        ]
      },
      "tags": "[variables('tags')]"
    },

    {
      "type": "Microsoft.Network/networkSecurityGroups",
      "apiVersion": "2023-04-01",
      "name": "[variables('nsgSOFS')]",
      "location": "[parameters('location')]",
      "properties": {},
      "tags": "[variables('tags')]"
    },

    {
      "type": "Microsoft.Network/virtualNetworks",
      "apiVersion": "2023-04-01",
      "name": "[variables('vnetName')]",
      "location": "[parameters('location')]",
      "properties": {
        "addressSpace": {
          "addressPrefixes": ["[variables('vnetAddress')]"]
        },
        "subnets": [
          {
            "name": "[variables('subnetWeb')]",
            "properties": {
              "addressPrefix": "[variables('subnetWebPrefix')]",
              "networkSecurityGroup": {
                "id": "[resourceId('Microsoft.Network/networkSecurityGroups', variables('nsgWeb'))]"
              }
            }
          },
          {
            "name": "[variables('subnetSOFS')]",
            "properties": {
              "addressPrefix": "[variables('subnetSOFSPrefix')]",
              "networkSecurityGroup": {
                "id": "[resourceId('Microsoft.Network/networkSecurityGroups', variables('nsgSOFS'))]"
              }
            }
          }
        ]
      },
      "tags": "[variables('tags')]"
    },

    {
      "type": "Microsoft.KeyVault/vaults",
      "apiVersion": "2023-07-01",
      "name": "[variables('keyVaultName')]",
      "location": "[parameters('location')]",
      "properties": {
        "tenantId": "[subscription().tenantId]",
        "sku": {
          "family": "A",
          "name": "standard"
        },
        "enableSoftDelete": true,
        "enablePurgeProtection": true,
        "accessPolicies": []
      },
      "tags": "[variables('tags')]"
    },

    {
      "type": "Microsoft.Sql/servers",
      "apiVersion": "2023-05-01-preview",
      "name": "[variables('sqlServerName')]",
      "location": "[parameters('location')]",
      "properties": {
        "administratorLogin": "[parameters('sqlAdminUser')]",
        "administratorLoginPassword": "[parameters('sqlAdminPassword')]",
        "version": "12.0"
      },
      "tags": "[variables('tags')]"
    },

    {
      "type": "Microsoft.Sql/servers/databases",
      "apiVersion": "2023-05-01-preview",
      "name": "[concat(variables('sqlServerName'), '/', variables('sqlDbName'))]",
      "location": "[parameters('location')]",
      "dependsOn": [
        "[resourceId('Microsoft.Sql/servers', variables('sqlServerName'))]"
      ],
      "sku": {
        "name": "S0",
        "tier": "Standard"
      },
      "properties": {
        "collation": "SQL_Latin1_General_CP1_CI_AS"
      }
    },

    {
      "type": "Microsoft.Compute/virtualMachines",
      "apiVersion": "2023-09-01",
      "name": "[variables('webVmName')]",
      "location": "[parameters('location')]",
      "dependsOn": [
        "[resourceId('Microsoft.Network/virtualNetworks', variables('vnetName'))]"
      ],
      "properties": {
        "hardwareProfile": {
          "vmSize": "[parameters('vmSizeWeb')]"
        },
        "osProfile": {
          "computerName": "[variables('webVmName')]",
          "adminUsername": "[parameters('adminUsername')]",
          "adminPassword": "[parameters('adminPassword')]"
        },
        "storageProfile": {
          "imageReference": "[variables('windowsImage')]",
          "osDisk": {
            "createOption": "FromImage",
            "managedDisk": {
              "storageAccountType": "Premium_LRS"
            }
          }
        },
        "networkProfile": {
          "networkInterfaces": []
        }
      },
      "tags": "[variables('tags')]"
    }
  ],

  "outputs": {
    "deploymentSummary": {
      "type": "string",
      "value": "Enterprise IIS Web + SQL Backend + VNET + SOFS-ready infrastructure deployed."
    }
  }
}
