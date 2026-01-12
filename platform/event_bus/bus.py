"""Event bus with Redis pub/sub backend support."""
import asyncio
import json
import logging
from typing import Optional, Callable, Any, Dict
from core.event_bus import EventBus as CoreEventBus, Event

logger = logging.getLogger(__name__)


class RedisPubSubBus(CoreEventBus):
    """Event bus with Redis pub/sub backend for distributed systems."""
    
    def __init__(self, redis_client=None, enable_logging: bool = True, channel_prefix: str = "masterchief"):
        super().__init__(enable_logging=enable_logging)
        self.redis_client = redis_client
        self.channel_prefix = channel_prefix
        self.pubsub = None
        self.listener_task = None
        
    async def init_redis(self, redis_client):
        """Initialize Redis pub/sub."""
        self.redis_client = redis_client
        if redis_client:
            self.pubsub = redis_client.pubsub()
            logger.info("Redis pub/sub initialized")
    
    async def publish(self, event: Event):
        """Publish event locally and to Redis if available."""
        # Publish locally first
        await super().publish(event)
        
        # Publish to Redis for distributed systems
        if self.redis_client:
            try:
                channel = f"{self.channel_prefix}:{event.type}"
                message = event.to_json()
                await asyncio.to_thread(self.redis_client.publish, channel, message)
                logger.debug(f"Published to Redis channel: {channel}")
            except Exception as e:
                logger.error(f"Failed to publish to Redis: {e}")
    
    def subscribe_redis_channel(self, event_type: str):
        """Subscribe to Redis channel for an event type."""
        if self.pubsub:
            channel = f"{self.channel_prefix}:{event_type}"
            self.pubsub.subscribe(channel)
            logger.info(f"Subscribed to Redis channel: {channel}")
    
    async def start_redis_listener(self):
        """Start listening to Redis pub/sub messages."""
        if not self.pubsub:
            logger.warning("Redis pub/sub not initialized")
            return
        
        async def listen():
            logger.info("Started Redis pub/sub listener")
            while True:
                try:
                    message = await asyncio.to_thread(self.pubsub.get_message, ignore_subscribe_messages=True)
                    if message and message['type'] == 'message':
                        data = json.loads(message['data'])
                        event = Event(**data)
                        # Publish locally (skip Redis republish)
                        await super().publish(event)
                except Exception as e:
                    logger.error(f"Error in Redis listener: {e}")
                    await asyncio.sleep(1)
        
        self.listener_task = asyncio.create_task(listen())
    
    async def stop_redis_listener(self):
        """Stop Redis listener."""
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped Redis pub/sub listener")
