#!/usr/bin/env python3

from main import app
from features.manager import init_feature_manager

def test_enhanced_features():
    # Initialize feature manager
    feature_manager = init_feature_manager(app)

    print('Testing enhanced features...')
    with app.test_client() as client:
        # Test features page
        response = client.get('/features')
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            checks = [
                ('GitHub Repository' in content, 'GitHub Repository option'),
                ('Load from GitHub' in content, 'Load from GitHub button'),
                ('Browse Repos' in content, 'Browse Repos tab'),
                ('Search GitHub' in content, 'Search GitHub tab'),
                ('Local File' in content, 'Local File tab'),
                ('From URL' in content, 'From URL tab'),
                ('From Repository' in content, 'From Repository tab'),
                ('tab-button' in content, 'Tab buttons'),
                ('repos-list' in content, 'Repository list'),
                ('scripts-list' in content, 'Scripts list')
            ]

            passed = 0
            for check, desc in checks:
                if check:
                    print(f'✓ {desc}')
                    passed += 1
                else:
                    print(f'✗ {desc}')

            print(f'\nPassed {passed}/{len(checks)} checks')
            print(f'Page content length: {len(content)} characters')
        else:
            print(f'✗ Features page failed with status {response.status_code}')

if __name__ == '__main__':
    test_enhanced_features()