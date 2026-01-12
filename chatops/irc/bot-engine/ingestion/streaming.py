"""Streaming data ingestion for IRC bot."""
import asyncio
import json
import logging
import time
from typing import Any, Dict, Optional
from enum import Enum

from .base import BaseIngestion, IngestionEvent, IngestionStatus

logger = logging.getLogger(__name__)


class StreamType(Enum):
    """Streaming platform types."""
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    REDIS = "redis"


class StreamingIngestion(BaseIngestion):
    """Streaming data ingestion (Kafka, RabbitMQ, Redis)."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize streaming ingestion.
        
        Config options:
            - stream_type: Type of stream (kafka, rabbitmq, redis)
            - connection: Connection config (brokers, host, etc.)
            - topic/queue/channel: Topic/queue/channel name
            - consumer_group: Consumer group (for Kafka)
            - auto_commit: Auto-commit offsets (default: True)
        """
        super().__init__(source_id, config)
        self.stream_type = StreamType(config.get('stream_type'))
        self.connection = config.get('connection', {})
        self.topic = config.get('topic')
        self.queue = config.get('queue')
        self.channel = config.get('channel')
        self.consumer_group = config.get('consumer_group', 'irc-bot')
        self.auto_commit = config.get('auto_commit', True)
        self._task = None
        self._consumer = None
        self._connection = None
    
    async def _setup_kafka(self):
        """Setup Kafka consumer."""
        try:
            from kafka import KafkaConsumer
            import json
            
            brokers = self.connection.get('brokers', ['localhost:9092'])
            
            self._consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=brokers,
                group_id=self.consumer_group,
                enable_auto_commit=self.auto_commit,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None
            )
            
            logger.info(f"Kafka consumer setup for topic: {self.topic}")
        except ImportError:
            logger.error("kafka-python not installed. Install with: pip install kafka-python")
            raise
    
    async def _setup_rabbitmq(self):
        """Setup RabbitMQ consumer."""
        try:
            import pika
            
            host = self.connection.get('host', 'localhost')
            port = self.connection.get('port', 5672)
            username = self.connection.get('username', 'guest')
            password = self.connection.get('password', 'guest')
            
            credentials = pika.PlainCredentials(username, password)
            parameters = pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=credentials
            )
            
            self._connection = pika.BlockingConnection(parameters)
            self._consumer = self._connection.channel()
            self._consumer.queue_declare(queue=self.queue, durable=True)
            
            logger.info(f"RabbitMQ consumer setup for queue: {self.queue}")
        except ImportError:
            logger.error("pika not installed. Install with: pip install pika")
            raise
    
    async def _setup_redis(self):
        """Setup Redis Pub/Sub consumer."""
        try:
            import redis.asyncio as redis
            
            host = self.connection.get('host', 'localhost')
            port = self.connection.get('port', 6379)
            db = self.connection.get('db', 0)
            password = self.connection.get('password')
            
            self._connection = await redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True
            )
            
            self._consumer = self._connection.pubsub()
            await self._consumer.subscribe(self.channel)
            
            logger.info(f"Redis Pub/Sub consumer setup for channel: {self.channel}")
        except ImportError:
            logger.error("redis not installed. Install with: pip install redis")
            raise
    
    async def _consume_kafka(self):
        """Consume messages from Kafka."""
        try:
            for message in self._consumer:
                if self.status != IngestionStatus.RUNNING:
                    break
                
                event = IngestionEvent(
                    source_type="stream",
                    source_id=self.source_id,
                    data=message.value,
                    metadata={
                        'stream_type': 'kafka',
                        'topic': message.topic,
                        'partition': message.partition,
                        'offset': message.offset,
                        'key': message.key.decode('utf-8') if message.key else None
                    },
                    timestamp=time.time()
                )
                
                await self._dispatch_event(event)
                
                # Manual commit if not auto-commit
                if not self.auto_commit:
                    self._consumer.commit()
        except Exception as e:
            logger.error(f"Error consuming from Kafka: {e}")
    
    async def _consume_rabbitmq(self):
        """Consume messages from RabbitMQ."""
        try:
            def callback(ch, method, properties, body):
                try:
                    data = json.loads(body.decode('utf-8'))
                except json.JSONDecodeError:
                    data = {'raw': body.decode('utf-8')}
                
                event = IngestionEvent(
                    source_type="stream",
                    source_id=self.source_id,
                    data=data,
                    metadata={
                        'stream_type': 'rabbitmq',
                        'queue': self.queue,
                        'delivery_tag': method.delivery_tag,
                        'routing_key': method.routing_key
                    },
                    timestamp=time.time()
                )
                
                # Dispatch event synchronously (RabbitMQ callback is sync)
                asyncio.create_task(self._dispatch_event(event))
                
                # Acknowledge message
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
            self._consumer.basic_consume(
                queue=self.queue,
                on_message_callback=callback,
                auto_ack=False
            )
            
            # Start consuming (blocking)
            self._consumer.start_consuming()
        except Exception as e:
            logger.error(f"Error consuming from RabbitMQ: {e}")
    
    async def _consume_redis(self):
        """Consume messages from Redis Pub/Sub."""
        try:
            async for message in self._consumer.listen():
                if self.status != IngestionStatus.RUNNING:
                    break
                
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                    except (json.JSONDecodeError, TypeError):
                        data = {'raw': message['data']}
                    
                    event = IngestionEvent(
                        source_type="stream",
                        source_id=self.source_id,
                        data=data,
                        metadata={
                            'stream_type': 'redis',
                            'channel': message['channel'],
                            'pattern': message.get('pattern')
                        },
                        timestamp=time.time()
                    )
                    
                    await self._dispatch_event(event)
        except Exception as e:
            logger.error(f"Error consuming from Redis: {e}")
    
    async def _consume_loop(self):
        """Main consumption loop."""
        try:
            if self.stream_type == StreamType.KAFKA:
                # Kafka consumer is blocking, run in executor
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._consume_kafka)
            elif self.stream_type == StreamType.RABBITMQ:
                # RabbitMQ consumer is blocking, run in executor
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._consume_rabbitmq)
            elif self.stream_type == StreamType.REDIS:
                # Redis consumer is async
                await self._consume_redis()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in consume loop: {e}")
    
    async def start(self):
        """Start streaming ingestion."""
        self.status = IngestionStatus.STARTING
        try:
            # Setup consumer based on type
            if self.stream_type == StreamType.KAFKA:
                await self._setup_kafka()
            elif self.stream_type == StreamType.RABBITMQ:
                await self._setup_rabbitmq()
            elif self.stream_type == StreamType.REDIS:
                await self._setup_redis()
            
            self.status = IngestionStatus.RUNNING
            self._task = asyncio.create_task(self._consume_loop())
            logger.info(f"Streaming ingestion started")
        except Exception as e:
            self.status = IngestionStatus.ERROR
            logger.error(f"Failed to start streaming ingestion: {e}")
            raise
    
    async def stop(self):
        """Stop streaming ingestion."""
        self.status = IngestionStatus.STOPPED
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        # Close connections
        if self.stream_type == StreamType.KAFKA and self._consumer:
            self._consumer.close()
        elif self.stream_type == StreamType.RABBITMQ:
            if self._consumer:
                self._consumer.stop_consuming()
            if self._connection:
                self._connection.close()
        elif self.stream_type == StreamType.REDIS:
            if self._consumer:
                await self._consumer.unsubscribe(self.channel)
            if self._connection:
                await self._connection.close()
        
        logger.info(f"Streaming ingestion stopped")
