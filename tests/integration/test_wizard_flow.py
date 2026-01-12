"""
Integration test for complete wizard flow via API.
"""

import tempfile
import shutil
from pathlib import Path
from flask import Flask

# Import blueprints
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'platform'))

from plugins.wizard.api import wizard_bp
from plugins.config_editor.api import config_editor_bp


def test_wizard_flow():
    """Test complete wizard flow through API."""
    print('Integration Test: Complete Wizard Flow')
    print('=' * 60)
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    print(f'Using temp directory: {temp_dir}')
    
    try:
        # Create Flask app
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Register blueprints
        app.register_blueprint(wizard_bp, url_prefix='/api/wizard')
        app.register_blueprint(config_editor_bp, url_prefix='/api/config')
        
        with app.test_client() as client:
            # Step 1: Start wizard
            response = client.post('/api/wizard/start')
            assert response.status_code == 201, "Failed to start wizard"
            data = response.get_json()
            session_id = data['session_id']
            print(f'✓ Step 1: Wizard started (session: {session_id[:8]}...)')
            
            # Step 2: Select plugin type
            response = client.post(
                f'/api/wizard/{session_id}/step/1',
                json={'plugin_type': 'python'}
            )
            assert response.status_code == 200, "Failed to select type"
            print('✓ Step 2: Plugin type selected (python)')
            
            # Step 3: Submit metadata
            response = client.post(
                f'/api/wizard/{session_id}/step/2',
                json={
                    'name': 'integration-test-plugin',
                    'description': 'Plugin created by integration test',
                    'version': '1.0.0',
                    'author': 'Integration Test Suite'
                }
            )
            assert response.status_code == 200, "Failed to submit metadata"
            print('✓ Step 3: Metadata submitted')
            
            # Step 4: Submit configuration
            response = client.post(
                f'/api/wizard/{session_id}/step/3',
                json={
                    'python_version': '3.10',
                    'venv_enabled': True,
                    'dependencies': ['flask']
                }
            )
            assert response.status_code == 200, "Failed to submit config"
            print('✓ Step 4: Configuration submitted')
            
            # Step 5: Complete wizard
            response = client.post(
                f'/api/wizard/{session_id}/complete',
                json={'confirm': True}
            )
            assert response.status_code == 200, "Failed to complete wizard"
            data = response.get_json()
            print('✓ Step 5: Wizard completed')
            
            # Verify status
            response = client.get(f'/api/wizard/{session_id}/status')
            assert response.status_code == 200
            data = response.get_json()
            assert data['session']['completed'] == True
            print('✓ Verified: Wizard marked as completed')
            
            # List sessions
            response = client.get('/api/wizard/sessions')
            assert response.status_code == 200
            data = response.get_json()
            assert data['count'] >= 1
            print(f'✓ Listed sessions: {data["count"]} active')
            
            # Delete session
            response = client.delete(f'/api/wizard/{session_id}')
            assert response.status_code == 200
            print('✓ Session deleted')
            
        print('\n' + '=' * 60)
        print('✅ INTEGRATION TEST PASSED!')
        print('All API endpoints working correctly')
        
        return True
        
    except AssertionError as e:
        print(f'\n✗ Test failed: {e}')
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    success = test_wizard_flow()
    sys.exit(0 if success else 1)
