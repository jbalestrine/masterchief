"""
Chat API endpoints for Echo bot.

Provides REST API and WebSocket handlers for live chat and training.
"""

import logging
import os
from flask import Blueprint, request, jsonify, send_from_directory
from flask_socketio import emit, join_room, leave_room
from typing import Dict, Any

from echo.chat_bot import get_chat_bot, ResponseQuality

logger = logging.getLogger(__name__)

# Create blueprint
chat_bp = Blueprint('chat', __name__)

# Get chat bot instance
chat_bot = get_chat_bot()


@chat_bp.route('/chat-ui', methods=['GET'])
def chat_ui():
    """Serve the chat UI HTML page."""
    chat_dir = os.path.dirname(__file__)
    return send_from_directory(chat_dir, 'chat.html')


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Send a message to Echo and get a response.
    
    Request body:
        {
            "message": "user message",
            "session_id": "optional session identifier"
        }
    
    Response:
        {
            "response": "Echo's response",
            "session_id": "session identifier",
            "timestamp": 1234567890.123,
            "message_id": "bot_1234567890123"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        session_id = data.get('session_id', 'default')
        
        # Get response from chat bot
        response = chat_bot.chat(user_message, session_id)
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/chat/history/<session_id>', methods=['GET'])
def get_history(session_id: str):
    """
    Get conversation history for a session.
    
    Query params:
        limit: Maximum messages to return (default: 50)
    
    Response:
        {
            "session_id": "session identifier",
            "messages": [
                {
                    "role": "user",
                    "content": "message",
                    "timestamp": 1234567890.123,
                    "message_id": "user_1234567890123"
                },
                ...
            ]
        }
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        
        messages = chat_bot.get_conversation_history(session_id, limit)
        
        return jsonify({
            'session_id': session_id,
            'messages': messages
        }), 200
        
    except Exception as e:
        logger.error(f"Get history error: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/chat/clear/<session_id>', methods=['DELETE'])
def clear_conversation(session_id: str):
    """
    Clear conversation history for a session.
    
    Response:
        {
            "status": "ok",
            "message": "Conversation cleared"
        }
    """
    try:
        chat_bot.clear_conversation(session_id)
        
        return jsonify({
            'status': 'ok',
            'message': f'Conversation cleared for session: {session_id}'
        }), 200
        
    except Exception as e:
        logger.error(f"Clear conversation error: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/train', methods=['POST'])
def train():
    """
    Submit training data to improve Echo's responses.
    
    Request body:
        {
            "user_message": "user's message",
            "bot_response": "Echo's response",
            "quality": "excellent|good|acceptable|poor",
            "feedback": "optional feedback text"
        }
    
    Response:
        {
            "status": "ok",
            "message": "Training data added"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        required_fields = ['user_message', 'bot_response', 'quality']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate quality
        try:
            quality = ResponseQuality(data['quality'])
        except ValueError:
            return jsonify({
                'error': f"Invalid quality. Must be one of: {[q.value for q in ResponseQuality]}"
            }), 400
        
        # Train the bot
        success = chat_bot.train(
            user_message=data['user_message'],
            bot_response=data['bot_response'],
            quality=quality,
            feedback=data.get('feedback')
        )
        
        if success:
            return jsonify({
                'status': 'ok',
                'message': 'Training data added successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to add training data'
            }), 500
        
    except Exception as e:
        logger.error(f"Training error: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get training statistics.
    
    Response:
        {
            "total_examples": 100,
            "quality_distribution": {
                "excellent": 30,
                "good": 40,
                "acceptable": 20,
                "poor": 10
            },
            "patterns_learned": 50
        }
    """
    try:
        stats = chat_bot.get_training_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        return jsonify({'error': str(e)}), 500


# WebSocket handlers
def init_chat_socketio(socketio):
    """
    Initialize WebSocket handlers for chat.
    
    Args:
        socketio: SocketIO instance
    """
    
    @socketio.on('chat_join')
    def handle_chat_join(data):
        """Handle user joining a chat session."""
        session_id = data.get('session_id', 'default')
        join_room(f"chat_{session_id}")
        
        logger.info(f"Client joined chat session: {session_id}")
        
        emit('chat_joined', {
            'session_id': session_id,
            'message': 'Joined chat with Echo 🌙'
        })
    
    @socketio.on('chat_leave')
    def handle_chat_leave(data):
        """Handle user leaving a chat session."""
        session_id = data.get('session_id', 'default')
        leave_room(f"chat_{session_id}")
        
        logger.info(f"Client left chat session: {session_id}")
        
        emit('chat_left', {
            'session_id': session_id,
            'message': 'Left chat session'
        })
    
    @socketio.on('chat_message')
    def handle_chat_message(data):
        """Handle incoming chat message via WebSocket."""
        try:
            user_message = data.get('message')
            session_id = data.get('session_id', 'default')
            
            if not user_message:
                emit('error', {'message': 'Message is required'})
                return
            
            # Get response from chat bot
            response = chat_bot.chat(user_message, session_id)
            
            # Emit response back to client
            emit('chat_response', response, room=f"chat_{session_id}")
            
            logger.info(f"Chat message processed for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Chat message error: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('chat_typing')
    def handle_typing(data):
        """Handle typing indicator."""
        session_id = data.get('session_id', 'default')
        is_typing = data.get('is_typing', False)
        
        # Broadcast typing status to others in the room
        emit('user_typing', {
            'session_id': session_id,
            'is_typing': is_typing
        }, room=f"chat_{session_id}", include_self=False)
    
    logger.info("Chat WebSocket handlers initialized")


def init_chat_api(app, socketio):
    """
    Initialize chat API with Flask app and SocketIO.
    
    Args:
        app: Flask application
        socketio: SocketIO instance
    """
    # Register blueprint
    app.register_blueprint(chat_bp, url_prefix='/api/v1')
    
    # Initialize WebSocket handlers
    init_chat_socketio(socketio)
    
    logger.info("Chat API initialized")
