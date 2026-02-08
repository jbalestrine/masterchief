from pydantic import BaseModel, Field, model_validator, ValidationError
from typing import List, Dict, Any, Optional


class VariableSpec(BaseModel):
    name: str
    type: Optional[str] = "string"
    default: Optional[Any] = None
    description: Optional[str] = None


class ResourceSpec(BaseModel):
    type: str
    name: str
    args: Optional[Dict[str, Any]] = Field(default_factory=dict)


class OutputSpec(BaseModel):
    name: str
    value: str


class ModuleSpec(BaseModel):
    module_name: str
    provider: str
    variables: List[VariableSpec] = Field(default_factory=list)
    resources: List[ResourceSpec] = Field(default_factory=list)
    outputs: List[OutputSpec] = Field(default_factory=list)
    caf: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @model_validator(mode='after')
    def check_provider(self):
        if self.provider not in ('aws', 'azurerm', 'google'):
            raise ValueError('provider must be one of: aws, azurerm, google')
        return self


def validate_spec(spec: dict) -> ModuleSpec:
    try:
        return ModuleSpec(**spec)
    except ValidationError as e:
        raise
