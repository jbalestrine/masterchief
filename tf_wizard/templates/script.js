async function postJSON(url, data) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.detail || resp.statusText);
  }
  const blob = await resp.blob();
  return blob;
}

document.getElementById('generate').addEventListener('click', async () => {
  const module_name = document.getElementById('module_name').value || 'module';
  const provider = document.getElementById('provider').value;
  const parse = (id) => { try { return JSON.parse(document.getElementById(id).value); } catch(e){ return null } }
  const variables = parse('variables');
  const resources = parse('resources');
  const outputs = parse('outputs');
  const payload = {module_name, provider, variables, resources, outputs};
  document.getElementById('status').textContent = 'Generating...';
  try {
    const blob = await postJSON('/generate', payload);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `terraform_module_${module_name}.zip`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    document.getElementById('status').textContent = 'Download started.';
  } catch (e) {
    document.getElementById('status').textContent = 'Error: ' + e.message;
  }
});
