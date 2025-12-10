import os
import requests
from dotenv import load_dotenv

load_dotenv('scraper/.env')
token = os.getenv('ED_API_TOKEN')
course_id = 84647 # CS182

headers = {'Authorization': token}

print(f"Probing threads for course {course_id}...")

urls_to_try = [
    f'https://us.edstem.org/api/courses/{course_id}/threads',
    f'https://us.edstem.org/api/courses/{course_id}/posts',
]

for url in urls_to_try:
    print(f"Trying GET {url}")
    resp = requests.get(url, headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("Success!")
        data = resp.json()
        print(f"Top level keys: {list(data.keys())}")
        threads = data.get('threads', [])
        users = data.get('users', [])
        print(f"Found {len(threads)} threads and {len(users)} users.")
        
        if threads:
            t = threads[0]
            print(f"Sample thread keys: {list(t.keys())}")
            print(f"Files field: {t.get('media', 'N/A')}") # EdStem often uses 'media' or 'files'
            print(f"Title: {t.get('title')}")
            
        if users:
            print(f"Sample user: {users[0]}")
        break
    else:
        print(f"Response: {resp.text[:200]}")
