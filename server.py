from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

current_gloss = "Waiting for speech..."

# Upgraded Hackathon UI with ARASAAC Integration
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HaptiHear | Live ARASAAC Translation</title>
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            margin: 0;
            padding-top: 50px;
        }
        h1 { color: #bb86fc; font-size: 2.5rem; margin-bottom: 5px; }
        .subtitle { color: #a0a0a0; font-size: 1.2rem; margin-bottom: 50px; }
        
        /* The container that holds all the symbol cards */
        #symbol-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            max-width: 90%;
            min-height: 200px;
        }

        /* Individual Word/Pictogram Card */
        .symbol-card {
            background-color: #1e1e1e;
            border: 2px solid #333;
            border-radius: 15px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            min-width: 150px;
            min-height: 180px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            transition: transform 0.2s, border-color 0.2s;
        }
        
        .symbol-card:hover {
            transform: translateY(-5px);
            border-color: #bb86fc;
        }

        .pictogram {
            width: 120px;
            height: 120px;
            object-fit: contain;
            background-color: #ffffff; /* ARASAAC images have transparent backgrounds, white helps them pop */
            border-radius: 10px;
            padding: 5px;
            margin-bottom: 15px;
        }

        .fallback-icon {
            width: 120px;
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            color: #555;
            background-color: #2a2a2a;
            border-radius: 10px;
            margin-bottom: 15px;
        }

        .gloss-word {
            font-size: 1.5rem;
            font-weight: bold;
            letter-spacing: 1px;
            color: #bb86fc;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>HaptiHear</h1>
    <div class="subtitle">Real-Time NLP to ARASAAC Pictogram Engine</div>
    
    <div id="symbol-container">
        <div class="symbol-card"><div class="gloss-word">Listening...</div></div>
    </div>

    <script>
        let lastDisplayedText = "";

        async function fetchArasaacData(words) {
            const container = document.getElementById('symbol-container');
            container.innerHTML = ''; // Clear the board

            // Fetch all pictograms concurrently for a smooth UI update
            const symbolPromises = words.map(async (word) => {
                // 1. Clean the word for the API (Handle [QUESTION] marker specifically)
                let cleanWord = word.toLowerCase().replace(/[^a-z0-9]/g, '');
                if (word === '[QUESTION]') cleanWord = 'question';
                
                let imgSrc = null;

                // 2. Query the ARASAAC API
                if (cleanWord) {
                    try {
                        const res = await fetch(`https://api.arasaac.org/api/pictograms/en/search/${cleanWord}`);
                        if (res.ok) {
                            const data = await res.json();
                            // If a pictogram exists, grab the first (most relevant) ID
                            if (data && data.length > 0) {
                                const picId = data[0]._id;
                                imgSrc = `https://static.arasaac.org/pictograms/${picId}/${picId}_300.png`;
                            }
                        }
                    } catch (e) { console.error("ARASAAC fetch error:", e); }
                }
                return { word: word, imgSrc: imgSrc };
            });

            const symbols = await Promise.all(symbolPromises);

            // 3. Render the UI Cards
            symbols.forEach(symbol => {
                const card = document.createElement('div');
                card.className = 'symbol-card';

                if (symbol.imgSrc) {
                    const img = document.createElement('img');
                    img.src = symbol.imgSrc;
                    img.className = 'pictogram';
                    card.appendChild(img);
                } else {
                    // Fallback for names, numbers, or missing words
                    const fallback = document.createElement('div');
                    fallback.className = 'fallback-icon';
                    fallback.innerText = '~';
                    card.appendChild(fallback);
                }

                const label = document.createElement('div');
                label.className = 'gloss-word';
                label.innerText = symbol.word;
                card.appendChild(label);

                container.appendChild(card);
            });
        }

        // Poll the Render server every 500ms for new Colab text
        setInterval(() => {
            fetch('/api/current')
                .then(response => response.json())
                .then(data => {
                    if (data.text && data.text !== lastDisplayedText) {
                        lastDisplayedText = data.text;
                        const wordsArray = data.text.split(' ').filter(w => w.length > 0);
                        fetchArasaacData(wordsArray);
                    }
                })
                .catch(err => console.error("Polling error:", err));
        }, 500);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/update', methods=['POST'])
def update_gloss():
    global current_gloss
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "Missing text"}), 400
    
    current_gloss = data['text']
    return jsonify({"status": "success"}), 200

