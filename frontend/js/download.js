async function downloadAdapter() {
  const id = document.getElementById("jobId").value;
  const msg = document.getElementById("message");

  if (!id) {
    msg.innerHTML = `<div class='text-red-400'>⚠ Enter job ID</div>`;
    return;
  }

  const url = `${API}/download/adapter/${id}`;

  try {
    const res = await fetch(url);

    if (!res.ok) {
      msg.innerHTML = `<div class='text-red-400'>❌ Adapter not ready or job not found</div>`;
      return;
    }

    const blob = await res.blob();
    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = `adapter_job_${id}.zip`;
    document.body.appendChild(link);
    link.click();
    link.remove();

    msg.innerHTML = `<div class='text-green-400'>✅ Download started</div>`;

  } catch (e) {
    msg.innerHTML = `<div class='text-red-400'>❌ Error: ${e.message}</div>`;
  }
}
