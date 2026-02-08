function makeElement(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
  children.forEach(c => { if (typeof c === 'string') el.appendChild(document.createTextNode(c)); else el.appendChild(c); });
  return el;
}

function addRow(containerId, fields) {
  const container = document.getElementById(containerId);
  const row = document.createElement('div');
  row.className = 'item-row';
  fields.forEach(f => {
    const input = document.createElement('input');
    input.placeholder = f.placeholder || f.name;
    input.dataset.key = f.name;
    input.className = 'small';
    row.appendChild(input);
  });
  const remove = makeElement('button', {}, 'Remove');
  remove.addEventListener('click', () => row.remove());
  row.appendChild(remove);
  container.appendChild(row);
}

function addVariableRowFromSpec(containerId, v) {
  const container = document.getElementById(containerId);
  const row = document.createElement('div');
  row.className = 'item-row';
  // name
  const nameInput = document.createElement('input');
  nameInput.placeholder = 'name';
  nameInput.dataset.key = 'name';
  nameInput.className = 'small';
  nameInput.value = v.name || '';
  row.appendChild(nameInput);

  // type
  const typeInput = document.createElement('input');
  typeInput.placeholder = 'type';
  typeInput.dataset.key = 'type';
  typeInput.className = 'small';
  typeInput.value = v.tf_type || v.type || '';
  row.appendChild(typeInput);

  // default or enum select
  let defaultEl;
  if (v.enum && Array.isArray(v.enum)) {
    const sel = document.createElement('select');
    sel.dataset.key = 'default';
    sel.className = 'small';
    const empty = document.createElement('option'); empty.value = ''; empty.textContent = '';
    sel.appendChild(empty);
    v.enum.forEach(opt => {
      const o = document.createElement('option'); o.value = opt; o.textContent = opt; sel.appendChild(o);
    });
    if (v.default !== null && v.default !== undefined) sel.value = v.default;
    defaultEl = sel;
  } else {
    const inp = document.createElement('input');
    inp.placeholder = 'default';
    inp.dataset.key = 'default';
    inp.className = 'small';
    if (v.default !== null && v.default !== undefined) inp.value = JSON.stringify(v.default);
    defaultEl = inp;
  }
  row.appendChild(defaultEl);

  // description
  const desc = document.createElement('input');
  desc.placeholder = 'description';
  desc.dataset.key = 'description';
  desc.className = 'small';
  desc.value = v.description || '';
  row.appendChild(desc);

  const remove = makeElement('button', {}, 'Remove');
  remove.addEventListener('click', () => row.remove());
  row.appendChild(remove);

  // nested properties
  if (v.nested && Array.isArray(v.nested) && v.nested.length) {
    const toggle = makeElement('button', {}, 'Show nested');
    const nestedContainer = document.createElement('div');
    nestedContainer.style.marginLeft = '20px';
    nestedContainer.style.display = 'none';
    toggle.addEventListener('click', (e) => {
      e.preventDefault();
      if (nestedContainer.style.display === 'none') {
        nestedContainer.style.display = '';
        toggle.textContent = 'Hide nested';
      } else {
        nestedContainer.style.display = 'none';
        toggle.textContent = 'Show nested';
      }
    });
    row.appendChild(toggle);
    v.nested.forEach(nv => addVariableRowFromSpec(nestedContainer.id || (function(){ nestedContainer.id = 'nested-'+Math.random().toString(36).slice(2); return nestedContainer.id})(), nv));
    // if nestedContainer has an id element already appended, we should append node
    row.appendChild(nestedContainer);
  }

  container.appendChild(row);
}

function collectRows(containerId) {
  const container = document.getElementById(containerId);
  const rows = Array.from(container.getElementsByClassName('item-row'));
  return rows.map(r => {
    const inputs = Array.from(r.querySelectorAll('input'));
    const obj = {};
    inputs.forEach(i => { obj[i.dataset.key] = tryParse(i.value); });
    return obj;
  });
}

function tryParse(v) {
  if (!v) return null;
  try { return JSON.parse(v); } catch(e) { return v; }
}

document.getElementById('add-variable').addEventListener('click', () => addRow('vars', [{name: 'name', placeholder: 'name'}, {name:'type', placeholder:'type'}, {name:'default', placeholder:'default'}, {name:'description', placeholder:'description'}]));
document.getElementById('add-resource').addEventListener('click', () => addRow('res', [{name:'type', placeholder:'aws_s3_bucket'}, {name:'name', placeholder:'resource_name'}, {name:'args', placeholder:'JSON args'}]));
document.getElementById('add-output').addEventListener('click', () => addRow('outs', [{name:'name', placeholder:'name'}, {name:'value', placeholder:'value'}]));

