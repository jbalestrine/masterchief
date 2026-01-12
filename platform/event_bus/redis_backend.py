"""Redis-based event bus implementation (OPTIONAL)."""
import json
import logging
import threading
from typing import Any, Callable, Dict, List
from collections import defaultdict

logger = logging.getLogger(__name__)


class RedisEventBus:
    """
    Redis-based event bus for distributed pub/sub (OPTIONAL).
    
    This backend requires Redis to be installed and configured.
    Use this for production deployments that need to scale horizontally.
    """
    
    def __init__(self, redis_url: str = None):
        """
        Initialize Redis event bus.
        
        Args:
            redis_url: Redis connection URL (default: redis://localhost:6379/0)
        """
        try:
            import redis
        except ImportError:
            raise ImportError(
                "Redis package is required for RedisEventBus. "
                "Install it with: pip install redis"
            )
        
        if redis_url is None:
            import os
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        
        self.redis_url = redis_url
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.RLock()
        self._listener_thread = None
        self._running = False
        
        logger.info(f"Initialized Redis event bus: {redis_url}")
    
    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe a handler to an event type.
        
        Args:
            event_type: The event type to subscribe to
            handler: Callable that accepts (event_type, data) arguments
        """
        with self._lock:
            # Add handler to local registry
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)
                logger.debug(f"Subscribed handler to event type: {event_type}")
            
            # Subscribe to Redis channel if first subscriber
            if len(self._subscribers[event_type]) == 1:
                self.pubsub.subscribe(event_type)
                
                # Start listener thread if not running
                if not self._running:
                    self._start_listener()
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """
        Unsubscribe a handler from an event type.
        
        Args:
            event_type: The event type to unsubscribe from
            handler: The handler to remove
        """
        with self._lock:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
                logger.debug(f"Unsubscribed handler from event type: {event_type}")
            
            # Unsubscribe from Redis if no more handlers
            if not self._subscribers[event_type]:
                self.pubsub.unsubscribe(event_type)
                del self._subscribers[event_type]
    
    def publish(self, event_type: str, data: Any):
        """
        Publish an event to Redis.
        
        Args:
            event_type: The type of event
            data: Event data (must be JSON-serializable)
        """
        try:
            # Serialize data to JSON
            message = json.dumps(data)
            
            # Publish to Redis
            self.redis_client.publish(event_type, message)
            logger.debug(f"Published event to Redis: {event_type}")
        except Exception as e:
            logger.error(f"Error publishing event to Redis: {e}", exc_info=True)
    
    async def publish_async(self, event_type: str, data: Any):
        """
        Publish an event asynchronously.
        
        Args:
            event_type: The type of event
            data: Event data
        """
        # Redis pub/sub is synchronous, so we just call publish
        self.publish(event_type, data)
    
    def _start_listener(self):
        """Start the Redis listener thread."""
        if self._listener_thread is None or not self._listener_thread.is_alive():
            self._running = True
            self._listener_thread = threading.Thread(
                target=self._listen_loop,
                daemon=True,
                name="RedisEventBusListener"
            )
            self._listener_thread.start()
            logger.info("Started Redis event listener thread")
    
    def _listen_loop(self):
        """Listen for messages from Redis."""
        logger.info("Redis listener loop started")
        
        try:
            for message in self.pubsub.listen():
                if not self._running:
                    break
                
                if message['type'] == 'message':
                    event_type = message['channel']
                    
                    try:
                        # Deserialize message data
                        data = json.loads(message['data'])
                        
                        # Get handlers for this event type
                        with self._lock:
                            handlers = self._subscribers.get(event_type, []).copy()
                        
                        # Execute handlers
                        for handler in handlers:
                            try:
                                handler(event_type, data)
                            except Exception as e:
                                logger.error(
                                    f"Error in event handler for {event_type}: {e}",
                                    exc_info=True
                                )
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode message data: {e}")
        except Exception as e:
            logger.error(f"Error in Redis listener loop: {e}", exc_info=True)
        finally:
            logger.info("Redis listener loop stopped")
    
    def stop(self):
        """Stop the event bus and cleanup resources."""
        self._running = False
        if self.pubsub:
            self.pubsub.close()
        if self._listener_thread:
            self._listener_thread.join(timeout=5)
        logger.info("Redis event bus stopped")
    
    def get_subscriber_count(self, event_type: str = None) -> int:
        """
        Get the number of subscribers.
        
        Args:
            event_type: Optional event type to filter by
            
        Returns:
            Number of subscribers
        """
        with self._lock:
            if event_type:
                return len(self._subscribers.get(event_type, []))
            return sum(len(handlers) for handlers in self._subscribers.values())
    
    def get_event_types(self) -> List[str]:
        """
        Get all registered event types.
        
        Returns:
            List of event type strings
        """
        with self._lock:
            return list(self._subscribers.keys())
