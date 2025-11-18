// DARK MODE
document.getElementById("darkToggle").addEventListener("change", () => {
  document.documentElement.classList.toggle("dark");
});

// ======================
//       QUICK SCAN
// ======================
document.getElementById("btn-quick").onclick = async () => {
  const url = document.getElementById("quick-url").value.trim();
  if (!url) return alert("Masukkan URL");

  const res = await fetch("/scan/web", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  const data = await res.json();
  console.log("Single Scan:", data);
};


// ======================
//       BULK SCAN
// ======================
const btnBulk = document.getElementById("btn-bulk");
const btnStop = document.getElementById("btn-stop-bulk");

btnBulk.onclick = async () => {
  const txt = document.getElementById("bulk-urls").value.trim();
  if (!txt) return alert("Masukkan list URL!");

  btnBulk.disabled = true;
  btnStop.disabled = false;

  const urls = txt.split(/\r?\n/).map((u) => u.trim()).filter(Boolean);

  const res = await fetch("/scan/bulk", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ urls }),
  });

  const result = await res.json();
  console.log("Bulk Result:", result);

  btnBulk.disabled = false;
  btnStop.disabled = true;
};

btnStop.onclick = async () => {
  await fetch("/scan/stop", { method: "POST" });
};


// ======================
//       WEBSOCKET
// ======================
const ws = new WebSocket(
  (location.protocol === "https:" ? "wss://" : "ws://") +
    location.host +
    "/scan/ws"
);

ws.onmessage = (ev) => {
  const p = JSON.parse(ev.data);

  if (!p.data) return;

  const d = p.data;

  const tbody = document.getElementById("history-body");

  const row = document.createElement("tr");
  row.innerHTML = `
    <td>${d.url}</td>
    <td>${d.status_code ?? "-"}</td>
    <td>${d.latency_ms ?? "-"}</td>
    <td>${new Date(d.created_at).toLocaleTimeString()}</td>
  `;

  tbody.prepend(row);

  // suara notif
  if (d.status_code >= 500) {
    document.getElementById("notifSound").play();
  }
};
