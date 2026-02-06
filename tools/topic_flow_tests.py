import time
import json
import sys
from pathlib import Path
import urllib.request, urllib.parse

# Ensure repo root is on sys.path so local imports work
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from echo.conversation_storage import get_storage

BASE='http://127.0.0.1:8080'

def post_chat(message, session_id):
    url = BASE + '/api/echo/chat'
    data = json.dumps({'message': message, 'session_id': session_id}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)

def run_scenario(name, steps):
    print(f"\n--- Scenario: {name} ---")
    session = f"test_{name.replace(' ','_').lower()}"
    storage = get_storage()

    passed = True
    for i, step in enumerate(steps, start=1):
        print(f"User ({i}): {step['user']}")
        resp = post_chat(step['user'], session)
        bot_text = resp.get('response','') if isinstance(resp, dict) else str(resp)
        print('Bot reply:', bot_text)

        # small delay for persistence
        time.sleep(0.2)

        meta = storage.get_session_meta(session) or {}
        topic = meta.get('topic_state') or {}

        # assertions if any
        expect = step.get('expect')
        if expect:
            ok = False
            if 'in_reply' in expect:
                ok = any(token.lower() in bot_text.lower() for token in expect['in_reply'])
            if 'meta_stage' in expect:
                ok = ok and (topic.get('stage') == expect['meta_stage']) if ok else (topic.get('stage') == expect['meta_stage'])
            if 'meta_contains' in expect:
                # ensure any of the expected substrings in key_points
                kp = topic.get('key_points', [])
                joined = ' '.join(kp)
                ok = ok and all(s.lower() in joined.lower() for s in expect['meta_contains']) if ok else all(s.lower() in joined.lower() for s in expect['meta_contains'])
            print('  Expectation:', expect, '->', 'PASS' if ok else 'FAIL')
            passed = passed and ok

    # final check for completion
    final_meta = storage.get_session_meta(session) or {}
    print('Final topic_state:', json.dumps(final_meta.get('topic_state'), indent=2))
    print('Scenario result:', 'PASS' if passed else 'FAIL')
    return passed

if __name__=='__main__':
    scenarios = [
        (
            'ARM template',
            [
                {'user': "I want to create an ARM template to deploy a web app and an API.", 'expect': {'in_reply': ["explore"], 'meta_stage': 'exploration'}},
                {'user': "Also, include an Azure Function and a storage account.", 'expect': {'in_reply': ["updated the plan", "updated"], 'meta_stage': 'refinement', 'meta_contains': ['Azure Function','storage account']}},
                {'user': "Add monitoring and alerts, and use Application Insights.", 'expect': {'in_reply': ["updated the plan","Anything else"], 'meta_stage': 'refinement'}},
                {'user': "Is this okay?", 'expect': {'in_reply': ["Here's what I have so far","proceed"], 'meta_stage': 'validation'}},
                {'user': "Done", 'expect': {'in_reply': ["summary","start something new","Done"], 'meta_stage': 'complete'}},
            ]
        ),
        (
            'Web app planning',
            [
                {'user': "Can you help me plan a web app architecture for a multi-tenant SaaS?", 'expect': {'in_reply': ["explore"], 'meta_stage': 'exploration'}},
                {'user': "Also include tenant isolation and horizontal scaling.", 'expect': {'in_reply': ["updated the plan","updated"], 'meta_stage': 'refinement'}},
                {'user': "We will use Postgres and Redis, add them to the plan.", 'expect': {'meta_contains': ['Postgres','Redis'], 'meta_stage': 'refinement'}},
                {'user': "Looks good, confirm.", 'expect': {'in_reply': ["Here's what I have so far","proceed","refine"], 'meta_stage': 'validation'}},
                {'user': "that's all, thanks", 'expect': {'in_reply': ["summary","start something new","Done"], 'meta_stage': 'complete'}},
            ]
        )
    ]

    # Additional robustness checks: multiple phrasing variants for triggers
    variant_scenarios = []

    new_topic_variants = [
        "I want to create an ARM template to deploy a web app and an API.",
        "I need an ARM template to deploy a web app and an API.",
        "Can you help me create an ARM template for a web app and API?",
        "task: Create ARM template for web app + API"
    ]
    for i, msg in enumerate(new_topic_variants, start=1):
        variant_scenarios.append((f'New-topic-variant-{i}', [
            {'user': msg, 'expect': {'in_reply': ['explore'], 'meta_stage': 'exploration'}}
        ]))

    refinement_variants = [
        "Also, include an Azure Function and a storage account.",
        "Add an Azure Function and storage account.",
        "Please add Azure Function + storage account.",
        "Update: include Azure Function and a storage account"
    ]
    for i, msg in enumerate(refinement_variants, start=1):
        variant_scenarios.append((f'Refine-variant-{i}', [
            {'user': "I want to create an ARM template to deploy a web app and an API.", 'expect': {'in_reply': ['explore'], 'meta_stage': 'exploration'}},
            {'user': msg, 'expect': {'in_reply': ['updated the plan', 'updated'], 'meta_stage': 'refinement'}}
        ]))

    validation_variants = [
        "Is this okay?",
        "Does this work?",
        "Is this correct?",
        "Looks good, confirm."
    ]
    for i, msg in enumerate(validation_variants, start=1):
        variant_scenarios.append((f'Validate-variant-{i}', [
            {'user': "I want to create an ARM template to deploy a web app and an API.", 'expect': {'in_reply': ['explore'], 'meta_stage': 'exploration'}},
            {'user': "Also, include an Azure Function and a storage account.", 'expect': {'in_reply': ['updated the plan', 'updated'], 'meta_stage': 'refinement'}},
            {'user': msg, 'expect': {'in_reply': ["Here's what I have so far", 'proceed'], 'meta_stage': 'validation'}}
        ]))

    completion_variants = [
        "Done",
        "I'm finished",
        "that's all, thanks",
        "complete"
    ]
    for i, msg in enumerate(completion_variants, start=1):
        variant_scenarios.append((f'Complete-variant-{i}', [
            {'user': "I want to create an ARM template to deploy a web app and an API.", 'expect': {'in_reply': ['explore'], 'meta_stage': 'exploration'}},
            {'user': "Also, include an Azure Function and a storage account.", 'expect': {'in_reply': ['updated the plan', 'updated'], 'meta_stage': 'refinement'}},
            {'user': "Is this okay?", 'expect': {'in_reply': ["Here's what I have so far", 'proceed'], 'meta_stage': 'validation'}},
            {'user': msg, 'expect': {'in_reply': ['summary', 'Done', 'start something new'], 'meta_stage': 'complete'}}
        ]))

    # extend main scenarios with variants
    scenarios.extend(variant_scenarios)

    results = []
    for name, steps in scenarios:
        ok = run_scenario(name, steps)
        results.append((name, ok))

    print('\nSummary:')
    for name, ok in results:
        print(f"  {name}: {'PASS' if ok else 'FAIL'}")

    exit_code = 0 if all(ok for _,ok in results) else 2
    raise SystemExit(exit_code)