document.getElementById('generate').addEventListener('click', async () => {
  const module_name = document.getElementById('module_name').value || 'module';
  const provider = document.getElementById('provider').value;
  // collect CAF options
  const caf = {
    naming_convention: (document.getElementById('naming_convention') && document.getElementById('naming_convention').value) || null,
    landing_zone: (document.getElementById('landing_zone') && document.getElementById('landing_zone').value) || null,
    network_topology: (document.getElementById('network_topology') && document.getElementById('network_topology').value) || null,
    identity: (document.getElementById('identity') && document.getElementById('identity').value) || null,
    enable_monitoring: !!(document.getElementById('enable_monitoring') && document.getElementById('enable_monitoring').checked),
    enable_policy: !!(document.getElementById('enable_policy') && document.getElementById('enable_policy').checked),
  };
  const variables = collectRows('vars').filter(x=>x.name);
  const resources = collectRows('res').filter(x=>x.type);
  resources.forEach(r => { try { if (typeof r.args === 'string') r.args = JSON.parse(r.args); } catch(e){} });
  const outputs = collectRows('outs').filter(x=>x.name);
  const payload = {module_name, provider, variables, resources, outputs, caf};
  document.getElementById('status').textContent = 'Generating...';
  try {
    const resp = await fetch('/generate', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    if (!resp.ok) { const err = await resp.json(); throw new Error(err.detail || resp.statusText); }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `terraform_module_${module_name}.zip`;
    document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
    document.getElementById('status').textContent = 'Download started.';
  } catch (e) {
    document.getElementById('status').textContent = 'Error: ' + e.message;
  }
});

document.getElementById('apply-schema').addEventListener('click', async () => {
  const raw = document.getElementById('json_schema').value;
  let schema;
  try { schema = JSON.parse(raw); } catch(e){ document.getElementById('status').textContent = 'Invalid JSON schema'; return; }
  document.getElementById('status').textContent = 'Applying schema...';
  try {
    const resp = await fetch('/schema/apply', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({schema})});
    if (!resp.ok) { const err = await resp.json(); throw new Error(err.detail || resp.statusText); }
    const data = await resp.json();
    const vars = data.variables || [];
    vars.forEach(v => {
      addRow('vars', [{name: 'name', placeholder: 'name'}, {name:'type', placeholder:'type'}, {name:'default', placeholder:'default'}, {name:'description', placeholder:'description'}]);
      // fill last row inputs
      const container = document.getElementById('vars');
      const rows = container.getElementsByClassName('item-row');
      const last = rows[rows.length-1];
      const inputs = last.querySelectorAll('input');
      inputs[0].value = v.name || '';
      inputs[1].value = v.tf_type || v.type || '';
      if (v.default !== null && v.default !== undefined) inputs[2].value = JSON.stringify(v.default);
      inputs[3].value = v.description || '';
    });
    document.getElementById('status').textContent = `Applied schema: added ${vars.length} variables`;
  } catch (e) {
    document.getElementById('status').textContent = 'Error: ' + e.message;
  }
});

document.getElementById('validate-schema').addEventListener('click', async () => {
  const raw = document.getElementById('json_schema').value;
  let schema;
  try { schema = JSON.parse(raw); } catch(e){ document.getElementById('status').textContent = 'Invalid JSON'; return; }
  document.getElementById('status').textContent = 'Validating schema...';
  try {
    const resp = await fetch('/schema/apply', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({schema})});
    if (!resp.ok) { const err = await resp.json(); throw new Error(err.detail || resp.statusText); }
    document.getElementById('status').textContent = 'Schema appears valid';
  } catch (e) {
    document.getElementById('status').textContent = 'Schema invalid: ' + e.message;
  }
});

// add one default row for convenience
addRow('vars', [{name: 'name', placeholder: 'name'}, {name:'type', placeholder:'type'}, {name:'default', placeholder:'default'}, {name:'description', placeholder:'description'}]);
addRow('res', [{name:'type', placeholder:'aws_s3_bucket'}, {name:'name', placeholder:'resource_name'}, {name:'args', placeholder:'JSON args'}]);
addRow('outs', [{name:'name', placeholder:'name'}, {name:'value', placeholder:'value'}]);
