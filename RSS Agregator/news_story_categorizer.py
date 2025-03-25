import pandas as pd
import csv
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from collections import Counter
import re
import string

# Download necessary NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

def load_articles(csv_file):
    """Load articles from CSV file."""
    df = pd.read_csv(csv_file)
    return df

def preprocess_text(text):
    """Clean and preprocess text."""
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def generate_article_features(df):
    """Generate features for each article by combining title and content."""
    features = []
    for _, row in df.iterrows():
        title = preprocess_text(row['Title'])
        content = preprocess_text(row['Content'])
        
        # Combine title (weighted higher) with content
        combined = title + " " + title + " " + title + " " + content
        features.append(combined)
        
    return features

def cluster_articles(features, threshold=0.3):
    """Cluster articles based on content similarity."""
    # Create TF-IDF vectors
    stop_words = set(stopwords.words('english'))
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words=stop_words,
        ngram_range=(1, 3)  # Use unigrams, bigrams, and trigrams
    )
    
    tfidf_matrix = vectorizer.fit_transform(features)
    
    # Calculate cosine similarity between all pairs of articles
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Initialize article clusters
    n_articles = len(features)
    clusters = {i: [i] for i in range(n_articles)}
    cluster_id = 0
    
    # Merge clusters based on similarity
    merged = set()
    for i in range(n_articles):
        if i in merged:
            continue
            
        for j in range(i + 1, n_articles):
            if j in merged:
                continue
                
            if similarity_matrix[i, j] > threshold:
                # Merge clusters
                current_cluster = clusters[i]
                other_cluster = clusters[j]
                
                clusters[i] = current_cluster + other_cluster
                merged.add(j)
                del clusters[j]
    
    # Renumber the clusters
    final_clusters = {}
    for i, cluster in enumerate(clusters.values()):
        final_clusters[i] = cluster
        
    return final_clusters

def generate_story_headlines(df, clusters):
    """Generate headlines for each news story cluster."""
    story_headlines = {}
    
    for cluster_id, article_indices in clusters.items():
        if len(article_indices) < 1:
            continue
            
        # Extract all words from titles in this cluster
        all_title_words = ""
        for idx in article_indices:
            title = df.iloc[idx]['Title']
            all_title_words += " " + preprocess_text(title)
        
        # Count word frequency (excluding stopwords)
        stop_words = stopwords.words('english')
        words = [word for word in all_title_words.split() if word not in stop_words and len(word) > 2]
        word_counts = Counter(words)
        
        # Get the most common words
        top_words = [word for word, _ in word_counts.most_common(5)]
        
        # Use the representative title as the story headline
        if article_indices:
            # Get first article's title as base
            headline = df.iloc[article_indices[0]]['Title']
            
            # Alternatively, construct a headline from common words
            if len(top_words) >= 3:
                constructed_headline = " ".join(top_words[:5]).capitalize()
                
                # Use the constructed headline if it's more informative
                if len(constructed_headline.split()) >= 3:
                    headline = constructed_headline
                    
            story_headlines[cluster_id] = headline
            
    return story_headlines

def categorize_news_stories(input_csv, output_csv, min_articles_per_story=2):
    """
    Categorize news articles into news stories and save the top 10 stories to a CSV file.
    
    Args:
        input_csv: Path to the input CSV file containing articles
        output_csv: Path to the output CSV file for categorized stories
        min_articles_per_story: Minimum number of articles required for a valid news story
    """
    # Load articles
    df = load_articles(input_csv)
    
    # Generate features for clustering
    features = generate_article_features(df)
    
    # Cluster articles
    clusters = cluster_articles(features, threshold=0.25)
    
    # Filter clusters with minimum article count
    valid_clusters = {k: v for k, v in clusters.items() if len(v) >= min_articles_per_story}
    
    # Generate headlines for each story
    story_headlines = generate_story_headlines(df, valid_clusters)
    
    # Sort stories by number of articles (descending)
    sorted_stories = sorted(
        valid_clusters.items(), 
        key=lambda x: len(x[1]), 
        reverse=True
    )
    
    # Select top 10 stories (or fewer if there aren't 10)
    top_stories = sorted_stories[:10]
    
    # Write to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Story', 'Number of Articles', 'Source', 'Title', 'Published Date', 'Link'])
        
        for i, (cluster_id, article_indices) in enumerate(top_stories):
            story_headline = story_headlines.get(cluster_id, f"Story {i+1}")
            
            for idx in article_indices:
                article = df.iloc[idx]
                writer.writerow([
                    story_headline,
                    len(article_indices),
                    article['Source'],
                    article['Title'],
                    article['Published Date'],
                    article['Link']
                ])
    
    print(f"Categorized {sum(len(indices) for _, indices in top_stories)} articles into {len(top_stories)} news stories.")
    print(f"Results saved to {output_csv}")
    
    # Return the number of stories and articles processed
    return len(top_stories), sum(len(indices) for _, indices in top_stories)

if __name__ == "__main__":
    input_file = "news_articles.csv"
    output_file = "categorized_news_stories.csv"
    
    num_stories, num_articles = categorize_news_stories(input_file, output_file)
    print(f"Top {num_stories} news stories containing {num_articles} articles have been saved to {output_file}") 