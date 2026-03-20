# Data Upload System for Echo Bot Training

## Overview

This system provides a simple and powerful way to upload training data and files that Echo (the bot) can learn from. You can upload various types of files including training data, audio samples for voice cloning, configuration files, and more.

## Quick Start

### 1. Start the Platform

First, start the MasterChief platform:

```bash
cd /home/runner/work/masterchief/masterchief
python platform/app.py
```

The API will be available at: `http://localhost:8080`

### 2. Upload Your First File

#### Using curl (Command Line)

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
  -F "description=Echo voice sample"
```

#### Using the Web Interface

1. Open `docs/examples/data-upload-ui.html` in your web browser
2. Drag and drop your file or click to browse
3. Select the purpose (Training or Ingestion)
4. Add a description
5. Click "Upload File"

#### Using Python

```python
import requests

def upload_file(filepath, purpose='training', description=''):
    """Upload a file to the platform."""
    url = 'http://localhost:8080/api/v1/data/upload'
    
    with open(filepath, 'rb') as f:
        files = {'file': f}
        data = {
            'purpose': purpose,
            'description': description
        }
        
        response = requests.post(url, files=files, data=data)
        return response.json()

# Upload a file
result = upload_file('training_data.json', 
                     purpose='training', 
                     description='Bot knowledge base')
print(result)
```

## What Can You Upload?

### For Training Echo

Echo can learn from various types of data:

1. **Text Data** (`.txt`, `.md`)
   - Conversation examples
   - Q&A pairs
   - Knowledge base articles

2. **Structured Data** (`.json`, `.yaml`, `.csv`)
   - Training datasets
   - Configuration examples
   - Command responses

3. **Audio Files** (`.wav`, `.mp3`, `.ogg`, `.flac`)
   - Voice samples for voice cloning
   - Pronunciation examples
   - Audio training data

### For Data Ingestion

Files uploaded for ingestion are automatically processed:

1. **Logs** (`.log`)
   - Application logs
   - System logs
   - Error logs

2. **Metrics** (`.json`, `.csv`)
   - Performance metrics
   - System statistics
   - Monitoring data

3. **Configuration** (`.yaml`, `.json`)
   - Service configurations
   - Deployment configs
   - Environment settings

## Common Use Cases

### 1. Training Echo's Voice

To train Echo's voice, upload multiple audio samples (5-10 samples recommended):

```bash
# Upload voice samples
for i in {1..5}; do
  curl -X POST http://localhost:8080/api/v1/data/upload \
    -F "file=@voice_sample_$i.wav" \
    -F "purpose=training" \
    -F "category=audio" \
    -F "description=Echo voice training sample $i"
done
```

### 2. Teaching Echo New Commands

Upload JSON files with command definitions:

```json
{
  "commands": [
    {
      "name": "deploy",
      "description": "Deploy an application",
      "response": "Deploying {app} to {environment}...",
      "examples": [
        "deploy myapp to production",
        "deploy the api to staging"
      ]
    }
  ]
}
```

```bash
curl -X POST http://localhost:8080/api/v1/data/upload \
  -F "file=@commands.json" \
  -F "purpose=training" \
  -F "description=New bot commands"
```

### 3. Bulk Upload Training Data

Upload multiple files at once using Python:

```python
import os
import requests
from pathlib import Path

def bulk_upload(directory, purpose='training'):
    """Upload all files in a directory."""
    api_url = 'http://localhost:8080/api/v1/data/upload'
    results = []
    
    for filepath in Path(directory).glob('*'):
        if not filepath.is_file():
            continue
        
        print(f"Uploading {filepath.name}...")
        
        with open(filepath, 'rb') as f:
            files = {'file': f}
            data = {'purpose': purpose}
            
            response = requests.post(api_url, files=files, data=data)
            results.append({
                'file': filepath.name,
                'success': response.status_code == 201,
                'response': response.json()
            })
    
    return results

# Upload all files in a directory
results = bulk_upload('./training_data', purpose='training')

# Print summary
successful = sum(1 for r in results if r['success'])
print(f"\nUploaded {successful}/{len(results)} files successfully")
```

### 4. Monitoring Uploads

Check what files have been uploaded:

```bash
# List all files
curl http://localhost:8080/api/v1/data/files

# List only training files
curl "http://localhost:8080/api/v1/data/files?purpose=training"

# List only audio files
curl "http://localhost:8080/api/v1/data/files?category=audio"

# Get statistics
curl http://localhost:8080/api/v1/data/stats
```

## File Organization

Uploaded files are automatically organized by purpose and category:

```
data/
├── uploads/          # Files for ingestion
│   ├── text/
│   ├── data/
│   ├── audio/
│   └── archive/
└── training/         # Files for training
    ├── text/
    ├── data/
    ├── audio/
    └── archive/
```

Each file has an associated `.meta.json` file with metadata:
- Original filename
- Upload timestamp
- File hash (for integrity)
- Description
- Custom metadata

## API Endpoints

Full API documentation is available in [`docs/DATA_UPLOAD_API.md`](../DATA_UPLOAD_API.md)

- `POST /api/v1/data/upload` - Upload a file
- `GET /api/v1/data/files` - List uploaded files
- `GET /api/v1/data/files/<path>` - Get/download a file
- `DELETE /api/v1/data/files/<path>` - Delete a file
- `GET /api/v1/data/stats` - Get upload statistics

## Troubleshooting

### File Type Not Allowed

Make sure your file has one of the supported extensions:
- Text: `.txt`, `.md`, `.log`
- Data: `.json`, `.yaml`, `.yml`, `.csv`, `.xml`
- Audio: `.wav`, `.mp3`, `.ogg`, `.flac`
- Archive: `.zip`, `.tar`, `.gz`, `.tgz`

### Upload Fails

1. Check that the platform is running: `curl http://localhost:8080/health`
2. Check file size (max 100MB by default)
3. Check file permissions
4. Check platform logs for errors

### Can't See Uploaded Files

1. Verify the upload was successful (check response)
2. List files: `curl http://localhost:8080/api/v1/data/files`
3. Check the correct purpose: `?purpose=training` or `?purpose=ingestion`

## Next Steps

After uploading files:

1. **For Training Data**: The bot will use these files to learn and improve responses
2. **For Voice Samples**: Use the voice trainer to create a voice model
3. **For Ingestion**: Files are automatically processed by the ingestion system

See the main documentation for more details on:
- Voice cloning: `docs/VOICE_AUTOMATION_SUMMARY.md`
- Data ingestion: `DATA_INGESTION_SUMMARY.md`
- Bot commands: `chatops/irc/bot-engine/README.md`

## Examples

See the `docs/examples/` directory for more examples:
- `data-upload-ui.html` - Web interface for uploads
- `data-ingestion-examples.md` - Data ingestion examples

## Support

For issues or questions:
- Check the main README: `README.md`
- Review API docs: `docs/DATA_UPLOAD_API.md`
- Open an issue on GitHub
