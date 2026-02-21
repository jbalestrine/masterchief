text = open('main.py', encoding='utf-8').read()
start = text.find('MODULES_TEMPLATE=')
end   = text.find('{% endblock %}"""', start) + 20
chunk = text[start:end]
bad = [(i, hex(ord(c)), repr(c)) for i,c in enumerate(chunk) if ord(c) > 0xFFFF or (0xD800 <= ord(c) <= 0xDFFF)]
if bad:
    print('Problematic chars:', bad[:20])
else:
    print('No surrogates/high codepoints.')
    # Check for anything werkzeug would choke on
    try:
        chunk.encode('utf-8')
        print('encode OK')
    except UnicodeEncodeError as e:
        print('Encode error:', e)
        ctx = chunk[max(0,e.start-40):e.end+40]
        print('Context:', repr(ctx))
