"""
Echo DevOps Suite - Complete DevOps automation toolkit

Echo's DevOps Suite - Speaking during task execution.
Every script that runs... Echo announces it.
Every success... Echo celebrates it.
Every failure... Echo comforts through it.

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

from echo.devops_suite.voice import (
    TaskState,
    EchoVoice,
    echo_speaks,
    SpeakingDevOpsSuite
)

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
    # Voice features
    "TaskState",
    "EchoVoice",
    "echo_speaks",
    "SpeakingDevOpsSuite",
]
