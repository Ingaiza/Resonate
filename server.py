from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

# Live Audio Payload
current_payload = {"mode1": "Waiting for speech...", "mode2": "WAIT FOR SPEECH", "mode3": "SPEECH WAIT"}

# Testing Queue Variables
pending_test_sentence = ""
latest_test_result = ""
feedback_logs = []

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RESONATE | Live Translation & Testing</title>
    <style>
        body {
            background-color: #121212; color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex; flex-direction: column; align-items: center;
            min-height: 100vh; margin: 0; padding-top: 20px;
        }
        h1 { color: #bb86fc; font-size: 2.5rem; margin-bottom: 0px; }
        .subtitle { color: #a0a0a0; font-size: 1.1rem; margin-bottom: 20px; }
        
        /* Navigation Tabs */
        .tabs { display: flex; gap: 15px; margin-bottom: 30px; }
        .tab-btn {
            background-color: #1e1e1e; color: #bb86fc;
            border: 2px solid #bb86fc; border-radius: 8px;
            padding: 8px 16px; cursor: pointer; font-weight: bold; transition: 0.3s;
        }
        .tab-btn.active { background-color: #bb86fc; color: #121212; }
        
        /* Views */
        #live-view, #testing-view { width: 100%; display: flex; flex-direction: column; align-items: center; }
        #testing-view { display: none; }
        
        /* Mode Toggle (Live View) */
        .toggle-container {
            display: flex; background-color: #1e1e1e; border-radius: 30px;
            padding: 5px; margin-bottom: 40px; border: 1px solid #333;
        }
        .toggle-container input[type="radio"] { display: none; }
        .toggle-label {
            padding: 10px 20px; cursor: pointer; border-radius: 25px;
            color: #888; font-weight: bold; transition: all 0.3s;
        }
        .toggle-container input[type="radio"]:checked + .toggle-label { background-color: #bb86fc; color: #121212; }

        /* ARASAAC Cards */
        #symbol-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; max-width: 90%; }
        .symbol-card {
            background-color: #1e1e1e; border: 2px solid #333; border-radius: 15px;
            padding: 20px; display: flex; flex-direction: column; align-items: center;
            justify-content: space-between; min-width: 150px; min-height: 180px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }
        .pictogram { width: 120px; height: 120px; object-fit: contain; background-color: #ffffff; border-radius: 10px; padding: 5px; margin-bottom: 15px; }
        .fallback-icon { width: 120px; height: 120px; display: flex; align-items: center; justify-content: center; font-size: 3rem; color: #555; background-color: #2a2a2a; border-radius: 10px; margin-bottom: 15px; }
        .gloss-word { font-size: 1.5rem; font-weight: bold; letter-spacing: 1px; color: #bb86fc; text-align: center; text-transform: uppercase; }

        /* Testing Panel UI */
        .test-panel {
            background-color: #1e1e1e; border: 1px solid #333; border-radius: 15px;
            padding: 30px; width: 80%; max-width: 600px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5); text-align: left;
        }
        .input-group { margin-bottom: 20px; }
        label { display: block; color: #a0a0a0; margin-bottom: 8px; font-weight: bold; }
        input[type="text"] {
            width: 95%; padding: 12px; border-radius: 8px; border: 1px solid #555;
            background-color: #121212; color: #fff; font-size: 1.1rem;
        }
        button {
            background-color: #bb86fc; color: #121212; border: none; border-radius: 8px;
            padding: 12px 20px; font-size: 1.1rem; font-weight: bold; cursor: pointer; width: 100%; margin-top: 10px;
        }
        button:hover { background-color: #a368fc; }
        .system-output {
            background-color: #2a2a2a; padding: 15px; border-radius: 8px;
            color: #4CAF50; font-family: monospace; font-size: 1.2rem; font-weight: bold; min-height: 25px;
        }
    </style>
</head>
<body>
    <h1>RESONATE</h1>
    <div class="subtitle">Real-Time NLP to ARASAAC Pictogram Engine</div>
    
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('live')">Live Demo Mode</button>
        <button class="tab-btn" onclick="switchTab('testing')">KSL Expert Testing</button>
    </div>

    <div id="live-view">
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
    </div>

    <div id="testing-view">
        <div class="test-panel">
            <div class="input-group">
                <label>1. Enter Test Sentence (English):</label>
                <input type="text" id="test-input" placeholder="e.g. My delivery will arrive at 5 PM">
                <button onclick="requestTranslation()">Generate Translation</button>
            </div>
            <div class="input-group">
                <label>2. RESONATE Output:</label>
                <div id="sys-output" class="system-output">Waiting for input...</div>
            </div>
            <div class="input-group">
                <label>3. Your Recommended/Expected KSL Output:</label>
                <input type="text" id="expert-input" placeholder="Enter corrected syntax here...">
                <button onclick="submitFeedback()" style="background-color: #03dac6;">Submit Feedback to Team</button>
            </div>
        </div>
    </div>

    <script>
        // --- Tab Switching ---
        function switchTab(tab) {
            document.getElementById('live-view').style.display = tab === 'live' ? 'flex' : 'none';
            document.getElementById('testing-view').style.display = tab === 'testing' ? 'flex' : 'none';
            document.querySelectorAll('.tab-btn')[0].className = tab === 'live' ? 'tab-btn active' : 'tab-btn';
            document.querySelectorAll('.tab-btn')[1].className = tab === 'testing' ? 'tab-btn active' : 'tab-btn';
        }

        // --- Live Mode Logic ---
        let latestData = { mode1: "", mode2: "", mode3: "" };
        let lastDisplayedText = "";

        document.querySelectorAll('input[name="mode"]').forEach(r => r.addEventListener('change', updateDisplay));

        function updateDisplay() {
            const selectedMode = document.querySelector('input[name="mode"]:checked').value;
            const text = latestData[selectedMode];
            if (text && text !== lastDisplayedText) {
                lastDisplayedText = text;
                fetchArasaacData(text.split(' ').filter(w => w.length > 0));
            }
        }

        async function fetchArasaacData(words) {
            const container = document.getElementById('symbol-container');
            container.innerHTML = ''; 
            const symbolPromises = words.map(async (word) => {
                let cleanWord = word.toLowerCase().replace(/[^a-z0-9]/g, '');
                if (word === '[QUESTION]') cleanWord = 'question';
                if (cleanWord === 'am' || cleanWord === 'pm') cleanWord = 'force_fallback_string'; // Banishes the shepherd!
                
                let imgSrc = null;
                if (cleanWord) {
                    try {
                        const res = await fetch(`https://api.arasaac.org/api/pictograms/en/search/${cleanWord}`);
                        if (res.ok) {
                            const data = await res.json();
                            if (data && data.length > 0) imgSrc = `https://static.arasaac.org/pictograms/${data[0]._id}/${data[0]._id}_300.png`;
                        }
                    } catch (e) {}
                }
                return { word, imgSrc };
            });

            const symbols = await Promise.all(symbolPromises);
            symbols.forEach(symbol => {
                const card = document.createElement('div'); card.className = 'symbol-card';
                if (symbol.imgSrc) {
                    const img = document.createElement('img'); img.src = symbol.imgSrc; img.className = 'pictogram'; card.appendChild(img);
                } else {
                    const fallback = document.createElement('div'); fallback.className = 'fallback-icon'; fallback.innerText = '~'; card.appendChild(fallback);
                }
                const label = document.createElement('div'); label.className = 'gloss-word'; label.innerText = symbol.word; card.appendChild(label);
                container.appendChild(card);
            });
        }

        setInterval(() => {
            if(document.getElementById('live-view').style.display !== 'none') {
                fetch('/api/current').then(r => r.json()).then(data => { latestData = data; updateDisplay(); }).catch(e=>{});
            }
        }, 500);

        // --- Testing Mode Logic ---
        let testPollingTimer = null;

        function requestTranslation() {
            const txt = document.getElementById('test-input').value;
            if(!txt) return;
            document.getElementById('sys-output').innerText = "Processing in Colab backend...";
            document.getElementById('sys-output').style.color = "#bb86fc";
            
            fetch('/api/test/request', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({text: txt})
            }).then(() => {
                // Start polling for result
                if(testPollingTimer) clearInterval(testPollingTimer);
                testPollingTimer = setInterval(pollForResult, 1000);
            });
        }

        function pollForResult() {
            fetch('/api/test/fetch_result').then(r => r.json()).then(data => {
                if(data.result) {
                    document.getElementById('sys-output').innerText = data.result;
                    document.getElementById('sys-output').style.color = "#4CAF50";
                    clearInterval(testPollingTimer);
                }
            });
        }

        function submitFeedback() {
            const original = document.getElementById('test-input').value;
            const system = document.getElementById('sys-output').innerText;
            const expected = document.getElementById('expert-input').value;
            if(!expected) { alert("Please enter an expected output."); return; }

            fetch('/api/test/feedback', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({original, system, expected})
            }).then(() => {
                alert("Feedback submitted successfully! Thank you.");
                document.getElementById('test-input').value = "";
                document.getElementById('sys-output').innerText = "Waiting for input...";
                document.getElementById('expert-input').value = "";
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_PAGE)

# --- LIVE DEMO ENDPOINTS ---
@app.route('/api/update', methods=['POST'])
def update_gloss():
    global current_payload
    current_payload = request.json
    return jsonify({"status": "success"}), 200

@app.route('/api/current', methods=['GET'])
def get_current_gloss():
    return jsonify(current_payload), 200

# --- TESTING FEEDBACK ENDPOINTS ---
@app.route('/api/test/request', methods=['POST'])
def request_test():
    global pending_test_sentence, latest_test_result
    pending_test_sentence = request.json.get('text', '')
    latest_test_result = "" # Clear old result
    return jsonify({"status": "queued"}), 200

@app.route('/api/test/poll', methods=['GET'])
def poll_test():
    global pending_test_sentence
    txt = pending_test_sentence
    pending_test_sentence = "" # Clear it so Colab only processes it once
    return jsonify({"text": txt}), 200

@app.route('/api/test/result', methods=['POST'])
def post_test_result():
    global latest_test_result
    latest_test_result = request.json.get('result', '')
    return jsonify({"status": "success"}), 200

@app.route('/api/test/fetch_result', methods=['GET'])
def fetch_test_result():
    return jsonify({"result": latest_test_result}), 200

@app.route('/api/test/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    data['timestamp'] = str(datetime.datetime.now())
    feedback_logs.append(data)
    print(f"NEW FEEDBACK RECIEVED: {data}")
    return jsonify({"status": "logged"}), 200

# Hidden endpoint for you to view/download the collected feedback!
@app.route('/api/view_feedback', methods=['GET'])
def view_feedback():
    return jsonify({"total_logs": len(feedback_logs), "logs": feedback_logs}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
