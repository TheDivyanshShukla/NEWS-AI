from flask import Flask, request, jsonify
from duckduckgo_search import DDGS
from rich import print
import arrow
from flask_cors import CORS  # Import CORS

def Search(keywords, timelimit):
    news_list = []
    with DDGS() as webs_instance:
        WEBS_news_gen = webs_instance.news(
            keywords,
            region="wt-wt",
            safesearch="off",
            timelimit=timelimit,
            max_results=100
        )
        for r in WEBS_news_gen:
            r['date'] = arrow.get(r['date']).humanize()
            if r["image"]:
                print(r)
                news_list.append(r)
    return news_list

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

@app.route('/api/search', methods=['GET'])
def search():
    # Retrieve the keyword and time limit from query parameters
    keyword = request.args.get('keyword', "blinkit")
    time_limit = request.args.get('timelimit', default=0.5, type=float)
    
    # Check if keyword is provided
    if not keyword:
        return jsonify({'error': 'Keyword is required'}), 400
    
    # Get news data using the Search function
    news_data = Search(keyword, time_limit)
    
    # Return the news data as JSON
    return jsonify(news_data)

@app.route('/')
def main():
    return """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Article</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.16/dist/tailwind.min.css" rel="stylesheet">
    <style>
        body,
        html {
            min-height: 100vh;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            background-color: #1f2937;
            color: #f9fafb;
        }

        .container {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            padding: 20px;
        }

        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #1f2937;
            padding: 8px;
            box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .btn {
            margin: 0 10px;
        }
    </style>
</head>

<body>
    <div class="container mx-auto">
        <div class="flex flex-col md:flex-row gap-4 mb-4">
            <input type="text" id="keywordInput" class="px-4 py-2 border border-gray-500 rounded bg-gray-700 text-white" placeholder="Enter keyword">
            <button id="searchBtn" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Search</button>
        </div>
        <div class="flex flex-col md:flex-row gap-4">
            <img id="articleImage" src="https://th.bing.com/th/id/OIG1.4sOC2_8QeObxXmAjG633?w=1024&h=1024&rs=1&pid=ImgDetMain" alt="PlayStation 5" class="md:w-1/7 rounded" style="width: 100%;">
            <div>
                <h1 id="articleTitle" class="text-xl font-bold mb-4"></h1>
                <p id="articleBody" class="text-gray-400 mb-4"></p>
            </div>
        </div>
    </div>

    <footer class="footer">
        <a id="prevBtn" href="#" class="btn bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Prev</a>
        <a id="readMoreBtn" href="#" target="_blank" class="btn bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Read More</a>
        <a id="nextBtn" href="#" class="btn bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Next</a>
    </footer>

    <script>
        let currentIndex = 0;
        let articles = [];

        // Fetch data from server
        async function fetchData(keyword = 'politics', timeLimit = 0.5) {
            const url = `${window.location.origin}/api/search?keyword=${encodeURIComponent(keyword)}&timelimit=${timeLimit}`;
            // Fetch data from server URL
            const response = await fetch(url);

            // Check the response status
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            // Parse the JSON data from the response
            articles = await response.json();
            // Display the first article initially
            displayArticle(currentIndex);
        }

        // Display the article based on the current index
        function displayArticle(index) {
            const article = articles[index];
            if (!article) return;

            const articleImage = document.getElementById('articleImage');
            const articleTitle = document.getElementById('articleTitle');
            const articleBody = document.getElementById('articleBody');
            const readMoreBtn = document.getElementById('readMoreBtn');

            // Update the content of the article
            articleImage.src = article.image;
            articleTitle.innerText = article.title;
            articleBody.innerText = article.body;
            readMoreBtn.href = article.url;
        }

        // Event handlers for buttons
        function onPrevClick(event) {
            event.preventDefault();
            if (currentIndex > 0) {
                currentIndex--;
                displayArticle(currentIndex);
            }
        }

        function onNextClick(event) {
            event.preventDefault();
            if (currentIndex < articles.length - 1) {
                currentIndex++;
                displayArticle(currentIndex);
            }
        }

        // Event handler for search button
        function onSearchClick(event) {
            event.preventDefault();
            const keywordInput = document.getElementById('keywordInput');
            const keyword = keywordInput.value.trim();
            if (keyword) {
                fetchData(keyword);
            }
        }

        // Add event listeners to buttons
        document.getElementById('prevBtn').addEventListener('click', onPrevClick);
        document.getElementById('nextBtn').addEventListener('click', onNextClick);
        document.getElementById('searchBtn').addEventListener('click', onSearchClick);

    </script>
</body>

</html>"""

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)
