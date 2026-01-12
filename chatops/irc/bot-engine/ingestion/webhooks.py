"""Webhook ingestion for IRC bot."""
import asyncio
import hashlib
import hmac
import json
import logging
from typing import Any, Dict, Optional
import time

from flask import Flask, request, jsonify
from werkzeug.serving import make_server

from .base import BaseIngestion, IngestionEvent, IngestionStatus

logger = logging.getLogger(__name__)


class WebhookIngestion(BaseIngestion):
    """Webhook receiver for various webhook types."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize webhook ingestion.
        
        Config options:
            - port: Port to listen on (default: 8080)
            - host: Host to bind to (default: 0.0.0.0)
            - secret: Secret for signature validation
            - webhook_type: Type of webhook (github, gitlab, jenkins, alertmanager, generic)
        """
        super().__init__(source_id, config)
        self.port = config.get('port', 8080)
        self.host = config.get('host', '0.0.0.0')
        self.secret = config.get('secret')
        self.webhook_type = config.get('webhook_type', 'generic')
        self.app = Flask(f"webhook_{source_id}")
        self.server = None
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes for webhook receiver."""
        
        @self.app.route('/webhook', methods=['POST'])
        def receive_webhook():
            """Receive and process webhook."""
            try:
                # Validate signature if secret is configured
                if self.secret:
                    if not self._validate_signature(request):
                        return jsonify({"error": "Invalid signature"}), 401
                
                # Parse webhook data
                data = request.get_json() or {}
                headers = dict(request.headers)
                
                # Process based on webhook type
                event_data = self._process_webhook(data, headers)
                
                # Create and dispatch event
                event = IngestionEvent(
                    source_type="webhook",
                    source_id=self.source_id,
                    data=event_data,
                    metadata={
                        "webhook_type": self.webhook_type,
                        "headers": headers,
                        "remote_addr": request.remote_addr
                    },
                    timestamp=time.time()
                )
                
                # Dispatch in async context
                asyncio.create_task(self._dispatch_event(event))
                
                return jsonify({"status": "received"}), 200
                
            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({"status": "healthy"}), 200
    
    def _validate_signature(self, request) -> bool:
        """Validate webhook signature based on type."""
        if self.webhook_type == 'github':
            return self._validate_github_signature(request)
        elif self.webhook_type == 'gitlab':
            return self._validate_gitlab_signature(request)
        else:
            # Generic HMAC validation
            signature = request.headers.get('X-Webhook-Signature')
            if not signature:
                return False
            
            payload = request.get_data()
            expected = hmac.new(
                self.secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected)
    
    def _validate_github_signature(self, request) -> bool:
        """Validate GitHub webhook signature."""
        signature = request.headers.get('X-Hub-Signature-256')
        if not signature:
            return False
        
        payload = request.get_data()
        expected = 'sha256=' + hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected)
    
    def _validate_gitlab_signature(self, request) -> bool:
        """Validate GitLab webhook signature."""
        token = request.headers.get('X-Gitlab-Token')
        return token == self.secret if token else False
    
    def _process_webhook(self, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Process webhook data based on type."""
        if self.webhook_type == 'github':
            return self._process_github_webhook(data, headers)
        elif self.webhook_type == 'gitlab':
            return self._process_gitlab_webhook(data, headers)
        elif self.webhook_type == 'jenkins':
            return self._process_jenkins_webhook(data, headers)
        elif self.webhook_type == 'alertmanager':
            return self._process_alertmanager_webhook(data, headers)
        elif self.webhook_type == 'pagerduty':
            return self._process_pagerduty_webhook(data, headers)
        else:
            return data
    
    def _process_github_webhook(self, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Process GitHub webhook."""
        event_type = headers.get('X-Github-Event', 'unknown')
        
        processed = {
            'event_type': event_type,
            'repository': data.get('repository', {}).get('full_name'),
            'sender': data.get('sender', {}).get('login'),
        }
        
        if event_type == 'push':
            processed.update({
                'ref': data.get('ref'),
                'commits': data.get('commits', []),
                'head_commit': data.get('head_commit')
            })
        elif event_type == 'pull_request':
            pr = data.get('pull_request', {})
            processed.update({
                'action': data.get('action'),
                'pr_number': pr.get('number'),
                'pr_title': pr.get('title'),
                'pr_state': pr.get('state')
            })
        elif event_type == 'issues':
            issue = data.get('issue', {})
            processed.update({
                'action': data.get('action'),
                'issue_number': issue.get('number'),
                'issue_title': issue.get('title')
            })
        
        processed['raw_data'] = data
        return processed
    
    def _process_gitlab_webhook(self, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Process GitLab webhook."""
        event_type = data.get('object_kind', 'unknown')
        
        return {
            'event_type': event_type,
            'project': data.get('project', {}).get('name'),
            'user': data.get('user', {}).get('username'),
            'raw_data': data
        }
    
    def _process_jenkins_webhook(self, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Process Jenkins webhook."""
        return {
            'event_type': 'build',
            'job_name': data.get('name'),
            'build_number': data.get('build', {}).get('number'),
            'status': data.get('build', {}).get('status'),
            'url': data.get('build', {}).get('url'),
            'raw_data': data
        }
    
    def _process_alertmanager_webhook(self, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Process Alertmanager webhook."""
        alerts = data.get('alerts', [])
        return {
            'event_type': 'alert',
            'status': data.get('status'),
            'alerts': [
                {
                    'status': alert.get('status'),
                    'labels': alert.get('labels', {}),
                    'annotations': alert.get('annotations', {}),
                    'starts_at': alert.get('startsAt'),
                    'ends_at': alert.get('endsAt')
                }
                for alert in alerts
            ],
            'raw_data': data
        }
    
    def _process_pagerduty_webhook(self, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Process PagerDuty webhook."""
        messages = data.get('messages', [])
        return {
            'event_type': 'incident',
            'messages': [
                {
                    'type': msg.get('type'),
                    'incident': msg.get('incident', {}),
                    'created_on': msg.get('created_on')
                }
                for msg in messages
            ],
            'raw_data': data
        }
    
    async def start(self):
        """Start the webhook server."""
        self.status = IngestionStatus.STARTING
        try:
            # Run server in a separate thread
            self.server = make_server(self.host, self.port, self.app, threaded=True)
            
            # Start server in background
            import threading
            thread = threading.Thread(target=self.server.serve_forever)
            thread.daemon = True
            thread.start()
            
            self.status = IngestionStatus.RUNNING
            logger.info(f"Webhook server started on {self.host}:{self.port}")
        except Exception as e:
            self.status = IngestionStatus.ERROR
            logger.error(f"Failed to start webhook server: {e}")
            raise
    
    async def stop(self):
        """Stop the webhook server."""
        if self.server:
            self.server.shutdown()
            self.server = None
        self.status = IngestionStatus.STOPPED
        logger.info(f"Webhook server stopped")
