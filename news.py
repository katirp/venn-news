# from requests_html import HTMLSession
# import newspaper

# session = HTMLSession()
# url = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen"

# r = session.get(url)
# r.html.render(sleep=1, scrolldown=0)

# grouped_articles = {} # dictionary where the items are lists of dictionaries

# topics = r.html.find(".PO9Zff.Ccj79.kUVvS") # selects the topic html element

# for topic in topics:
#     article_list = []
#     articles = topic.find("article") # selects the article class html blocks within the topic element
#     if not articles:
#         print("No articles found in topic: ", topic)
#         continue
#     for block in articles:
#         article = block.find(".gPFEn", first=True) # selects the individual article element which includes the title and link
#         if not article: 
#             print("No article found in block: ", block)
#             continue
#         article_dic = {
#             "title": article.text,
#             "link": article.absolute_links
#         }
#         article_list.append(article_dic)
#     if article_list:
#         grouped_articles[article_list[0]["title"]] = article_list # uses the first article title as the topic

# print(len(grouped_articles))
# keys = list(grouped_articles.keys())
# for key in keys:
#     print(key)
# print(grouped_articles[keys[0]])

# test_url = grouped_articles[keys[0]][0]["link"]
# print(test_url)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import newspaper

# Configure Chrome WebDriver
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run without opening a window
# chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")


service = Service("/opt/homebrew/bin/chromedriver")  # Update with your ChromeDriver path
driver = webdriver.Chrome(service=service, options=chrome_options)

url = "https://news.google.com/home?hl=en-US&gl=US&ceid=US:en"
driver.get(url)
time.sleep(5)  # Allow time for page to load

# article_links = driver.find_elements(By.CLASS_NAME, 'gPFEn')
article_links = driver.find_elements(By.CLASS_NAME, 'WwrzSb')
print(len(article_links))

article_links[0].click()
time.sleep(1000)

# for article in article_links:
#     print(article.text)
#     print(article.get_attribute('href'))
