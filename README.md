# venn-news
# Problem

News sites are biased. News sites have too much information on them. 

Attempts to solve bias:

- Particle
- GroundNews

Attemps to solve complexity:

- Drudge Report

Problem with apps that try to solve bias: they are BORING!! They are lists of dry facts. Not interesting to read at all, and so they fail to gain traction and a committed user base. The Drudge Report, on the other hand, is highly sensationalist and as a result has been in business for decades. But it is not a complete and unbiased view of the news.

<aside>
💡

There are no competitiors who are able to present an **unbiased, simplified, and interesting** news page.

</aside>

(Based on our current research)

# Solution

**Venn News** displays the top 20 trending topics each day on a simple homepage. Clicking on a topic will bring the user to an AI-generated summary of where different sources agree and where they disagree. At the bottom, links to the different articles will be displayed. The summary will be generated in a tone that is engaging and fun to read. Users will get an unbiased overview of the day’s news. It is the ideal starting point for avid news readers to begin their day, or the one-stop-shop for casual news readers.

# High-Level Process

1. Each morning at XX:00 AM, go to a preconfigured list of top news websites and automatically scrape the headlines. deposit in a list with links to each of the articles and a unique ID for each record. There should likely be several hundred headlines
2. Using API, prompt ChatGPT “using the list of headlines, create a list of the top 10 news topics and provide unique IDs of articles that fit into each topic”
3. For each of the top 20 news topics that day, prompt ChatGPT “using the web links provided for each news topic, summarize all news articles into one. Tell me where they all agree and also tell me what the key differences are and which are making claims that contradict others.”
4. Take these results, and put them in a very simple webpage that makes it easy for viewers to see the top 20 categories. Users can click any of the topics and are taken to a simple page. 

# Tech Stack

### **Frontend:**

- **Next.js** – Offers server-side rendering (SSR) for better performance and SEO.

### **Backend:**

- **FastAPI (Python) or Node.js with Express.js** – FastAPI is great for handling API calls and integrates well with AI-based processing. If you prefer JavaScript/TypeScript, use Node.js.
- **PostgreSQL** – A reliable SQL database to store articles and metadata.
- **Newspaper4k/Selenium** – For web scraping.
- **GPT-4/Gemini** – For summarization and analysis.

<img width="660" alt="image" src="https://github.com/user-attachments/assets/aa1ad5fd-45f4-473a-b6a9-8e72345142fd" />

scrape articles

How to determine what 20 articles to feature every day? 

Approach 1

- find a way to scrape articles by most read in the past 24 hrs

Approach 2

- scrape the headlines on a news frontpage into a list. put into one big list
    - also scrape the first 50-100 words of each article, as the headline is not enough information for chatgpt to determine what the article is about
- feed that list to chatgpt and have it group the articles into topics. each topic contains the links to all related articles.
    - Question: is chatgpt’s context window large enough for this task? might need to use an ai with a larger context window like gemini
- the 20 topics displayed on final webpage are the topics with the most articles linked to them. The idea is that topics that are written about the most extensively across news sites are the most important.

now we have a list of 20 topics, each topic paired with links to its articles 

create agree/disagree summaries

Approach

- Feed each topic and list of articles into chatgpt, prompting it to generate sections where the news sites agree/disagree

Display topics and summaries on webpage

- front page is a list of topics. when you click on one, it opens a page with the agree/disagree summary and links to the topics.
