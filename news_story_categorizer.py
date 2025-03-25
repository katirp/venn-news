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
import os
import openai
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Download necessary NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# Set up OpenAI API key from environment variables
# The API key will be loaded from .env file

def generate_openai_headline(article_titles, top_words, api_key=None):
    """
    Generate an engaging headline using OpenAI's API based on article titles and top words.
    
    Args:
        article_titles: List of article titles in the cluster
        top_words: List of most common words across all titles
        api_key: OpenAI API key (optional)
    
    Returns:
        A string containing the AI-generated headline
    """
    # Use provided API key or fall back to environment variable
    if api_key:
        openai.api_key = api_key
    else:
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        
    if not openai.api_key:
        print("Warning: No OpenAI API key found. Skipping OpenAI headline generation.")
        return None
    
    try:
        # Create a prompt for headline generation
        prompt = f"""Generate a compelling, clickworthy news headline that captures the essence of these related news articles. 
Write it in the style of The Drudge Report. 

Articles:
{'\n'.join('- ' + title for title in article_titles[:5])}

Top keywords: {', '.join(top_words[:10])}

Generate ONE engaging headline (max 12 words)."
"""

        # Make API call
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skilled news editor who creates engaging headlines."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        # Extract and clean headline
        headline = response.choices[0].message.content.strip()
        
        # Remove quotes if present
        headline = headline.strip('"\'')
        
        return headline
    
    except Exception as e:
        print(f"Error generating OpenAI headline: {e}")
        return None

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
        stop_words='english',
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

def generate_story_headlines(df, clusters, use_openai=True, api_key=None):
    """Generate engaging headlines for each news story cluster."""
    story_headlines = {}
    
    for cluster_id, article_indices in clusters.items():
        if len(article_indices) < 1:
            continue
            
        # Get all titles and their processed forms
        all_titles = []
        processed_titles = []
        for idx in article_indices:
            title = df.iloc[idx]['Title']
            all_titles.append(title)
            processed_titles.append(preprocess_text(title))
        
        # Combine all processed titles to find common words
        all_words = " ".join(processed_titles)
        
        # Get most common words (excluding stopwords)
        stop_words = stopwords.words('english')
        words = [word for word in all_words.split() if word not in stop_words and len(word) > 2]
        word_counts = Counter(words)
        
        # Get the most common words
        top_words = [word for word, _ in word_counts.most_common(10)]
        
        # Try OpenAI headline generation first if enabled
        headline = None
        if use_openai and len(article_indices) >= 2:
            headline = generate_openai_headline(all_titles, top_words, api_key)
            
            # Add a small delay to avoid hitting rate limits
            time.sleep(0.5)
        
        # If OpenAI failed or is disabled, fall back to our algorithm
        if not headline:
            # Find the title that contains the most common words
            best_title_idx = 0
            best_title_score = 0
            
            for i, title in enumerate(processed_titles):
                # Count how many top words appear in this title
                title_words = set(title.split())
                score = sum(1 for word in top_words if word in title_words)
                
                if score > best_title_score:
                    best_title_score = score
                    best_title_idx = i
            
            # Get the best title as our base
            headline = all_titles[best_title_idx]
        
        story_headlines[cluster_id] = headline
            
    return story_headlines

def categorize_news_stories(input_csv, output_csv, min_articles_per_story=2, use_openai=True, api_key=None):
    """
    Categorize news articles into news stories and save the top 20 stories to a CSV file.
    
    Args:
        input_csv: Path to the input CSV file containing articles
        output_csv: Path to the output CSV file for categorized stories
        min_articles_per_story: Minimum number of articles required for a valid news story
        use_openai: Whether to use OpenAI API for headline generation
        api_key: OpenAI API key (optional)
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
    story_headlines = generate_story_headlines(df, valid_clusters, use_openai=use_openai, api_key=api_key)
    
    # Sort stories by number of articles (descending)
    sorted_stories = sorted(
        valid_clusters.items(), 
        key=lambda x: len(x[1]), 
        reverse=True
    )
    
    # Select top 20 stories (or fewer if there aren't 20)
    top_stories = sorted_stories[:20]
    
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