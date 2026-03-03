from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Now holding all three modes
current_payload = {
    "mode1": "Waiting for speech...",
    "mode2": "WAIT FOR SPEECH",
    "mode3": "SPEECH WAIT"
}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RESONATE | Live ARASAAC Translation</title>
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
            padding-top: 30px;
        }
        h1 { color: #bb86fc; font-size: 2.5rem; margin-bottom: 5px; }
        .subtitle { color: #a0a0a0; font-size: 1.2rem; margin-bottom: 30px; }
        
        /* 🛑 NEW: Mode Toggle UI */
        .toggle-container {
            display: flex;
            background-color: #1e1e1e;
            border-radius: 30px;
            padding: 5px;
            margin-bottom: 40px;
            border: 1px solid #333;
        }
        .toggle-container input[type="radio"] { display: none; }
        .toggle-label {
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 25px;
            color: #888;
            font-weight: bold;
            transition: all 0.3s;
        }
        .toggle-container input[type="radio"]:checked + .toggle-label {
            background-color: #bb86fc;
            color: #121212;
        }

        #symbol-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            max-width: 90%;
            min-height: 200px;
        }

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
            background-color: #ffffff;
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
            text-transform: uppercase;
        }
    </style>
</head>
<body>
    <h1>RESONATE</h1>
    <div class="subtitle">Real-Time NLP to ARASAAC Pictogram Engine</div>
    
    <div class="toggle-container">
        <input type="radio" id="mode1" name="mode" value="mode1">
        <label for="mode1" class="toggle-label">1. Raw Text</label>
        
        <input type="radio" id="mode2" name="mode" value="mode2" checked>
        <label for="mode2" class="toggle-label">2. Semi-Lemmatized</label>
        
        <input type="radio" id="mode3" name="mode" value="mode3">
        <label for="mode3" class="toggle-label">3. Sign Language</label>
    </div>

    <div id="symbol-container">
        <div class="symbol-card"><div class="gloss-word">Listening...</div></div>
    </div>

    <script>
        let latestData = { mode1: "", mode2: "", mode3: "" };
        let lastDisplayedText = "";

        // Instantly switch display when a new mode is clicked!
        document.querySelectorAll('input[name="mode"]').forEach(radio => {
            radio.addEventListener('change', updateDisplay);
        });

        function updateDisplay() {
            const selectedMode = document.querySelector('input[name="mode"]:checked').value;
            const textToDisplay = latestData[selectedMode];
            
            if (textToDisplay && textToDisplay !== lastDisplayedText) {
                lastDisplayedText = textToDisplay;
                const wordsArray = textToDisplay.split(' ').filter(w => w.length > 0);
                fetchArasaacData(wordsArray);
            }
        }

        async function fetchArasaacData(words) {
            const container = document.getElementById('symbol-container');
            container.innerHTML = ''; 

            const symbolPromises = words.map(async (word) => {
                let cleanWord = word.toLowerCase().replace(/[^a-z0-9]/g, '');
                if (word === '[QUESTION]') cleanWord = 'question';
                if (cleanWord === 'am' || cleanWord === 'pm') cleanWord = 'force_fallback_string';
                
                
                let imgSrc = null;

                if (cleanWord) {
                    try {
                        const res = await fetch(`https://api.arasaac.org/api/pictograms/en/search/${cleanWord}`);
                        if (res.ok) {
                            const data = await res.json();
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

            symbols.forEach(symbol => {
                const card = document.createElement('div');
                card.className = 'symbol-card';

                if (symbol.imgSrc) {
                    const img = document.createElement('img');
                    img.src = symbol.imgSrc;
                    img.className = 'pictogram';
                    card.appendChild(img);
                } else {
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

        setInterval(() => {
            fetch('/api/current')
                .then(response => response.json())
                .then(data => {
                    latestData = data;
                    updateDisplay();
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
    global current_payload
    data = request.json
    if not data or 'mode1' not in data:
        return jsonify({"error": "Missing payload data"}), 400
    
    current_payload = data
    return jsonify({"status": "success"}), 200

@app.route('/api/current', methods=['GET'])
def get_current_gloss():
    return jsonify(current_payload), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
