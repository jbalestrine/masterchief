"""
Echo DevOps Suite - Complete DevOps automation toolkit

Every script that runs... Echo can announce it.
Every success... Echo can celebrate it.
Every failure... Echo can comfort through it.

Never silent. Always present.
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

try:
    from echo.devops_suite.voice import TaskState, EchoVoice, echo_speaks, SpeakingDevOpsSuite
except ImportError:
    # Voice module may not be available in all configurations
    TaskState = None
    EchoVoice = None
    echo_speaks = None
    SpeakingDevOpsSuite = None

__all__ = [
    # Core suite
    "DevOpsMasterSuite",
    "DevOpsPhase",
    "DevOpsTask",
    "CustomTemplate",
    "ScriptType",
    "TaskParser",
    "TemplateEngine",
    "devops_suite",
    "TaskState",
    "EchoVoice",
    "echo_speaks",
    "SpeakingDevOpsSuite",
]

