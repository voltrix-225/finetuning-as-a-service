let jobs = JSON.parse(localStorage.getItem("jobs") || "[]");
// leave empty for now — only save in train page

document.getElementById("uploadBtn").onclick = async () => {
  const name = document.getElementById("datasetName").value;
  const file = document.getElementById("fileInput").files[0];
  const status = document.getElementById("uploadStatus");

  if (!name || !file) {
    status.textContent = "⚠ Enter name & choose file";
    status.className = "text-red-400 glitch";
    return;
  }

  const form = new FormData();
  form.append("name", name);
  form.append("file", file);

  status.textContent = "⏳ Uploading...";   
  status.className = "text-yellow-300 pulse-text";

  try {
    const res = await fetch(`${API}/api/datasets/upload`, {
      method: "POST",
      body: form,
    });

    if (!res.ok) throw new Error();
    const data = await res.json();
    localStorage.setItem("lastDatasetId", data.id);

    status.textContent = "✅ Uploaded Successfully!";
    status.className = "text-green-400 neon-glow";
  } catch {
    status.textContent = "❌ Upload failed";
    status.className = "text-red-400 glitch";
  }
};
