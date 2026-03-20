"""
MasterChief Azure Integration Module
Provides Azure SDK integration for resource management
"""

import logging
from typing import Dict, List, Any, Optional
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
try:
    from azure.mgmt.web import WebSiteManagementClient
    WEB_CLIENT_AVAILABLE = True
except ImportError:
    WEB_CLIENT_AVAILABLE = False
    WebSiteManagementClient = None
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError

from auth_config import auth_config

logger = logging.getLogger(__name__)

class AzureIntegration:
    """Azure SDK integration for resource management"""

    def __init__(self):
        self.config = auth_config.get_azure_config()
        self.credential = None
        self.subscription_id = self.config.get('subscription_id')

        # Initialize clients
        self._init_clients()

    def _init_clients(self):
        """Initialize Azure SDK clients"""
        try:
            if self.config.get('client_id') and self.config.get('client_secret') and self.config.get('tenant_id'):
                # Use service principal authentication
                self.credential = ClientSecretCredential(
                    tenant_id=self.config['tenant_id'],
                    client_id=self.config['client_id'],
                    client_secret=self.config['client_secret']
                )
            else:
                # Use default credential (managed identity, CLI, etc.)
                self.credential = DefaultAzureCredential()

            # Initialize clients
            if self.subscription_id:
                self.resource_client = ResourceManagementClient(self.credential, self.subscription_id)
                self.compute_client = ComputeManagementClient(self.credential, self.subscription_id)
                self.storage_client = StorageManagementClient(self.credential, self.subscription_id)
                if WEB_CLIENT_AVAILABLE:
                    self.web_client = WebSiteManagementClient(self.credential, self.subscription_id)
                else:
                    self.web_client = None

        except Exception as e:
            logger.error(f"Failed to initialize Azure clients: {e}")
            self.credential = None

    def is_configured(self) -> bool:
        """Check if Azure integration is properly configured"""
        return self.credential is not None and self.subscription_id is not None

    # Subscription Management
    def list_subscriptions(self) -> List[Dict[str, Any]]:
        """List available Azure subscriptions"""
        try:
            if not self.is_configured():
                return []

            # For service principal, we can only access the configured subscription
            if isinstance(self.credential, ClientSecretCredential):
                return [{
                    'subscription_id': self.subscription_id,
                    'display_name': f'Subscription {self.subscription_id}',
                    'state': 'Enabled'
                }]

            # For other credential types, we could list all subscriptions
            # This would require additional permissions
            return []

        except Exception as e:
            logger.error(f"Error listing subscriptions: {e}")
            return []

    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details"""
        try:
            if not self.is_configured() or subscription_id != self.subscription_id:
                return None

            return {
                'subscription_id': subscription_id,
                'display_name': f'Subscription {subscription_id}',
                'state': 'Enabled'
            }

        except Exception as e:
            logger.error(f"Error getting subscription {subscription_id}: {e}")
            return None

    # Resource Group Management
    def list_resource_groups(self) -> List[Dict[str, Any]]:
        """List resource groups in the subscription"""
        try:
            if not self.is_configured():
                return []

            resource_groups = []
            for rg in self.resource_client.resource_groups.list():
                resource_groups.append({
                    'name': rg.name,
                    'location': rg.location,
                    'tags': rg.tags or {},
                    'provisioning_state': getattr(rg, 'provisioning_state', 'Unknown')
                })

            return resource_groups

        except Exception as e:
            logger.error(f"Error listing resource groups: {e}")
            return []

    def create_resource_group(self, name: str, location: str, tags: Dict[str, str] = None) -> bool:
        """Create a new resource group"""
        try:
            if not self.is_configured():
                return False

            rg_params = {
                'location': location,
                'tags': tags or {}
            }

            result = self.resource_client.resource_groups.create_or_update(name, rg_params)
            return result.name == name

        except Exception as e:
            logger.error(f"Error creating resource group {name}: {e}")
            return False

    def delete_resource_group(self, name: str) -> bool:
        """Delete a resource group"""
        try:
            if not self.is_configured():
                return False

            result = self.resource_client.resource_groups.delete(name)
            return True

        except Exception as e:
            logger.error(f"Error deleting resource group {name}: {e}")
            return False

    # Virtual Machine Management
    def list_virtual_machines(self) -> List[Dict[str, Any]]:
        """List virtual machines in the subscription"""
        try:
            if not self.is_configured():
                return []

            vms = []
            for vm in self.compute_client.virtual_machines.list_all():
                vms.append({
                    'name': vm.name,
                    'location': vm.location,
                    'resource_group': vm.id.split('/')[4],
                    'vm_size': vm.hardware_profile.vm_size,
                    'os_type': vm.storage_profile.os_disk.os_type,
                    'power_state': getattr(vm, 'power_state', 'Unknown'),
                    'tags': vm.tags or {}
                })

            return vms

        except Exception as e:
            logger.error(f"Error listing virtual machines: {e}")
            return []

    def start_virtual_machine(self, resource_group: str, vm_name: str) -> bool:
        """Start a virtual machine"""
        try:
            if not self.is_configured():
                return False

            result = self.compute_client.virtual_machines.start(resource_group, vm_name)
            return True

        except Exception as e:
            logger.error(f"Error starting VM {vm_name}: {e}")
            return False

    def stop_virtual_machine(self, resource_group: str, vm_name: str) -> bool:
        """Stop a virtual machine"""
        try:
            if not self.is_configured():
                return False

            result = self.compute_client.virtual_machines.power_off(resource_group, vm_name)
            return True

        except Exception as e:
            logger.error(f"Error stopping VM {vm_name}: {e}")
            return False

    # Storage Account Management
    def list_storage_accounts(self) -> List[Dict[str, Any]]:
        """List storage accounts in the subscription"""
        try:
            if not self.is_configured():
                return []

            storage_accounts = []
            for sa in self.storage_client.storage_accounts.list():
                storage_accounts.append({
                    'name': sa.name,
                    'location': sa.location,
                    'resource_group': sa.id.split('/')[4],
                    'sku': sa.sku.name,
                    'kind': sa.kind,
                    'tags': sa.tags or {}
                })

            return storage_accounts

        except Exception as e:
            logger.error(f"Error listing storage accounts: {e}")
            return []

    def create_storage_account(self, resource_group: str, name: str, location: str) -> bool:
        """Create a storage account"""
        try:
            if not self.is_configured():
                return False

            sa_params = {
                'location': location,
                'sku': {'name': 'Standard_LRS'},
                'kind': 'StorageV2'
            }

            result = self.storage_client.storage_accounts.create(resource_group, name, sa_params)
            return result.name == name

        except Exception as e:
            logger.error(f"Error creating storage account {name}: {e}")
            return False

    # App Service Management
    def list_app_services(self) -> List[Dict[str, Any]]:
        """List app services in the subscription"""
        if not WEB_CLIENT_AVAILABLE or not self.is_configured():
            return []

        try:

            apps = []
            for app in self.web_client.web_apps.list():
                apps.append({
                    'name': app.name,
                    'location': app.location,
                    'resource_group': app.id.split('/')[4],
                    'default_hostname': app.default_hostname,
                    'state': app.state,
                    'tags': app.tags or {}
                })

            return apps

        except Exception as e:
            logger.error(f"Error listing app services: {e}")
            return []

    def create_app_service(self, resource_group: str, name: str, location: str) -> bool:
        """Create an app service"""
        if not WEB_CLIENT_AVAILABLE:
            return False

        try:
            if not self.is_configured():
                return False

            app_params = {
                'location': location,
                'server_farm_id': f'/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Web/serverfarms/Default1'
            }

            result = self.web_client.web_apps.create_or_update(resource_group, name, app_params)
            return result.name == name

        except Exception as e:
            logger.error(f"Error creating app service {name}: {e}")
            return False

# Global Azure integration instance
azure_integration = AzureIntegration()