@app.route('/api/current', methods=['GET'])
def get_current_gloss():
    return jsonify({"text": current_gloss}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

current_gloss = "Waiting for speech..."

# Upgraded Hackathon UI with ARASAAC Integration
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HaptiHear | Live ARASAAC Translation</title>
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            margin: 0;
            padding-top: 50px;
        }
        h1 { color: #bb86fc; font-size: 2.5rem; margin-bottom: 5px; }
        .subtitle { color: #a0a0a0; font-size: 1.2rem; margin-bottom: 50px; }
        
        /* The container that holds all the symbol cards */
        #symbol-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            max-width: 90%;
            min-height: 200px;
        }

        /* Individual Word/Pictogram Card */
        .symbol-card {
            background-color: #1e1e1e;
            border: 2px solid #333;
            border-radius: 15px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            min-width: 150px;
            min-height: 180px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            transition: transform 0.2s, border-color 0.2s;
        }
        
        .symbol-card:hover {
            transform: translateY(-5px);
            border-color: #bb86fc;
        }

        .pictogram {
            width: 120px;
            height: 120px;
            object-fit: contain;
            background-color: #ffffff; /* ARASAAC images have transparent backgrounds, white helps them pop */
            border-radius: 10px;
            padding: 5px;
            margin-bottom: 15px;
        }

        .fallback-icon {
            width: 120px;
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            color: #555;
            background-color: #2a2a2a;
            border-radius: 10px;
            margin-bottom: 15px;
        }

        .gloss-word {
            font-size: 1.5rem;
            font-weight: bold;
            letter-spacing: 1px;
            color: #bb86fc;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>HaptiHear</h1>
    <div class="subtitle">Real-Time NLP to ARASAAC Pictogram Engine</div>
    
    <div id="symbol-container">
        <div class="symbol-card"><div class="gloss-word">Listening...</div></div>
    </div>

    <script>
        let lastDisplayedText = "";

        async function fetchArasaacData(words) {
            const container = document.getElementById('symbol-container');
            container.innerHTML = ''; // Clear the board

            // Fetch all pictograms concurrently for a smooth UI update
            const symbolPromises = words.map(async (word) => {
                // 1. Clean the word for the API (Handle [QUESTION] marker specifically)
                let cleanWord = word.toLowerCase().replace(/[^a-z0-9]/g, '');
                if (word === '[QUESTION]') cleanWord = 'question';
                
                let imgSrc = null;

                // 2. Query the ARASAAC API
                if (cleanWord) {
                    try {
                        const res = await fetch(`https://api.arasaac.org/api/pictograms/en/search/${cleanWord}`);
                        if (res.ok) {
                            const data = await res.json();
                            // If a pictogram exists, grab the first (most relevant) ID
                            if (data && data.length > 0) {
                                const picId = data[0]._id;
                                imgSrc = `https://static.arasaac.org/pictograms/${picId}/${picId}_300.png`;
                            }
                        }
                    } catch (e) { console.error("ARASAAC fetch error:", e); }
                }
                return { word: word, imgSrc: imgSrc };
            });

            const symbols = await Promise.all(symbolPromises);

            // 3. Render the UI Cards
            symbols.forEach(symbol => {
                const card = document.createElement('div');
                card.className = 'symbol-card';

                if (symbol.imgSrc) {
                    const img = document.createElement('img');
                    img.src = symbol.imgSrc;
                    img.className = 'pictogram';
                    card.appendChild(img);
                } else {
                    // Fallback for names, numbers, or missing words
                    const fallback = document.createElement('div');
                    fallback.className = 'fallback-icon';
                    fallback.innerText = '~';
                    card.appendChild(fallback);
                }

                const label = document.createElement('div');
                label.className = 'gloss-word';
                label.innerText = symbol.word;
                card.appendChild(label);

                container.appendChild(card);
            });
        }

        // Poll the Render server every 500ms for new Colab text
        setInterval(() => {
            fetch('/api/current')
                .then(response => response.json())
                .then(data => {
                    if (data.text && data.text !== lastDisplayedText) {
                        lastDisplayedText = data.text;
                        const wordsArray = data.text.split(' ').filter(w => w.length > 0);
                        fetchArasaacData(wordsArray);
                    }
                })
                .catch(err => console.error("Polling error:", err));
        }, 500);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/update', methods=['POST'])
def update_gloss():
    global current_gloss
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "Missing text"}), 400
    
    current_gloss = data['text']
    return jsonify({"status": "success"}), 200

@app.route('/api/current', methods=['GET'])
def get_current_gloss():
    return jsonify({"text": current_gloss}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
