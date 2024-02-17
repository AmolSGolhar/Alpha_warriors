from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from newsapi import NewsApiClient
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

app = Flask(__name__)

def fetch_news_suggestions(title):
    newsapi = NewsApiClient(api_key='2dd5305e4fd041e099342d1631da2d40')
    news_articles = newsapi.get_everything(q=title, language='en', sort_by='relevancy')
    news_urls = [article['url'] for article in news_articles['articles'][:5]]
    return news_urls

def extract_content_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = ' '.join([p.text for p in soup.find_all('p')])
            return text
        else:
            print("Failed to fetch content from the URL.")
            return None
    except Exception as e:
        print("An error occurred:", e)
        return None
    
def analyze_news_articles(statement, news_urls):
    nltk.download('punkt')
    nltk.download('stopwords')

    statement_tokens = word_tokenize(statement.lower())
    stop_words = set(stopwords.words('english'))
    support_counter = 0
    refute_counter = 0

    for url in news_urls:
        article_content = extract_content_from_url(url)
        if article_content:
            article_tokens = word_tokenize(article_content.lower())
            filtered_article_tokens = [word for word in article_tokens if word not in stop_words]
            statement_in_article_count = sum(1 for word in statement_tokens if word in filtered_article_tokens)
            if statement_in_article_count > len(statement_tokens) / 2:
                support_counter += 1
            elif statement_in_article_count > 0:
                refute_counter += 1

    if support_counter > refute_counter:
        return "True"
    elif refute_counter > support_counter:
        return "False"
    else:
        return "Unknown"

def check_statement(statement, api_key):
    url = f'https://factchecktools.googleapis.com/v1alpha1/claims:search?query={statement}&key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        if 'claims' in result and result['claims']:
            claim = result['claims'][0]
            verdict = claim['text']
            dict_result = {}
            if 'claimReview' in claim:
                review = claim['claimReview'][0]
                dict_result = {"Claim Statement": statement,"Title" : review['title'], "publisher" : review['publisher']['name'], "Claim" : review['textualRating']}
                if 'reviewDate' in review:
                    dict_result['Date'] = review['reviewDate']
                news_suggestions = fetch_news_suggestions(statement)
                if news_suggestions:
                    dict_result['News Suggestions'] = news_suggestions
                    verdict = analyze_news_articles(statement, news_suggestions)
                    dict_result['Verdict given on website'] = verdict
                else:
                    dict_result['News Suggestions'] = "No suggestions"
            return dict_result
        else:
            return {"Claim Statement": statement,'Response':"No fact-checking information found for the statement.", "Verdict": "Unknown"}
    else:
        return {"Claim Statement": statement, 'Response': "Failed to fetch fact-checking information.", "Verdict": "Unknown"}


@app.route('/')
def home():
    return render_template('index.html')
    
@app.route('/result', methods=['POST'])
def result():
    fact = request.form['fact']
    result = check_statement(fact, 'AIzaSyBlVuzLCAq7awLh21EqOiF8f6rV1ll_e_E')
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
