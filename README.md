# CS182 EC Website

This project is a web application designed to display data scraped from EdStem. It consists of a Python-based scraper and a simple HTML/CSS/JS client.

## Project Structure

- **`client/`**: Contains the frontend code.
  - `index.html`: The main entry point for the website.
  - `style.css`: Styles for the website.
  - `script.js`: Logic to fetch and display the scraped data.
  - `data.json`, `filtered_data.json`, `categorized_data.json`: Data files in various stages of processing.
- **`scraper/`**: Contains the backend scraping logic.
  - `edpy/`: The `edpy` library used for interacting with the EdStem API.
  - `scrape.py`: The main script to fetch data.
  - `probe_api.py`, `test_import.py`: Helper and testing scripts.
  - `requirements.txt`: Python dependencies.
- **`filter_script.py`**: Utility script to fuzzy filter "Special Participation E" posts.
- **`parse_jsons.py`**: Script to categorize and summarize posts using Gemini API.
- **`cs182website.html`**: Final website html file.

**Website link:** [https://cs182-ec-website.pages.dev/](https://cs182-ec-website.pages.dev/)

## Website Design Process

### 1. Scraper Setup

Before running the website with real data, you need to scrape it. The scraper setup was inspired by [edpy](https://github.com/bachtran02/edpy.git).

1.  **Prerequisites**: Ensure you have Python installed.
2.  **Navigate to the scraper directory**:
    ```bash
    cd scraper
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure API Token**:
    - Create a file named `.env` in the `scraper/` directory.
    - Add your EdStem API token to it:
      ```
      ED_API_TOKEN=your_actual_token_here
      ```
      *(Note: Do not commit `.env` to version control).*

5.  **Run the Scraper**:
    ```bash
    python scrape.py
    ```
    - This will fetch the data and save it to `../client/data.json`.

**Development:**

- **Formatting**: Please ensure code is formatted cleanly.
- **Scraping**: The `scrape.py` script is currently set up to fetch basic info. You can modify it to fetch more specific data endpoints available in `edpy`.

### 2. Fuzzy Filtering Script

We have a utility script `filter_script.py` designed to filter posts for "Special Participation E" while handling typos and similar category names.

**Usage:**
```bash
python filter_script.py
```
This reads `client/data.json` and outputs `client/filtered_data.json`.

**How it Works:**
The script uses a **"Smart" Fuzzy Matching** approach:

1.  **Fuzzy Matching (Levenshtein Distance)**:
    - It scans the project title using a sliding window.
    - It calculates the Levenshtein edit distance between the window and "Special Participation E".
    - This allows it to catch typos like "Special Particpation E".

2.  **Category Disambiguation**:
    - A simple fuzzy match would confuse "Special Participation A" with "E" (distance of 1).
    - The script calculates the edit distance to **all** categories (A, B, C, D, E).
    - It only keeps the post if "E" is the **strictly closest** match.
    - This ensures we catch typos of "E" but correctly reject "Special Participation A/B/C/D".

### 3. Categorization Script (`parse_jsons.py`)

This script enriches the filtered posts using the **Gemini API** with Gemini-2.5-flash. It reads from `client/filtered_data.json` and generates `client/categorized_data.json`.

**Functionality:**
1.  **Summarization**: Generates a concise summary (under 25 words) for each post.
2.  **Categorization**: Classifies each post into one of the 6 defined categories (see below) based on its content.
3.  **Link Extraction**: Intelligently identifies the "Primary App Link" (e.g., a deployed web app), distinguishes "Attachments" (PDFs/files on EdStem), and separates other "Post Body Links".

**Categories:**
The categories were defined by Gemini-3 Pro upon parsing the `client/filtered_data.json` file:

1. Interactive AI Tutors
2. Visualizations and Simulations
3. AI for Debugging & Misconceptions Analysis
4. Practice Problems, Quizzes & Exam Prep
5. Note-taking & Knowledge Organization
6. Research Paper Analysis

### 4. UI Design

We used Gemini 3 Pro on antigravity to generate the website given the `client/categorized_data.json` file with minimal human intervention. We only improved a bit on the colors and visual design, while the main layout of the website seen now was completely generate by Gemini. 

For choosing the featured posts, we basically prompted Gemini to select a few posts that it thought was most aligned with the syllabus of CS182/282A, to which we attached a copy of the syllabus.

**Key Features of our website:**
1. Simple card layout for each project which includes the following fields
    - Project Title
    - 25 word summary (generated using Gemini-2.5-Flash, using the whole context)
    - Name of the student
    - Category of the project (classified using Gemini-2.5-Flash)
    - Main artifact website/link
    - More links to other attachments found in the edstem post
2. Click a card to read more about the post 
3. Filter projects by category
4. Search feature that searches the title as well as the 25 word summary so that you won't miss a project 
5. Simple static HTML page that can be hosted without any complicated backend
