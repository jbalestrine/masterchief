DASHBOARD_TEMPLATE = """
{% block content %}
<div class="dashboard-grid">
  <div class="card">
    <h3>CPU Usage</h3>
    <div class="stat-value">{{ stats['cpu']['percent'] }}%</div>
    <div class="stat-label">Cores: {{ stats['cpu']['count'] }}</div>
  </div>
  <div class="card">
    <h3>Memory Usage</h3>
    <div class="stat-value">{{ (stats['memory']['used']/1024/1024/1024)|round(2) }} GB / {{ (stats['memory']['total']/1024/1024/1024)|round(2) }} GB</div>
    <div class="progress-bar"><div class="progress-fill" style="width:{{ stats['memory']['percent'] }}%"></div></div>
    <div class="stat-label">{{ stats['memory']['percent'] }}% used</div>
  </div>
  <div class="card">
    <h3>Disk Usage</h3>
    <div class="stat-value">{{ (stats['disk']['used']/1024/1024/1024)|round(2) }} GB / {{ (stats['disk']['total']/1024/1024/1024)|round(2) }} GB</div>
    <div class="progress-bar"><div class="progress-fill" style="width:{{ stats['disk']['percent'] }}%"></div></div>
    <div class="stat-label">{{ stats['disk']['percent'] }}% used</div>
  </div>
  <div class="card">
    <h3>Uptime</h3>
    <div class="stat-value">{{ (stats['uptime']/3600)|round(2) }} hours</div>
    <div class="stat-label">System Uptime</div>
  </div>
</div>
{% endblock %}
"""
