import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_DEPLOYMENT_NAME = os.getenv("OPENAI_DEPLOYMENT_NAME")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE")

# google custom search api Configuration
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# mail service configurations
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_ENDPOINT = os.getenv("TOKEN_ENDPOINT")
API_ENDPOINT = os.getenv("API_ENDPOINT")
ALERT_FROM = os.getenv("FROM_EMAIL")
TEST_MAIL_ADDRESS = os.getenv("TEST_MAIL_ADDRESS")

# logger level
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO").upper()


# List of all required environment variables
required_vars = [
    "AZURE_OPENAI_API_KEY",
    "OPENAI_API_BASE",
    "OPENAI_DEPLOYMENT_NAME",
    "OPENAI_API_VERSION",
    "OPENAI_API_TYPE",
    "GOOGLE_CSE_ID",
    "GOOGLE_API_KEY",
    "CLIENT_ID",
    "CLIENT_SECRET",
    "TOKEN_ENDPOINT",
    "API_ENDPOINT",
    "TEST_MAIL_ADDRESS",
    "FROM_EMAIL",
    "LOGGING_LEVEL",
]

# Check for missing environment variables
missing_vars = [var_name for var_name in required_vars if not os.getenv(var_name)]

if missing_vars:
    raise ValueError(
        f"Missing required environment variables: {', '.join(missing_vars)}"
    )
