#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from main import app
    print("SUCCESS: main.py imported successfully")

    # Check for feature routes
    feature_routes = [rule.rule for rule in app.url_map.iter_rules() if 'feature' in rule.rule.lower()]
    print(f"Found {len(feature_routes)} feature-related routes:")
    for route in feature_routes:
        print(f"  - {route}")

    # Test the features page with test client
    with app.test_client() as client:
        response = client.get('/features')
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            print("SUCCESS: /features page loads")
            print(f"Page content length: {len(content)} characters")

            # Check for key elements
            checks = [
                'Feature Manager',
                'GitHub Repository',
                'Browse Repos',
                'Search GitHub'
            ]
            passed = 0
            for check in checks:
                if check in content:
                    print(f"  ✓ {check} found")
                    passed += 1
                else:
                    print(f"  ✗ {check} NOT found")

            print(f"UI checks: {passed}/{len(checks)} passed")
        else:
            print(f"ERROR: /features page failed with status {response.status_code}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()