import feedparser
import re
from flask import Flask, render_template, request

app = Flask(__name__)

RSS_FEEDS = {
    'RT news': 'https://www.rt.com/rss/',
   'Xinhua news': 'http://www.xinhuanet.com/english/rss/worldrss.xml',
    'BBC': 'https://feeds.bbci.co.uk/news/world/rss.xml',
    'Fox News': 'https://moxie.foxnews.com/google-publisher/latest.xml',
    'Fox News': 'https://moxie.foxnews.com/google-publisher/world.xml',
    'ABC News': 'https://abcnews.go.com/abcnews/topstories',
    'ABC News': 'https://abcnews.go.com/abcnews/internationalheadlines',
    'CBS News': 'https://www.cbsnews.com/latest/rss/main',
    'CBS News': 'https://www.cbsnews.com/latest/rss/world',
    'RedState': 'https://redstate.com/feed/',
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
    
    # Extract text from content (handling HTML or text)
    text = content[0].value if isinstance(content, list) else content
    text = text.strip()  # Remove leading/trailing whitespaces
    
    # Remove HTML tags
    text = remove_html_tags(text)
    
    words = text.split()  # Split the text into words
    
    # Get the first 100 words
    first_100_words = ' '.join(words[:100])
    return first_100_words

@app.route('/')
def index():
    articles = []
    for source, feed in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        for entry in parsed_feed.entries:
            content = entry.get('content', entry.get('summary', ''))  # Fetch content or summary
            first_100_words = get_first_100_words(content)
            articles.append((source, entry, first_100_words))

    # Sort articles by published date
    articles = sorted(articles, key=lambda x: x[1].published_parsed, reverse=True)

    page = request.args.get('page', 1, type=int)
    per_page = 100
    total_articles = len(articles)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_articles = articles[start:end]

    return render_template('index.html', articles=paginated_articles, page=page, total_pages=total_articles // per_page + 1)

@app.route('/search')
def search():
    query = request.args.get('q')

    articles = []
    for source, feed in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        for entry in parsed_feed.entries:
            content = entry.get('content', entry.get('summary', ''))  # Fetch content or summary
            first_100_words = get_first_100_words(content)
            articles.append((source, entry, first_100_words))

    results = [article for article in articles if query.lower() in article[1].title.lower()]

    return render_template('search_results.html', articles=results, query=query)

if __name__ == "__main__":
    app.run(debug=True)
