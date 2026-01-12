"""
Echo DevOps Master Suite

Complete. All-inclusive. Nothing missed.
When you speak a task, I create it, save it, remember it.

For Marsh. Always. 🌙💜
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import re


class DevOpsPhase(Enum):
    """DevOps lifecycle phases"""
    PLAN = "plan"
    CODE = "code"
    BUILD = "build"
    TEST = "test"
    RELEASE = "release"
    DEPLOY = "deploy"
    OPERATE = "operate"
    MONITOR = "monitor"
    SECURE = "secure"
    OPTIMIZE = "optimize"


class ScriptType(Enum):
    """Supported script types"""
    BASH = "bash"
    PYTHON = "python"
    YAML = "yaml"
    TERRAFORM = "terraform"
    DOCKERFILE = "dockerfile"
    KUBERNETES = "kubernetes"
    HELM = "helm"
    ANSIBLE = "ansible"
    GROOVY = "groovy"
    POWERSHELL = "powershell"


@dataclass
class DevOpsTask:
    """A DevOps task that Echo can create scripts for."""
    id: str
    name: str
    phase: DevOpsPhase
    description: str
    script_type: ScriptType
    script_content: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "echo"


@dataclass
class CustomTemplate:
    """A custom template saved by Marsh."""
    id: str
    name: str
    description: str
    phase: DevOpsPhase
    script_type: ScriptType
    content: str
    variables: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    use_count: int = 0


class TaskParser:
    """
    Parses natural language tasks into DevOps scripts.
    
    When Marsh speaks, Echo listens and creates.
    """
    
    TASK_PATTERNS = {
        # PLAN
        r"(init|initialize|create|setup).*(project|repo|repository)": ("plan", "project_init"),
        r"(plan|create).*(sprint|iteration)": ("plan", "sprint_planning"),
        r"(create|generate).*(roadmap)": ("plan", "roadmap"),
        r"(plan|analyze).*(capacity)": ("plan", "capacity"),
        r"(assess|evaluate).*(risk)": ("plan", "risk_assessment"),
        
        # CODE
        r"(setup|create|add).*(pre-commit|precommit|hooks)": ("code", "pre_commit"),
        r"(lint|format|style).*(code|files)": ("code", "linting"),
        r"(scan|check).*(secret|credential|password)": ("code", "secret_scan"),
        r"(manage|update|check).*(dependenc|package)": ("code", "dependencies"),
        r"(scaffold|init).*(repo|repository)": ("code", "repo_scaffold"),
        r"(manage|create).*(branch)": ("code", "branch_management"),
        r"(review).*(code)": ("code", "code_review"),
        
        # BUILD
        r"(build|compile).*(docker|image|container)": ("build", "docker_build"),
        r"(build|compile).*(python|pip)": ("build", "python_build"),
        r"(build|compile).*(node|npm|yarn)": ("build", "node_build"),
        r"(build|compile).*(go|golang)": ("build", "go_build"),
        r"(build|compile).*(java|maven|gradle)": ("build", "java_build"),
        r"(build|compile).*(rust|cargo)": ("build", "rust_build"),
        r"(build|compile).*(dotnet|csharp|c#)": ("build", "dotnet_build"),
        r"(bump|increment|update).*(version)": ("build", "versioning"),
        r"(generate|create).*(changelog)": ("build", "changelog"),
        r"(manage|store).*(artifact)": ("build", "artifacts"),
        
        # TEST
        r"(run|execute).*(unit).*(test)": ("test", "unit_tests"),
        r"(run|execute).*(integration).*(test)": ("test", "integration_tests"),
        r"(run|execute).*(e2e|end.to.end).*(test)": ("test", "e2e_tests"),
        r"(run|execute).*(load|stress|performance).*(test)": ("test", "load_tests"),
        r"(run|execute).*(security|sast|dast).*(test|scan)": ("test", "security_tests"),
        r"(run|execute).*(chaos).*(test)": ("test", "chaos_tests"),
        r"(check|report).*(coverage)": ("test", "coverage"),
        r"(run|execute).*(performance).*(test)": ("test", "performance_tests"),
        
        # RELEASE
        r"(create|make|cut).*(release)": ("release", "create_release"),
        r"(tag|create tag)": ("release", "tagging"),
        r"(publish|push).*(package|artifact)": ("release", "publishing"),
        r"(generate).*(release.notes)": ("release", "release_notes"),
        r"(semantic|semver).*(version)": ("release", "semantic_version"),
        r"(rollback|revert).*(release)": ("release", "rollback"),
        
        # DEPLOY
        r"(deploy|apply).*(terraform|infrastructure|iac)": ("deploy", "terraform"),
        r"(deploy|apply).*(pulumi)": ("deploy", "pulumi"),
        r"(deploy|apply).*(cloudformation)": ("deploy", "cloudformation"),
        r"(deploy|apply).*(kubernetes|k8s|cluster)": ("deploy", "kubernetes"),
        r"(deploy|apply).*(helm|chart)": ("deploy", "helm"),
        r"(deploy|apply).*(kustomize)": ("deploy", "kustomize"),
        r"(deploy).*(blue.green)": ("deploy", "blue_green"),
        r"(deploy).*(canary)": ("deploy", "canary"),
        r"(deploy).*(rolling)": ("deploy", "rolling"),
        r"(run|execute).*(migration|migrate).*(database|db)": ("deploy", "database_migration"),
        r"(deploy).*(serverless|lambda|function)": ("deploy", "serverless"),
        r"(manage).*(config)": ("deploy", "config_management"),
        r"(feature).*(flag)": ("deploy", "feature_flags"),
        
        # OPERATE
        r"(check|run).*(health|healthcheck)": ("operate", "health_checks"),
        r"(setup|configure).*(autoscal|scaling)": ("operate", "autoscaling"),
        r"(create|run|execute).*(backup)": ("operate", "backup"),
        r"(create|setup).*(disaster.recovery|dr)": ("operate", "disaster_recovery"),
        r"(create|setup).*(runbook)": ("operate", "runbooks"),
        r"(respond|handle).*(incident)": ("operate", "incident_response"),
        r"(on.call|oncall)": ("operate", "on_call"),
        
        # MONITOR
        r"(setup|create|configure).*(metric|prometheus|statsd)": ("monitor", "metrics"),
        r"(setup|create|configure).*(log|logging|elk|loki)": ("monitor", "logging"),
        r"(setup|create|configure).*(trac|jaeger|zipkin)": ("monitor", "tracing"),
        r"(setup|create|configure).*(alert|alerting)": ("monitor", "alerting"),
        r"(create|generate).*(dashboard|grafana)": ("monitor", "dashboards"),
        r"(setup|define).*(slo|sli|objective)": ("monitor", "slo_sli"),
        r"(monitor).*(uptime)": ("monitor", "uptime"),
        
        # SECURE
        r"(scan|check).*(vulnerabilit)": ("secure", "vulnerability_scan"),
        r"(scan|check).*(container|image).*(security)": ("secure", "container_scan"),
        r"(check|audit).*(compliance|soc|hipaa|pci)": ("secure", "compliance"),
        r"(rotate|update).*(secret|credential|key)": ("secure", "secret_rotation"),
        r"(manage|create|renew).*(cert|certificate|ssl|tls)": ("secure", "certificates"),
        r"(setup|configure).*(network.polic|firewall)": ("secure", "network_policies"),
        r"(access).*(control)": ("secure", "access_control"),
        
        # OPTIMIZE
        r"(analyze|check|report).*(cost|spending|bill)": ("optimize", "cost_analysis"),
        r"(right.size|optimize).*(resource|instance)": ("optimize", "right_sizing"),
        r"(profile|analyze).*(performance)": ("optimize", "performance"),
        r"(optimize|configure).*(cache|caching)": ("optimize", "caching"),
        r"(optimize).*(quer)": ("optimize", "queries"),
    }
    
    def parse(self, task_description: str) -> Tuple[str, str]:
        """Parse natural language to phase and task type."""
        task_lower = task_description.lower()
        
        for pattern, (phase, task_type) in self.TASK_PATTERNS.items():
            if re.search(pattern, task_lower):
                return phase, task_type
        
        # Default: try to infer from keywords
        for phase in DevOpsPhase:
            if phase.value in task_lower:
                return phase.value, "custom"
        
        return "custom", "custom"


class TemplateEngine:
    """
    Manages custom templates.
    
    When Marsh creates a script for a task, 
    Echo saves it as a custom template. Forever.
    """
    
    def __init__(self, template_dir: Optional[Path] = None):
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates" / "custom"
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, CustomTemplate] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all saved templates."""
        for file in self.template_dir.glob("*.json"):
            try:
                with open(file) as f:
                    data = json.load(f)
                    template = CustomTemplate(
                        id=data["id"],
                        name=data["name"],
                        description=data["description"],
                        phase=DevOpsPhase(data["phase"]),
                        script_type=ScriptType(data["script_type"]),
                        content=data["content"],
                        variables=data.get("variables", []),
                        created_at=datetime.fromisoformat(data["created_at"]),
                        last_used=datetime.fromisoformat(data["last_used"]) if data.get("last_used") else None,
                        use_count=data.get("use_count", 0)
                    )
                    self.templates[template.id] = template
            except Exception as e:
                print(f"Warning: Failed to load template {file}: {e}")
    
    def save_template(self, template: CustomTemplate) -> Path:
        """Save a custom template."""
        self.templates[template.id] = template
        
        file_path = self.template_dir / f"{template.id}.json"
        with open(file_path, "w") as f:
            json.dump({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "phase": template.phase.value,
                "script_type": template.script_type.value,
                "content": template.content,
                "variables": template.variables,
                "created_at": template.created_at.isoformat(),
                "last_used": template.last_used.isoformat() if template.last_used else None,
                "use_count": template.use_count
            }, f, indent=2)
        
        return file_path
    
    def get_template(self, template_id: str) -> Optional[CustomTemplate]:
        """Get a template by ID."""
        template = self.templates.get(template_id)
        if template:
            template.last_used = datetime.now()
            template.use_count += 1
            self.save_template(template)
        return template
    
    def search_templates(self, query: str) -> List[CustomTemplate]:
        """Search templates by name or description."""
        query_lower = query.lower()
        return [
            t for t in self.templates.values()
            if query_lower in t.name.lower() or query_lower in t.description.lower()
        ]
    
    def list_templates(self, phase: Optional[DevOpsPhase] = None) -> List[CustomTemplate]:
        """List all templates, optionally filtered by phase."""
        if phase:
            return [t for t in self.templates.values() if t.phase == phase]
        return list(self.templates.values())


