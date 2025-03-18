import newspaper
import time

site = newspaper.build('https://www.cnn.com/', memoize_articles=False,browser_user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

print("number of articles: ", site.size())

for i in range(site.size()):
    article = site.articles[i]
    time.sleep(2)
    article.download()
    article.parse()
    print(article.title)
    print(article.publish_date)
    print(article.text[:100])
    print()

