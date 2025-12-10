import os
import json
import argparse
import time
from typing import List, Optional, Literal
from google import genai
from pydantic import BaseModel, Field

# --- CONFIGURATION ---
API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY")
client = genai.Client(api_key=API_KEY)

CATEGORIES = Literal[
    "Interactive AI Tutors",
    "Visualizations and Simulations",
    "AI for Debugging & Misconceptions Analysis",
    "Practice Problems, Quizzes & Exam Prep",
    "Note-taking & Knowledge Organization",
    "Research Paper Analysis"
]

# --- 1. DATA MODEL ---
class EnrichedPostData(BaseModel):
    post_summary: str = Field(description="A concise summary of the post within 25 words.")
    post_category: CATEGORIES = Field(description="The category that best fits the post.")
    primary_app_link: List[str] = Field(description="Main website url if the user has developed a webapp or any primary link of the post.")
    attachments: List[str] = Field(description="any url that has https://static.us.edusercontent.com in it. these are files user uploaded.")
    body_links: List[str] = Field(description="any other links that are not attachments or primary app link.")

# --- 2. THE EXTRACTOR ---
def enrich_post(post: dict) -> EnrichedPostData:
    content_to_analyze = {
        "title": post.get("project_title", ""),
        "content_xml": post.get("content_xml", "")
    }
    
    prompt = f"""
    Analyze the following EdStem post and extract the required information.
    
    POST DATA:
    {json.dumps(content_to_analyze, ensure_ascii=False)}
    """
    
    max_retries = 3
    base_delay = 60
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
        model="gemini-2.5-flash", 
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": EnrichedPostData,
                },
            )
            return response.parsed
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < max_retries - 1:
                    print(f"Rate limit hit for post {post.get('guid')}. Sleeping for {base_delay} seconds before retry {attempt + 1}/{max_retries}...")
                    time.sleep(base_delay)
                    continue
            
            print(f"Error enriching post {post.get('guid')}: {e}")
            return None
    return None

# --- 3. EXECUTION ---
def main():
    parser = argparse.ArgumentParser(description="Enrich posts with Gemini.")
    parser.add_argument("--limit", type=int, help="Limit number of posts to process (for testing).")
    args = parser.parse_args()

    input_file = '/Users/kithminiherath/Desktop/cs182-ec-website/client/filtered_data.json'
    output_file = '/Users/kithminiherath/Desktop/cs182-ec-website/client/categorized_data.json'

    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file {input_file} not found.")
        return

    posts = data.get('posts', [])
    if args.limit:
        posts = posts[:args.limit]
        print(f"Limiting to first {args.limit} posts.")

    enriched_posts = []
    
    print(f"Processing {len(posts)} posts...")
    
    for i, post in enumerate(posts):
        print(f"[{i+1}/{len(posts)}] Processing {post.get('guid')}...")
        
        enrichment = enrich_post(post)
        
        if enrichment:
            new_post = {
                "guid": post.get("guid"),
                "author": post.get("author"),
                "project_title": post.get("project_title"),
                "post_body": post.get("post_body"),
                "created_at": post.get("created_at"),
                "content_xml": post.get("content_xml"),
                "post_summary": enrichment.post_summary,
                "post_category": enrichment.post_category,
                "primary_app_link": enrichment.primary_app_link,
                "body_links": enrichment.body_links,
                "attachments": enrichment.attachments,
            }
            enriched_posts.append(new_post)
        else:
            print(f"Skipping post {post.get('guid')} due to error.")
            # Optionally keep original post or handle differently
        
        time.sleep(7.0) # Rate limit strict: 10 RPM = 1 request every 6s

    output_data = {
        "status": data.get("status"),
        "course_id": data.get("course_id"),
        "scraped_at": data.get("scraped_at"),
        "post_count": len(enriched_posts),
        "posts": enriched_posts
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=4)
    
    print(f"Saved enriched data to {output_file}")

if __name__ == "__main__":
    main()