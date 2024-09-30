import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

login_url = 'https://transkribus.eu/TrpServer/rest/auth/login'

def login_transkribus():
    """
    Logs in to the Transkribus API using credentials from environment variables.

    Returns:
        str: The session ID upon spiuccessful login.

    Raises:
        Exception: If the login fails, an exception is raised with the error details.
    """
    # Retrieve credentials from environment variables
    username = os.getenv('TRANSKRIBUS_USER')
    password = os.getenv('TRANSKRIBUS_PASSWORD')

    if not username or not password:
        raise ValueError("Transkribus username or password not found in environment variables.")

    # Make the login request
    response = requests.post(login_url, data={'user': username, 'pw': password})
    
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        session_id = root.find('sessionId').text
        print("Successfully logged in to Transkribus.")
        return session_id
    else:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")
