"""Tests for data ingestion system."""
import asyncio
import pytest
import tempfile
import os
from pathlib import Path

from chatops.irc.bot_engine.ingestion.base import (
    BaseIngestion, IngestionEvent, IngestionManager, IngestionStatus
)


class MockIngestion(BaseIngestion):
    """Mock ingestion source for testing."""
    
    async def start(self):
        self.status = IngestionStatus.RUNNING
    
    async def stop(self):
        self.status = IngestionStatus.STOPPED


@pytest.mark.asyncio
async def test_ingestion_manager_register():
    """Test registering ingestion sources."""
    manager = IngestionManager()
    source = MockIngestion("test_source", {})
    
    manager.register_source(source)
    
    assert "test_source" in manager.sources
    assert manager.get_source("test_source") == source


@pytest.mark.asyncio
async def test_ingestion_manager_unregister():
    """Test unregistering ingestion sources."""
    manager = IngestionManager()
    source = MockIngestion("test_source", {})
    
    manager.register_source(source)
    manager.unregister_source("test_source")
    
    assert "test_source" not in manager.sources


@pytest.mark.asyncio
async def test_ingestion_manager_start_stop():
    """Test starting and stopping all sources."""
    manager = IngestionManager()
    source1 = MockIngestion("source1", {})
    source2 = MockIngestion("source2", {})
    
    manager.register_source(source1)
    manager.register_source(source2)
    
    await manager.start_all()
    
    assert source1.status == IngestionStatus.RUNNING
    assert source2.status == IngestionStatus.RUNNING
    
    await manager.stop_all()
    
    assert source1.status == IngestionStatus.STOPPED
    assert source2.status == IngestionStatus.STOPPED


@pytest.mark.asyncio
async def test_ingestion_event_handler():
    """Test event handler registration and dispatch."""
    source = MockIngestion("test", {})
    received_events = []
    
    def handler(event):
        received_events.append(event)
    
    source.add_handler(handler)
    
    event = IngestionEvent(
        source_type="test",
        source_id="test",
        data={"key": "value"},
        metadata={},
        timestamp=0.0
    )
    
    await source._dispatch_event(event)
    
    assert len(received_events) == 1
    assert received_events[0].data["key"] == "value"


@pytest.mark.asyncio
async def test_ingestion_status():
    """Test ingestion source status."""
    source = MockIngestion("test", {"config": "value"})
    
    status = source.get_status()
    
    assert status["source_id"] == "test"
    assert status["source_type"] == "MockIngestion"
    assert status["status"] == "stopped"
    assert status["config"]["config"] == "value"


@pytest.mark.asyncio
async def test_file_ingestion_json():
    """Test file ingestion with JSON files."""
    from chatops.irc.bot_engine.ingestion.files import FileIngestion
    
    # Create temporary directory and file
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.json"
        test_file.write_text('{"name": "test", "value": 123}')
        
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        source = FileIngestion("file_test", {
            "path": tmpdir,
            "pattern": "*.json",
            "formats": ["json"],
            "initial_scan": True
        })
        
        source.add_handler(handler)
        
        await source.start()
        await asyncio.sleep(0.5)  # Wait for initial scan
        await source.stop()
        
        assert len(received_events) > 0
        assert received_events[0].data["name"] == "test"
        assert received_events[0].data["value"] == 123


@pytest.mark.asyncio
async def test_webhook_signature_validation():
    """Test webhook signature validation."""
    from chatops.irc.bot_engine.ingestion.webhooks import WebhookIngestion
    import hmac
    import hashlib
    
    source = WebhookIngestion("webhook_test", {
        "port": 8081,
        "secret": "test_secret",
        "webhook_type": "github"
    })
    
    # Mock request object
    class MockRequest:
        def __init__(self):
            self.headers = {}
            self._data = b'{"test": "data"}'
        
        def get_data(self):
            return self._data
    
    request = MockRequest()
    payload = request.get_data()
    
    # Generate valid signature
    expected = 'sha256=' + hmac.new(
        b'test_secret',
        payload,
        hashlib.sha256
    ).hexdigest()
    
    request.headers['X-Hub-Signature-256'] = expected
    
    # Validate
    assert source._validate_github_signature(request)


@pytest.mark.asyncio
async def test_api_ingestion_auth_headers():
    """Test API ingestion authentication headers."""
    from chatops.irc.bot_engine.ingestion.api import APIIngestion
    
    # Test API key auth
    source = APIIngestion("api_test", {
        "url": "http://example.com/api",
        "auth_type": "api_key",
        "auth_config": {
            "key": "X-API-Key",
            "value": "test_key_123"
        }
    })
    
    headers = source._get_auth_headers()
    assert headers["X-API-Key"] == "test_key_123"
    
    # Test Bearer auth
    source = APIIngestion("api_test2", {
        "url": "http://example.com/api",
        "auth_type": "bearer",
        "auth_config": {
            "token": "bearer_token_123"
        }
    })
    
    headers = source._get_auth_headers()
    assert headers["Authorization"] == "Bearer bearer_token_123"


@pytest.mark.asyncio
async def test_log_parsing_syslog():
    """Test log parsing with syslog format."""
    from chatops.irc.bot_engine.ingestion.logs import LogIngestion
    
    source = LogIngestion("log_test", {
        "path": "/tmp/test.log",
        "format": "syslog"
    })
    
    # Test syslog format
    line = "Jan 12 10:30:45 hostname appname: test message"
    parsed = source._parse_syslog(line)
    
    assert parsed is not None
    assert parsed["hostname"] == "hostname"
    assert parsed["tag"] == "appname"
    assert parsed["message"] == "test message"


@pytest.mark.asyncio
async def test_log_parsing_json():
    """Test log parsing with JSON format."""
    from chatops.irc.bot_engine.ingestion.logs import LogIngestion
    
    source = LogIngestion("log_test", {
        "path": "/tmp/test.log",
        "format": "json"
    })
    
    line = '{"level": "info", "message": "test log", "timestamp": "2026-01-12"}'
    parsed = source._parse_json(line)
    
    assert parsed is not None
    assert parsed["level"] == "info"
    assert parsed["message"] == "test log"


@pytest.mark.asyncio
async def test_metrics_threshold_checking():
    """Test metrics threshold checking."""
    from chatops.irc.bot_engine.ingestion.metrics import MetricsIngestion
    
    source = MetricsIngestion("metrics_test", {
        "metric_type": "prometheus",
        "connection": {"host": "localhost", "port": 9090},
        "query": "cpu_usage",
        "threshold": 80,
        "threshold_condition": "gt"
    })
    
    # Test greater than
    assert source._check_threshold(85) == True
    assert source._check_threshold(75) == False
    
    # Test less than
    source.threshold_condition = "lt"
    assert source._check_threshold(75) == True
    assert source._check_threshold(85) == False
    
    # Test equal
    source.threshold_condition = "eq"
    assert source._check_threshold(80) == True
    assert source._check_threshold(85) == False
