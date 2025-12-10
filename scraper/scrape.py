import os
import json
import requests
from dotenv import load_dotenv
import sys
import time

COURSE_ID = 84647 # CS182 / EECS182

def main():
    # Load env from .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path)
    
    token = os.getenv('ED_API_TOKEN')
    if not token:
        print("Error: ED_API_TOKEN not found in .env")
        return

    print(f"Initializing scraper for Course ID: {COURSE_ID}")
    
    headers = {'Authorization': token}
    
    all_threads = []
    limit = 30 # EdStem default/safe limit
    offset = 0
    page_num = 1
    
    try:
        while True:
            print(f"Fetching page {page_num} (offset={offset})...")
            url = f'https://us.edstem.org/api/courses/{COURSE_ID}/threads'
            params = {
                'limit': limit,
                'offset': offset,
                'sort': 'new' 
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                print(f"Error fetching data: {response.status_code}")
                # print(response.text)
                break
                
            json_data = response.json()
            threads = json_data.get('threads', [])
            
            if not threads:
                print("No more threads found.")
                break
                
            all_threads.extend(threads)
            print(f"  Got {len(threads)} threads. Total: {len(all_threads)}")
            
            offset += len(threads)
            page_num += 1
            
            # Simple rate limiting or check to avoid infinite loops
            if len(threads) < limit:
                print("Reached end of list.")
                break
            
            time.sleep(0.5) # Be nice to the API

        print(f"Finished scraping. Total threads: {len(all_threads)}")
        
        data = {
            "status": "success",
            "course_id": COURSE_ID,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "post_count": len(all_threads),
            "posts": all_threads
        }

        output_path = os.path.join(os.path.dirname(__file__), '../client/data.json')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {os.path.abspath(output_path)}")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
