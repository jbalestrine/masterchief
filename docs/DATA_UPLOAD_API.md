# Data Upload API Documentation

## Overview

The Data Upload API provides a comprehensive interface for uploading, managing, and processing training data for Echo (the bot) and general data ingestion. This system allows users to upload files through a REST API, which are then automatically categorized, stored, and made available for ingestion and training purposes.

## Features

- **File Upload**: Upload files for training or data ingestion
- **Multiple Formats**: Support for JSON, YAML, CSV, XML, text, audio, and archive files
- **Automatic Categorization**: Files are automatically categorized by type
- **Metadata Tracking**: Track upload time, file hash, size, and custom metadata
- **File Management**: List, download, and delete uploaded files
- **Statistics**: Get detailed statistics about uploaded data
- **Training Integration**: Uploaded training data can be used for voice cloning and bot training
- **Ingestion Integration**: Files uploaded for ingestion are automatically processed

## API Endpoints

### Upload File

Upload a file for data ingestion or training.

**Endpoint:** `POST /api/v1/data/upload`

**Content-Type:** `multipart/form-data`

**Form Parameters:**
- `file` (required): The file to upload
- `purpose` (optional): Either `'training'` or `'ingestion'` (default: `'ingestion'`)
- `category` (optional): File category (auto-detected from extension if not provided)
- `description` (optional): Description of the file
- `metadata` (optional): Additional metadata as JSON string

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "file": {
    "path": "data/uploads/data/training_data_20260112_234500.json",
    "filename": "training_data_20260112_234500.json",
    "original_filename": "training_data.json",
    "category": "data",
    "purpose": "ingestion",
    "size": 1024,
    "hash": "abc123...",
    "uploaded_at": "2026-01-12T23:45:00"
  }
}
```

**Example using curl:**
```bash
# Upload a training file
curl -X POST http://localhost:8080/api/v1/data/upload \
  -F "file=@training_data.json" \
  -F "purpose=training" \
  -F "description=Bot training data"

# Upload audio for voice training
curl -X POST http://localhost:8080/api/v1/data/upload \
  -F "file=@voice_sample.wav" \
  -F "purpose=training" \
  -F "category=audio" \
  -F "description=Echo voice sample"

# Upload with custom metadata
curl -X POST http://localhost:8080/api/v1/data/upload \
  -F "file=@data.csv" \
  -F "purpose=ingestion" \
  -F 'metadata={"source":"production","version":"1.0"}'
```

**Example using Python:**
```python
import requests

# Upload a file
with open('training_data.json', 'rb') as f:
    files = {'file': f}
    data = {
        'purpose': 'training',
        'description': 'Bot training data'
    }
    response = requests.post('http://localhost:8080/api/v1/data/upload', 
                            files=files, 
                            data=data)
    print(response.json())
```

### List Files

List uploaded files with optional filtering.

**Endpoint:** `GET /api/v1/data/files`

**Query Parameters:**
- `purpose` (optional): Filter by purpose (`'training'` or `'ingestion'`)
- `category` (optional): Filter by category (`'text'`, `'data'`, `'audio'`, `'archive'`)
- `limit` (optional): Maximum number of files to return (default: 100)
- `offset` (optional): Number of files to skip (default: 0)

**Response:**
```json
{
  "success": true,
  "total": 10,
  "limit": 100,
  "offset": 0,
  "files": [
    {
      "path": "data/training/audio/voice_sample_20260112_234500.wav",
      "filename": "voice_sample_20260112_234500.wav",
      "category": "audio",
      "purpose": "training",
      "size": 524288,
      "hash": "def456...",
      "uploaded_at": "2026-01-12T23:45:00",
      "description": "Echo voice sample"
    }
  ]
}
```

**Example:**
```bash
# List all files
curl http://localhost:8080/api/v1/data/files

# List training files only
curl "http://localhost:8080/api/v1/data/files?purpose=training"

# List audio files
curl "http://localhost:8080/api/v1/data/files?category=audio"

# Pagination
curl "http://localhost:8080/api/v1/data/files?limit=10&offset=20"
```

### Get File

Download a file or retrieve its metadata.

**Endpoint:** `GET /api/v1/data/files/<file_path>`

**Query Parameters:**
- `metadata` (optional): Set to `'true'` to get metadata instead of file content

**Response (metadata):**
```json
{
  "success": true,
  "metadata": {
    "filename": "training_data.json",
    "saved_as": "training_data_20260112_234500.json",
    "category": "data",
    "purpose": "training",
    "size": 1024,
    "hash": "abc123...",
    "uploaded_at": "2026-01-12T23:45:00",
    "description": "Bot training data"
  }
}
```

**Example:**
```bash
# Download file
curl http://localhost:8080/api/v1/data/files/training/audio/voice.wav -o voice.wav

# Get metadata
curl "http://localhost:8080/api/v1/data/files/training/audio/voice.wav?metadata=true"
```

### Delete File

Delete a file and its metadata.

**Endpoint:** `DELETE /api/v1/data/files/<file_path>`

**Response:**
```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8080/api/v1/data/files/training/audio/voice.wav
```

### Get Statistics

Get statistics about uploaded data.

**Endpoint:** `GET /api/v1/data/stats`

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_files": 25,
    "total_size": 10485760,
    "by_purpose": {
      "ingestion": {
        "count": 15,
        "size": 6291456,
        "by_category": {
          "data": {"count": 10, "size": 5242880},
          "text": {"count": 5, "size": 1048576}
        }
      },
      "training": {
        "count": 10,
        "size": 4194304,
        "by_category": {
          "audio": {"count": 8, "size": 3670016},
          "text": {"count": 2, "size": 524288}
        }
      }
    },
    "by_category": {
      "data": {"count": 10, "size": 5242880},
      "text": {"count": 7, "size": 1572864},
      "audio": {"count": 8, "size": 3670016}
    }
  }
}
```

