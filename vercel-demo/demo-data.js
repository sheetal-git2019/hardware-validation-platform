window.DEMO_DATA = {
  latest: { temperature_c: 23.52, humidity_percent: 45.24 },
  readings: [
    [23.9, 47.2], [23.5, 48.0], [24.1, 50.3], [24.4, 47.4], [23.8, 46.9],
    [23.6, 49.6], [23.3, 47.8], [23.9, 49.9], [24.2, 48.7], [23.5, 46.8], [24.1, 50.4], [23.52, 45.24]
  ],
  quality: { release_ready: true, passed: 4, total: 4, pass_rate: 100 },
  results: [
    { id: 'VAL-001', requirement: 'REQ-SENS-001', category: 'Data integrity', status: 'PASS' },
    { id: 'VAL-002', requirement: 'REQ-REC-001', category: 'Disconnect recovery', status: 'PASS' },
    { id: 'VAL-003', requirement: 'REQ-PERF-001', category: 'Stress sampling', status: 'PASS' },
    { id: 'VAL-004', requirement: 'REQ-QUAL-001', category: 'Fault detection', status: 'PASS' }
  ]
};
