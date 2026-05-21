#!/usr/bin/env node
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const dashboardDir = path.join(root, 'grafana', 'dashboards');
const grafanaUrl = process.env.GRAFANA_URL || 'http://localhost:3009';
const user = process.env.GRAFANA_ADMIN_USER || 'admin';
const password = process.env.GRAFANA_ADMIN_PASSWORD || 'admin';
const auth = Buffer.from(`${user}:${password}`).toString('base64');

const files = [
  'dmr-overview.json',
  'dmr-electrification-fuel-transition.json',
  'dmr-market-leasing-brands.json',
  'dmr-performance-practicality.json',
  'dmr-inspection-compliance.json',
  'dmr-history-heritage.json',
  'dmr-environmental-profile.json',
  'dmr-body-colour-preferences.json',
  'dmr-engine-extinction.json',
  'dmr-paper-speed.json',
  'dmr-acoustic-profile.json',
  'dmr-model-year-lag.json',
  'dmr-shrinking-engine.json',
  'dmr-weight-power.json',
  'dmr-accident-files.json',
  'dmr-wheelbase-creep.json',
  'dmr-fake-two-seater.json',
  'dmr-tow-it-all.json',
  'dmr-sound-of-silence.json',
  'dmr-track-width-creep.json',
  'dmr-nox-co-honesty.json',
  'dmr-driving-habits.json',
  'dmr-chiptuning-hall.json',
  'dmr-250-club.json',
  'dmr-vintage-leasing.json',
  'dmr-diesel-last-stand.json',
  'dmr-red-car-myth.json',
  'dmr-ghost-fleet.json',
  'dmr-turbocharging-era.json',
  'dmr-brand-invasion.json',
  'dmr-door-seat-matrix.json',
  'dmr-seven-seat-explosion.json',
  'dmr-dormant-fleet.json',
  'dmr-brand-concentration.json',
  'dmr-alphabet-of-brands.json',
];

function defaultVars(dashboard) {
  const vars = {};
  for (const variable of dashboard.templating?.list || []) {
    const current = variable.current?.value ?? variable.current?.text;
    if (current !== undefined) vars[variable.name] = String(current);
  }
  return vars;
}

function interpolate(query, vars) {
  return query
    .replaceAll('${fuel}', vars.fuel || 'All')
    .replaceAll('${year_from}', vars.year_from || '1900')
    .replaceAll('${year_to}', vars.year_to || '2026');
}

function postJson(url, payload) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const body = JSON.stringify(payload);
    const req = http.request(
      {
        hostname: parsed.hostname,
        port: parsed.port || 80,
        path: parsed.pathname,
        method: 'POST',
        headers: {
          Authorization: `Basic ${auth}`,
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(body),
        },
      },
      (res) => {
        let text = '';
        res.setEncoding('utf8');
        res.on('data', (chunk) => {
          text += chunk;
        });
        res.on('end', () => resolve({ status: res.statusCode, text }));
      },
    );
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function queryGrafana(query, panel) {
  const res = await postJson(`${grafanaUrl}/api/ds/query`, {
    from: '1900-01-01T00:00:00Z',
    to: 'now',
    queries: [
      {
        datasource: { type: 'elasticsearch', uid: 'dmr-elasticsearch' },
        intervalMs: 1000,
        maxDataPoints: 1000,
        query,
        queryType: 'esql',
        refId: 'A',
      },
    ],
  });
  let body;
  try {
    body = JSON.parse(res.text);
  } catch {
    throw new Error(`${panel}: HTTP ${res.status}; non-JSON response ${res.text.slice(0, 500)}`);
  }
  const result = body.results?.A;
  if (res.status >= 400 || result?.status >= 400 || result?.error) {
    throw new Error(`${panel}: HTTP ${res.status}; ${JSON.stringify(result || body).slice(0, 1200)}`);
  }
  return result?.frames?.length || 0;
}

const failures = [];
let checked = 0;

for (const file of files) {
  const dashboard = JSON.parse(fs.readFileSync(path.join(dashboardDir, file), 'utf8'));
  const vars = defaultVars(dashboard);
  for (const panel of dashboard.panels || []) {
    for (const target of panel.targets || []) {
      if (target.queryType !== 'esql' || !target.query) continue;
      const label = `${dashboard.uid} / panel ${panel.id} / ${panel.title}`;
      const query = interpolate(target.query, vars);
      checked += 1;
      try {
        const frames = await queryGrafana(query, label);
        console.log(`ok ${label} (${frames} frame${frames === 1 ? '' : 's'})`);
      } catch (error) {
        failures.push(error.message);
        console.error(`fail ${error.message}`);
      }
    }
  }
}

console.log(`checked=${checked} failures=${failures.length}`);
if (failures.length) {
  process.exitCode = 1;
}
