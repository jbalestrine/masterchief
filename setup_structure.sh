#!/bin/bash

# Create core directory structure
mkdir -p core/{module-loader,config-engine,event-bus,cli}
mkdir -p modules/{terraform/azure/{networking,compute,storage,database,web-integration,security},ansible/{playbooks,roles,inventory},powershell-dsc/{configurations,resources},kubernetes/{helm-charts,kustomize,policies}}
mkdir -p chatops/irc/{inspircd,bot-engine,data-ingestion,web-client}
mkdir -p platform/{web-ide,scripts,addons,system-manager,cmdb,portal,catalog}
mkdir -p observability/{dashboards,alerts,logging,slo}
mkdir -p security/{policies,compliance,secrets}
mkdir -p pipelines/{github-actions,templates,gitops}
mkdir -p resilience/{backup,dr,chaos}
mkdir -p docs/{architecture,runbooks,adrs}
mkdir -p tests/{unit,integration,e2e}
mkdir -p config/{global,environments}

# Create __init__.py files for Python packages
find . -type d -name "core" -o -name "modules" -o -name "chatops" -o -name "platform" -o -name "observability" -o -name "security" -o -name "pipelines" -o -name "resilience" | while read dir; do
  if [ -d "$dir" ]; then
    touch "$dir/__init__.py"
  fi
done

# Create subdirectory __init__.py files
find core modules chatops platform observability security pipelines resilience -type d -exec touch {}/__init__.py \; 2>/dev/null || true

echo "Directory structure created successfully"
