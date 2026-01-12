"""Data upload and management API."""
import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app, send_file

logger = logging.getLogger(__name__)

data_bp = Blueprint('data', __name__)

# Configuration
UPLOAD_FOLDER = Path("data/uploads")
TRAINING_FOLDER = Path("data/training")
ALLOWED_EXTENSIONS = {
    'text': {'txt', 'md', 'log'},
    'data': {'json', 'yaml', 'yml', 'csv', 'xml'},
    'audio': {'wav', 'mp3', 'ogg', 'flac'},
    'archive': {'zip', 'tar', 'gz', 'tgz'}
}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


def init_directories():
    """Initialize data directories."""
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    TRAINING_FOLDER.mkdir(parents=True, exist_ok=True)
    for category in ['text', 'data', 'audio', 'archive']:
        (UPLOAD_FOLDER / category).mkdir(parents=True, exist_ok=True)
        (TRAINING_FOLDER / category).mkdir(parents=True, exist_ok=True)


def allowed_file(filename: str) -> Optional[str]:
    """Check if file extension is allowed and return category."""
    if '.' not in filename:
        return None
    
    ext = filename.rsplit('.', 1)[1].lower()
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return category
    return None


def get_file_hash(filepath: Path) -> str:
    """Calculate SHA256 hash of file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def save_metadata(filepath: Path, metadata: Dict[str, Any]):
    """Save metadata for uploaded file."""
    metadata_path = filepath.parent / f"{filepath.stem}.meta.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)


def load_metadata(filepath: Path) -> Optional[Dict[str, Any]]:
    """Load metadata for a file."""
    metadata_path = filepath.parent / f"{filepath.stem}.meta.json"
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            return json.load(f)
    return None


@data_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a file for data ingestion or training.
    
    Form data:
        - file: File to upload (required)
        - purpose: 'training' or 'ingestion' (default: 'ingestion')
        - category: File category (optional, auto-detected from extension)
        - description: File description (optional)
        - metadata: Additional metadata as JSON string (optional)
    
    Returns:
        JSON response with upload status and file information
    """
    init_directories()
    
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Get parameters
    purpose = request.form.get('purpose', 'ingestion')
    if purpose not in ['training', 'ingestion']:
        return jsonify({"error": "Invalid purpose. Must be 'training' or 'ingestion'"}), 400
    
    description = request.form.get('description', '')
    user_metadata = request.form.get('metadata', '{}')
    
    try:
        user_metadata = json.loads(user_metadata)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid metadata JSON"}), 400
    
    # Validate file type
    category = allowed_file(file.filename)
    if category is None:
        allowed_exts = []
        for exts in ALLOWED_EXTENSIONS.values():
            allowed_exts.extend(exts)
        return jsonify({
            "error": f"File type not allowed. Allowed extensions: {', '.join(sorted(allowed_exts))}"
        }), 400
    
    # Override category if provided
    if 'category' in request.form:
        requested_category = request.form['category']
        if requested_category in ALLOWED_EXTENSIONS:
            category = requested_category
    
    # Secure filename
    filename = secure_filename(file.filename)
    
    # Determine target directory
    base_folder = TRAINING_FOLDER if purpose == 'training' else UPLOAD_FOLDER
    target_dir = base_folder / category
    
    # Add timestamp to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name_parts = filename.rsplit('.', 1)
    if len(name_parts) == 2:
        filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
    else:
        filename = f"{filename}_{timestamp}"
    
    filepath = target_dir / filename
    
    # Save file
    try:
        file.save(str(filepath))
        logger.info(f"File uploaded: {filepath}")
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500
    
    # Calculate file hash
    file_hash = get_file_hash(filepath)
    
    # Create metadata
    metadata = {
        "filename": file.filename,
        "saved_as": filename,
        "category": category,
        "purpose": purpose,
        "size": filepath.stat().st_size,
        "hash": file_hash,
        "uploaded_at": datetime.now().isoformat(),
        "description": description,
        **user_metadata
    }
    
    # Save metadata
    save_metadata(filepath, metadata)
    
    # Trigger ingestion if needed
    if purpose == 'ingestion':
        try:
            trigger_ingestion(filepath, category, metadata)
        except Exception as e:
            logger.error(f"Error triggering ingestion: {e}")
            # Don't fail the upload if ingestion fails
    
    return jsonify({
        "success": True,
        "message": "File uploaded successfully",
        "file": {
            "path": str(filepath.relative_to(base_folder.parent)),
            "filename": filename,
            "original_filename": file.filename,
            "category": category,
            "purpose": purpose,
            "size": metadata["size"],
            "hash": file_hash,
            "uploaded_at": metadata["uploaded_at"]
        }
    }), 201


