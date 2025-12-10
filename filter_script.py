import json
import difflib

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def get_min_substring_distance(text, phrase):
    """
    Returns the minimum edit distance between 'phrase' and any substring of 'text'.
    """
    if not text:
        return float('inf')
        
    text = ' '.join(text.lower().split())
    phrase = ' '.join(phrase.lower().split())
    
    n_text = len(text)
    n_phrase = len(phrase)
    
    if n_phrase > n_text + 5: # Optimization: simple length check
        return n_phrase # roughly
        
    min_dist = float('inf')
    
    # Check substrings of length close to len(phrase)
    # Range of window sizes to check roughly covers insertions/deletions
    start_len = max(1, n_phrase - 4)
    end_len = min(n_text, n_phrase + 4)
    
    for length in range(start_len, end_len + 1):
        for i in range(n_text - length + 1):
            window = text[i : i + length]
            dist = levenshtein_distance(window, phrase)
            if dist < min_dist:
                min_dist = dist
                if min_dist == 0: return 0
                
    return min_dist

input_file = '/Users/kithminiherath/Desktop/cs182-ec-website/client/data.json'
output_file = '/Users/kithminiherath/Desktop/cs182-ec-website/client/filtered_data.json'

try:
    with open(input_file, 'r') as f:
        data = json.load(f)

    if 'posts' not in data:
        print("Error: 'posts' key not found in data")
        exit(1)

    original_count = len(data['posts'])
    filtered_posts = []
    
    categories = {
        'a': "special participation a",
        'b': "special participation b",
        'c': "special participation c",
        'd': "special participation d",
        'e': "special participation e"
    }
    
    for post in data['posts']:
        title = post.get('project_title', '')
        if not title:
            continue
            
        # Calculate distance to all categories
        distances = {}
        for cat_key, phrase in categories.items():
            distances[cat_key] = get_min_substring_distance(title, phrase)
            
        dist_e = distances['e']
        
        # Criteria:
        # 1. Distance to E must be within tolerance (e.g. 4)
        # 2. Distance to E must be strictly better than A, B, C, D
        #    This separates "Special Participation A" (dist_e=1, dist_a=0) from "Special Participation E" (dist_e=0, dist_a=1)
        
        is_closest_to_e = True
        for cat_key in ['a', 'b', 'c', 'd']:
            if distances[cat_key] <= dist_e:
                is_closest_to_e = False
                break
        
        if dist_e <= 4 and is_closest_to_e:
            filtered_posts.append(post)

    data['posts'] = filtered_posts
    if 'post_count' in data:
        data['post_count'] = len(filtered_posts)

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Successfully filtered data with refined fuzzy matching (disambiguating categories). Kept {len(filtered_posts)} out of {original_count} posts.")
    print(f"Saved to {output_file}")

except Exception as e:
    print(f"An error occurred: {e}")
