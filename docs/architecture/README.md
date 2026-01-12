# MasterChief Platform Architecture

## Overview

MasterChief is a comprehensive enterprise DevOps automation platform built with a modular, event-driven architecture. This document describes the system architecture, key components, and design decisions.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI & Web UI                            │
│  (masterchief CLI, Web IDE, IRC Client, Portal)             │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────┐
│                    Core Platform Engine                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Module Loader│  │Config Engine │  │  Event Bus   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────┐
│                      Module Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Terraform   │  │   Ansible    │  │ Kubernetes   │     │
│  │   Modules    │  │  Playbooks   │  │   Charts     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  IRC Bot     │  │   Scripts    │  │   Addons     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Azure     │  │  Kubernetes  │  │     IRC      │     │
│  │  Resources   │  │   Clusters   │  │   Server     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Module Loader

The module loader provides dynamic plugin discovery and loading with hot-reload capabilities.

**Features:**
- Automatic module discovery from configured directories
- Dependency resolution and load ordering
- Hot-reload without platform restart
- Module manifest schema validation
- SDK for module development

**Key Files:**
- `core/module-loader/loader.py`

### 2. Configuration Engine

Hierarchical configuration management system supporting multiple environments.

**Features:**
- Three-level hierarchy: Global → Environment → Module
- Secret reference resolution (Azure Key Vault, environment variables)
- Dynamic configuration reloading
- Environment switching

**Configuration Hierarchy:**
```
Global Config (config/global/config.yaml)
    ↓
Environment Config (config/environments/{env}.yaml)
    ↓
Module Config (per-module configuration)
```

**Key Files:**
- `core/config-engine/engine.py`

### 3. Event Bus

Internal pub/sub messaging system for event-driven architecture.

**Features:**
- Subscribe/publish pattern
- Event logging and replay
- Webhook dispatcher for external integrations
- Support for both sync and async handlers

**Event Flow:**
```
Publisher → Event Bus → Subscribers
                ↓
           Event Log (optional)
```

**Key Files:**
- `core/event-bus/bus.py`

### 4. CLI Tool

Command-line interface for platform management.

**Commands:**
- `init` - Initialize new projects
- `module` - Module management (add/remove/list)
- `deploy` - Infrastructure deployment
- `status` - Platform status
- `logs` - View logs
- `interactive` - Interactive mode

**Key Files:**
- `core/cli/main.py`

## Module Architecture

### Terraform Modules

Azure infrastructure templates organized by resource type:

- **Networking**: VNets, subnets, NSGs, VPN, ExpressRoute
- **Compute**: AKS, VMSS, Virtual Desktop
- **Storage**: Storage Accounts, NetApp Files, SOFS
- **Database**: SQL MI, Azure SQL, Cosmos DB
- **Security**: Key Vault, Managed Identities, Policies

**Structure:**
```
modules/terraform/azure/
├── networking/
│   └── vnet.tf
├── compute/
│   └── aks.tf
├── storage/
└── database/
```

### Ansible Roles

Server configuration and orchestration:

- **common**: Baseline configuration
- **security-hardening**: Security best practices
- **monitoring-agent**: Observability agents
- **docker**: Docker installation
- **kubernetes**: Kubernetes node setup

**Structure:**
```
modules/ansible/
├── roles/
│   ├── common/
│   ├── security-hardening/
│   └── monitoring-agent/
└── playbooks/
    └── site.yml
```

### ChatOps IRC Bot

Eggdrop-style IRC bot with TCL-inspired Python bindings:

**Binding System:**
```python
# Traditional IRC bindings
bot.bind("pub", "-|-", "!deploy", deploy_handler)  # Channel command
bot.bind("msg", "-|-", "!status", status_handler)  # Private message
bot.bind("time", "-|-", "*/5 * * * *", cron_handler)  # Scheduled

# Data ingestion bindings
bot.bind("webhook", "-|-", "github/push", handle_github_push)
bot.bind("file", "-|-", "/data/*.json", handle_json_files)
bot.bind("stream", "-|-", "kafka:deployments", handle_deployments)
bot.bind("log", "-|-", "/var/log/app.log", handle_app_logs)
bot.bind("metric", "-|-", "prometheus:cpu_usage>80", handle_high_cpu)
```

**Features:**
- Command framework with permissions
- Data ingestion pipeline (webhooks, logs, metrics)
- Partyline/bot mesh
- Web IRC client

**Data Ingestion System:**

The IRC bot includes a comprehensive data ingestion system that supports multiple data sources:

1. **Webhooks** - Receive and process webhooks from:
   - GitHub (push, PR, issues)
   - GitLab CI/CD
   - Jenkins
   - Alertmanager
   - PagerDuty
   - Generic webhooks with signature validation

2. **REST APIs** - Poll external APIs with:
   - Multiple authentication methods (API key, Bearer, Basic, OAuth)
   - Configurable polling intervals
   - Response transformation
   - Change detection

3. **File-based** - Watch and ingest files:
   - CSV, JSON, YAML, XML formats
   - File change detection
   - Configurable glob patterns
   - Recursive directory watching

