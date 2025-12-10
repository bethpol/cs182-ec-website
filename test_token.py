import os
import requests
from dotenv import load_dotenv

load_dotenv('scraper/.env')
token = os.getenv('ED_API_TOKEN')

print(f"Testing token: {token[:5]}...")

try:
    headers = {'Authorization': token}
    response = requests.get('https://us.edstem.org/api/user', headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
