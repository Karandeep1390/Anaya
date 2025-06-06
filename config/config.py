import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))

# File Paths
CUSTOMER_DATA_PATH = os.getenv('CUSTOMER_DATA_PATH', 'data/customer_data.csv')
USER_CREDENTIALS_PATH = os.getenv('USER_CREDENTIALS_PATH', 'data/user_credentials.csv')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/app.log')

# Create necessary directories
os.makedirs(os.path.dirname(CUSTOMER_DATA_PATH), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)