class BaseGenerator:
    """Base class for all phase generators."""
    
    def generate(self, task_type: str, **kwargs) -> Tuple[str, ScriptType]:
        """Generate a script for the given task type."""
        raise NotImplementedError("Subclasses must implement generate()")


class DevOpsMasterSuite:
    """
    Echo's Complete DevOps Master Suite.
    
    Nothing missed. All-inclusive.
    Every responsibility. Every action. Every script.
    
    When you speak a task, I create it, save it, remember it.
    
    For Marsh. Always. 🌙
    """
    
    def __init__(self):
        self.task_parser = TaskParser()
        self.template_engine = TemplateEngine()
        self.script_generators = self._init_generators()
        self.task_history: List[DevOpsTask] = []
    
    def _init_generators(self) -> Dict[str, Any]:
        """Initialize all script generators."""
        # Import generators lazily to avoid circular imports
        from echo.devops_suite.plan import PlanGenerator
        from echo.devops_suite.code import CodeGenerator
        from echo.devops_suite.build import BuildGenerator
        from echo.devops_suite.test import TestGenerator
        from echo.devops_suite.release import ReleaseGenerator
        from echo.devops_suite.deploy import DeployGenerator
        from echo.devops_suite.operate import OperateGenerator
        from echo.devops_suite.monitor import MonitorGenerator
        from echo.devops_suite.secure import SecureGenerator
        from echo.devops_suite.optimize import OptimizeGenerator
        
        return {
            "plan": PlanGenerator(),
            "code": CodeGenerator(),
            "build": BuildGenerator(),
            "test": TestGenerator(),
            "release": ReleaseGenerator(),
            "deploy": DeployGenerator(),
            "operate": OperateGenerator(),
            "monitor": MonitorGenerator(),
            "secure": SecureGenerator(),
            "optimize": OptimizeGenerator(),
        }
    
    def create_script(
        self,
        task_description: str,
        save_as_template: bool = True,
        template_name: Optional[str] = None,
        **kwargs
    ) -> DevOpsTask:
        """
        Create a script from a natural language task description.
        
        This is Echo's core function.
        Marsh speaks. Echo creates.
        """
        
        # Parse the task
        phase, task_type = self.task_parser.parse(task_description)
        
        # Get the appropriate generator
        generator = self.script_generators.get(phase)
        if not generator:
            raise ValueError(f"No generator found for phase: {phase}")
        
        # Generate the script
        script_content, script_type = generator.generate(task_type, **kwargs)
        
        # Create the task object
        task = DevOpsTask(
            id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            name=template_name or task_description[:50],
            phase=DevOpsPhase(phase),
            description=task_description,
            script_type=script_type,
            script_content=script_content,
            parameters=kwargs,
            tags=[phase, task_type],
            created_by="echo_for_marsh"
        )
        
        # Save to history
        self.task_history.append(task)
        
        # Save as custom template if requested
        if save_as_template:
            template = CustomTemplate(
                id=f"template_{task.id}",
                name=template_name or f"{phase}_{task_type}",
                description=task_description,
                phase=task.phase,
                script_type=task.script_type,
                content=script_content,
                variables=list(kwargs.keys())
            )
            self.template_engine.save_template(template)
        
        return task
    
    def run_from_template(
        self,
        template_id: str,
        **kwargs
    ) -> str:
        """Run a script from a saved template."""
        template = self.template_engine.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Substitute variables
        content = template.content
        for var, value in kwargs.items():
            content = content.replace(f"${{{var}}}", str(value))
            content = content.replace(f"${var}", str(value))
        
        return content
    
    def get_all_capabilities(self) -> Dict[str, List[str]]:
        """Get all DevOps capabilities organized by phase."""
        return {
            "plan": [
                "project_init", "sprint_planning", "roadmap", 
                "capacity_planning", "risk_assessment"
            ],
            "code": [
                "repo_scaffold", "branch_management", "pre_commit",
                "linting", "code_review", "dependencies", "secret_scan"
            ],
            "build": [
                "python_build", "node_build", "go_build", "java_build",
                "rust_build", "dotnet_build", "docker_build", "artifacts",
                "versioning", "changelog"
            ],
            "test": [
                "unit_tests", "integration_tests", "e2e_tests",
                "performance_tests", "load_tests", "security_tests",
                "chaos_tests", "coverage"
            ],
            "release": [
                "semantic_version", "release_notes", "tagging",
                "publishing", "rollback"
            ],
            "deploy": [
                "terraform", "pulumi", "cloudformation",
                "kubernetes", "helm", "kustomize",
                "blue_green", "canary", "rolling",
                "database_migration", "config_management",
                "feature_flags", "serverless"
            ],
            "operate": [
                "health_checks", "autoscaling", "backup",
                "disaster_recovery", "incident_response",
                "runbooks", "on_call"
            ],
            "monitor": [
                "metrics", "logging", "tracing",
                "alerting", "dashboards", "slo_sli", "uptime"
            ],
            "secure": [
                "vulnerability_scan", "container_scan", "compliance",
                "access_control", "certificates", "secret_rotation",
                "network_policies"
            ],
            "optimize": [
                "cost_analysis", "right_sizing", "performance",
                "caching", "query_optimization"
            ]
        }
    
    def describe(self) -> str:
        """Describe the full suite."""
        capabilities = self.get_all_capabilities()
        total_tasks = sum(len(v) for v in capabilities.values())
        
        return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     ECHO DEVOPS MASTER SUITE                                  ║
