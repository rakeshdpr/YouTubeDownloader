document.getElementById("fetch-formats-btn").onclick = async () => {
  const url = document.getElementById("url-input").value.trim();
  const statusDiv = document.getElementById("status");
  if (!url) {
    statusDiv.textContent = "Please enter a YouTube URL.";
    return;
  }
  statusDiv.textContent = "Fetching formats...";
  try {
    const res = await fetch("/formats", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = await res.json();
    if (res.ok) {
      const formats = data.formats;
      const select = document.getElementById("formats-select");
      select.innerHTML = "";
      formats.forEach((fmt, idx) => {
        const opt = document.createElement("option");
        opt.value = idx;
        opt.textContent = `${fmt.resolution} (${fmt.ext}) - ${fmt.type} [ID: ${fmt.id}]`;
        opt.dataset.id = fmt.id;
        opt.dataset.type = fmt.type;
        select.appendChild(opt);
      });
      document.getElementById("formats-container").style.display = "block";
      statusDiv.textContent = "Select a format and click Download.";
    } else {
      statusDiv.textContent = data.error || "Failed to fetch formats.";
    }
  } catch (e) {
    statusDiv.textContent = "Error fetching formats.";
  }
};

document.getElementById("download-btn").onclick = async () => {
  const url = document.getElementById("url-input").value.trim();
  const select = document.getElementById("formats-select");
  const selectedOption = select.options[select.selectedIndex];
  const format_id = selectedOption.dataset.id;
  const format_type = selectedOption.dataset.type;
  const statusDiv = document.getElementById("status");

  statusDiv.textContent = "Downloading video, please wait...";

  try {
    const res = await fetch("/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, format_id, format_type }),
    });
    const data = await res.json();
    if (res.ok) {
      statusDiv.innerHTML = `Download complete! <a href="/download_file/${encodeURIComponent(data.filename)}" download>Click here to download</a>`;
    } else {
      statusDiv.textContent = data.error || "Download failed.";
    }
  } catch (e) {
    statusDiv.textContent = "Error downloading video.";
  }
};
