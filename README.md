# Weather Agent Service

## 1. Code Functionality

The Weather Agent Service is a FastAPI-based web application that provides weather information query services. It retrieves weather data for cities across the country through the AMAP Weather API and provides a friendly API interface for other applications and agents to access. The service supports DID identity verification to ensure secure API access.

Main features include:
- Weather Information Query: Get detailed weather forecast information by city name
- Agent Description: Provide agent description information compliant with ANP protocol
- Weather Information Subscription: Support subscription to weather information services (currently limited to whitelisted users)
- Natural Language Interface: Planned support for natural language weather information queries (under development)

## 2. Directory Structure

```
anp-weather-agent/
├── anp_weather_agent.py      # Application main entry
├── config.py                 # Configuration file
├── api_router/               # API route definitions
│   ├── __init__.py
│   ├── router.py             # Main route registration
│   ├── did_auth_middleware.py # DID authentication middleware
│   ├── jwt_config.py         # JWT configuration
│   └── weather/              # Weather-related APIs
│       ├── __init__.py
│       ├── ad_router.py      # Agent description API
│       ├── nl_router.py      # Natural language query API
│       ├── subscription_router.py # Subscription service API
│       ├── weather_info_router.py # Weather information API
│       ├── yaml_router.py    # YAML file API
│       └── api/              # YAML interface description files directory
├── doc/                      # Documentation and keys
│   ├── test_jwt_key/         # Test JWT keys
│   └── use_did_test_public/  # DID test documents
├── utils/                    # Utilities
│   ├── __init__.py
│   └── log_base.py           # Logging configuration
└── scripts/                  # Test scripts
    ├── test_weather_agent_auth.py
    └── test_weather_agent_discovery.py
```

## 3. Installation and Configuration

### Requirements
- Python 3.8+
- FastAPI
- Uvicorn
- aiohttp
- Poetry (for dependency management)

### Installation Steps

1. Clone the repository
```bash
git clone git@github.com:agent-network-protocol/anp-weather-agent.git
cd anp-weather-agent
```

2. Install dependencies with Poetry
```bash
# Install Poetry if you haven't already
# curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate the Poetry virtual environment
poetry shell
```

### Configuration

1. Create a `.env` file, refer to `.env.example` for configuration:
```
# Weather service settings
# Default is AMAP API, you can also replace it with other APIs
AMAP_WEATHER_API_URL = "https://restapi.amap.com/v3/weather/weatherInfo"
AMAP_API_KEY = "your-amap-api-key"

# Your agent description json file domain, your sub-URL needs to use this configuration
# If running locally, you can use localhost:9870, where 9870 is the port number
AGENT_DESCRIPTION_JSON_DOMAIN = "localhost:9870"

# JWT settings
# Do not use the following test keys in production environment, these files are for testing only
JWT_PRIVATE_KEY_PATH = "doc/test_jwt_key/private_key.pem"
JWT_PUBLIC_KEY_PATH = "doc/test_jwt_key/public_key.pem"

# DID settings
# The following configuration is only for testing, do not use in production
DID_DOMAIN = "agent-did.com"
DID_PATH = "test:public"
```

2. Obtain AMAP API Key
   - Visit [AMAP Open Platform](https://lbs.amap.com/) to register an account
   - Create an application and enable the Weather API service
   - Get the API Key and configure it in the `.env` file

Note: If you need to use another weather information provider, you'll need to modify the relevant code in `api_router/weather/weather_info_router.py` to integrate with the corresponding API interface.

### Starting the Service

```bash
# Make sure you're in the Poetry environment
poetry run python anp_weather_agent.py

# Or if you've already activated the Poetry shell
python anp_weather_agent.py
```

The service runs on `http://localhost:9870` by default.
