#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template_string
import threading

# Try to import the project's chat bot
try:
    from echo.chat_bot import get_chat_bot
except Exception:
    get_chat_bot = None

app = Flask(__name__)

INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Quick Echo Chat</title>
  <style>body{font-family:Arial,Helvetica,sans-serif;margin:20px} #log{height:60vh;overflow:auto;border:1px solid #ccc;padding:8px} #prompt{width:80%}</style>
</head>
<body>
  <h2>Quick Echo Chat (local)</h2>
  <div id="log"></div>
  <div style="margin-top:8px">
    <input id="prompt" placeholder="Type a message" />
    <button id="send">Send</button>
  </div>
  <script>
    const log=document.getElementById('log');
    const prompt=document.getElementById('prompt');
    document.getElementById('send').onclick = async function(){
      const t = prompt.value.trim(); if(!t) return;
      append('You: '+t);
      prompt.value='';
      try{
        const res = await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t})});
        const j = await res.json();
        append('Echo: '+(j.reply||j.error||'no reply'));
      }catch(e){append('Error: '+e.message)}
    }
    function append(s){
      const p=document.createElement('div'); p.textContent=s; log.appendChild(p); log.scrollTop=log.scrollHeight; }
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json(force=True)
    text = (data or {}).get('text', '')
    if not text:
        return jsonify({'error':'no text provided'})
    if get_chat_bot is None:
        return jsonify({'error':'project chat bot not importable from echo.chat_bot'})
    try:
        bot = get_chat_bot()
        # some bots expect a dict or simple call; try call interface
        if hasattr(bot, 'respond'):
            reply = bot.respond(text)
        elif hasattr(bot, '__call__'):
            reply = bot(text)
        else:
            reply = str(bot)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print('Quick Echo Chat available at http://127.0.0.1:8081/')
    app.run(host='127.0.0.1', port=8081)
