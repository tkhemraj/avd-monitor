"""App configuration — loaded from environment or .env file."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Azure credentials (optional — falls back to demo mode)
    AZURE_SUBSCRIPTION_ID: str = os.getenv("AZURE_SUBSCRIPTION_ID", "")
    AZURE_RESOURCE_GROUP: str = os.getenv("AZURE_RESOURCE_GROUP", "")
    AZURE_HOST_POOL: str = os.getenv("AZURE_HOST_POOL", "")

    # App
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() != "false"
    REFRESH_INTERVAL_SECONDS: int = int(os.getenv("REFRESH_INTERVAL_SECONDS", "30"))
    APP_TITLE: str = os.getenv("APP_TITLE", "AVD Pressure Monitor")
    PORT: int = int(os.getenv("PORT", "8000"))

    @property
    def azure_configured(self) -> bool:
        return bool(
            self.AZURE_SUBSCRIPTION_ID
            and self.AZURE_RESOURCE_GROUP
            and self.AZURE_HOST_POOL
        )


settings = Settings()
