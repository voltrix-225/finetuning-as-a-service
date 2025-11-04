async function loadTrainedModels() {
  const res = await fetch(`${API}/models/trained`);
  const models = await res.json();

  const select = document.getElementById("modelSelect");
  const base = document.getElementById("baseModel");
  const adapter = document.getElementById("adapterId");

  if (models.length === 0) {
    select.innerHTML = `<option>No trained models found</option>`;
    return;
  }

  select.innerHTML = "";
  models.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m.job_id;
    opt.textContent = `Job ${m.job_id}: ${m.base_model}`;
    select.appendChild(opt);
  });

  const latest = models[0];
  select.value = latest.job_id;
  base.value = latest.base_model;
  adapter.value = latest.job_id;
  
  select.addEventListener("change", () => {
    const selected = models.find(v => v.job_id == select.value);
    base.value = selected.base_model;
    adapter.value = selected.job_id;
  });
}

async function infer() {
  const btn = document.getElementById("runBtn");
  btn.innerText = "⏳ Generating...";
  btn.disabled = true;

  const prompt = document.getElementById("prompt").value;
  const out = document.getElementById("result");
  
  out.innerHTML += `<div class="user-msg">> ${prompt}</div>`;

  const form = new FormData();
  form.append("base_model", document.getElementById("baseModel").value);
  form.append("adapter_job_id", document.getElementById("adapterId").value);
  form.append("prompt", prompt);

  const res = await fetch(`${API}/infer`, { method: "POST", body: form });
  const json = await res.json();

  out.innerHTML += `<div class="bot-msg">${json.response}</div>`;

  out.scrollTop = out.scrollHeight;

  btn.innerText = "✨ Generate Response";
  btn.disabled = false;
}

document.addEventListener("DOMContentLoaded", () => {
  loadTrainedModels();
  document.getElementById("runBtn").onclick = infer;
});
