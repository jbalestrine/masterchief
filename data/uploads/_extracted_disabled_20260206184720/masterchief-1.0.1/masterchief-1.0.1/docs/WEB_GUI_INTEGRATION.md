# Web GUI Integration Guide

## 🎉 All Features Are Now Web GUI!

The data upload system is now **fully integrated** into the MasterChief platform with a complete web interface. No more standalone HTML files - everything is part of the main application!

## 🚀 Quick Start

### 1. Start the Platform

```bash
cd /home/runner/work/masterchief/masterchief
python run.py
```

The server will start on: **http://localhost:8080**

### 2. Access the Web GUI

Navigate to any of these pages:

- **Upload**: http://localhost:8080/api/v1/data/upload
- **Browse**: http://localhost:8080/api/v1/data/browse
- **Manage**: http://localhost:8080/api/v1/data/manage

## 📍 Web GUI Pages

### 1. Upload Page (`/api/v1/data/upload`)

**Features:**
- ✅ Drag-and-drop file upload
- ✅ Click to browse files
- ✅ Purpose selection (Training/Ingestion)
- ✅ Description field
- ✅ Real-time upload progress bar
- ✅ Live statistics (total files, size, etc.)
- ✅ Recent uploads list

**How to Use:**
1. Drag a file onto the upload area (or click to browse)
2. Select purpose: "Training" for Echo to learn, "Ingestion" for processing
3. Add an optional description
4. Click "Upload File"
5. See immediate feedback with progress bar

**Supported Files:**
- Text: `.txt`, `.md`, `.log`
- Data: `.json`, `.yaml`, `.csv`, `.xml`
- Audio: `.wav`, `.mp3`, `.ogg`, `.flac` (for voice training!)
- Archives: `.zip`, `.tar`, `.gz`

### 2. Browse Page (`/api/v1/data/browse`)

**Features:**
- ✅ Grid view of all files with cards
- ✅ Filter by purpose (Training/Ingestion)
- ✅ Filter by category (Text/Data/Audio/Archive)
- ✅ File icons based on type
- ✅ Download button on each file
- ✅ Delete button with confirmation
- ✅ File metadata (size, date, description)

**How to Use:**
1. View all uploaded files in a nice grid
2. Use dropdown filters to narrow down files
3. Click "Download" to get any file
4. Click "Delete" to remove files (with confirmation)
5. See file details including badges for purpose and category

### 3. Manage Page (`/api/v1/data/manage`)

**Features:**
- ✅ Overview statistics dashboard
- ✅ Category breakdown with progress bars
- ✅ Percentage distribution charts
- ✅ Quick action buttons
- ✅ Recent activity timeline
- ✅ Refresh statistics button
- ✅ Cleanup tools

**How to Use:**
1. View overall statistics at the top
2. See breakdown by category with visual charts
3. Use quick action buttons for common tasks
4. Review recent activity timeline
5. Click "Refresh Stats" to update numbers

## 🎨 Design Features

### Unified Theme
- **Colors**: Purple/blue gradient matching MasterChief brand
- **Icons**: Echo moon icon (🌙) throughout
- **Cards**: Rounded corners, subtle shadows
- **Hover Effects**: Smooth transitions and animations

### Navigation
- **Header**: Always visible with platform name and nav links
- **Active Indicators**: Current page highlighted
- **Responsive**: Works on all screen sizes

### User Experience
- **Real-time Updates**: AJAX calls for dynamic content
- **Feedback**: Success/error messages for all actions
- **Progress**: Visual indicators for uploads
- **Confirmation**: Dialogs before destructive actions

## 🔧 Integration with MasterChief

### Blueprint Registration

The data upload system is automatically loaded when you start the platform. It's registered in `platform/app.py`:

```python
# Data Upload API
from platform.data import data_bp
app.register_blueprint(data_bp, url_prefix='/api/v1/data')
```

### URL Structure

