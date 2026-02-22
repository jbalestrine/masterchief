"""Unit tests for data upload API."""
import json
import shutil
import pytest
from pathlib import Path
from io import BytesIO
from platform.data.api import data_bp, init_directories, allowed_file, get_file_hash


@pytest.fixture
def app():
    """Create Flask app for testing."""
    from flask import Flask
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(data_bp, url_prefix='/api/v1/data')
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def cleanup():
    """Cleanup test data after tests."""
    yield
    # Clean up test files
    for folder in [Path("data/uploads"), Path("data/training")]:
        if folder.exists():
            shutil.rmtree(folder)


def test_allowed_file():
    """Test file extension validation."""
    # Valid files
    assert allowed_file("test.json") == "data"
    assert allowed_file("test.yaml") == "data"
    assert allowed_file("test.yml") == "data"
    assert allowed_file("test.csv") == "data"
    assert allowed_file("test.txt") == "text"
    assert allowed_file("test.wav") == "audio"
    assert allowed_file("test.mp3") == "audio"
    
    # Invalid files
    assert allowed_file("test.exe") is None
    assert allowed_file("test.sh") is None
    assert allowed_file("test") is None


def test_init_directories():
    """Test directory initialization."""
    init_directories()
    
    # Check upload directories
    assert Path("data/uploads").exists()
    assert Path("data/uploads/text").exists()
    assert Path("data/uploads/data").exists()
    assert Path("data/uploads/audio").exists()
    assert Path("data/uploads/archive").exists()
    
    # Check training directories
    assert Path("data/training").exists()
    assert Path("data/training/text").exists()
    assert Path("data/training/data").exists()
    assert Path("data/training/audio").exists()
    assert Path("data/training/archive").exists()


def test_upload_json_file(client, cleanup):
    """Test uploading a JSON file."""
    data = {
        'file': (BytesIO(b'{"test": "data"}'), 'test.json'),
        'purpose': 'ingestion',
        'description': 'Test JSON file'
    }
    
    response = client.post('/api/v1/data/upload', 
                          data=data,
                          content_type='multipart/form-data')
    
    assert response.status_code == 201
    result = json.loads(response.data)
    assert result['success'] is True
    assert 'file' in result
    assert result['file']['category'] == 'data'
    assert result['file']['purpose'] == 'ingestion'


def test_upload_training_file(client, cleanup):
    """Test uploading a training file."""
    data = {
        'file': (BytesIO(b'This is training data'), 'training.txt'),
        'purpose': 'training',
        'description': 'Training text file'
    }
    
    response = client.post('/api/v1/data/upload', 
                          data=data,
                          content_type='multipart/form-data')
    
    assert response.status_code == 201
    result = json.loads(response.data)
    assert result['success'] is True
    assert result['file']['purpose'] == 'training'
    assert result['file']['category'] == 'text'


def test_upload_with_metadata(client, cleanup):
    """Test uploading a file with custom metadata."""
    metadata = {
        'source': 'test',
        'version': '1.0'
    }
    
    data = {
        'file': (BytesIO(b'test content'), 'test.txt'),
        'purpose': 'ingestion',
        'metadata': json.dumps(metadata)
    }
    
    response = client.post('/api/v1/data/upload', 
                          data=data,
                          content_type='multipart/form-data')
    
    assert response.status_code == 201


def test_upload_invalid_file_type(client, cleanup):
    """Test uploading an invalid file type."""
    data = {
        'file': (BytesIO(b'test'), 'test.exe'),
        'purpose': 'ingestion'
    }
    
    response = client.post('/api/v1/data/upload', 
                          data=data,
                          content_type='multipart/form-data')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result


def test_upload_no_file(client, cleanup):
    """Test upload without file."""
    response = client.post('/api/v1/data/upload')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result


def test_upload_invalid_purpose(client, cleanup):
    """Test upload with invalid purpose."""
    data = {
        'file': (BytesIO(b'test'), 'test.txt'),
        'purpose': 'invalid'
    }
    
    response = client.post('/api/v1/data/upload', 
                          data=data,
                          content_type='multipart/form-data')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result


def test_list_files_empty(client, cleanup):
    """Test listing files when empty."""
    response = client.get('/api/v1/data/files')
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] is True
    assert result['total'] == 0
    assert len(result['files']) == 0


def test_list_files_with_uploads(client, cleanup):
    """Test listing files after uploads."""
    # Upload a file first
    data = {
        'file': (BytesIO(b'test'), 'test.txt'),
        'purpose': 'ingestion'
    }
    client.post('/api/v1/data/upload', 
               data=data,
               content_type='multipart/form-data')
    
    # List files
    response = client.get('/api/v1/data/files')
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] is True
    assert result['total'] >= 1


def test_list_files_filter_by_purpose(client, cleanup):
    """Test filtering files by purpose."""
    # Upload ingestion file
    data1 = {
        'file': (BytesIO(b'test1'), 'test1.txt'),
        'purpose': 'ingestion'
    }
    client.post('/api/v1/data/upload', 
               data=data1,
               content_type='multipart/form-data')
    
    # Upload training file
    data2 = {
        'file': (BytesIO(b'test2'), 'test2.txt'),
        'purpose': 'training'
    }
    client.post('/api/v1/data/upload', 
               data=data2,
               content_type='multipart/form-data')
    
    # Filter by ingestion
    response = client.get('/api/v1/data/files?purpose=ingestion')
    result = json.loads(response.data)
    assert all(f['purpose'] == 'ingestion' for f in result['files'])
    
    # Filter by training
    response = client.get('/api/v1/data/files?purpose=training')
    result = json.loads(response.data)
    assert all(f['purpose'] == 'training' for f in result['files'])


def test_get_stats(client, cleanup):
    """Test getting upload statistics."""
    # Upload some files
    for i in range(3):
        data = {
            'file': (BytesIO(b'test' * 100), f'test{i}.txt'),
            'purpose': 'ingestion'
        }
        client.post('/api/v1/data/upload', 
                   data=data,
                   content_type='multipart/form-data')
    
    response = client.get('/api/v1/data/stats')
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] is True
    assert 'stats' in result
    assert result['stats']['total_files'] >= 3
    assert result['stats']['total_size'] > 0


def test_delete_file(client, cleanup):
    """Test deleting a file."""
    # Upload a file
    data = {
        'file': (BytesIO(b'test content'), 'test.txt'),
        'purpose': 'ingestion'
    }
    upload_response = client.post('/api/v1/data/upload', 
                                  data=data,
                                  content_type='multipart/form-data')
    
    upload_result = json.loads(upload_response.data)
    file_path = upload_result['file']['path']
    
    # Delete the file
    delete_response = client.delete(f'/api/v1/data/files/{file_path}')
    
    assert delete_response.status_code == 200
    delete_result = json.loads(delete_response.data)
    assert delete_result['success'] is True


def test_get_file_metadata(client, cleanup):
    """Test getting file metadata."""
    # Upload a file
    data = {
        'file': (BytesIO(b'test content'), 'test.txt'),
        'purpose': 'ingestion',
        'description': 'Test file'
    }
    upload_response = client.post('/api/v1/data/upload', 
                                  data=data,
                                  content_type='multipart/form-data')
    
    upload_result = json.loads(upload_response.data)
    file_path = upload_result['file']['path']
    
    # Get metadata
    response = client.get(f'/api/v1/data/files/{file_path}?metadata=true')
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] is True
    assert 'metadata' in result
    assert result['metadata']['description'] == 'Test file'
