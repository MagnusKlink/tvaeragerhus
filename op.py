import asyncio
import os
from onepassword.client import Client
from django.core.exceptions import ImproperlyConfigured

async def get_secret_async(secret_reference: str) -> str:
    """Asynchronously authenticates and resolves a 1Password secret."""
    token = os.getenv("OP_SERVICE_ACCOUNT_TOKEN")
    if not token:
        raise ValueError("OP_SERVICE_ACCOUNT_TOKEN environment variable is missing.")

    client = await Client.authenticate(
        auth=token,
        integration_name="Django Tvaeragerhus 1P Integration",
        integration_version="v1.0.0"
    )
    secret_value = await client.secrets.resolve(secret_reference)
    
    # Print success message to the terminal
    print(f"Successfully got secret from 1Password: {secret_reference}")
    
    return secret_value

def get_secret(secret_reference: str, fallback: str = None) -> str:
    """Synchronous wrapper for settings.py, calling the async function internally."""
    try:
        return asyncio.run(get_secret_async(secret_reference))
    except Exception as e:
        if fallback is not None:
            return fallback
        raise ImproperlyConfigured(f"Failed to fetch secret from 1Password: {e}")