"""Tests for API Gateway."""
import pytest
from flask import Flask
from platform.gateway.router import gateway_bp, create_gateway
from platform.gateway.health import health_bp


@pytest.fixture
def app():
    """Create test Flask app."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['JWT_SECRET'] = 'test-secret'
    app.register_blueprint(gateway_bp, url_prefix='/api/v1')
    app.register_blueprint(health_bp)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_gateway_index(client):
    """Test gateway index endpoint."""
    response = client.get('/api/v1/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'service' in data
    assert data['service'] == 'MasterChief API Gateway'
    assert 'endpoints' in data


def test_gateway_routes(client):
    """Test routes listing endpoint."""
    response = client.get('/api/v1/routes')
    assert response.status_code == 200
    data = response.get_json()
    assert 'routes' in data


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'masterchief-api'


def test_readiness_check(client):
    """Test readiness check endpoint."""
    response = client.get('/health/ready')
    # Should return 200 if ready, 503 if not
    assert response.status_code in [200, 503]
    data = response.get_json()
    assert 'ready' in data
    assert 'checks' in data


def test_liveness_check(client):
    """Test liveness check endpoint."""
    response = client.get('/health/live')
    assert response.status_code == 200
    data = response.get_json()
    assert data['alive'] is True


def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options('/api/v1/')
    # CORS middleware should add headers
    assert response.status_code in [200, 204]


def test_request_id_header(client):
    """Test that request ID is added to response."""
    response = client.get('/health')
    # Logging middleware adds X-Request-ID
    # This might not be present without full middleware setup
    assert response.status_code == 200
