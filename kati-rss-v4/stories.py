import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

def scrape_article_text(url):
    """Fetch the article text from a given URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from common article tags
        paragraphs = soup.find_all('p')
        article_text = ' '.join(p.get_text() for p in paragraphs)
        
        return article_text.strip()
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

def update_csv_with_article_text(input_csv, output_csv):
    """Reads a CSV file, scrapes article text, and writes the updated CSV."""
    df = pd.read_csv(input_csv)
    
    if 'Link' not in df.columns:
        print("Error: No 'Link' column found in the CSV file.")
        return
    
    article_texts = []
    total_articles = len(df)
    
    for index, link in enumerate(df['Link'], start=1):
        print(f"Fetching article {index} of {total_articles}")
        article_texts.append(scrape_article_text(link))
        time.sleep(5)  # Wait 5 seconds between requests
    
    df['Article Text'] = article_texts
    
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"Updated CSV saved to {output_csv}")

if __name__ == "__main__":
    input_file = "categorized_news_stories.csv"
    output_file = "updated_categorized_news_stories.csv"
    update_csv_with_article_text(input_file, output_file)
