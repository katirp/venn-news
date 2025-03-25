import os
import sys
import news_story_categorizer
from dotenv import load_dotenv
import re

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for OpenAI API key
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if not openai_key:
        print("OpenAI API key not found in .env file or environment variables.")
        print("You can set it now, add it to the .env file, or enter 'skip' to run without OpenAI:")
        key_input = input("Enter your OpenAI API key: ")
        
        if key_input.lower() == 'skip':
            use_openai = False
            api_key = None
        else:
            api_key = key_input
            use_openai = True
            
            # Offer to save the key to .env file
            save_to_env = input("Would you like to save this API key to your .env file? (y/n): ")
            if save_to_env.lower() == 'y':
                try:
                    with open('.env', 'r') as env_file:
                        env_content = env_file.read()
                    
                    # Check if OPENAI_API_KEY is already in the file
                    if 'OPENAI_API_KEY=' in env_content:
                        # Replace the existing key
                        new_content = re.sub(r'OPENAI_API_KEY=.*', f'OPENAI_API_KEY={api_key}', env_content)
                    else:
                        # Add the key if not found
                        new_content = env_content + f'\nOPENAI_API_KEY={api_key}\n'
                    
                    with open('.env', 'w') as env_file:
                        env_file.write(new_content)
                    
                    print("API key saved to .env file successfully!")
                except Exception as e:
                    print(f"Error saving API key to .env file: {e}")
    else:
        print("OpenAI API key found in .env file or environment variables.")
        api_key = openai_key
        use_openai = True
    
    # Input and output files
    input_file = "news_articles.csv"
    output_file = "categorized_news_stories.csv"
    
    # Run categorization
    print(f"Starting news story categorization {' with OpenAI' if use_openai else ' without OpenAI'}")
    num_stories, num_articles = news_story_categorizer.categorize_news_stories(
        input_file, 
        output_file,
        use_openai=use_openai,
        api_key=api_key
    )
    
    print(f"Success! {num_stories} news stories with {num_articles} articles saved to {output_file}")
    
    # Display the top stories
    print("\nTop story headlines:")
    import pandas as pd
    df = pd.read_csv(output_file)
    for headline in sorted(set(df['Story'])):
        print(f"- {headline}")

if __name__ == "__main__":
    main() 