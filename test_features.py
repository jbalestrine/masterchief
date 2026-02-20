#!/usr/bin/env python3

from main import app
from features.manager import init_feature_manager

def test_features():
    # Initialize feature manager
    feature_manager = init_feature_manager(app)

    print('Testing Flask app routes...')
    with app.test_client() as client:
        # Test features page
        response = client.get('/features')
        if response.status_code == 200:
            print('✓ Features page loads successfully')
            content = response.get_data(as_text=True)
            if 'Feature Manager' in content:
                print('✓ Feature Manager title found')
            if 'Create New Feature' in content:
                print('✓ Create New Feature button found')
            if 'GitHub Repository' in content:
                print('✓ GitHub loading option found')
            if 'Script File' in content:
                print('✓ Script loading option found')
            print(f'Page content length: {len(content)} characters')
        else:
            print(f'✗ Features page failed with status {response.status_code}')
            print(f'Response: {response.get_data(as_text=True)}')

if __name__ == '__main__':
    test_features()