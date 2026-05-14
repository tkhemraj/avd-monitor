"""Azure SDK client — wraps credential acquisition and SDK clients."""

from ..config import settings

try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.desktopvirtualization import DesktopVirtualizationMgmtClient
    from azure.monitor.query import MetricsQueryClient
    from azure.mgmt.compute import ComputeManagementClient
    _AZURE_AVAILABLE = True
except ImportError:
    _AZURE_AVAILABLE = False


class AzureClientBundle:
    """Lazily initialises all Azure SDK clients from a single credential."""

    def __init__(self):
        if not _AZURE_AVAILABLE:
            raise RuntimeError("Azure SDK packages are not installed. Run: pip install azure-identity azure-mgmt-desktopvirtualization azure-monitor-query azure-mgmt-compute")
        credential = DefaultAzureCredential()
        sub = settings.AZURE_SUBSCRIPTION_ID
        self.avd = DesktopVirtualizationMgmtClient(credential, sub)
        self.metrics = MetricsQueryClient(credential)
        self.compute = ComputeManagementClient(credential, sub)


_bundle: AzureClientBundle | None = None


def get_clients() -> AzureClientBundle:
    global _bundle
    if _bundle is None:
        _bundle = AzureClientBundle()
    return _bundle