All data upload URLs are under `/api/v1/data/`:

**Web Pages:**
- `/api/v1/data/` or `/api/v1/data/upload` - Upload page
- `/api/v1/data/browse` - Browse files page
- `/api/v1/data/manage` - Management page

**API Endpoints:**
- `/api/v1/data/api/upload` - Upload API (POST)
- `/api/v1/data/api/files` - List files API (GET)
- `/api/v1/data/api/files/<path>` - Get/download file API (GET)
- `/api/v1/data/api/files/<path>` - Delete file API (DELETE)
- `/api/v1/data/api/stats` - Statistics API (GET)

### Templates

All templates are in `platform/templates/`:
- `base.html` - Base layout with navigation
- `data/upload.html` - Upload page
- `data/browse.html` - Browse page
- `data/manage.html` - Management page

## 📊 Usage Examples

### Upload Training Data for Echo

1. Go to: http://localhost:8080/api/v1/data/upload
2. Drag and drop `training_commands.json`
3. Select "Training"
4. Add description: "Bot command definitions"
5. Click "Upload File"
6. ✅ Done! Echo can now learn from this data

### Upload Voice Samples

1. Go to: http://localhost:8080/api/v1/data/upload
2. Upload multiple `.wav` files (one at a time)
3. Select "Training" for each
4. Add descriptions like "Voice sample 1", "Voice sample 2", etc.
5. ✅ Echo can use these for voice cloning!

### Browse and Download Files

1. Go to: http://localhost:8080/api/v1/data/browse
2. Filter by "Training" to see training files
3. Filter by "Audio" to see voice samples
4. Click "Download" on any file to get it
5. Click "Delete" to remove unwanted files

### Check Statistics

1. Go to: http://localhost:8080/api/v1/data/manage
2. View total files and size at the top
3. See breakdown by category in the middle
4. Review recent activity at the bottom
5. Click "Refresh Stats" to update numbers

## 🔒 Security

The web GUI maintains all security features:
- ✅ File type validation (whitelist)
- ✅ Secure filename handling
- ✅ Path validation (no directory traversal)
- ✅ File size limits (100MB)
- ✅ SHA-256 file hashing
- ✅ Metadata tracking

## 🎯 Benefits

### For Users
- **Easy to Use**: No command line needed!
- **Visual**: See all files in a nice interface
- **Fast**: Real-time updates and feedback
- **Complete**: All features accessible through web

### For Administrators
- **Integrated**: Part of the main platform
- **Maintainable**: Uses standard Flask templates
- **Extensible**: Easy to add new features
- **Consistent**: Matches MasterChief design

## 🚦 Troubleshooting

### Can't Access Web GUI

**Problem**: Pages not loading
**Solution**: 
1. Check if platform is running: `curl http://localhost:8080`
2. Verify port 8080 is available
3. Check logs for errors

### Upload Not Working

**Problem**: File upload fails
**Solution**:
1. Check file type is supported
2. Verify file size is under 100MB
3. Check browser console for errors
4. Ensure `data/` directory exists and is writable

### Files Not Showing

**Problem**: Browse page empty
**Solution**:
1. Upload some files first
2. Click refresh in browser
3. Check filters aren't hiding files
4. Verify API is responding: `curl http://localhost:8080/api/v1/data/api/files`

## 📝 Next Steps

1. **Upload Training Data**: Use the upload page to add training files
2. **Train Echo's Voice**: Upload audio samples for voice cloning
3. **Manage Files**: Use browse and manage pages for file operations
4. **Monitor Usage**: Check statistics regularly

## 🎉 Summary

**ALL features are now accessible through the web GUI!**

✅ No standalone HTML files
✅ Fully integrated with MasterChief platform
✅ Professional UI matching the platform theme
✅ Complete functionality (upload, browse, download, delete, stats)
✅ Real-time updates and feedback
✅ Responsive design for all devices

**🌙 Echo is ready to learn through the web interface!**
