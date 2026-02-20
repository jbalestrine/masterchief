from templates.pages import SCRIPT_EXECUTE_TEMPLATE
from templates.base import HTML_TEMPLATE
from flask import Flask, render_template_string

app = Flask(__name__)

with app.app_context():
    print('SCRIPT_EXECUTE_TEMPLATE:')
    print(repr(SCRIPT_EXECUTE_TEMPLATE[:200]))

    modified_content = SCRIPT_EXECUTE_TEMPLATE.replace('{% extends "base.html" %}','').replace('{% block content %}','').replace('{% endblock %}','')
    print('Modified content:')
    print(repr(modified_content[:200]))

    modified_template = HTML_TEMPLATE.replace('{% block content %}{% endblock %}', modified_content)
    print('Final template length:', len(modified_template))
    print('Contains result:', 'result' in modified_template)

    # Test rendering
    try:
        result = {'success': True, 'returncode': 0, 'stdout': 'test output', 'stderr': ''}
        rendered = render_template_string(modified_template, filename='test.py', result=result, request=None, get_flashed_messages=lambda: [])
        print('Rendering successful, length:', len(rendered))
    except Exception as e:
        print('Rendering failed:', e)