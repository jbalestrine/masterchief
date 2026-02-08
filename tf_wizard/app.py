from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
import uvicorn
import io
import json
from .generator import generate_module_zip
import os
from jsonschema import Draft7Validator
from .generator import tf_type_from_spec

app = FastAPI(title="TF Wizard")

HERE = os.path.dirname(__file__)
templates = Environment(loader=FileSystemLoader(os.path.join(HERE, "templates")), autoescape=select_autoescape())

# Mount static assets (JS/CSS)
app.mount("/static", StaticFiles(directory=os.path.join(HERE, "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    tmpl = templates.get_template("index.html")
    return tmpl.render()


@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    try:
        zip_bytes = generate_module_zip(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StreamingResponse(io.BytesIO(zip_bytes), media_type="application/zip", headers={"Content-Disposition": f"attachment; filename=terraform_module_{data.get('module_name','module')}.zip"})



@app.post('/schema/apply')
async def apply_schema(request: Request):
    payload = await request.json()
    schema = payload.get('schema')
    if not schema:
        raise HTTPException(status_code=400, detail='schema is required')
    # Validate schema is valid JSON Schema (Draft7)
    try:
        Draft7Validator.check_schema(schema)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'invalid schema: {e}')

    props = schema.get('properties', {})
    vars_out = []
    def build_var(name, meta):
        js_type = meta.get('type')
        # Use generator helper to build tf_type (supports dict schema too)
        tf_type = tf_type_from_spec(meta) if isinstance(meta, dict) else tf_type_from_spec(js_type or '')

        v = {
            'name': name,
            'type': js_type or 'string',
            'tf_type': tf_type,
            'default': meta.get('default') if isinstance(meta, dict) and 'default' in meta else None,
            'description': meta.get('description', '') if isinstance(meta, dict) else '',
        }
        # if object with nested properties, return nested details
        if isinstance(meta, dict) and meta.get('type') == 'object' and isinstance(meta.get('properties'), dict):
            nested = []
            for nk, nv in meta.get('properties', {}).items():
                nested.append(build_var(nk, nv))
            v['nested'] = nested
        if isinstance(meta, dict) and 'enum' in meta:
            v['enum'] = meta.get('enum')
        return v

    for name, meta in props.items():
        vars_out.append(build_var(name, meta))
    return {'variables': vars_out}


if __name__ == "__main__":
    uvicorn.run("tf_wizard.app:app", host="127.0.0.1", port=8000, reload=True)