**Example:**
```bash
curl http://localhost:8080/api/v1/data/stats
```

## Supported File Types

### Data Files (`data` category)
- JSON (`.json`)
- YAML (`.yaml`, `.yml`)
- CSV (`.csv`)
- XML (`.xml`)

### Text Files (`text` category)
- Plain text (`.txt`)
- Markdown (`.md`)
- Log files (`.log`)

### Audio Files (`audio` category)
- WAV (`.wav`)
- MP3 (`.mp3`)
- OGG (`.ogg`)
- FLAC (`.flac`)

### Archive Files (`archive` category)
- ZIP (`.zip`)
- TAR (`.tar`)
- GZIP (`.gz`, `.tgz`)

## Use Cases

### 1. Training Echo's Voice

Upload audio samples for voice cloning:

```bash
# Upload multiple voice samples
for sample in voice_sample_*.wav; do
  curl -X POST http://localhost:8080/api/v1/data/upload \
    -F "file=@$sample" \
    -F "purpose=training" \
    -F "category=audio" \
    -F "description=Echo voice training sample"
done
```

### 2. Bot Knowledge Training

Upload training data for the bot to learn from:

```bash
# Upload JSON training data
curl -X POST http://localhost:8080/api/v1/data/upload \
  -F "file=@bot_knowledge.json" \
  -F "purpose=training" \
  -F "description=Bot knowledge base"

# Upload CSV with Q&A pairs
curl -X POST http://localhost:8080/api/v1/data/upload \
  -F "file=@qa_pairs.csv" \
  -F "purpose=training" \
  -F "description=Question and answer pairs"
```

### 3. Data Ingestion

Upload files for automatic processing by the ingestion system:

```bash
# Upload metrics data
curl -X POST http://localhost:8080/api/v1/data/upload \
  -F "file=@metrics.json" \
  -F "purpose=ingestion" \
  -F 'metadata={"source":"prometheus","timestamp":"2026-01-12T23:00:00"}'

# Upload logs
curl -X POST http://localhost:8080/api/v1/data/upload \
  -F "file=@application.log" \
  -F "purpose=ingestion" \
  -F "description=Application logs for analysis"
```

### 4. Bulk Upload Script

Python script for bulk uploading:

```python
import os
import requests
from pathlib import Path

def bulk_upload(directory, purpose='training'):
    """Upload all supported files in a directory."""
    api_url = 'http://localhost:8080/api/v1/data/upload'
    
    for filepath in Path(directory).glob('*'):
        if not filepath.is_file():
            continue
        
        print(f"Uploading {filepath.name}...")
        
        with open(filepath, 'rb') as f:
            files = {'file': f}
            data = {'purpose': purpose}
            
            response = requests.post(api_url, files=files, data=data)
            
            if response.status_code == 201:
                print(f"  ✓ Uploaded successfully")
            else:
                print(f"  ✗ Failed: {response.json().get('error', 'Unknown error')}")

# Upload all training data
bulk_upload('./training_data', purpose='training')
```

## Integration with Ingestion System

When files are uploaded with `purpose=ingestion`, they are automatically made available to the existing data ingestion system. The ingestion system can then:

1. **Process the file** based on its type
2. **Parse the content** (JSON, CSV, XML, etc.)
3. **Trigger appropriate handlers** registered in the bot
4. **Generate events** that the bot can respond to

This seamless integration allows uploaded files to be immediately processed by the bot's ingestion pipeline.

## Security Considerations

1. **File Type Validation**: Only allowed file extensions can be uploaded
2. **Secure Filenames**: Filenames are sanitized using `secure_filename()`
3. **Path Validation**: File paths are validated to prevent directory traversal attacks
4. **File Hashing**: SHA-256 hashes are computed for integrity verification
5. **Size Limits**: Maximum file size is 100MB (configurable)

## Directory Structure

Uploaded files are organized as follows:

```
data/
├── uploads/          # Ingestion files
│   ├── text/
│   ├── data/
│   ├── audio/
│   └── archive/
└── training/         # Training files
    ├── text/
    ├── data/
    ├── audio/
    └── archive/
```

Each file has an associated `.meta.json` file containing metadata.

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful GET/DELETE request
- `201 Created`: File uploaded successfully
- `400 Bad Request`: Invalid request (missing file, invalid parameters)
- `403 Forbidden`: Invalid file path or security violation
- `404 Not Found`: File not found
- `500 Internal Server Error`: Server error

All error responses include a JSON body with an `error` field describing the issue.

## Future Enhancements

Planned improvements for the upload system:

1. **Web UI**: Browser-based upload interface
2. **Batch Upload**: Support for uploading multiple files at once
3. **File Processing Status**: Track processing status of uploaded files
4. **Automatic Training**: Trigger training jobs when sufficient data is uploaded
5. **File Validation**: Content validation beyond just file extension
6. **Compression**: Automatic compression of large files
7. **Cloud Storage**: Option to store files in cloud storage (S3, Azure Blob)
8. **Access Control**: User authentication and authorization for uploads
