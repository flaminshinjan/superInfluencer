import requests
import os
from dotenv import load_dotenv
from urllib.parse import quote

# Load environment variables
load_dotenv()

class ContentAggregationAgent:
    def __init__(self, company_name, company_info):
        self.company_name = company_name
        self.company_info = company_info
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        self.jina_auth_token = os.getenv("JINA_AUTH_TOKEN")  # Token for Jina Scraper API
        self.openai_api_key = os.getenv("OPENAI_API_KEY")  # OpenAI API Key

    def google_search(self):
        print("Performing Google Search...")
        query = f"{self.company_name} {self.company_info}".replace(" ", "%20")
        url = f"https://google-search72.p.rapidapi.com/search?q={query}&lr=en-US&num=10"
        headers = {
            "X-Rapidapi-Key": self.rapidapi_key,
            "X-Rapidapi-Host": "google-search72.p.rapidapi.com",
        }
        response = requests.get(url, headers=headers)
        print(f"Google Search Response ({response.status_code}): {response.text[:200]}...")
        if response.status_code == 200:
            try:
                results = response.json().get("items", [])
                return [result.get("link") for result in results if result.get("link")]
            except ValueError:
                print("Error: Invalid JSON response for Google Search.")
        return []

    def scrape_url(self, url):
        print(f"Scraping URL: {url}")
        fallback_url = f"https://r.jina.ai/{quote(url)}"
        headers = {
            "Authorization": f"Bearer {self.jina_auth_token}"
        }
        response = requests.get(fallback_url, headers=headers)

        # Print raw response for debugging
        print(f"Raw Response ({response.status_code}): {response.text}")

        if response.status_code == 200:
            try:
                data = response.json()
                if "text" in data:
                    content = data.get("text", "")
                    print(f"Scraped Content for {url} (first 200 chars): {content[:200]}...")
                    return content
            except ValueError:
                print(f"Warning: Response is not valid JSON. Returning raw text content.")
                return response.text  # Fallback to raw text
        else:
            print(f"Error scraping {url}: {response.status_code}, {response.text[:200]}")
        return None

    def process_with_gpt(self, content):
        print("Processing content with GPT...")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that cleans up web content."},
                {"role": "user", "content": f"Clean and summarize the following content:\n\n{content}"}
            ],
            "temperature": 0.7
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            try:
                reply = response.json()["choices"][0]["message"]["content"]
                print(f"GPT Response (first 200 chars): {reply[:200]}...")
                return reply
            except (KeyError, ValueError):
                print("Error: Invalid GPT API response.")
        else:
            print(f"Error calling GPT API: {response.status_code}, {response.text}")
        return None

    def process_search_results(self):
        # Step 1: Perform Google Search
        search_results = self.google_search()
        print(f"Google Search Results: {search_results}")

        # Step 2: Scrape each result
        scraped_results = {}
        for url in search_results:
            scraped_content = self.scrape_url(url)
            if scraped_content:
                # Process scraped content with GPT
                cleaned_content = self.process_with_gpt(scraped_content)
                if cleaned_content:
                    scraped_results[url] = cleaned_content

        return scraped_results

    def save_to_file(self, results, file_name="cleaned_content.txt"):
        print(f"Saving cleaned content to {file_name}...")
        with open(file_name, "w", encoding="utf-8") as f:
            for url, content in results.items():
                f.write(f"URL: {url}\n")
                f.write(f"Content:\n{content}\n")
                f.write("-" * 80 + "\n")
        print(f"Saved cleaned content to {file_name}.")

if __name__ == "__main__":
    # Input company name and information
    company_name = "Share Ventures"
    company_info = "share venture capitalist firm for funding startups grow and incubate products"

    # Initialize the agent
    agent = ContentAggregationAgent(company_name, company_info)

    # Process search results and scrape them
    results = agent.process_search_results()

    # Save the results to a file
    agent.save_to_file(results)

    print("\nFinal Scraped and Cleaned Results:")
    for url, content in results.items():
        print(f"URL: {url}")
        print(f"Content: {content[:500]}...")  # Display first 500 characters
        print("\n")
