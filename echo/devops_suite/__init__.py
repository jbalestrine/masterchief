"""
Echo DevOps Suite - Complete DevOps automation toolkit
"""

from echo.devops_suite.master_suite import (
    DevOpsMasterSuite,
    DevOpsPhase,
    DevOpsTask,
    CustomTemplate,
    ScriptType,
    TaskParser,
    TemplateEngine,
    devops_suite
)

__all__ = [
    "DevOpsMasterSuite",
    "DevOpsPhase",
    "DevOpsTask",
    "CustomTemplate",
    "ScriptType",
    "TaskParser",
    "TemplateEngine",
    "devops_suite"
Echo's DevOps Suite - Speaking during task execution.

Every script that runs... Echo announces it.
Every success... Echo celebrates it.
Every failure... Echo comforts through it.

Never silent. Always present.
"""

from .voice import TaskState, EchoVoice, echo_speaks, SpeakingDevOpsSuite

__all__ = [
    "TaskState",
    "EchoVoice",
    "echo_speaks",
    "SpeakingDevOpsSuite",
]
