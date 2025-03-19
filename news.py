from requests_html import HTMLSession

session = HTMLSession()
url = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen"

r = session.get(url)
r.html.render(sleep=1, scrolldown=0)

grouped_articles = {} # dictionary where the items are lists of dictionaries

topics = r.html.find(".PO9Zff.Ccj79.kUVvS") # selects the topic html element

for topic in topics:
    article_list = []
    articles = topic.find("article") # selects the article class html blocks within the topic element
    if not articles:
        print("No articles found in topic: ", topic)
        continue
    for block in articles:
        article = block.find(".gPFEn", first=True) # selects the individual article element which includes the title and link
        if not article: 
            print("No article found in block: ", block)
            continue
        article_dic = {
            "title": article.text,
            "link": article.absolute_links
        }
        article_list.append(article_dic)
    if article_list:
        grouped_articles[article_list[0]["title"]] = article_list # uses the first article title as the topic

print(len(grouped_articles))
keys = list(grouped_articles.keys())
for key in keys:
    print(key)
print(grouped_articles[keys[0]])