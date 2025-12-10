import os
import json
import requests
from dotenv import load_dotenv
import sys
import time
import re

COURSE_ID = 84647 # CS182 / EECS182

def extract_links(content_xml):
    if not content_xml:
        return []
    # Simple regex to find hrefs in xml content
    return re.findall(r'href="([^"]+)"', content_xml)

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
    user_map = {} # id -> name
    
    limit = 30
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
                break
                
            json_data = response.json()
            threads = json_data.get('threads', [])
            users = json_data.get('users', [])
            
            # Update user map
            for u in users:
                user_id = u.get('id')
                name = u.get('name')
                if user_id and name:
                    user_map[user_id] = name
            
            if not threads:
                print("No more threads found.")
                break
                
            all_threads.extend(threads)
            print(f"  Got {len(threads)} threads. Total: {len(all_threads)}")
            
            offset += len(threads)
            page_num += 1
            
            if len(threads) < limit:
                print("Reached end of list.")
                break
            
            time.sleep(0.5)

        print(f"Finished scraping. Processing {len(all_threads)} threads...")
        
        processed_posts = []
        for thread in all_threads:
            # Map valid fields as requested
            
            # Author
            user_id = thread.get('user_id')
            author_name = user_map.get(user_id, "Unknown User")
            
            # Links
            content = thread.get('content', '')
            links = extract_links(content)
            
            # Attachments (EdStem usually puts file info in 'media' or 'files')
            # Check for generic 'files' or 'media' list
            attachments = []
            if 'media' in thread and thread['media']:
                # media objects usually have 'url' or 'key'
                 attachments.extend(thread['media'])
            if 'files' in thread:
                 attachments.extend(thread['files'])
            
            post_obj = {
                "guid": thread.get('id'),                # Requested: guid
                "author": author_name,                   # Requested: author
                "project_title": thread.get('title'),    # Requested: project title
                "post_body": thread.get('document'),     # Requested: post body
                "content_xml": content,                  # Keeping original just in case
                "links": links,                          # Requested: links
                "attachments": attachments,              # Requested: attachments
                
                # Extra metadata
                "created_at": thread.get('created_at'),
                "category": thread.get('category')
            }
            processed_posts.append(post_obj)

        data = {
            "status": "success",
            "course_id": COURSE_ID,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "post_count": len(processed_posts),
            "posts": processed_posts
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
