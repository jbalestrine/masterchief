"""
TAP Generator - Technical Architectural Plans

Generates comprehensive architectural documentation across 10 phases.
Every connection runs on code.
"""

from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass


class TAPPhase(Enum):
    """Technical Architectural Plan phases."""
    CONTEXT = "context"              # Why are we building this?
    REQUIREMENTS = "requirements"    # What must it do?
    ARCHITECTURE = "architecture"    # How is it structured?
    COMPONENTS = "components"        # What are the pieces?
    INTERFACES = "interfaces"        # How do pieces connect?
    DATA_FLOW = "data_flow"         # How does data move?
    SECURITY = "security"           # How is it protected?
    DEPLOYMENT = "deployment"       # How is it deployed?
    MONITORING = "monitoring"       # How is it observed?
    DECISIONS = "decisions"         # Why these choices? (ADRs)


class TAPGenerator:
    """Generates Technical Architectural Plans."""
    
    def generate_all_phases(
        self,
        name: str,
        description: str,
        components: List[Any],
        connections: List[Any],
        goals: List[str],
        architecture_style: str
    ) -> Dict[TAPPhase, str]:
        """Generate all TAP phases."""
        phases = {}
        
        phases[TAPPhase.CONTEXT] = self._generate_context(
            name, description, goals
        )
        phases[TAPPhase.REQUIREMENTS] = self._generate_requirements(
            goals, components
        )
        phases[TAPPhase.ARCHITECTURE] = self._generate_architecture(
            architecture_style, components
        )
        phases[TAPPhase.COMPONENTS] = self._generate_components(
            components
        )
        phases[TAPPhase.INTERFACES] = self._generate_interfaces(
            connections
        )
        phases[TAPPhase.DATA_FLOW] = self._generate_data_flow(
            components, connections
        )
        phases[TAPPhase.SECURITY] = self._generate_security(
            components, connections
        )
        phases[TAPPhase.DEPLOYMENT] = self._generate_deployment(
            components, architecture_style
        )
        phases[TAPPhase.MONITORING] = self._generate_monitoring(
            components
        )
        phases[TAPPhase.DECISIONS] = self._generate_decisions(
            architecture_style, components
        )
        
        return phases
    
    def _generate_context(
        self,
        name: str,
        description: str,
        goals: List[str]
    ) -> str:
        """Generate CONTEXT phase."""
        goals_text = "\n".join(f"- {goal}" for goal in goals)
        
        return f"""## Why are we building {name}?

{description}

### Goals
{goals_text}

### Vision
This system is designed to be technical, script-driven, and precise. 
Every component serves a clear purpose, every connection is documented,
and every decision is traceable."""
    
    def _generate_requirements(
        self,
        goals: List[str],
        components: List[Any]
    ) -> str:
        """Generate REQUIREMENTS phase."""
        reqs = []
        for i, goal in enumerate(goals, 1):
            reqs.append(f"**FR{i}**: {goal}")
        
        comp_count = len(components)
        reqs.append(f"**NFR1**: Support {comp_count} integrated components")
        reqs.append("**NFR2**: High availability (99.9% uptime)")
        reqs.append("**NFR3**: Scalable architecture")
        reqs.append("**NFR4**: Secure by default")
        reqs.append("**NFR5**: Observable and monitorable")
        
        return "## What must it do?\n\n### Functional Requirements\n" + "\n".join(reqs[:len(goals)]) + \
               "\n\n### Non-Functional Requirements\n" + "\n".join(reqs[len(goals):])
    
    def _generate_architecture(
        self,
        architecture_style: str,
        components: List[Any]
    ) -> str:
        """Generate ARCHITECTURE phase."""
        layers = {}
        for comp in components:
            layer = comp.layer if hasattr(comp, 'layer') else comp.get('layer', 'application')
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(comp)
        
        layer_text = []
        for layer, comps in sorted(layers.items()):
            comp_names = [c.name if hasattr(c, 'name') else c.get('name') for c in comps]
            layer_text.append(f"**{layer.title()}**: {', '.join(comp_names)}")
        
        return f"""## How is it structured?

### Architecture Style
{architecture_style.title()}

### Layers
{chr(10).join(layer_text)}

### Design Principles
- **Separation of Concerns**: Each layer has clear responsibilities
- **Loose Coupling**: Components interact through well-defined interfaces
- **High Cohesion**: Related functionality is grouped together
- **Scalability**: Horizontal scaling at each layer
- **Resilience**: Fault tolerance and graceful degradation"""
    
    def _generate_components(self, components: List[Any]) -> str:
        """Generate COMPONENTS phase."""
        comp_text = []
        for comp in components:
            if hasattr(comp, 'name'):
                name = comp.name
                tech = comp.technology
                desc = comp.description or "Core component"
            else:
                name = comp.get('name', 'Component')
                tech = comp.get('technology', 'Unknown')
                desc = comp.get('description', 'Core component')
            
            comp_text.append(f"""### {name}
**Technology**: {tech}
**Description**: {desc}
""")
        
        return "## What are the pieces?\n\n" + "\n".join(comp_text)
    
    def _generate_interfaces(self, connections: List[Any]) -> str:
        """Generate INTERFACES phase."""
        conn_text = []
        for conn in connections:
            if hasattr(conn, 'source'):
                source = conn.source
                target = conn.target
                protocol = conn.protocol
                desc = conn.description or "Standard connection"
            else:
                source = conn.get('source', 'Unknown')
                target = conn.get('target', 'Unknown')
                protocol = conn.get('protocol', 'HTTP')
                desc = conn.get('description', 'Standard connection')
            
            conn_text.append(f"- **{source} → {target}**: {protocol} - {desc}")
        
        return "## How do pieces connect?\n\n" + "\n".join(conn_text) + \
               "\n\n### Interface Standards\n" + \
               "- RESTful APIs for HTTP communication\n" + \
               "- gRPC for high-performance internal services\n" + \
               "- Message queues for async operations\n" + \
               "- GraphQL for flexible data queries"
    
    def _generate_data_flow(
        self,
        components: List[Any],
        connections: List[Any]
    ) -> str:
        """Generate DATA_FLOW phase."""
        return """## How does data move?

### Data Flow Patterns
1. **Request-Response**: Synchronous client-server communication
2. **Event-Driven**: Asynchronous message passing
3. **Streaming**: Real-time data pipelines
4. **Batch Processing**: Scheduled data operations

### Data States
- **In-Transit**: Encrypted using TLS 1.3
- **At-Rest**: Encrypted using AES-256
- **In-Use**: Memory encryption where applicable

### Data Pipeline
1. Data ingestion from sources
2. Validation and sanitization
3. Processing and transformation
4. Storage and persistence
5. Retrieval and delivery"""
    
    def _generate_security(
        self,
        components: List[Any],
        connections: List[Any]
    ) -> str:
        """Generate SECURITY phase."""
        return """## How is it protected?

### Security Layers
1. **Network Security**: Firewall, DDoS protection, VPN
2. **Application Security**: Input validation, output encoding, CSRF protection
3. **Data Security**: Encryption at rest and in transit
4. **Identity & Access**: OAuth 2.0, JWT, RBAC
5. **Monitoring**: Security logging, anomaly detection

### Security Best Practices
- Principle of least privilege
- Defense in depth
- Zero trust architecture
- Regular security audits
- Automated vulnerability scanning
- Incident response plan

### Compliance
- GDPR compliance for data privacy
- SOC 2 Type II certification
- Regular penetration testing"""
    
    def _generate_deployment(
        self,
        components: List[Any],
        architecture_style: str
    ) -> str:
        """Generate DEPLOYMENT phase."""
        return f"""## How is it deployed?

### Deployment Strategy
**Strategy**: {architecture_style.title()} with containerization

### Environments
- **Development**: Local development with Docker Compose
- **Staging**: Pre-production validation environment
- **Production**: Multi-region cloud deployment

### CI/CD Pipeline
1. **Build**: Automated builds on commit
2. **Test**: Unit, integration, and E2E tests
3. **Security Scan**: Vulnerability and secrets scanning
4. **Deploy**: Blue-green deployment with rollback
5. **Verify**: Smoke tests and health checks

### Infrastructure
- Container orchestration: Kubernetes
- Service mesh: Istio
- Infrastructure as Code: Terraform
- Configuration management: Ansible
- Monitoring: Prometheus + Grafana"""
    
    def _generate_monitoring(self, components: List[Any]) -> str:
        """Generate MONITORING phase."""
        comp_names = [
            c.name if hasattr(c, 'name') else c.get('name', 'Component')
            for c in components
        ]
        
        return f"""## How is it observed?

### Observability Pillars

#### 1. Metrics
- System metrics: CPU, memory, disk, network
- Application metrics: Request rate, error rate, latency
- Business metrics: User activity, conversions

#### 2. Logs
- Structured logging (JSON format)
- Centralized log aggregation
- Log retention and archival

#### 3. Traces
- Distributed tracing across services
- Request flow visualization
- Performance bottleneck identification

### Monitoring Stack
- **Metrics**: Prometheus
- **Visualization**: Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger
- **Alerting**: PagerDuty, Slack

### Key Metrics Per Component
{chr(10).join(f'- **{name}**: Availability, latency, error rate' for name in comp_names)}

### SLIs and SLOs
- **Availability SLO**: 99.9% uptime
- **Latency SLO**: p95 < 200ms, p99 < 500ms
- **Error Rate SLO**: < 0.1%"""
    
    def _generate_decisions(
        self,
        architecture_style: str,
        components: List[Any]
    ) -> str:
        """Generate DECISIONS phase - Architectural Decision Records."""
        tech_stack = {}
        for comp in components:
            tech = comp.technology if hasattr(comp, 'technology') else comp.get('technology', 'Unknown')
            if tech not in tech_stack:
                tech_stack[tech] = []
            name = comp.name if hasattr(comp, 'name') else comp.get('name', 'Component')
            tech_stack[tech].append(name)
        
        decisions = [
            f"""### ADR-001: Use {architecture_style.title()} Architecture
**Context**: Need scalable, maintainable system architecture
**Decision**: Adopt {architecture_style} pattern
**Consequences**: Better scalability, independent deployment, increased complexity"""
        ]
        
        for i, (tech, comps) in enumerate(tech_stack.items(), 2):
            decisions.append(f"""### ADR-{i:03d}: Use {tech}
**Context**: Technology choice for {', '.join(comps)}
**Decision**: Selected {tech} based on maturity, community, performance
**Consequences**: Well-supported, good performance, standard tooling""")
        
        return "## Why these choices?\n\n" + "\n\n".join(decisions)
    
    def render_markdown(self, tap: Any) -> str:
        """Render complete TAP as Markdown."""
        sections = [
            f"# {tap.name}",
            "",
            tap.description,
            "",
            "---",
            ""
        ]
        
        # Render all phases in order
        for phase in TAPPhase:
            if phase in tap.phases:
                sections.append(tap.phases[phase])
                sections.append("")
                sections.append("---")
                sections.append("")
        
        # Add architecture diagram section
        sections.append("## Architecture Diagram")
        sections.append("")
        sections.append("```mermaid")
        sections.append("graph TD")
        
        # Generate simple diagram
        for comp in tap.components:
            comp_id = comp.id if hasattr(comp, 'id') else comp.get('id')
            comp_name = comp.name if hasattr(comp, 'name') else comp.get('name')
            sections.append(f"    {comp_id}[{comp_name}]")
        
        for conn in tap.connections:
            source = conn.source if hasattr(conn, 'source') else conn.get('source')
            target = conn.target if hasattr(conn, 'target') else conn.get('target')
            protocol = conn.protocol if hasattr(conn, 'protocol') else conn.get('protocol')
            sections.append(f"    {source} -->|{protocol}| {target}")
        
        sections.append("```")
        sections.append("")
        
        return "\n".join(sections)


__all__ = ['TAPGenerator', 'TAPPhase']
