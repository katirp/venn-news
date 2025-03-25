import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter

# Download stopwords if not already present
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Load the CSV file
csv_file = "news_articles.csv"  # Ensure the file is in the same directory
df = pd.read_csv(csv_file)

# Ensure necessary columns exist
if 'Title' not in df.columns or 'Content' not in df.columns:
    raise ValueError("CSV file must contain 'Title' and 'Content' columns.")

# Combine title and content for analysis
df['text'] = df['Title'] + " " + df['Content']

# Remove stopwords and preprocess text
def clean_text(text):
    words = text.lower().split()  # Convert to lowercase and split into words
    words = [word for word in words if word not in stop_words]  # Remove stopwords
    return " ".join(words)

df['clean_text'] = df['text'].apply(clean_text)

# Use TF-IDF vectorization to identify key terms
vectorizer = TfidfVectorizer(max_features=500)
tfidf_matrix = vectorizer.fit_transform(df['clean_text'])

# Use KMeans clustering to group similar stories
num_clusters = 20  # Extract the top 20 most common topics
kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(tfidf_matrix)

# Count the most frequent stories
cluster_counts = Counter(df['Cluster'])
top_clusters = cluster_counts.most_common(20)

# Get top 20 news headlines based on cluster size
top_headlines = []
for cluster, _ in top_clusters:
    headline = df[df['Cluster'] == cluster]['Title'].iloc[0]  # Pick the first title in each cluster
    top_headlines.append(headline)

# Display the top 20 news headlines
print("Top 20 Trending News Headlines:")
for i, headline in enumerate(top_headlines, 1):
    print(f"{i}. {headline}")
