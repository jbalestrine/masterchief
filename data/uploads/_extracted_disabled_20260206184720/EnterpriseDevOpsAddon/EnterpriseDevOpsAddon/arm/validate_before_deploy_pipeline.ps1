az deployment group validate --resource-group $(resourceGroupName) --template-file $(armTemplateFile) --parameters @$(armParametersFile)
