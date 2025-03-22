import feedparser
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

@app.route('/')
def index():
    articles = []
    for source, feed in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        entries = {(source, entry) for entry in parsed_feed.entries}
        articles.extend(entries)

    articles = sorted(articles, key=lambda x: x[1].published_parsed, reverse=True)

    page = request.qrgs.get('page',1, type=int)
    per_page = 10
    total_articles = len(articles)
    start = (page-1)
    end = start + per_page
    paginated_artices = articles[start:end]

    return render_template( template_name_or_list='index.html',articles=paginated_artices, page=page, total_pages = total_articles // per_page +1)

@app.route ('/search')
def search():
    query = request.arge.get('q')

    articles = []
    for source, feed in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        entries = [(source, entry) for entry in parsed_feed.entries]
        articles.extend(entries)

    results  = [article for article in articles if query.lower() in article[1].title.lower()]

    return render_template(template_name_or_list= 'search_results.html', articles=results, query=query) 


if __name__ == "__main__":
    app.run(debug=True)