@data_bp.route('/files', methods=['GET'])
def list_files():
    """
    List uploaded files.
    
    Query parameters:
        - purpose: Filter by purpose ('training' or 'ingestion')
        - category: Filter by category
        - limit: Maximum number of files to return (default: 100)
        - offset: Number of files to skip (default: 0)
    
    Returns:
        JSON response with list of files and their metadata
    """
    init_directories()
    
    # Get filters
    purpose = request.args.get('purpose')
    category = request.args.get('category')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    # Collect files
    files_list = []
    
    def scan_directory(base_folder: Path, folder_purpose: str):
        """Scan a directory for files."""
        for cat_dir in base_folder.iterdir():
            if not cat_dir.is_dir():
                continue
            
            cat_name = cat_dir.name
            if category and cat_name != category:
                continue
            
            for filepath in cat_dir.glob('*'):
                # Skip metadata files
                if filepath.suffix == '.json' and filepath.stem.endswith('.meta'):
                    continue
                
                if not filepath.is_file():
                    continue
                
                # Load metadata
                metadata = load_metadata(filepath)
                if metadata is None:
                    # Create basic metadata if missing
                    metadata = {
                        "filename": filepath.name,
                        "category": cat_name,
                        "purpose": folder_purpose,
                        "size": filepath.stat().st_size,
                        "uploaded_at": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                    }
                
                files_list.append({
                    "path": str(filepath.relative_to(base_folder.parent)),
                    "filename": filepath.name,
                    "category": cat_name,
                    "purpose": folder_purpose,
                    **metadata
                })
    
    # Scan directories based on purpose filter
    if purpose is None or purpose == 'ingestion':
        scan_directory(UPLOAD_FOLDER, 'ingestion')
    
    if purpose is None or purpose == 'training':
        scan_directory(TRAINING_FOLDER, 'training')
    
    # Sort by upload time (newest first)
    files_list.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
    
    # Apply pagination
    total = len(files_list)
    files_list = files_list[offset:offset + limit]
    
    return jsonify({
        "success": True,
        "total": total,
        "limit": limit,
        "offset": offset,
        "files": files_list
    })


