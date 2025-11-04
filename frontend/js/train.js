const datasetBox = document.getElementById("datasetId");
const modelBox = document.getElementById("baseModel");
const statusBox = document.getElementById("trainStatus");

datasetBox.value = localStorage.getItem("lastDatasetId") || "";

// Load models
async function loadModels() {
  try {
    const res = await fetch(`${API}/models`);
    const data = await res.json();

    modelBox.innerHTML = data.models
      .map(m => `<option value="${m.id}">${m.name}</option>`)
      .join("");
  } catch {
    modelBox.innerHTML = "<option>Error loading models</option>";
  }
}
loadModels();

// Train click
document.getElementById("trainBtn").onclick = async () => {
  const dataset_id = datasetBox.value;
  const base_model = modelBox.value;
  const epochs = document.getElementById("epochs").value || 1;

  if (!dataset_id) {
    statusBox.textContent = "⚠ Upload dataset first!";
    statusBox.className = "text-red-400 glitch";
    return;
  }

  statusBox.textContent = "⏳ Queuing...";
  statusBox.className = "text-yellow-300 pulse-text";

  const form = new FormData();
  form.append("dataset_id", dataset_id);
  form.append("base_model", base_model);
  form.append("epochs", epochs);

  try {
    const res = await fetch(`${API}/start_training/`, { method: "POST", body: form });
    if (!res.ok) throw new Error();

    const data = await res.json();

    // ✅ Save job id from backend correct field
    const jobs = JSON.parse(localStorage.getItem("jobs") || "[]");
    jobs.push(data.id);   // <- correct for /start_training/
    localStorage.setItem("jobs", JSON.stringify(jobs));

    localStorage.setItem("lastDatasetId", dataset_id);

    statusBox.textContent = `✅ Training queued (Job ${data.id})`;
    statusBox.className = "text-green-400 neon-glow";
  } catch {
    statusBox.textContent = "❌ Failed";
    statusBox.className = "text-red-400 glitch";
  }
};
