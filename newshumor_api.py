import requests
from flask import Flask, request, jsonify

# Initialize Flask App
app = Flask(__name__)

# API Keys (Replace with your actual API keys)
NEWS_API_KEY = "f74cad685e394e0c8e59b080db191e1b"  # Get from https://newsapi.org/
GROQ_API_KEY="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"
# Get from https://console.groq.com/

# API Endpoints
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
GROQ_LLM_URL = "https://api.groq.com/openai/v1/chat/completions"

def fetch_news(country="us", category="technology", q=None):
    """
    Fetches top news articles from NewsAPI.

    Args:
        country (str): Country code (e.g., "us", "pk").
        category (str): News category (e.g., "technology", "business").
        q (str): Optional search query.

    Returns:
        list: A list of news articles.
    """
    params = {
        "apiKey": NEWS_API_KEY,
        "country": country,
        "category": category,
        "q": q,
        "pageSize": 5,  # Fetch only 5 articles
    }

    try:
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data["status"] == "ok":
            return data.get("articles", [])
        else:
            return {"error": "Unexpected API response"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def transform_to_humor(news_text):
    """
    Converts a news article into a humorous version using Groq LLM API.

    Args:
        news_text (str): The original news article.

    Returns:
        str: Humorous version of the article.
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-8b-8192",  # Update model based on Groq's API documentation
        "messages": [
            {"role": "system", "content": "Rewrite this news article in a humorous way. Use funny twists and emojis."},
            {"role": "user", "content": news_text}
        ]
    }

    try:
        response = requests.post(GROQ_LLM_URL, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]  # Extract humor response
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

@app.route('/humor-news', methods=['GET'])
def humor_news():
    """
    Flask API endpoint to fetch news and transform it into humorous versions.

    Query Parameters:
        country (str): Country code (default: "us").
        category (str): News category (default: "technology").
        q (str): Optional search keyword.

    Returns:
        JSON: List of humorous news articles.
    """
    country = request.args.get("country", "us")
    category = request.args.get("category", "technology")
    q = request.args.get("q", None)

    news_articles = fetch_news(country, category, q)

    if "error" in news_articles:
        return jsonify({"status": "error", "message": news_articles["error"]}), 400

    transformed_news = []
    for article in news_articles:
        humorous_text = transform_to_humor(article["description"] or article["title"])
        transformed_news.append({
            "title": article["title"],
            "original_description": article.get("description", "No description available"),
            "humorous_description": humorous_text
        })

    return jsonify({"status": "success", "data": transformed_news})

if __name__ == '__main__':
    app.run(debug=True)