@data_bp.route('/files/<path:file_path>', methods=['GET'])
def get_file(file_path: str):
    """
    Get a specific file.
    
    Args:
        file_path: Relative path to the file
    
    Returns:
        File download or file metadata (if ?metadata=true)
    """
    # Security: ensure path is within allowed directories
    try:
        full_path = Path("data") / file_path
        full_path = full_path.resolve()
        
        # Check if path is within data directory
        if not str(full_path).startswith(str(Path("data").resolve())):
            return jsonify({"error": "Invalid file path"}), 403
        
        if not full_path.exists():
            return jsonify({"error": "File not found"}), 404
        
        # Return metadata if requested
        if request.args.get('metadata') == 'true':
            metadata = load_metadata(full_path)
            if metadata is None:
                return jsonify({"error": "Metadata not found"}), 404
            return jsonify({"success": True, "metadata": metadata})
        
        # Return file
        return send_file(str(full_path), as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error getting file: {e}")
        return jsonify({"error": str(e)}), 500


@data_bp.route('/files/<path:file_path>', methods=['DELETE'])
def delete_file(file_path: str):
    """
    Delete a file and its metadata.
    
    Args:
        file_path: Relative path to the file
    
    Returns:
        JSON response with deletion status
    """
    try:
        full_path = Path("data") / file_path
        full_path = full_path.resolve()
        
        # Security check
        if not str(full_path).startswith(str(Path("data").resolve())):
            return jsonify({"error": "Invalid file path"}), 403
        
        if not full_path.exists():
            return jsonify({"error": "File not found"}), 404
        
        # Delete metadata file
        metadata_path = full_path.parent / f"{full_path.stem}.meta.json"
        if metadata_path.exists():
            metadata_path.unlink()
        
        # Delete file
        full_path.unlink()
        
        logger.info(f"File deleted: {full_path}")
        
        return jsonify({
            "success": True,
            "message": "File deleted successfully"
        })
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return jsonify({"error": str(e)}), 500


@data_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get statistics about uploaded data.
    
    Returns:
        JSON response with statistics
    """
    init_directories()
    
    stats = {
        "total_files": 0,
        "total_size": 0,
        "by_purpose": {},
        "by_category": {}
    }
    
    def count_files(base_folder: Path, purpose: str):
        """Count files in a directory."""
        count = 0
        size = 0
        by_category = {}
        
        for cat_dir in base_folder.iterdir():
            if not cat_dir.is_dir():
                continue
            
            cat_name = cat_dir.name
            cat_count = 0
            cat_size = 0
            
            for filepath in cat_dir.glob('*'):
                # Skip metadata files
                if filepath.suffix == '.json' and filepath.stem.endswith('.meta'):
                    continue
                
                if not filepath.is_file():
                    continue
                
                cat_count += 1
                cat_size += filepath.stat().st_size
            
            by_category[cat_name] = {
                "count": cat_count,
                "size": cat_size
            }
            count += cat_count
            size += cat_size
        
        return count, size, by_category
    
    # Count ingestion files
    ing_count, ing_size, ing_cats = count_files(UPLOAD_FOLDER, 'ingestion')
    stats["by_purpose"]["ingestion"] = {
        "count": ing_count,
        "size": ing_size,
        "by_category": ing_cats
    }
    
    # Count training files
    train_count, train_size, train_cats = count_files(TRAINING_FOLDER, 'training')
    stats["by_purpose"]["training"] = {
        "count": train_count,
        "size": train_size,
        "by_category": train_cats
    }
    
    # Aggregate by category
    all_categories = set(ing_cats.keys()) | set(train_cats.keys())
    for cat in all_categories:
        cat_count = ing_cats.get(cat, {}).get('count', 0) + train_cats.get(cat, {}).get('count', 0)
        cat_size = ing_cats.get(cat, {}).get('size', 0) + train_cats.get(cat, {}).get('size', 0)
        stats["by_category"][cat] = {
            "count": cat_count,
            "size": cat_size
        }
    
    stats["total_files"] = ing_count + train_count
    stats["total_size"] = ing_size + train_size
    
    return jsonify({
        "success": True,
        "stats": stats
    })


def trigger_ingestion(filepath: Path, category: str, metadata: Dict[str, Any]):
    """
    Trigger ingestion processing for uploaded file.
    
    This integrates with the existing ingestion system to process
    the uploaded file through the appropriate handlers.
    """
    logger.info(f"Triggering ingestion for {filepath}")
    
    # This is a placeholder for integration with the ingestion system
    # In a full implementation, this would:
    # 1. Create an IngestionEvent
    # 2. Dispatch it to the appropriate handlers
    # 3. Process the file based on its type
    
    # For now, just log it
    logger.info(f"File ready for ingestion: {filepath} (category: {category})")
