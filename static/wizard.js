// Simple helper for script save (used by /scripts/edit form)
async function saveScript(path, content) {
  const res = await fetch('/api/scripts/save', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({path, content})
  });
  return res.json();
}

// Submit template form via fetch and open preview in a new window
async function submitTemplateForm(kind, formEl) {
  const formData = new FormData(formEl);
  const body = {};
  for (const [k,v] of formData.entries()) body[k]=v;
  const res = await fetch('/templates/' + kind, {method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body)});
  const html = await res.text();
  const w = window.open();
  w.document.write(html);
}

// Save generated template from preview page by calling /api/templates/save
async function saveGeneratedTemplate(name, kind, content) {
  const res = await fetch('/api/templates/save', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name, kind, content})});
  return res.json();
}

// Feature flags save helper
async function saveFeatureFlags(flags) {
  const res = await fetch('/api/features/save', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(flags)});
  return res.json();
}
