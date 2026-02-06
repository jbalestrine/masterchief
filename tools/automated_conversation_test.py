import urllib.request, urllib.parse, json, sys

BASE='http://127.0.0.1:8080'

def post_chat(message, session_id='auto_test_1'):
    url = BASE + '/api/echo/chat'
    data = json.dumps({'message': message, 'session_id': session_id}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.load(resp)
    except Exception as e:
        return {'error': str(e)}

def get_history(session_id='auto_test_1'):
    url = BASE + '/api/echo/history?session_id=' + urllib.parse.quote(session_id)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.load(resp)
    except Exception as e:
        return {'error': str(e)}

if __name__=='__main__':
    session='auto_test_1'
    convo = [
        "what is 1+1?",
        "what would be the next number after that?",
        "and if you add them together, what do you get?",
        "use addition to answer the question as the operator is '+'",
        "yes. so what is the answer to the 2 numbers we used to calculate the answer to my question?"
    ]
    print('Starting automated conversation test, session=',session)
    for i,m in enumerate(convo, start=1):
        print(f'\nUser ({i}):', m)
        r = post_chat(m, session)
        print('Bot reply:', json.dumps(r, indent=2))
    print('\nFetching persisted history...')
    h = get_history(session)
    print(json.dumps(h, indent=2))
