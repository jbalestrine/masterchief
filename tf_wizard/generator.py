"""
TF Wizard Generator – generates Terraform module ZIP archives from a spec dict.

Public API
----------
- generate_module_zip(spec: dict) -> bytes
- tf_type_from_spec(meta: dict | str) -> str
"""

from __future__ import annotations

import io
import json
import textwrap
import zipfile
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Type mapping helpers
# ---------------------------------------------------------------------------

_JS_TO_TF: Dict[str, str] = {
    "string": "string",
    "number": "number",
    "integer": "number",
    "boolean": "bool",
    "bool": "bool",
    "array": "list(string)",
    "object": "map(string)",
}


def tf_type_from_spec(meta: Any) -> str:
    """Convert a JSON‑schema property description (or a plain type string) to
    a Terraform type expression.

    Supports:
    * plain string type names – ``"string"`` → ``"string"``
    * dict with ``type`` key – ``{"type": "array", "items": {"type": "number"}}``
      → ``"list(number)"``
    * nested objects – ``{"type": "object", "properties": {...}}`` → ``object({...})``
    """
    if isinstance(meta, str):
        return _JS_TO_TF.get(meta.lower(), "string")

    if not isinstance(meta, dict):
        return "string"

    js_type = (meta.get("type") or "string").lower()

    # ----- array -----
    if js_type == "array":
        items = meta.get("items", {})
        inner = tf_type_from_spec(items) if isinstance(items, dict) else "string"
        return f"list({inner})"

    # ----- object with properties -----
    if js_type == "object" and isinstance(meta.get("properties"), dict):
        parts: List[str] = []
        for k, v in meta["properties"].items():
            parts.append(f"    {k} = {tf_type_from_spec(v)}")
        inner_block = "\n".join(parts)
        return f"object({{\n{inner_block}\n  }})"

    # ----- plain object (map) -----
    if js_type == "object":
        return "map(string)"

    return _JS_TO_TF.get(js_type, "string")


# ---------------------------------------------------------------------------
# Terraform file renderers
# ---------------------------------------------------------------------------

def _render_variable_block(var: dict) -> str:
    """Render a single ``variable`` block for *variables.tf*."""
    name = var.get("name", "unnamed")
    tf_type = var.get("tf_type") or tf_type_from_spec(var.get("type", "string"))
    description = var.get("description", "")
    default = var.get("default")
    sensitive = var.get("sensitive", False)
    validation = var.get("validation")

    lines = [f'variable "{name}" {{']
    lines.append(f'  type        = {tf_type}')
    if description:
        lines.append(f'  description = "{description}"')
    if default is not None:
        lines.append(f'  default     = {_tf_value(default)}')
    if sensitive:
        lines.append("  sensitive   = true")
    if validation and isinstance(validation, dict):
        cond = validation.get("condition", "true")
        err  = validation.get("error_message", "Invalid value.")
        lines.append("  validation {")
        lines.append(f'    condition     = {cond}')
        lines.append(f'    error_message = "{err}"')
        lines.append("  }")
    lines.append("}\n")
    return "\n".join(lines)


def _render_output_block(out: dict) -> str:
    name = out.get("name", "unnamed")
    value = out.get("value", '""')
    description = out.get("description", "")
    lines = [f'output "{name}" {{']
    lines.append(f"  value       = {value}")
    if description:
        lines.append(f'  description = "{description}"')
    lines.append("}\n")
    return "\n".join(lines)


def _tf_value(val: Any) -> str:
    """Render a Python value as a Terraform literal."""
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        return f'"{val}"'
    if isinstance(val, list):
        inner = ", ".join(_tf_value(v) for v in val)
        return f"[{inner}]"
    if isinstance(val, dict):
        inner = ", ".join(f'{k} = {_tf_value(v)}' for k, v in val.items())
        return f"{{{inner}}}"
    return f'"{val}"'


# ---------------------------------------------------------------------------
# Main ZIP generator
# ---------------------------------------------------------------------------

def generate_module_zip(spec: dict) -> bytes:
    """Generate a Terraform module as an in‑memory ZIP file and return raw
    bytes.

    Expected *spec* keys:

    * ``module_name`` – name used for the root folder inside the zip
    * ``variables``   – list of variable dicts (name, type, description, default, …)
    * ``outputs``     – list of output dicts  (name, value, description)
    * ``providers``   – list of provider dicts (name, source, version)
    * ``resources``   – list of resource dicts (type, name, attributes)
    * ``backend``     – optional backend config dict
    """
    module_name: str = spec.get("module_name", "module")
    variables: List[dict] = spec.get("variables", [])
    outputs: List[dict] = spec.get("outputs", [])
    providers: List[dict] = spec.get("providers", [])
    resources: List[dict] = spec.get("resources", [])
    backend: Optional[dict] = spec.get("backend")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        prefix = f"{module_name}/"

        # --- versions.tf (terraform block) ---
        tf_block_lines = ['terraform {']
        if providers:
            tf_block_lines.append("  required_providers {")
            for p in providers:
                pname = p.get("name", "aws")
                source = p.get("source", f"hashicorp/{pname}")
                version = p.get("version", ">= 1.0")
                tf_block_lines.append(f"    {pname} = {{")
                tf_block_lines.append(f'      source  = "{source}"')
                tf_block_lines.append(f'      version = "{version}"')
                tf_block_lines.append("    }")
            tf_block_lines.append("  }")
        if backend:
            btype = backend.get("type", "local")
            tf_block_lines.append(f'  backend "{btype}" {{')
            for bk, bv in backend.items():
                if bk == "type":
                    continue
                tf_block_lines.append(f'    {bk} = "{bv}"')
            tf_block_lines.append("  }")
        tf_block_lines.append("}\n")
        zf.writestr(prefix + "versions.tf", "\n".join(tf_block_lines))

        # --- variables.tf ---
        var_blocks = [_render_variable_block(v) for v in variables]
        zf.writestr(prefix + "variables.tf", "\n".join(var_blocks) if var_blocks else "# No variables defined\n")

        # --- outputs.tf ---
        out_blocks = [_render_output_block(o) for o in outputs]
        zf.writestr(prefix + "outputs.tf", "\n".join(out_blocks) if out_blocks else "# No outputs defined\n")

        # --- main.tf (resources) ---
        main_lines: List[str] = []
        for r in resources:
            rtype = r.get("type", "null_resource")
            rname = r.get("name", "this")
            attrs = r.get("attributes", {})
            main_lines.append(f'resource "{rtype}" "{rname}" {{')
            for ak, av in attrs.items():
                main_lines.append(f"  {ak} = {_tf_value(av)}")
            main_lines.append("}\n")
        zf.writestr(prefix + "main.tf", "\n".join(main_lines) if main_lines else "# Add resources here\n")

        # --- README.md ---
        readme = textwrap.dedent(f"""\
            # {module_name}

            Terraform module generated by **MasterChief TF Wizard**.

            ## Variables

            | Name | Type | Description |
            |------|------|-------------|
            """)
        for v in variables:
            readme += f"| {v.get('name','')} | {v.get('type','string')} | {v.get('description','')} |\n"
        zf.writestr(prefix + "README.md", readme)

    return buf.getvalue()
