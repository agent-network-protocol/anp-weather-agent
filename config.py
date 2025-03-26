import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base directory configuration
BASE_DIR = Path(__file__).parent

# DID configurations
DID_DOMAIN = os.getenv("DID_DOMAIN", "agent-did.com")
DID_PATH = os.getenv("DID_PATH", "test:public")

AGENT_DESCRIPTION_JSON_DOMAIN = os.getenv(
    "AGENT_DESCRIPTION_JSON_DOMAIN", "agent-connect.ai"
)

# Weather service settings
AMAP_WEATHER_API_URL = os.getenv(
    "AMAP_WEATHER_API_URL", "https://restapi.amap.com/v3/weather/weatherInfo"
)
AMAP_API_KEY = os.getenv("AMAP_API_KEY", "apikey-test")

# JWT settings
JWT_PRIVATE_KEY_PATH = os.getenv(
    "JWT_PRIVATE_KEY_PATH", str(BASE_DIR / "doc" / "test_jwt_key" / "private_key.pem")
)
JWT_PUBLIC_KEY_PATH = os.getenv(
    "JWT_PUBLIC_KEY_PATH", str(BASE_DIR / "doc" / "test_jwt_key" / "public_key.pem")
)
