const byId = (id) => document.getElementById(id);
function drawTrend(readings) {
  const canvas = byId('trend'), ctx = canvas.getContext('2d'), values = readings.filter(r => r.connected).slice(-100);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (!values.length) { ctx.fillStyle = '#a9b7c6'; ctx.fillText('No valid measurements yet', 20, 30); return; }
  const chart = (key, color, min, max) => { ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.beginPath(); values.forEach((r, i) => { const x = i * canvas.width / Math.max(1, values.length - 1); const y = canvas.height - ((r[key] - min) / (max - min)) * (canvas.height - 24) - 12; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); ctx.stroke(); };
  chart('temperature_c', '#f59e0b', -40, 80); chart('humidity_percent', '#38bdf8', 0, 100);
  ctx.fillStyle = '#f59e0b'; ctx.fillText('Temperature (orange)', 12, 18); ctx.fillStyle = '#38bdf8'; ctx.fillText('Humidity (blue)', 160, 18);
}
async function refresh() {
  const [readings, runs] = await Promise.all([fetch('/api/readings').then(r => r.json()), fetch('/api/regressions').then(r => r.json())]);
  const latest = readings.at(-1); if (latest) { byId('temperature').textContent = latest.temperature_c ?? '—'; byId('humidity').textContent = latest.humidity_percent ?? '—'; byId('connection').textContent = latest.connected ? 'Connected' : 'Disconnected'; byId('connection').className = latest.connected ? 'pass' : 'fail'; byId('last-seen').textContent = new Date(latest.timestamp).toLocaleString(); }
  const run = runs.at(-1); if (run) { const quality = run.quality_summary; byId('regression').textContent = run.status; byId('regression').className = run.status === 'PASS' ? 'pass' : 'fail'; byId('regression-time').textContent = new Date(run.finished_at).toLocaleString(); byId('release-gate').textContent = quality ? (quality.release_ready ? 'READY' : 'BLOCKED') : 'LEGACY'; byId('release-gate').className = !quality || quality.release_ready ? 'pass' : 'fail'; byId('quality-summary').textContent = quality ? `${quality.passed}/${quality.total_cases} passed · ${quality.pass_rate_percent}%` : 'Run predates quality metrics'; }
  byId('runs').innerHTML = runs.slice().reverse().slice(0, 10).map(run => `<tr><td>${new Date(run.finished_at).toLocaleString()}</td><td>${run.run_id.slice(0, 8)}</td><td class="${run.status === 'PASS' ? 'pass' : 'fail'}">${run.status}</td><td>${run.results.map(x => `${x.test_id || x.name}: ${x.status}`).join(', ')}</td></tr>`).join(''); drawTrend(readings);
}
refresh(); setInterval(refresh, 5000);