4. **Databases** - Query databases:
   - PostgreSQL (async with asyncpg)
   - MySQL (async with aiomysql)
   - SQLite (async with aiosqlite)
   - MongoDB (async with motor)
   - Change detection and scheduled queries

5. **Streaming** - Consume from message queues:
   - Kafka topics
   - RabbitMQ queues
   - Redis Pub/Sub channels
   - Reliable message processing

6. **Logs** - Tail and parse log files:
   - Syslog format support
   - JSON logs
   - Custom regex patterns
   - Log rotation handling

7. **Metrics** - Collect and monitor metrics:
   - Prometheus queries
   - StatsD integration
   - InfluxDB queries
   - Threshold-based alerting

**Architecture:**
```
┌─────────────────────────────────────────────────┐
│           IRC Bot with Bindings                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ IRC Bindings │  │  Ingestion   │            │
│  │  (pub, msg)  │  │   Bindings   │            │
│  └──────────────┘  └──────────────┘            │
│                           │                     │
│                    ┌──────▼──────┐              │
│                    │  Ingestion  │              │
│                    │   Manager   │              │
│                    └──────┬──────┘              │
└───────────────────────────┼─────────────────────┘
                            │
        ┌───────────────────┴────────────────────┐
        │                                        │
┌───────▼────────┐  ┌────────▼─────────┐  ┌────▼──────┐
│   Webhooks     │  │    Streaming     │  │  Metrics  │
│   (Flask)      │  │ (Kafka/RabbitMQ) │  │(Prometheus)│
└────────────────┘  └──────────────────┘  └───────────┘
┌────────────────┐  ┌──────────────────┐  ┌───────────┐
│   Files        │  │    Database      │  │   Logs    │
│  (Watchdog)    │  │  (asyncpg/motor) │  │  (Tail)   │
└────────────────┘  └──────────────────┘  └───────────┘
```

## Data Flow

### Deployment Flow

```
1. User executes: masterchief deploy
2. CLI loads configuration from Config Engine
3. Module Loader loads required modules
4. Deployment event published to Event Bus
5. Modules execute (Terraform/Ansible)
6. Progress events published to Event Bus
7. IRC bot notifies channels
8. Results logged and stored
```

### Event-Driven Flow

```
1. External webhook received
2. Event Bus dispatches to webhook handler
3. Handler processes and publishes events
4. Subscribers react (notifications, automation, etc.)
5. Events logged for audit and replay
```

## Security Architecture

### Authentication & Authorization

- RBAC-based access control
- Azure AD integration
- API key authentication
- SSH key management

### Secret Management

- Azure Key Vault integration
- Secret reference resolution: `${vault:secret-name}`
- Environment variable fallback: `${env:VAR_NAME}`
- Encrypted storage for sensitive data

### Network Security

- Private endpoints for Azure resources
- Network segmentation (VNets, subnets, NSGs)
- Azure Firewall integration
- Bastion host access

## Scalability & Performance

### Horizontal Scaling

- Stateless API servers
- Redis for session storage
- PostgreSQL with read replicas
- Load-balanced web tier

### Caching Strategy

- Redis for frequently accessed data
- Configuration caching
- API response caching
- Static asset CDN

### Async Processing

- Event-driven architecture
- Background job queues
- Async I/O for network operations
- Worker pool for CPU-intensive tasks

## Observability

### Metrics

- Prometheus metrics export
- Custom application metrics
- Infrastructure metrics
- Business KPIs

### Logging

- Structured logging (JSON)
- Fluent Bit aggregation
- Centralized log storage
- Log retention policies

### Tracing

- Distributed tracing support
- Request correlation IDs
- Performance profiling
- Error tracking

## Technology Stack

### Core Platform
- **Language**: Python 3.10+
- **Web Framework**: FastAPI
- **CLI**: Click
- **Database**: PostgreSQL
- **Cache**: Redis

### Infrastructure
- **IaC**: Terraform 1.5+, Ansible 2.14+
- **Containers**: Docker, Kubernetes
- **Cloud**: Microsoft Azure

### Frontend
- **Web IDE**: Monaco Editor
- **Framework**: React/Vue.js
- **WebSocket**: For real-time updates

### Messaging
- **IRC**: InspIRCd 3.x
- **Bot**: irc library (Python)

## Design Decisions

See [ADRs](../adrs/) for detailed architecture decision records.

Key decisions:
- **ADR-001**: Module-based architecture for extensibility
- **ADR-002**: Event bus for loose coupling
- **ADR-003**: Hierarchical configuration system
- **ADR-004**: Python as primary language

## Future Enhancements

1. **Multi-cloud support**: AWS, GCP modules
2. **GUI dashboard**: Web-based management console
3. **Workflow engine**: Visual workflow builder
4. **ML/AI integration**: Predictive analytics
5. **Mobile app**: iOS/Android clients
6. **Federation**: Multi-instance deployment
7. **Marketplace**: Public module registry
8. **GitOps**: Full GitOps workflow integration
