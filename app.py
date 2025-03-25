import feedparser
import re
import time
import csv
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for
import newspaper
from news_story_categorizer import categorize_news_stories
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

RSS_FEEDS = {
    'RT news': 'https://www.rt.com/rss/',
    'Newsmax': 'https://www.newsmax.com/rss/Newsfront/16/',
    'BBC': 'https://feeds.bbci.co.uk/news/world/rss.xml',
    'Fox News': 'https://moxie.foxnews.com/google-publisher/latest.xml',
    'Fox News': 'https://moxie.foxnews.com/google-publisher/world.xml',
    'ABC News': 'https://abcnews.go.com/abcnews/topstories',
    'ABC News': 'https://abcnews.go.com/abcnews/internationalheadlines',
    'CBS News': 'https://www.cbsnews.com/latest/rss/main',
    'CBS News': 'https://www.cbsnews.com/latest/rss/world',
    'Huffington Post': 'https://chaski.huffpost.com/us/auto/vertical/us-news'
}

# Function to remove HTML tags from content
def remove_html_tags(content):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', content)

# Function to get the first 100 words from the article content
def get_first_100_words(content):
    if not content:
        return ''
    
    text = content[0].value if isinstance(content, list) else content
    text = text.strip()  # Remove leading/trailing whitespaces
    
    # Remove HTML tags
    text = remove_html_tags(text)
    
    words = text.split()  # Split the text into words
    
    # Get the first 100 words
    first_100_words = ' '.join(words[:100])
    return first_100_words

# Function to filter articles published in the last 48 hours
def is_recent(entry):
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        entry_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
        return entry_time >= datetime.now() - timedelta(hours=48)
    return False  # Exclude if no published date is available

# Function to save articles to a CSV file
def save_to_csv(articles, filename="news_articles.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "Title", "Published Date", "Content", "Link"])  # Header

        for source, article, content in articles:
            writer.writerow([source, article.title, article.get("published", "N/A"), content, article.link])

@app.route('/')
def index():
    # Redirect the root URL to the stories page
    return redirect(url_for('news_stories'))

@app.route('/all-articles')
def all_articles():
    articles = []
    for source, feed in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        for entry in parsed_feed.entries:
            if not is_recent(entry):  # Filter out old articles
                continue

            description = entry.get('description', '')  
            summary = entry.get('summary', '')  
            content = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
            text = content or summary or description  
            first_100_words = get_first_100_words(text)

            articles.append((source, entry, first_100_words))

    print(articles[0][1].link)
    test_article = newspaper.Article(articles[0][1].link)
    test_article.download()
    test_article.parse()
    print(test_article.title)
    print(test_article.publish_date)
    print(test_article.text[:10000])
    print()
    # Sort articles by published date
    articles = sorted(articles, key=lambda x: x[1].published_parsed, reverse=True)

    # Save articles to CSV file
    save_to_csv(articles)

    page = request.args.get('page', 1, type=int)
    per_page = 1000
    total_articles = len(articles)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_articles = articles[start:end]

    return render_template('index.html', articles=paginated_articles, page=page, total_pages=max(1, total_articles // per_page + 1))

@app.route('/search')
def search():
    query = request.args.get('q')

    articles = []
    for source, feed in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        for entry in parsed_feed.entries:
            if not is_recent(entry):  # Filter only recent articles
                continue

            description = entry.get('description', '')  
            summary = entry.get('summary', '')  
            content = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
            text = content or summary or description  
            first_100_words = get_first_100_words(text)

            articles.append((source, entry, first_100_words))

    results = [article for article in articles if query.lower() in article[1].title.lower()]

    return render_template('search_results.html', articles=results, query=query)

@app.route('/stories')
def news_stories():
    # Check if OpenAI should be used (default to true)
    use_openai = request.args.get('openai', 'true').lower() == 'true'
    
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # Categorize news stories and save to CSV
    input_file = "news_articles.csv"
    output_file = "categorized_news_stories.csv"
    
    # Run the categorization
    categorize_news_stories(input_file, output_file, use_openai=use_openai, api_key=api_key)
    
    # Read the categorized stories
    categorized_df = pd.read_csv(output_file)
    
    # Group by story
    story_groups = categorized_df.groupby('Story')
    
    # Prepare data for template
    stories = []
    for story_name, group in story_groups:
        articles = []
        num_articles = group['Number of Articles'].iloc[0]  # All rows have same count
        
        for _, row in group.iterrows():
            articles.append({
                'source': row['Source'],
                'title': row['Title'],
                'date': row['Published Date'],
                'link': row['Link']
            })
        
        stories.append({
            'headline': story_name,
            'count': num_articles,
            'articles': articles
        })
    
    # Sort stories by article count (descending)
    stories.sort(key=lambda x: x['count'], reverse=True)
    
    return render_template('stories.html', stories=stories)

if __name__ == "__main__":
    app.run(debug=True)
