"""Metrics ingestion for IRC bot."""
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from enum import Enum

from .base import BaseIngestion, IngestionEvent, IngestionStatus

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric source types."""
    PROMETHEUS = "prometheus"
    STATSD = "statsd"
    INFLUXDB = "influxdb"


class MetricsIngestion(BaseIngestion):
    """Metrics collection and threshold-based alerting."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize metrics ingestion.
        
        Config options:
            - metric_type: Type of metrics (prometheus, statsd, influxdb)
            - connection: Connection config (host, port, etc.)
            - query: Metric query or metric name
            - polling_interval: Seconds between polls (default: 30)
            - threshold: Threshold value for alerting
            - threshold_condition: Condition (gt, lt, eq, gte, lte)
        """
        super().__init__(source_id, config)
        self.metric_type = MetricType(config.get('metric_type'))
        self.connection = config.get('connection', {})
        self.query = config.get('query')
        self.polling_interval = config.get('polling_interval', 30)
        self.threshold = config.get('threshold')
        self.threshold_condition = config.get('threshold_condition', 'gt')
        self._task = None
        self._client = None
    
    async def _setup_prometheus(self):
        """Setup Prometheus client."""
        try:
            import httpx
            
            host = self.connection.get('host', 'localhost')
            port = self.connection.get('port', 9090)
            self.prometheus_url = f"http://{host}:{port}"
            self._client = httpx.AsyncClient()
            
            logger.info(f"Prometheus client setup: {self.prometheus_url}")
        except ImportError:
            logger.error("httpx not installed. Install with: pip install httpx")
            raise
    
    async def _setup_statsd(self):
        """Setup StatsD client."""
        try:
            import statsd
            
            host = self.connection.get('host', 'localhost')
            port = self.connection.get('port', 8125)
            self._client = statsd.StatsClient(host, port)
            
            logger.info(f"StatsD client setup: {host}:{port}")
        except ImportError:
            logger.error("statsd not installed. Install with: pip install statsd")
            raise
    
    async def _setup_influxdb(self):
        """Setup InfluxDB client."""
        try:
            from influxdb_client import InfluxDBClient
            
            url = self.connection.get('url', 'http://localhost:8086')
            token = self.connection.get('token')
            org = self.connection.get('org')
            
            self._client = InfluxDBClient(url=url, token=token, org=org)
            
            logger.info(f"InfluxDB client setup: {url}")
        except ImportError:
            logger.error("influxdb-client not installed. Install with: pip install influxdb-client")
            raise
    
    async def _query_prometheus(self) -> Optional[Dict[str, Any]]:
        """Query Prometheus metrics."""
        try:
            url = f"{self.prometheus_url}/api/v1/query"
            params = {'query': self.query}
            
            response = await self._client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success':
                results = data.get('data', {}).get('result', [])
                
                # Extract metric values
                metrics = []
                for result in results:
                    metric = result.get('metric', {})
                    value = result.get('value', [None, None])
                    
                    metrics.append({
                        'metric': metric,
                        'timestamp': value[0],
                        'value': float(value[1]) if value[1] else None
                    })
                
                return {'metrics': metrics}
            
            return None
        except Exception as e:
            logger.error(f"Error querying Prometheus: {e}")
            return None
    
    async def _query_statsd(self) -> Optional[Dict[str, Any]]:
        """Query StatsD metrics."""
        # Note: StatsD is typically push-only, not query-able
        # This would require a StatsD backend like Graphite
        logger.warning("StatsD querying not implemented (push-only protocol)")
        return None
    
    async def _query_influxdb(self) -> Optional[Dict[str, Any]]:
        """Query InfluxDB metrics."""
        try:
            query_api = self._client.query_api()
            bucket = self.connection.get('bucket', 'default')
            
            result = query_api.query(self.query, org=self.connection.get('org'))
            
            metrics = []
            for table in result:
                for record in table.records:
                    metrics.append({
                        'measurement': record.get_measurement(),
                        'field': record.get_field(),
                        'value': record.get_value(),
                        'timestamp': record.get_time(),
                        'tags': record.values
                    })
            
            return {'metrics': metrics}
        except Exception as e:
            logger.error(f"Error querying InfluxDB: {e}")
            return None
    
    def _check_threshold(self, value: float) -> bool:
        """Check if value meets threshold condition."""
        if self.threshold is None:
            return False
        
        threshold = float(self.threshold)
        
        if self.threshold_condition == 'gt':
            return value > threshold
        elif self.threshold_condition == 'gte':
            return value >= threshold
        elif self.threshold_condition == 'lt':
            return value < threshold
        elif self.threshold_condition == 'lte':
            return value <= threshold
        elif self.threshold_condition == 'eq':
            return value == threshold
        
        return False
    
    async def _poll_loop(self):
        """Main polling loop."""
        while self.status == IngestionStatus.RUNNING:
            try:
                # Query metrics based on type
                data = None
                if self.metric_type == MetricType.PROMETHEUS:
                    data = await self._query_prometheus()
                elif self.metric_type == MetricType.STATSD:
                    data = await self._query_statsd()
                elif self.metric_type == MetricType.INFLUXDB:
                    data = await self._query_influxdb()
                
                if data and data.get('metrics'):
                    # Check thresholds
                    alerts = []
                    for metric in data['metrics']:
                        value = metric.get('value')
                        if value is not None and self._check_threshold(value):
                            alerts.append({
                                'metric': metric,
                                'threshold': self.threshold,
                                'condition': self.threshold_condition,
                                'triggered': True
                            })
                    
                    # Dispatch event if there are metrics (or alerts)
                    if alerts or not self.threshold:
                        event = IngestionEvent(
                            source_type="metric",
                            source_id=self.source_id,
                            data=data,
                            metadata={
                                'metric_type': self.metric_type.value,
                                'query': self.query,
                                'alerts': alerts,
                                'alert_count': len(alerts)
                            },
                            timestamp=time.time()
                        )
                        
                        await self._dispatch_event(event)
                
                await asyncio.sleep(self.polling_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in poll loop: {e}")
                await asyncio.sleep(self.polling_interval)
    
    async def start(self):
        """Start metrics ingestion."""
        self.status = IngestionStatus.STARTING
        try:
            # Setup client based on type
            if self.metric_type == MetricType.PROMETHEUS:
                await self._setup_prometheus()
            elif self.metric_type == MetricType.STATSD:
                await self._setup_statsd()
            elif self.metric_type == MetricType.INFLUXDB:
                await self._setup_influxdb()
            
            self.status = IngestionStatus.RUNNING
            self._task = asyncio.create_task(self._poll_loop())
            logger.info(f"Metrics ingestion started")
        except Exception as e:
            self.status = IngestionStatus.ERROR
            logger.error(f"Failed to start metrics ingestion: {e}")
            raise
    
    async def stop(self):
        """Stop metrics ingestion."""
        self.status = IngestionStatus.STOPPED
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        # Close client
        if self._client:
            if self.metric_type == MetricType.PROMETHEUS:
                await self._client.aclose()
            elif self.metric_type == MetricType.INFLUXDB:
                self._client.close()
        
        logger.info(f"Metrics ingestion stopped")
