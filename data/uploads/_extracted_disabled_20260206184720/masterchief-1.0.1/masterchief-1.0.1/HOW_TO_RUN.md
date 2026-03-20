# 🚀 GET IT RUNNING - SIMPLE INSTRUCTIONS

## ONE COMMAND TO RUN EVERYTHING:

```bash
python run.py
```

That's it! This single file starts the entire platform including the data upload web GUI.

## Step-by-Step (First Time):

### 1. Install Dependencies (One Time Only)

```bash
pip install -r requirements.txt
```

This installs Flask, SocketIO, and all other required packages.

### 2. Run the Platform

```bash
python run.py
```

### 3. Open Your Browser

Go to: **http://localhost:8080/api/v1/data/upload**

You'll see:
- 📤 **Upload Page** - Drag and drop files
- 📁 **Browse Page** - View all files
- ⚙️ **Manage Page** - Statistics and analytics

## What Gets Started:

✅ Flask web server  
✅ Data upload REST API  
✅ Three web GUI pages  
✅ All platform features  

## Upload Training Data for Echo:

1. Open http://localhost:8080/api/v1/data/upload
2. Drag a file onto the upload area
3. Select "Training" or "Ingestion"
4. Click "Upload File"
5. Done! Echo can now learn from your data

## Supported Files:

- **Text**: `.txt`, `.md`, `.log`
- **Data**: `.json`, `.yaml`, `.csv`, `.xml`
- **Audio**: `.wav`, `.mp3`, `.ogg`, `.flac` ← For voice training!
- **Archives**: `.zip`, `.tar`, `.gz`

## Troubleshooting:

**Problem**: `ModuleNotFoundError: No module named 'flask'`  
**Solution**: Run `pip install -r requirements.txt`

**Problem**: Port 8080 already in use  
**Solution**: Edit `run.py` line 87 and change `port=8080` to another port

**Problem**: Can't access web interface  
**Solution**: Make sure you see "✅ Platform ready!" message, then open http://localhost:8080/api/v1/data/upload

## That's It!

**ONE FILE. ONE COMMAND. EVERYTHING WORKS.**

```bash
python run.py
```

🌙 MasterChief makes it simple.
