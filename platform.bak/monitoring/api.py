"""
Monitoring & Health API endpoints
"""

from flask import Blueprint, jsonify, request
import psutil

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/health', methods=['GET'])
def get_health():
    """Get system health"""
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    status = 'healthy'
    if cpu_percent > 80 or mem.percent > 90 or disk.percent > 90:
        status = 'warning'
    
    return jsonify({
        'status': status,
        'cpu': {
            'percent': cpu_percent,
            'cores': psutil.cpu_count()
        },
        'memory': {
            'total': mem.total,
            'available': mem.available,
            'percent': mem.percent
        },
        'disk': {
            'total': disk.total,
            'used': disk.used,
            'percent': disk.percent
        }
    })

@monitoring_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get detailed metrics"""
    return jsonify({
        'cpu': {
            'percent': psutil.cpu_percent(interval=1),
            'per_cpu': psutil.cpu_percent(interval=1, percpu=True),
            'load_avg': psutil.getloadavg()
        },
        'memory': dict(psutil.virtual_memory()._asdict()),
        'disk': dict(psutil.disk_usage('/')._asdict()),
        'network': psutil.net_io_counters()._asdict()
    })

@monitoring_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get active alerts"""
    alerts = []
    
    # Check for resource alerts
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 80:
        alerts.append({
            'severity': 'warning',
            'message': f'CPU usage high: {cpu_percent}%',
            'timestamp': '2026-01-12T07:48:00Z'
        })
    
    mem = psutil.virtual_memory()
    if mem.percent > 90:
        alerts.append({
            'severity': 'critical',
            'message': f'Memory usage critical: {mem.percent}%',
            'timestamp': '2026-01-12T07:48:00Z'
        })
    
    return jsonify({'alerts': alerts})
