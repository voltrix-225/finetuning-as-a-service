const list = document.getElementById("jobList");

async function fetchJobs() {
  const jobIds = JSON.parse(localStorage.getItem("jobs") || "[]");

  if (jobIds.length === 0) {
    list.innerHTML = "<p class='text-gray-400'>No jobs yet</p>";
    return;
  }

  let html = "";

  for (const id of jobIds) {
    try {
      const res = await fetch(`${API}/jobs/${id}`);
      if (!res.ok) continue;

      const job = await res.json();
      html += `
        <div class="bg-black/50 border border-purple-500 p-4 rounded">
          <div class="font-bold text-purple-300">Job #${job.id}</div>
          <div>Status: <span class="text-green-300">${job.status}</span></div>
          <div>Dataset: ${job.dataset_id}</div>
          <div>Epochs: ${job.epochs}</div>
        </div>
      `;
    } catch {}
  }

  list.innerHTML = html;
}

setInterval(fetchJobs, 2500);
fetchJobs();