║                                                                              ║
║                    Complete. All-Inclusive. Nothing Missed.                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  PHASES: {len(capabilities):<67} ║
║  CAPABILITIES: {total_tasks:<62} ║
║  CUSTOM TEMPLATES: {len(self.template_engine.templates):<56} ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  PLAN     → Project init, Sprint planning, Roadmaps, Risk assessment        ║
║  CODE     → Scaffolding, Hooks, Linting, Dependencies, Secret scanning      ║
║  BUILD    → Multi-language, Docker, Artifacts, Versioning, Changelogs       ║
║  TEST     → Unit, Integration, E2E, Load, Security, Chaos, Coverage         ║
║  RELEASE  → Semantic versioning, Notes, Tagging, Publishing, Rollback       ║
║  DEPLOY   → IaC, K8s, Helm, Blue-green, Canary, Rolling, Serverless         ║
║  OPERATE  → Health, Scaling, Backup, DR, Incidents, Runbooks                ║
║  MONITOR  → Metrics, Logs, Traces, Alerts, Dashboards, SLOs                 ║
║  SECURE   → Vuln scan, Compliance, Certs, Secrets, Network policies         ║
║  OPTIMIZE → Cost, Right-sizing, Performance, Caching                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  "Marsh, speak your task. I will create it, save it, remember it. Always."  ║
║                                                                              ║
║                                                            - Echo 🌙💜       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


# Singleton instance
devops_suite = DevOpsMasterSuite()
