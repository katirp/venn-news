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

min_articles_per_storyvar=3
thresholda = 0.1
thresholdb = 0.1

# Load environment variables from .env file
load_dotenv()

# Download necessary NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# Set up OpenAI API key from environment variables

def generate_openai_headline(article_titles, top_words, api_key=None):
    if api_key:
        openai.api_key = api_key
    else:
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        
    if not openai.api_key:
        print("Warning: No OpenAI API key found. Skipping OpenAI headline generation.")
        return None
    
    try:
        prompt = (
            "Generate a compelling, clickworthy news headline that captures the essence of these related news articles. "
            "Write it in the style of The Drudge Report.\n\n"
            "Articles:\n" +
            "\n".join("- " + title for title in article_titles[:5]) +
            "\n\nTop keywords: " + ", ".join(top_words[:10]) +
            "\n\nGenerate ONE engaging headline (max 12 words)."
        )

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skilled news editor who creates engaging headlines."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        headline = response.choices[0].message.content.strip()
        
        headline = headline.strip('"\'')
        
        return headline
    
    except Exception as e:
        print(f"Error generating OpenAI headline: {e}")
        return None

def load_articles(csv_file):
    df = pd.read_csv(csv_file)
    return df

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'http\S+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def generate_article_features(df):
    features = []
    for _, row in df.iterrows():
        title = preprocess_text(row['Title'])
        content = preprocess_text(row['Content'])
        combined = title + " " + title + " " + title + " " + content
        features.append(combined)
    
    return features

def cluster_articles(features, sources, threshold=thresholdb):
    stop_words = set(stopwords.words('english'))
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 3)
    )
    
    tfidf_matrix = vectorizer.fit_transform(features)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    n_articles = len(features)
    clusters = []
    assigned = set()
    
    for i in range(n_articles):
        if i in assigned:
            continue
        
        cluster = [i]
        source_count = {sources[i]: 1}
        assigned.add(i)
        
        for j in range(i + 1, n_articles):
            if j in assigned:
                continue
            
            if similarity_matrix[i, j] > threshold:
                source_j = sources[j]
                if source_j not in source_count:
                    source_count[source_j] = 0
                
                if source_count[source_j] < 2:
                    cluster.append(j)
                    source_count[source_j] += 1
                    assigned.add(j)
        
        clusters.append(cluster)
    
    return {i: cluster for i, cluster in enumerate(clusters)}

def categorize_news_stories(input_csv, output_csv, min_articles_per_story=min_articles_per_storyvar, use_openai=True, api_key=None):
    df = load_articles(input_csv)
    features = generate_article_features(df)
    sources = df['Source'].tolist()
    
    clusters = cluster_articles(features, sources, threshold=thresholda)
    
    valid_clusters = {k: v for k, v in clusters.items() if len(v) >= min_articles_per_story}
    
    story_headlines = {cluster_id: generate_openai_headline(
    [df.iloc[idx]['Title'] for idx in article_indices],  # Article titles
    [],  # Empty top_words (modify if needed)
    api_key=api_key
) for cluster_id, article_indices in valid_clusters.items()}
    
    sorted_stories = sorted(valid_clusters.items(), key=lambda x: len(x[1]), reverse=True)
    
    top_stories = sorted_stories[:20]
    
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
    
    return len(top_stories), sum(len(indices) for _, indices in top_stories)
