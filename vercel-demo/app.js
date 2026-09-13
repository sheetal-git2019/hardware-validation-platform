const data = window.DEMO_DATA;
const el = (id) => document.getElementById(id);
el('temperature').textContent = data.latest.temperature_c;
el('humidity').textContent = data.latest.humidity_percent;
el('gate').textContent = data.quality.release_ready ? 'READY' : 'BLOCKED';
el('gate').className = data.quality.release_ready ? 'pass' : 'fail';
el('gate-detail').textContent = 'No blocking failures';
el('status').textContent = 'PASS'; el('status').className = 'pass';
el('case-count').textContent = `${data.quality.passed}/${data.quality.total} passed · ${data.quality.pass_rate}%`;
el('results').innerHTML = data.results.map(row => `<tr><td>${row.id}</td><td>${row.requirement}</td><td>${row.category}</td><td class="pass">${row.status}</td></tr>`).join('');
const canvas = el('trend'), ctx = canvas.getContext('2d');
ctx.clearRect(0, 0, canvas.width, canvas.height);
function line(index, color, min, max) { ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.beginPath(); data.readings.forEach((reading, i) => { const x = i * canvas.width / (data.readings.length - 1); const y = canvas.height - ((reading[index] - min) / (max - min)) * (canvas.height - 42) - 14; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); ctx.stroke(); }
line(0, '#f59e0b', -40, 80); line(1, '#38bdf8', 0, 100);
ctx.font = '14px system-ui'; ctx.fillStyle = '#f59e0b'; ctx.fillText('Temperature (orange)', 14, 22); ctx.fillStyle = '#38bdf8'; ctx.fillText('Humidity (blue)', 175, 22);
