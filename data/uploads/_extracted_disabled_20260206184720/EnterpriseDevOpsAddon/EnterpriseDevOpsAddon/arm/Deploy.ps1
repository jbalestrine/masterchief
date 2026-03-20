# Import module
Import-Module .\EnterpriseARM.psm1

# Example usage
$RG = "EnterpriseAppRG"
$Loc = "eastus"

Deploy-ARMTemplate -ResourceGroup $RG -Location $Loc

# Optional setup tasks
# Setup-IIS
# Setup-PythonDependencies
# Setup-WSL2
# Setup-Docker
