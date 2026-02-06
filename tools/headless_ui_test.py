from playwright.sync_api import sync_playwright
import threading, requests, time, json

URL = 'http://127.0.0.1:8080'
MSG_TEXT = 'Headless UI test message ' + time.strftime('%Y-%m-%d %H:%M:%S')

# Create session externally so we can drive SSE on the page
conn = requests.post(URL + '/irc/connect', json={'host':'127.0.0.1','port':6667,'nick':'headless'}, timeout=5).json()
session = conn.get('session')
token = conn.get('bridge_token')
print('External session:', session, 'token:', token)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL)
    page.wait_for_selector('#miniIrcMessages', timeout=5000)

    # inject an EventSource that appends lines into the UI messages pane
    inject_js = """
    (function(){
      const sess = '{SESSION}';
      const es = new EventSource('/irc/stream?session='+encodeURIComponent(sess)+'&last=0');
      es.onmessage = function(ev){ try{ const d = JSON.parse(ev.data||'{}'); const line = d.line||''; const box = document.querySelector('#miniIrcMessages'); if(box){ const div = document.createElement('div'); div.textContent = line; box.appendChild(div); box.scrollTop = box.scrollHeight; } }catch(e){} };
      window.__headless_es = es;
    })();
    """.replace('{SESSION}', session)
    page.evaluate(inject_js)

    # post bridged message
    body = {'session': session, 'channel': '#masterchief', 'message': MSG_TEXT}
    headers = {'Content-Type':'application/json'}
    if token:
        headers['X-BRIDGE-TOKEN'] = token
        body['bridge_token'] = token
    r = requests.post(URL + '/irc/bridge_send', json=body, headers=headers, timeout=5)
    print('/irc/bridge_send', r.status_code, r.text)

    # wait for DOM to include message text
    try:
        page.wait_for_function("() => document.querySelector('#miniIrcMessages') && document.querySelector('#miniIrcMessages').innerText.includes('" + MSG_TEXT + "')", timeout=5000)
        print('UI shows bridged message')
    except Exception:
        print('UI did not show bridged message within timeout')
    # close EventSource
    page.evaluate("window.__headless_es && window.__headless_es.close();")
    browser.close()
